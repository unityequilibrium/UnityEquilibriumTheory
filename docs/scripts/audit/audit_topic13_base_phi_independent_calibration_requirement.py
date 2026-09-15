"""Audit the Topic 13 base-Phi independent-calibration requirement.

This artifact records an admissible calibration route. It is deliberately an
open requirement, not a calibration result, and it never creates a physical
value for alpha_Phi_K.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_REL = "docs/topics/0.13_Thermodynamic_Bridge/BASE_PHI_INDEPENDENT_CALIBRATION_PROTOCOL.md"
OUT_REL = "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json"

REQUIRED_SNIPPETS = (
    "MAJOR_RESULT_CLOSURE:",
    "WHAT_IS_ACTUALLY_CLOSED:",
    "WHAT_REMAINS_OPEN:",
    "DEPENDENCY_UNLOCKED:",
    "STATUS:",
    "WHAT_CHANGED:",
    "EQUATION_OR_MAPPING:",
    "VERIFICATION:",
    "CONTROLLING_BLOCKER:",
    "NEXT_ACTION:",
    "CLAIM_BOUNDARY:",
    "Phi_E = Delta_u / e0",
    "Phi_E = s_material * Phi_base",
    "alpha_Phi_K = (e0 / c_v) * s_material",
    "Xie 2026",
    "No numerical scale",
)


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def build_artifact(protocol_text: str | None = None) -> dict[str, Any]:
    if protocol_text is None:
        protocol_text = (ROOT / PROTOCOL_REL).read_text(encoding="utf-8-sig")

    checks = {snippet: snippet in protocol_text for snippet in REQUIRED_SNIPPETS}
    protocol_present = (ROOT / PROTOCOL_REL).is_file()
    passed = protocol_present and all(checks.values())
    status = "PASS_OPEN_CALIBRATION_REQUIREMENT" if passed else "FAIL_CALIBRATION_PROTOCOL_CONTRACT"
    major_result = {
        "major_result_id": "T13_BASE_PHI_INDEPENDENT_CALIBRATION_REQUIREMENT",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "OPEN",
        "what_is_closed": [
            "the admissible independent base-Phi calibration route is specified",
            "the required paired SI/base-Phi inputs and provenance fields are explicit",
            "TTG target, Xie 2026 holdout, residuals, and post-inspection tuning are prohibited calibration inputs",
        ],
        "equation_or_mapping": {
            "phi_e_definition": "Phi_E = Delta_u / e0",
            "base_to_named_coordinate": "Phi_E = s_material * Phi_base",
            "conditional_base_alpha": "alpha_Phi_K = (e0 / c_v) * s_material",
            "measurement_operator": "Delta_Tq = alpha_Phi_K * Delta_Phi_base",
        },
        "units": {
            "Delta_u": "J m^-3",
            "e0": "J m^-3",
            "c_v": "J m^-3 K^-1",
            "Phi_base": "dimensionless normalized base Phi",
            "Phi_E": "dimensionless named energy-response coordinate",
            "s_material": "dimensionless scale between named and base coordinates",
            "alpha_Phi_K": "K per normalized base Phi",
            "Delta_Tq": "K or source-defined quasi-temperature unit, as declared by the paired source",
        },
        "derivation_class": "measurement and calibration protocol; no numerical calibration",
        "observable": "paired SI energy/response amplitude and base-Phi amplitude",
        "data_role": "PROTOCOL_NOT_EVIDENCE",
        "evidence_artifacts": [
            {
                "path": PROTOCOL_REL,
                "sha256": sha256(PROTOCOL_REL),
                "summary": {"status": "OPEN_INDEPENDENT_BASE_PHI_CALIBRATION_REQUIRED"},
            }
        ] if protocol_present else [],
        "verification_status": status,
        "open_blockers": [
            "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
            "base_Phi_to_Phi_E_mapping_not_derived",
            "e0_and_c_v_source_package_with_uncertainty_not_locked_for_base_calibration",
        ],
        "dependency_unlocked": "none; full Topic 13 and downstream Core/Gravity gates remain blocked",
        "claim_boundary": "This protocol closes only the acceptance criteria for a future calibration record. It emits no alpha_Phi_K, no prediction, no fit, and no external validation.",
    }
    return {
        "schema_version": "t13-base-phi-independent-calibration-requirement-v1",
        "artifact": "t13_base_phi_independent_calibration_requirement",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "protocol": {
            "path": PROTOCOL_REL,
            "sha256": sha256(PROTOCOL_REL) if protocol_present else None,
            "required_snippets": list(REQUIRED_SNIPPETS),
            "checks": checks,
        },
        "required_record_fields": [
            "source_identity",
            "locator",
            "matched_material_state_geometry",
            "base_Phi_amplitude",
            "SI_energy_or_response_amplitude",
            "units",
            "uncertainty",
            "preprocessing",
            "row_identity",
            "source_hash",
            "independence_statement",
        ],
        "forbidden_calibration_inputs": [
            "Xie 2026 numeric holdout",
            "TTG target residuals",
            "post-inspection parameter tuning",
            "synthetic replacement data",
        ],
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
        "next_controller": "Obtain a permitted paired record or an independently derived base-Phi-to-Phi_E map; do not use the named Phi_E coordinate convention as a base-Phi calibration.",
        "claim_boundary": major_result["claim_boundary"],
    }


def main() -> int:
    artifact = build_artifact()
    out = ROOT / OUT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "artifact": OUT_REL, "controlling_blocker": artifact["controlling_blocker"]}, indent=2))
    return 0 if artifact["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
