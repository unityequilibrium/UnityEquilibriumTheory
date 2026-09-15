"""Complete the machine-readable closure fields for the Topic 13 holdout lane."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"


def main() -> int:
    artifact = json.loads(PATH.read_text(encoding="utf-8-sig"))
    major = artifact["major_result"]
    open_blockers = list(major["what_remains_open"])
    completed = {
        "schema_version": artifact["schema_version"],
        "artifact": artifact["artifact"],
        "generated_at": artifact["generated_at"],
        "status": artifact["status"],
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": major["closure_level"],
        "what_is_closed": major["what_is_closed"],
        "what_remains_open": open_blockers,
        "equation_or_mapping": {
            "access_contract": "metadata_only_observed is distinct from numeric_payload_consumed",
            "holdout_rule": "numeric_payload_consumed = used_for_fit = used_for_tuning = used_for_calibration = used_for_threshold_adjustment = false",
        },
        "units": "not applicable; access-control metadata only",
        "derivation_class": "research provenance and access-control audit",
        "observable": "holdout access/consumption state",
        "data_role": "HOLDOUT",
        "verification_status": artifact["verification"],
        "open_blockers": open_blockers,
        "dependency_unlocked": major["dependency_unlocked"],
        "claim_boundary": major["claim_boundary"],
        "major_result": major,
        "source": artifact["source"],
        "audit": artifact["audit"],
        "verification": artifact["verification"],
        "evidence_artifacts": artifact["evidence_artifacts"],
        "controlling_blocker": artifact["controlling_blocker"],
        "next_action": artifact["next_action"],
    }
    PATH.write_text(json.dumps(completed, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print("completed Topic 13 holdout closure schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
