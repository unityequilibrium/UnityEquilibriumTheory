"""Audit the named energy-response bridge for Topic 13.

The audit proves the algebra and unit propagation of the ``Phi_E`` branch. It
does not turn the branch into a calibration of the base UET ``Phi`` variable.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.thermal_energy_response_bridge import (  # noqa: E402
    EnergyResponseInputs,
    alpha_phi_e_k,
    alpha_phi_e_uncertainty_K,
    delta_tq_from_delta_u,
    named_energy_response_branch_contract,
    phi_e_from_delta_u,
)


OUT = ROOT / "docs/core/artifacts/t13_energy_response_bridge_audit.json"
SOURCE_PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "graphite_heat_capacity_source_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


PRESERVED_TOP_LEVEL_FIELDS = (
    "source_anchor",
    "cp_cv_correction_contract",
    "standard_pbte_source_anchor",
    "pbte_numeric_input_availability",
)


def merge_prior_artifact(report: dict, prior: dict | None) -> dict:
    """Refresh generated fields without discarding prior provenance detail.

    The bridge audit is also consumed by aggregate Topic 13 registers. Older
    aggregate payloads may contain source anchors and evidence blocks that are
    not reconstructed by this focused formula audit. Preserve those blocks,
    while allowing the current generator to remain authoritative for the
    fields it emits.
    """

    if prior is None:
        return report

    merged = dict(report)
    preserved_top_level = []
    for key in PRESERVED_TOP_LEVEL_FIELDS:
        if key in prior and key not in merged:
            merged[key] = prior[key]
            preserved_top_level.append(key)

    current_major = dict(merged.get("major_result", {}))
    prior_major = dict(prior.get("major_result", {}))
    preserved_major_fields = []
    for key, value in prior_major.items():
        if key not in current_major:
            current_major[key] = value
            preserved_major_fields.append(key)

    prior_closed = prior_major.get("what_is_closed")
    current_closed = current_major.get("what_is_closed")
    if isinstance(prior_closed, list):
        closed = list(prior_closed)
        if isinstance(current_closed, str) and current_closed not in closed:
            closed.append(current_closed)
        elif isinstance(current_closed, list):
            for item in current_closed:
                if item not in closed:
                    closed.append(item)
        current_major["what_is_closed"] = closed

    current_evidence = list(current_major.get("evidence_artifacts", []))
    seen_paths = {
        item.get("path")
        for item in current_evidence
        if isinstance(item, dict) and item.get("path")
    }
    preserved_evidence_paths = []
    for item in prior_major.get("evidence_artifacts", []):
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if path and path not in seen_paths:
            current_evidence.append(item)
            seen_paths.add(path)
            preserved_evidence_paths.append(path)
    current_major["evidence_artifacts"] = current_evidence
    merged["major_result"] = current_major
    merged["artifact_provenance"] = {
        "prior_artifact_preserved": True,
        "preserved_top_level_fields": preserved_top_level,
        "preserved_major_result_fields": preserved_major_fields,
        "preserved_evidence_artifacts": preserved_evidence_paths,
    }
    return merged


def main() -> int:
    package = load(SOURCE_PACKAGE)
    contract = named_energy_response_branch_contract()
    witness_inputs = EnergyResponseInputs(
        e0_J_per_m3=2.0e6,
        cv_J_per_m3_K=5.0e5,
        sigma_e0_J_per_m3=1.0e5,
        sigma_cv_J_per_m3_K=5.0e4,
    )
    delta_u = 5.0e5
    witness_phi_e = phi_e_from_delta_u(delta_u, witness_inputs.e0_J_per_m3)
    witness_delta_tq = delta_tq_from_delta_u(delta_u, witness_inputs.cv_J_per_m3_K)
    witness_alpha = alpha_phi_e_k(witness_inputs)
    witness_sigma_alpha = alpha_phi_e_uncertainty_K(witness_inputs)

    rows = package.get("candidate_rows", [])
    checks = {
        "named_branch_definition_is_explicit": contract["definition"] == "Phi_E := Delta_u / e0",
        "standard_energy_to_temperature_map_is_explicit": (
            contract["standard_map"]
            == "Delta_Tq = Delta_u / c_v = (e0 / c_v) * Phi_E"
        ),
        "alpha_formula_is_implemented": abs(witness_alpha - 4.0) <= 1.0e-12,
        "response_map_is_implemented": abs(witness_delta_tq - witness_alpha * witness_phi_e) <= 1.0e-12,
        "uncertainty_propagation_is_implemented": abs(witness_sigma_alpha - 0.4472135954999579) <= 1.0e-12,
        "base_phi_identity_is_not_asserted": contract["base_Phi_identity"] == "not asserted",
        "base_phi_to_named_branch_remains_open": contract["base_Phi_to_Phi_E_map"] == "OPEN_DERIVATION_OR_CALIBRATION",
        "source_identity_is_recorded": package["source"]["source_id"] == "nist_srd69_graphite_cp",
        "source_locator_is_recorded": bool(package["source"]["source_locator"]),
        "source_rows_have_identity": bool(rows) and all(row.get("source_row_id") for row in rows),
        "source_rows_have_units": bool(rows) and all(row.get("reported_units") for row in rows),
        "source_uncertainty_gap_is_explicit": all(
            row.get("uncertainty", {}).get("status")
            in {
                "NOT_REPORTED_IN_NIST_TABLE",
                "EVALUATED_DEVIATION_BOUND_NOT_MEASUREMENT_UNCERTAINTY",
            }
            for row in rows
        ),
        "evaluated_deviation_not_promoted_to_uncertainty": any(
            row.get("uncertainty", {}).get("status")
            == "EVALUATED_DEVIATION_BOUND_NOT_MEASUREMENT_UNCERTAINTY"
            for row in rows
        ),
        "additional_source_identity_is_recorded": any(
            item.get("source_id") == "nist_scd30_graphite_mcdonald_1965"
            for item in package.get("additional_sources", [])
        ),
        "cv_conversion_gap_is_explicit": (
            package["required_quantity_contract"]["conversion_status"]
            == "OPEN_CP_TO_CV_AND_MOLAR_TO_VOLUMETRIC"
        ),
        "e0_gap_is_explicit": package["energy_scale_contract"]["status"] == "OPEN_NOT_SOURCE_LOCKED",
        "candidate_rows_not_consumed": all(
            row.get("data_role", "").endswith("NOT_CONSUMED") for row in rows
        ),
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "holdout_not_consumed": package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "calibration_path_excludes_holdout": package["holdout_policy"]["calibration_path_may_read_holdout"] is False,
        "no_base_alpha_calibration_emitted": True,
    }
    report = {
        "schema_version": "t13-energy-response-bridge-audit-v1",
        "artifact": "t13_energy_response_bridge_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_NAMED_BRANCH_OPEN_INPUTS" if all(checks.values()) else "FAIL",
        "major_result": {
            "major_result_id": "T13_PHI_E_TTG_BRIDGE_CONDITIONAL",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": "The named Phi_E energy-response branch, standard Delta_u-to-Delta_Tq algebra, explicit units, and independent-input uncertainty propagation are implemented.",
            "equation_or_mapping": {
                "named_response": "Phi_E = Delta_u / e0",
                "standard_observable": "Delta_Tq = Delta_u / c_v",
                "dimensional_bridge": "Delta_Tq = (e0 / c_v) * Phi_E",
                "conditional_alpha": "alpha_Phi_E_K = e0 / c_v",
                "uncertainty": "sigma_alpha/alpha = sqrt((sigma_e0/e0)^2 + (sigma_cv/c_v)^2)",
            },
            "units": {
                "Delta_u": "J m^-3",
                "e0": "J m^-3",
                "c_v": "J m^-3 K^-1",
                "Phi_E": "dimensionless named energy-response coordinate",
                "Delta_Tq": "K",
                "alpha_Phi_E_K": "K per normalized Phi_E",
            },
            "derivation_class": "named-branch algebra with explicit dimensional inputs and first-order uncertainty propagation",
            "observable": "Delta_Tq = alpha_Phi_E_K * Phi_E",
            "data_role": "source identity and formula audit; candidate Cp rows not consumed for calibration",
            "evidence_artifacts": [
                {"path": "docs/core/artifacts/t13_energy_response_bridge_audit.json"},
                {
                    "path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/graphite_heat_capacity_source_package.json",
                    "sha256": sha256(SOURCE_PACKAGE),
                },
            ],
            "verification_status": "PASS_NAMED_BRANCH_OPEN_INPUTS",
            "open_blockers": [
                "volumetric_c_v_not_source_locked",
                "Cp_to_c_v_conversion_not_closed",
                "source_uncertainty_for_c_v_not_reported",
                "e0_energy_density_scale_not_source_locked",
                "base_Phi_to_Phi_E_mapping_not_derived",
                "independent_alpha_Phi_K_calibration_missing",
            ],
            "dependency_unlocked": "named Phi_E formula lane only; no base Phi Kelvin prediction or downstream transport dependency",
            "claim_boundary": "This is a named conditional response branch. It does not identify Phi_E with base Phi, does not calibrate alpha_Phi_K, and does not consume TTG target data or Xie 2026 holdout data.",
        },
        "source_package": {
            "path": str(SOURCE_PACKAGE.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256(SOURCE_PACKAGE),
            "status": package["status"],
            "candidate_quantity": package["required_quantity_contract"]["candidate_quantity"],
            "required_quantity": package["required_quantity_contract"]["required_quantity"],
        },
        "conditional_inputs": {
            "c_v": {"status": "OPEN_CP_TO_CV_UNCERTAINTY", "units": "J m^-3 K^-1"},
            "e0": {"status": "OPEN_NOT_SOURCE_LOCKED", "units": "J m^-3"},
            "base_Phi_to_Phi_E": {
                "status": "OPEN_DERIVATION_OR_CALIBRATION",
                "units": "dimensionless response mapping",
            },
        },
        "checks": checks,
        "witness": {
            "role": "algebra, units, and uncertainty test only; not an external calibration",
            "delta_u_J_per_m3": delta_u,
            "Phi_E": witness_phi_e,
            "Delta_Tq_K": witness_delta_tq,
            "alpha_Phi_E_K_per_normalized_Phi_E": witness_alpha,
            "sigma_alpha_Phi_E_K": witness_sigma_alpha,
        },
        "numeric_calibration": {
            "alpha_Phi_K": None,
            "alpha_Phi_E_K": None,
            "status": "NOT_EMITTED_SOURCE_INPUTS_INCOMPLETE",
        },
        "controlling_blocker": "c_v_e0_and_base_Phi_to_Phi_E_inputs_not_source_locked",
        "next_controller": "source-lock volumetric c_v with uncertainty, independently derive or calibrate e0, and prove the base Phi-to-Phi_E mapping without TTG target residuals or Xie 2026",
        "claim_boundary": "The named energy-response algebra is closed for this lane only; Full Topic 13 remains blocked at dimensional calibration and thermodynamic closure.",
    }
    prior = None
    if OUT.exists():
        prior = load(OUT)
        if (
            prior.get("artifact") != report["artifact"]
            or prior.get("schema_version") != report["schema_version"]
        ):
            raise RuntimeError(
                "refusing to overwrite an existing artifact with a different "
                "artifact identity or schema; resolve the artifact contract first"
            )
        report = merge_prior_artifact(report, prior)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "controlling_blocker": report["controlling_blocker"],
                "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "PASS_NAMED_BRANCH_OPEN_INPUTS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
