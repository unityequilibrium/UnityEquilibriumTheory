"""Add the mp-48 lane as an explicit major-result register entry."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def main() -> int:
    audit = load(AUDIT_REL)
    package = load(PACKAGE_REL)
    if audit.get("status") != "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE":
        raise SystemExit(f"unexpected mp-48 audit status: {audit.get('status')}")
    register = load(REGISTER_REL)
    register["generated_at"] = date.today().isoformat()
    if not any(item.get("major_result_id") == "T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION" for item in register["entries"]):
        register["entries"].append({
            "major_result_id": "T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": package["major_result"]["what_is_closed"],
            "equation_or_mapping": package["major_result"]["equation_or_mapping"],
            "units": package["major_result"]["units"],
            "derivation_class": package["major_result"]["derivation_class"],
            "observable": package["major_result"]["observable"],
            "data_role": package["major_result"]["data_role"],
            "evidence_artifacts": [
                evidence(AUDIT_REL, {"status": audit["status"]}),
                evidence(PACKAGE_REL, {"status": package["status"]}),
            ],
            "verification_status": audit["status"],
            "open_blockers": package["major_result"]["open_blockers"],
            "dependency_unlocked": package["major_result"]["dependency_unlocked"],
            "claim_boundary": package["claim_boundary"],
        })
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    for item in full_entry.get("evidence_artifacts", []):
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    dependency.setdefault("topic13_partial_evidence", {})["register_sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "PASS_MP48_MAJOR_RESULT_REGISTERED",
        "entry_present": any(item.get("major_result_id") == "T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION" for item in register["entries"]),
        "register_sha256": digest(REGISTER_REL),
        "dependency_register_sha256": dependency["register"]["sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
