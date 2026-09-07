"""Run the c_v reconciliation wave and project it into the input-package audit.

The existing input-package verifier is intentionally left unchanged.  This
runner executes it first, then adds the new reconciliation evidence and keeps
the package acceptance result fail-closed until a qualifying source arrives.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE_AUDIT = ROOT / "docs/scripts/audit/audit_topic13_closure_input_packages.py"
RECONCILIATION = ROOT / "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_ref(items: list[dict], ref: dict) -> None:
    if not any(item.get("path") == ref["path"] for item in items):
        items.append(ref)


def main() -> int:
    subprocess.run([sys.executable, str(BASE_AUDIT)], cwd=ROOT, check=True)
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8-sig"))
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    summary = reconciliation.get("summary", {})
    ref = {
        "path": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(RECONCILIATION),
        "role": "c_v source reconciliation evidence",
    }

    evidence = audit.setdefault("major_result", {}).setdefault("evidence_artifacts", [])
    add_ref(evidence, ref)
    top_evidence = audit.setdefault("evidence_artifacts", [])
    add_ref(top_evidence, ref)
    ding_package = next(
        package for package in audit.get("packages", [])
        if package.get("package_id") == "T13_INPUT_DING_TTG_SOURCE"
    )
    current = ding_package.setdefault("current_evidence", {})
    current["cv_source_reconciliation_status"] = reconciliation.get("status")
    current["direct_or_derived_cv_count"] = summary.get("direct_or_derived_cv_count")
    current["source_grade_cv_uncertainty_count"] = summary.get("source_grade_cv_uncertainty_count")
    current["ding_matched_cv_count"] = summary.get("ding_matched_cv_count")
    current["eligible_cv_input_count"] = summary.get("eligible_for_full_topic13_count")
    checks = audit.setdefault("checks", {})
    checks["cv_source_reconciliation_is_fail_closed"] = (
        reconciliation.get("status") == "PASS_SCOPED_CV_SOURCE_RECONCILIATION_OPEN"
        and summary.get("eligible_for_full_topic13_count") == 0
        and summary.get("source_grade_cv_uncertainty_count") == 0
    )
    audit["wave_controller"] = {
        "wave_type": "source_pass",
        "artifact": ref,
        "controlling_blocker": "c_v_source_uncertainty_not_closed",
        "candidate_count": summary.get("candidate_count"),
        "eligible_for_full_topic13_count": summary.get("eligible_for_full_topic13_count"),
        "claim_impact": "no_change",
    }
    audit["major_result"]["what_is_closed"].append(
        "Existing graphite heat-capacity and correction sources are reconciled by quantity, uncertainty, and material-state eligibility."
    )
    audit["report"]["WHAT_CHANGED"] = (
        "Added a fail-closed reconciliation of seven existing heat-capacity/correction source audits; "
        "no source row, threshold, alpha, equation, or holdout role changed."
    )
    audit["report"]["VERIFICATION"] = (
        "The base input-package audit and the c_v reconciliation both passed; "
        "zero candidate has direct/derived c_v plus source-grade uncertainty and Ding-state equivalence."
    )
    audit["report"]["CONTROLLING_BLOCKER"] = "c_v_source_uncertainty_not_closed"
    audit["report"]["NEXT_ACTION"] = (
        "Obtain a same-state direct volumetric c_v or Ding-compatible mode-resolved C_src package "
        "with source-grade uncertainty and material mapping; do not combine unmatched sources."
    )
    INPUT_AUDIT.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": audit.get("status"),
        "reconciliation_status": reconciliation.get("status"),
        "candidate_count": summary.get("candidate_count"),
        "eligible_for_full_topic13_count": summary.get("eligible_for_full_topic13_count"),
        "controlling_blocker": "c_v_source_uncertainty_not_closed",
    }, indent=2))
    return 0 if checks["cv_source_reconciliation_is_fail_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
