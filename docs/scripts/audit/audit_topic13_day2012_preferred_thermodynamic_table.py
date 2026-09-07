"""Audit the Day 2012 preferred thermodynamic table as a scoped route boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "day_2012_preferred_thermodynamic_table_source_package.json"
)
OUT = ROOT / "docs/core/artifacts/t13_day2012_preferred_thermodynamic_table_boundary_audit.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    package = load(PACKAGE_REL)
    source = package["source"]
    table = package["table_transcription"]
    graphite = table["graphite"]
    acceptance = package["acceptance_contract"]
    holdout = package["holdout_policy"]

    checks = {
        "source_is_day_2012_table": source["source_id"] == "day_2012_revised_diamond_graphite_transition",
        "publisher_locator_present": source["publisher_locator"].startswith("https://"),
        "table_locator_present": source["primary_table_locator"] == "Table 2, printed page 56",
        "graphite_B0_value_and_uncertainty_present": graphite["B0_kbar"]["value"] == 338.0 and graphite["B0_kbar"]["two_sigma"] == 30.0,
        "graphite_dB_dT_value_and_uncertainty_present": graphite["dB_dT_kbar_per_K"]["value"] == -0.07 and graphite["dB_dT_kbar_per_K"]["two_sigma"] == 0.02,
        "graphite_alpha_function_present": bool(graphite["thermal_expansion_expression"]),
        "alpha_uncertainty_boundary_is_explicit": graphite["thermal_expansion_a0_uncertainty_status"] == "NOT_REPORTED_IN_TABLE",
        "assessment_is_not_same_specimen_pair": acceptance["same_specimen_pair_established"] is False,
        "direct_same_state_K_T_is_not_claimed": acceptance["K_T_is_direct_same_state_measurement"] is False,
        "ding_material_mapping_remains_open": acceptance["Ding_material_regime_mapping_closed"] is False,
        "no_cp_cv_correction_emitted": acceptance["numeric_cp_cv_correction_emitted"] is False,
        "full_topic13_not_accepted": acceptance["accepted_for_full_topic13"] is False,
        "alpha_calibration_not_accepted": acceptance["accepted_for_alpha_Phi_K_calibration"] is False,
        "ding_csrc_not_accepted": acceptance["accepted_for_Ding_C_src"] is False,
        "holdout_is_unconsumed": all(value is False for value in holdout.values()),
    }
    status = (
        "PASS_SCOPED_DAY2012_THERMODYNAMIC_ASSESSMENT_BOUNDARY_NO_GO"
        if all(checks.values())
        else "FAIL_DAY2012_THERMODYNAMIC_ASSESSMENT_BOUNDARY_AUDIT"
    )

    report = {
        "schema_version": "t13-day2012-preferred-thermodynamic-table-boundary-v1",
        "artifact": "t13_day2012_preferred_thermodynamic_table_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DAY2012_PREFERRED_THERMODYNAMIC_ASSESSMENT_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "ontology": package["ontology"],
            "formula_contract": package["formula_contract"],
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": "The Day 2012 Table 2 route is source-locked as a published thermodynamic assessment with a graphite bulk-modulus value and uncertainty, a temperature-dependent bulk-modulus formula, and an explicit graphite thermal-expansion function. The route is closed as a source-grade boundary because the table does not report uncertainty for the alpha function, does not establish a same-specimen alpha_V/K_T pair, and does not establish Ding TTG material equivalence.",
            "equation_or_mapping": {
                "graphite_volume_expansion": "V(T)/V0 = 1 + a0*(T - 298) - 20*a0*(sqrt(T) - sqrt(298))",
                "bulk_modulus_temperature": "K_T(T) = B(T) = B0 + Bprime*(T - 298)",
                "cp_cv_correction_contract": "c_p^V - c_v^V = T * alpha_V^2 * K_T",
                "numeric_correction_emitted": False
            },
            "units": {
                "temperature": "K",
                "V0": "J bar^-1",
                "B0_and_K_T": "kbar (converted to Pa only under a declared SI map)",
                "dB_dT": "kbar K^-1",
                "alpha_V": "K^-1"
            },
            "derivation_class": "published table transcription and source-compatibility boundary; no UET derivation",
            "observable": "graphite thermal-expansion and bulk-modulus inputs for a Cp-to-Cv correction",
            "data_role": "SOURCE_PROVENANCE_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {
                    "role": "day2012_source_package",
                    "path": PACKAGE_REL,
                    "sha256": sha256(PACKAGE_REL)
                },
                {
                    "role": "day2012_publisher_locator",
                    "locator": source["publisher_locator"],
                    "table_locator": source["primary_table_locator"]
                }
            ],
            "verification_status": status,
            "open_blockers": [
                "same_grade_alpha_V_and_K_T_missing",
                "alpha_V_source_uncertainty_not_reported",
                "material_regime_mapping_to_TTG_not_closed",
                "c_v_source_uncertainty_not_closed",
                "alpha_Phi_K_independent_calibration_missing"
            ],
            "dependency_unlocked": "Day 2012 route-level thermodynamic-assessment boundary only; no Cp-to-Cv input closure, Ding C_src, alpha_Phi_K, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This result does not claim that no future alpha_V/K_T source exists. It closes only the screened Day 2012 assessment route under the current source-grade acceptance contract."
        },
        "source": {
            "source_id": source["source_id"],
            "doi": source["doi"],
            "publisher_locator": source["publisher_locator"],
            "primary_table_locator": source["primary_table_locator"],
            "payload_state": source["payload_state"],
            "package_sha256": sha256(PACKAGE_REL)
        },
        "assessment_values": {
            "B0_kbar": graphite["B0_kbar"],
            "dB_dT_kbar_per_K": graphite["dB_dT_kbar_per_K"],
            "thermal_expansion_a0_K_minus_1": graphite["thermal_expansion_a0_K_minus_1"],
            "thermal_expansion_a0_uncertainty_status": graphite["thermal_expansion_a0_uncertainty_status"]
        },
        "acceptance": acceptance,
        "checks": checks,
        "controlling_blocker": "same_grade_alpha_V_and_K_T_missing",
        "next_controller": "Acquire a permitted same-state alpha_V and isothermal K_T record with row/state uncertainty and Ding-regime mapping, or obtain an independent SI Phi anchor. Do not combine the Day assessment with a different specimen or infer alpha_Phi_K.",
        "claim_boundary": "No numeric Cp-to-Cv correction, Ding C_src, alpha_Phi_K, TTG prediction, or Full Topic 13 closure is emitted."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
