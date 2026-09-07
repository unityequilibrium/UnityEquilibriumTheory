"""Audit the Kim 2018 graphite Green-Kubo external-input boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/kim_2018_graphite_green_kubo_source_package.json"
OUT = ROOT / "docs/core/artifacts/t13_kim_2018_graphite_green_kubo_external_input_audit.json"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    package = load(PACKAGE_PATH)
    source = package["source"]
    payload = package["source_payload"]
    state = payload["state"]
    rows = payload["coefficient_rows"]
    computed_hash = canonical_hash(payload)
    checks = {
        "source_identity_and_doi_present": bool(source["source_id"] == payload["source_id"] and source["doi"]),
        "publisher_and_public_locator_present": bool(source["publisher_locator"] and source["public_text_locator"]),
        "method_formula_locator_present": payload["formula_locator"] == "Eq. (2)",
        "uncertainty_formula_locator_present": payload["uncertainty_formula_locator"] == "Eq. (3)",
        "state_temperature_present": state["temperature_K"] == 300.0,
        "material_and_geometry_present": state["material"] == "pristine graphite" and state["model_cell_conventional_units"] == [14, 8, 8],
        "trajectory_and_convergence_metadata_present": state["nve_time_ns"] == 10.0 and state["minimum_trajectory_count"] >= 10 and payload["convergence_evidence"]["integration_time_convergence_reported"],
        "coefficient_rows_have_identity_units_uncertainty": all(
            row.get("row_id") and row.get("coefficient_name") and row.get("units") == "W m^-1 K^-1"
            and isinstance(row.get("value"), (int, float)) and isinstance(row.get("uncertainty"), (int, float))
            for row in rows
        ),
        "coefficient_rows_are_directionally_distinct": {row["direction"] for row in rows} == {"c_axis", "basal_plane"},
        "source_hash_matches_payload": source["source_payload_sha256"] == computed_hash,
        "external_input_not_uet_relabelled": package["acceptance"]["accepted_for_external_transport_input"] is True and package["acceptance"]["accepted_for_uet_physical_kubo_coefficient"] is False,
        "no_ding_or_alpha_promotion": package["acceptance"]["accepted_for_ding_C_src"] is False and package["acceptance"]["accepted_for_alpha_Phi_K_calibration"] is False,
        "holdout_untouched": all(value is False for key, value in package["holdout_policy"].items() if key != "calibration_path_may_read_holdout") and package["holdout_policy"]["calibration_path_may_read_holdout"] is False,
        "no_fit_or_threshold_change": package["holdout_policy"]["fit_performed"] is False and package["holdout_policy"]["alpha_Phi_K_fit_used"] is False and package["holdout_policy"]["threshold_changed"] is False,
    }
    status = (
        "PASS_SCOPED_SOURCE_LOCKED_EXTERNAL_GREEN_KUBO_INPUT"
        if all(checks.values())
        else "FAIL_KIM_2018_EXTERNAL_GREEN_KUBO_INPUT_AUDIT"
    )
    report = {
        "schema_version": "t13-kim2018-graphite-green-kubo-external-input-audit-v1",
        "artifact": "t13_kim_2018_graphite_green_kubo_external_input_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_KIM_2018_GRAPHITE_GREEN_KUBO_EXTERNAL_INPUT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "Kim 2018 pristine-graphite Green-Kubo source identity and method locators are source-locked in a bounded transcription package",
                "directional 300 K conductivity rows retain source-reported uncertainty and row identity",
                "integration-time, trajectory-ensemble, and half-timestep convergence disclosures are machine-readable",
                "the coefficient is admitted only as an external standard-physics transport input, not as a UET Phi coefficient"
            ],
            "what_remains_open": [
                "UET Phi or normalized space-response mapping for the external coefficient",
                "Ding TTG material/state equivalence and mode-resolved C_src",
                "raw heat-current correlator payload and source-grade uncertainty reproduction",
                "independent alpha_Phi_K and Full Topic 13 closure"
            ],
            "dependency_unlocked": "external standard-physics transport-input lane only; no UET physical transport, alpha, Ding C_src, Core, Gravity, or Full Topic 13 dependency unlock",
            "equation_or_mapping": {
                "green_kubo": payload["green_kubo_formula"],
                "external_record": "KuboCoefficientRecord_external -> directional lattice transport comparator only",
                "uet_mapping": "not emitted: Phi response and base-Phi amplitude remain open"
            },
            "units": {
                "coefficient": "W m^-1 K^-1",
                "temperature": "K",
                "space_response": "directional heat-current response; no normalized UET Phi unit",
                "source_hash": "SHA-256 of canonical local transcription payload"
            },
            "derivation_class": "source-locked external Green-Kubo transcription; no UET derivation",
            "observable": "standard-physics directional graphite thermal conductivity",
            "data_role": "EXTERNAL_INPUT_COMPARATOR_NOT_UET_CALIBRATION",
            "evidence_artifacts": [
                {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/kim_2018_graphite_green_kubo_source_package.json"},
                {"path": "docs/scripts/audit/audit_topic13_kim_2018_graphite_green_kubo_external_input.py"}
            ],
            "verification_status": status,
            "open_blockers": ["UET_space_response_and_base_Phi_mapping_missing"],
            "claim_boundary": package["claim_boundary"]
        },
        "source": {
            "source_id": source["source_id"],
            "doi": source["doi"],
            "source_payload_sha256": computed_hash,
            "payload_hash_matches_declared": checks["source_hash_matches_payload"],
            "payload_state": source["payload_state"],
            "material_regime_status": source["material_regime_status"]
        },
        "coefficient_rows": rows,
        "checks": checks,
        "acceptance": package["acceptance"],
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": "UET_space_response_and_base_Phi_mapping_missing",
        "next_controller": "derive or independently source-lock a UET space-response/Phi map; retain Kim 2018 only as an external standard-physics transport input until that mapping exists",
        "claim_boundary": package["claim_boundary"]
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "source_payload_sha256": computed_hash,
        "failed_checks": [key for key, value in checks.items() if not value],
        "accepted_for_uet_physical_kubo_coefficient": package["acceptance"]["accepted_for_uet_physical_kubo_coefficient"],
    }, indent=2))
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
