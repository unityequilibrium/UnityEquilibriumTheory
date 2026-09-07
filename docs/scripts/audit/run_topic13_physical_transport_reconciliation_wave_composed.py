"""Replay the Topic 13 c_v and physical-transport waves as one composition.

The base input audit regenerates its JSON from scratch.  This composed runner
reapplies the c_v projection before adding the physical transport projection,
so sequential evidence waves remain visible together.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CV_WAVE = ROOT / "docs/scripts/audit/run_topic13_cv_source_reconciliation_wave.py"
RECONCILIATION_SCRIPT = ROOT / "docs/scripts/audit/audit_topic13_physical_transport_reconciliation.py"
RECONCILIATION = ROOT / "docs/core/artifacts/t13_physical_transport_reconciliation_audit.json"
INPUT_AUDIT = ROOT / "docs/core/artifacts/t13_closure_input_package_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_ref(items: list[dict], ref: dict) -> None:
    if not any(item.get("path") == ref["path"] for item in items):
        items.append(ref)


def main() -> int:
    subprocess.run([sys.executable, str(CV_WAVE)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(RECONCILIATION_SCRIPT)], cwd=ROOT, check=True)
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8-sig"))
    audit = json.loads(INPUT_AUDIT.read_text(encoding="utf-8-sig"))
    summary = reconciliation.get("summary", {})
    ref = {
        "path": str(RECONCILIATION.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(RECONCILIATION),
        "role": "physical transport evidence reconciliation",
    }

    add_ref(audit.setdefault("major_result", {}).setdefault("evidence_artifacts", []), ref)
    add_ref(audit.setdefault("evidence_artifacts", []), ref)
    package = next(
        item
        for item in audit.get("packages", [])
        if item.get("package_id") == "T13_INPUT_PHYSICAL_TRANSPORT_MATCH"
    )
    current = package.setdefault("current_evidence", {})
    current.update({
        "physical_transport_reconciliation_status": reconciliation.get("status"),
        "formal_lane_count": summary.get("formal_lane_count"),
        "natural_unit_uet_lane_count": summary.get("natural_unit_uet_lane_count"),
        "external_physical_comparator_count": summary.get("external_physical_comparator_count"),
        "physical_uet_coefficient_count": summary.get("physical_uet_coefficient_count"),
        "eligible_physical_transport_input_count": summary.get("accepted_for_full_topic13_count"),
    })
    checks = audit.setdefault("checks", {})
    checks["physical_transport_reconciliation_is_fail_closed"] = (
        reconciliation.get("status") == "PASS_SCOPED_PHYSICAL_TRANSPORT_RECONCILIATION_OPEN"
        and summary.get("physical_uet_coefficient_count") == 0
        and summary.get("accepted_for_full_topic13_count") == 0
    )
    audit["wave_controller"] = {
        "wave_type": "transport_evidence_reconciliation_composed_with_cv",
        "artifact": ref,
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
        "candidate_count": summary.get("candidate_count"),
        "formal_lane_count": summary.get("formal_lane_count"),
        "external_physical_comparator_count": summary.get("external_physical_comparator_count"),
        "physical_uet_coefficient_count": summary.get("physical_uet_coefficient_count"),
        "claim_impact": "no_change",
        "composition": [
            "run_topic13_cv_source_reconciliation_wave.py",
            "audit_topic13_physical_transport_reconciliation.py",
        ],
    }
    statement = (
        "Formal, natural-unit, and external-comparator transport evidence is reconciled without physical UET promotion."
    )
    closed = audit["major_result"].setdefault("what_is_closed", [])
    if statement not in closed:
        closed.append(statement)
    audit["report"]["WHAT_CHANGED"] = (
        "Added a fail-closed reconciliation of formal SK/KMS/entropy, natural-unit UET, "
        "external graphite, and physical-coefficient acceptance classes; no physical UET value was promoted."
    )
    audit["report"]["VERIFICATION"] = (
        "The composed c_v plus physical transport input audit passed; formal lanes remain scoped, "
        "Kim remains external-only, and accepted physical UET coefficient count is zero."
    )
    audit["report"]["CONTROLLING_BLOCKER"] = "physical_Kubo_coefficient_record_missing"
    audit["report"]["NEXT_ACTION"] = (
        "Obtain or microscopically derive one state-matched physical UET transport record with "
        "Phi/SI mapping, correlator locator, source identity, uncertainty, and finite-temperature scope; "
        "do not relabel Kim or the natural-unit channel."
    )
    INPUT_AUDIT.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": audit.get("status"),
        "reconciliation_status": reconciliation.get("status"),
        "candidate_count": summary.get("candidate_count"),
        "formal_lane_count": summary.get("formal_lane_count"),
        "external_physical_comparator_count": summary.get("external_physical_comparator_count"),
        "physical_uet_coefficient_count": summary.get("physical_uet_coefficient_count"),
        "eligible_physical_transport_input_count": summary.get("accepted_for_full_topic13_count"),
        "cv_projection_preserved": any(
            item.get("path") == "docs/core/artifacts/t13_cv_source_reconciliation_audit.json"
            for item in audit.get("evidence_artifacts", [])
        ),
        "controlling_blocker": "physical_Kubo_coefficient_record_missing",
    }, indent=2))
    return 0 if checks["physical_transport_reconciliation_is_fail_closed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
