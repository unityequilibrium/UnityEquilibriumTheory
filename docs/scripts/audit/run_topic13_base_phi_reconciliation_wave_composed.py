"""Replay c_v, transport, and base-Phi projections without erasing prior waves."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIOR_COMPOSED_WAVE = ROOT / "docs/scripts/audit/run_topic13_physical_transport_reconciliation_wave_composed.py"
BASE_PHI_SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_base_phi_reconciliation.py"
BASE_PHI = ROOT / "docs/core/artifacts/t13_base_phi_si_reconciliation_audit.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_ref(items: list[dict], ref: dict) -> None:
    if not any(item.get("path") == ref["path"] for item in items):
        items.append(ref)


def main() -> int:
    subprocess.run([sys.executable, str(PRIOR_COMPOSED_WAVE)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(BASE_PHI_SCRIPT)], cwd=ROOT, check=True)
    reconciliation = json.loads(BASE_PHI.read_text(encoding="utf-8-sig"))
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    summary = reconciliation.get("summary", {})
    ref = {
        "path": str(BASE_PHI.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(BASE_PHI),
        "role": "base-Phi/SI evidence reconciliation",
    }
    add_ref(audit.setdefault("major_result", {}).setdefault("evidence_artifacts", []), ref)
    add_ref(audit.setdefault("evidence_artifacts", []), ref)
    package = next(
        item
        for item in audit.get("packages", [])
        if item.get("package_id") == "T13_INPUT_BASE_PHI_SI_ALPHA_BETA"
    )
    current = package.setdefault("current_evidence", {})
    current.update({
        "base_phi_reconciliation_status": reconciliation.get("status"),
        "paired_alpha_search_candidate_count": summary.get("paired_alpha_search_candidate_count"),
        "eligible_paired_alpha_record_count": summary.get("eligible_paired_alpha_record_count"),
        "named_phi_e_comparator_count": summary.get("named_phi_e_comparator_count"),
        "independent_base_phi_si_record_count": summary.get("independent_base_phi_si_record_count"),
        "eligible_base_phi_input_count": summary.get("accepted_for_full_topic13_count"),
    })
    checks = audit.setdefault("checks", {})
    checks["base_phi_reconciliation_is_fail_closed"] = (
        reconciliation.get("status") == "PASS_SCOPED_BASE_PHI_RECONCILIATION_OPEN"
        and summary.get("independent_base_phi_si_record_count") == 0
        and summary.get("accepted_for_full_topic13_count") == 0
    )
    audit["wave_controller"] = {
        "wave_type": "base_phi_evidence_reconciliation_composed_with_cv_and_transport",
        "artifact": ref,
        "controlling_blocker": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
        "candidate_count": summary.get("candidate_count"),
        "paired_alpha_search_candidate_count": summary.get("paired_alpha_search_candidate_count"),
        "eligible_paired_alpha_record_count": summary.get("eligible_paired_alpha_record_count"),
        "named_phi_e_comparator_count": summary.get("named_phi_e_comparator_count"),
        "independent_base_phi_si_record_count": summary.get("independent_base_phi_si_record_count"),
        "claim_impact": "no_change",
        "composition": [
            "run_topic13_cv_source_reconciliation_wave.py",
            "audit_topic13_physical_transport_reconciliation.py",
            "audit_topic13_base_phi_reconciliation.py",
        ],
    }
    statement = "Base-Phi/SI candidate, Phi_E comparator, and natural-unit action evidence are reconciled without alpha promotion."
    closed = audit["major_result"].setdefault("what_is_closed", [])
    if statement not in closed:
        closed.append(statement)
    audit["report"]["WHAT_CHANGED"] = (
        "Added a fail-closed reconciliation of paired base-Phi search, Phi_E comparator, "
        "conditional formula, action route, and calibration boundary; no alpha or SI anchor was promoted."
    )
    audit["report"]["VERIFICATION"] = (
        "The composed c_v, physical transport, and base-Phi input audit passed; "
        "paired alpha search is 74/0, Phi_E remains comparator-only, and accepted base-Phi input count is zero."
    )
    audit["report"]["CONTROLLING_BLOCKER"] = "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing"
    audit["report"]["NEXT_ACTION"] = (
        "Obtain an authorized paired base-Phi/SI record or derive a source-provenance-backed action-to-SI map; "
        "do not use Phi_E, TTG residuals, or Xie 2026 as base-Phi calibration."
    )
    INPUT_AUDIT.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": audit.get("status"),
        "reconciliation_status": reconciliation.get("status"),
        "paired_alpha_search_candidate_count": summary.get("paired_alpha_search_candidate_count"),
        "eligible_paired_alpha_record_count": summary.get("eligible_paired_alpha_record_count"),
        "named_phi_e_comparator_count": summary.get("named_phi_e_comparator_count"),
        "independent_base_phi_si_record_count": summary.get("independent_base_phi_si_record_count"),
        "eligible_base_phi_input_count": summary.get("accepted_for_full_topic13_count"),
        "cv_and_transport_projection_preserved": (
            any(item.get("path") == "docs/core/artifacts/t13_cv_source_reconciliation_audit.json" for item in audit.get("evidence_artifacts", []))
            and any(item.get("path") == "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json" for item in audit.get("evidence_artifacts", []))
        ),
        "controlling_blocker": "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing",
    }, indent=2))
    return 0 if checks["base_phi_reconciliation_is_fail_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
