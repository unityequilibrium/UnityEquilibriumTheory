"""Audit the metadata-only Xie 2026 holdout comparison preregistration."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PREREG_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_xie_2026_holdout_comparison_preregistration.json"
ACCESS_REL = "docs/core/artifacts/t13_xie_2026_holdout_access_audit.json"
PROGRESS_REL = "docs/core/artifacts/t13_full_closure_progress.json"
OUT_REL = "docs/core/artifacts/t13_xie_2026_holdout_preregistration_audit.json"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    prereg = load(PREREG_REL)
    access = load(ACCESS_REL)
    progress = load(PROGRESS_REL)
    access_audit = access.get("audit", {})
    holdout = prereg.get("holdout_policy", {})
    gate = prereg.get("access_gate", {})
    equations = prereg.get("major_result", {}).get("equation_or_mapping", {})
    required_ids = {
        item.get("package_id")
        for item in prereg.get("required_preconditions", [])
        if isinstance(item, dict)
    }
    required_root_ids = {
        "T13_INPUT_DING_TTG_SOURCE",
        "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
        "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
    }
    checks = {
        "schema_version_is_declared": prereg.get("schema_version") == "t13-xie-2026-holdout-comparison-preregistration-v1",
        "official_publisher_locator_is_declared": "nature.com/articles/s41467-026-70807-3" in prereg.get("source_metadata", {}).get("publisher_locator", ""),
        "holdout_role_is_declared": prereg.get("source_metadata", {}).get("data_role") == "HOLDOUT",
        "numeric_payload_is_not_archived": prereg.get("source_metadata", {}).get("numeric_payload_archived") is False and prereg.get("source_metadata", {}).get("source_payload_sha256") is None,
        "all_root_preconditions_are_declared": required_root_ids.issubset(required_ids),
        "numeric_access_is_locked": gate.get("allow_numeric_source_read") is False and gate.get("allow_source_archiving") is False and gate.get("allow_curve_digitization") is False,
        "fit_tuning_calibration_are_forbidden": all(gate.get(key) is False for key in ("allow_fit", "allow_tuning", "allow_calibration")),
        "threshold_adjustment_is_forbidden": gate.get("allow_threshold_adjustment") is False,
        "fixed_leakage_threshold_is_inherited": prereg.get("acceptance_metrics", {}).get("pre_arrival_leakage", {}).get("threshold") == 1.0e-6,
        "required_equations_are_declared": equations == {
            "measurement": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
            "uet": "y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)",
            "bridge": "Delta_Tq = alpha_Phi_K * Delta_Phi",
            "source_heat_capacity": "C_src(T) = sum_mu c_mu(T)",
        },
        "existing_access_audit_is_clean": access.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY" and access_audit.get("numeric_payload_consumed") is False and access_audit.get("used_for_calibration") is False and access_audit.get("used_for_fit") is False and access_audit.get("used_for_tuning") is False and access_audit.get("used_for_threshold_adjustment") is False,
        "prereg_holdout_flags_are_clean": all(holdout.get(key) is False for key in ("xie_2026_accessed", "xie_2026_source_data_consumed", "numeric_payload_consumed", "numeric_rows_consumed", "calibration_path_may_read_holdout", "target_fit_performed", "threshold_adjustment_performed")),
        "full_topic_remains_fail_closed": progress.get("canonical_status", {}).get("full_core_unlock") is False and progress.get("canonical_status", {}).get("claim_promotion") is False and progress.get("closure_arithmetic", {}).get("open", 0) > 0,
    }
    status = "PASS_SCOPED_XIE_2026_HOLDOUT_PREREGISTRATION_LOCKED" if all(checks.values()) else "FAIL_XIE_2026_HOLDOUT_PREREGISTRATION"
    evidence = [
        {"path": PREREG_REL, "sha256": sha256(PREREG_REL), "role": "locked metadata-only preregistration"},
        {"path": ACCESS_REL, "sha256": sha256(ACCESS_REL), "role": "existing unconsumed holdout audit"},
        {"path": PROGRESS_REL, "sha256": sha256(PROGRESS_REL), "role": "full Topic 13 fail-closed status"},
    ]
    open_blockers = [
        "all three Topic 13 root input packages remain blocked",
        "Xie numeric payload access is not authorized",
        "no external holdout comparison has been run",
    ]
    major_result = {
        "major_result_id": "T13_XIE_2026_HOLDOUT_COMPARISON_PREREGISTRATION",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "The future comparison protocol, fixed equations, access policy, and inherited leakage threshold are machine-readable.",
            "The preregistration is explicitly metadata-only and contains no numeric holdout payload.",
        ],
        "equation_or_mapping": equations,
        "units": prereg.get("major_result", {}).get("units", {}),
        "derivation_class": "metadata-only holdout preregistration and access-control audit",
        "observable": "holdout access state and future normalized response comparison contract",
        "data_role": "HOLDOUT",
        "evidence_artifacts": evidence,
        "verification_status": status,
        "open_blockers": open_blockers,
        "dependency_unlocked": "Future comparison readiness only; no Full Topic 13 or downstream unlock.",
        "claim_boundary": "This artifact is not an Xie result, prediction, calibration, external validation, or Full Topic 13 closure.",
    }
    report = {
        "MAJOR_RESULT_CLOSURE": "CLOSED_FOR_LANE",
        "WHAT_IS_ACTUALLY_CLOSED": "A metadata-only, no-fit holdout comparison contract is locked.",
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": "Future comparison protocol readiness only.",
        "STATUS": status,
        "WHAT_CHANGED": "Added a machine-readable preregistration without reading or archiving Xie numeric data.",
        "EQUATION_OR_MAPPING": "y_TTG = Delta_Tq(t)/Delta_Tq(0); y_TTG^UET = Delta_Phi(t)/Delta_Phi(0); Delta_Tq = alpha_Phi_K*Delta_Phi.",
        "VERIFICATION": "All fail-closed access, no-fit, no-tuning, threshold, equation, and current-gate checks passed." if status.startswith("PASS") else "One or more fail-closed checks failed.",
        "CONTROLLING_BLOCKER": "holdout_numeric_access_requires_accepted_root_inputs_and_separate_authorization",
        "NEXT_ACTION": "Acquire accepted non-holdout inputs first; do not read Xie numeric data until the access gate changes under a separately authorized comparison.",
        "CLAIM_BOUNDARY": "Preregistration only; not a thermal prediction, external validation, or Full Topic 13 closure.",
    }
    artifact = {
        "schema_version": "t13-xie-2026-holdout-preregistration-audit-v1",
        "artifact": "t13_xie_2026_holdout_preregistration_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "major_result": major_result,
        "checks": checks,
        "evidence_artifacts": evidence,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "numeric_payload_consumed": False,
            "calibration_path_may_read_holdout": False,
            "target_fit_performed": False,
            "threshold_adjustment_performed": False,
        },
        "report": report,
        "claim_promotion": False,
    }
    (ROOT / OUT_REL).write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed_checks": [key for key, value in checks.items() if not value], "artifact": OUT_REL}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
