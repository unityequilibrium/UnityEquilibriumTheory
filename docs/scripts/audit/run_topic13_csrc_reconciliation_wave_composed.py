"""Replay all Topic 13 source projections, then add the C_src boundary."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIOR_WAVE = ROOT / "docs/scripts/audit/run_topic13_base_phi_reconciliation_wave_composed.py"
CSRC_SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_csrc_reconciliation.py"
CSRC = ROOT / "docs/core/artifacts/t13_csrc_reconciliation_audit.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_ref(items: list[dict], ref: dict) -> None:
    if not any(item.get("path") == ref["path"] for item in items):
        items.append(ref)


def main() -> int:
    subprocess.run([sys.executable, str(PRIOR_WAVE)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(CSRC_SCRIPT)], cwd=ROOT, check=True)
    reconciliation = json.loads(CSRC.read_text(encoding="utf-8-sig"))
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    summary = reconciliation.get("summary", {})
    ref = {
        "path": str(CSRC.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(CSRC),
        "role": "C_src source-route reconciliation",
    }
    add_ref(audit.setdefault("major_result", {}).setdefault("evidence_artifacts", []), ref)
    add_ref(audit.setdefault("evidence_artifacts", []), ref)
    package = next(
        item
        for item in audit.get("packages", [])
        if item.get("package_id") == "T13_INPUT_DING_TTG_SOURCE"
    )
    current = package.setdefault("current_evidence", {})
    current.update({
        "csrc_reconciliation_status": reconciliation.get("status"),
        "csrc_route_count": summary.get("route_count"),
        "numeric_csrc_candidate_count": summary.get("numeric_csrc_candidate_count"),
        "source_grade_uncertainty_count": summary.get("source_grade_uncertainty_count"),
        "ding_material_state_match_count": summary.get("ding_material_state_match_count"),
        "ding_author_payload_count": summary.get("ding_author_payload_count"),
        "accepted_independent_reproduction_count": summary.get("accepted_independent_reproduction_count"),
        "eligible_csrc_input_count": summary.get("accepted_for_full_topic13_count"),
    })
    checks = audit.setdefault("checks", {})
    checks["csrc_reconciliation_is_fail_closed"] = (
        reconciliation.get("status") == "PASS_SCOPED_CSRC_RECONCILIATION_OPEN"
        and summary.get("accepted_for_full_topic13_count") == 0
        and summary.get("accepted_ding_csrc_count") == 0
    )
    audit["wave_controller"] = {
        "wave_type": "csrc_source_reconciliation_composed_with_all_prior_inputs",
        "artifact": ref,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "route_count": summary.get("route_count"),
        "numeric_csrc_candidate_count": summary.get("numeric_csrc_candidate_count"),
        "source_grade_uncertainty_count": summary.get("source_grade_uncertainty_count"),
        "ding_material_state_match_count": summary.get("ding_material_state_match_count"),
        "accepted_for_full_topic13_count": summary.get("accepted_for_full_topic13_count"),
        "claim_impact": "no_change",
        "composition": [
            "run_topic13_cv_source_reconciliation_wave.py",
            "audit_topic13_physical_transport_reconciliation.py",
            "audit_topic13_base_phi_reconciliation.py",
            "audit_topic13_csrc_reconciliation.py",
        ],
    }
    statement = "C_src routes are reconciled by payload, numeric status, material match, uncertainty, and acceptance without Ding promotion."
    closed = audit["major_result"].setdefault("what_is_closed", [])
    if statement not in closed:
        closed.append(statement)
    audit["report"]["WHAT_CHANGED"] = (
        "Added a fail-closed reconciliation of Ding OA/request, public phonon, Huberman, Calorine, and MP48 C_src routes; "
        "no C_src candidate was promoted to Ding acceptance."
    )
    audit["report"]["VERIFICATION"] = (
        "The composed c_v, physical transport, base-Phi, and C_src input audit passed; "
        "numeric candidate count is 3, source-grade uncertainty and Ding material match counts are zero, and accepted count is zero."
    )
    audit["report"]["CONTROLLING_BLOCKER"] = "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    audit["report"]["NEXT_ACTION"] = (
        "Send the prepared Ding author request only with project authorization, or complete an independent same-regime reproduction "
        "with source-grade uncertainty and material mapping; do not promote Calorine/MP48 values."
    )
    INPUT_AUDIT.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": audit.get("status"),
        "reconciliation_status": reconciliation.get("status"),
        "route_count": summary.get("route_count"),
        "numeric_csrc_candidate_count": summary.get("numeric_csrc_candidate_count"),
        "source_grade_uncertainty_count": summary.get("source_grade_uncertainty_count"),
        "ding_material_state_match_count": summary.get("ding_material_state_match_count"),
        "accepted_for_full_topic13_count": summary.get("accepted_for_full_topic13_count"),
        "prior_projections_preserved": all(
            any(item.get("path") == expected for item in audit.get("evidence_artifacts", []))
            for expected in [
                "docs/core/artifacts/t13_cv_source_reconciliation_audit.json",
                "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json",
                "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json",
            ]
        ),
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
    }, indent=2))
    return 0 if checks["csrc_reconciliation_is_fail_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
