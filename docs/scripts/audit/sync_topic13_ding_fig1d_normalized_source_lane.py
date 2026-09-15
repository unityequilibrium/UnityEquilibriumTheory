"""Synchronize the permitted Ding figure-derived normalized-source lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
FULL_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
LANE_REL = "docs/core/07_artifacts/topic13/t13_ding_fig1d_normalized_source_lane_audit.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
LANE_ID = "T13_DING_FIG1D_NORMALIZED_SOURCE_LANE"
ANCHOR_ID = "T13_DING_C_SRC_INDEPENDENT_REPRODUCTION_BOUNDARY"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def lane_record(major: dict, full_hash: str) -> dict:
    record = {
        field: major.get(field)
        for field in (
            "major_result_id",
            "topic",
            "closure_level",
            "what_is_closed",
            "equation_or_mapping",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "open_blockers",
            "dependency_unlocked",
            "claim_boundary",
        )
    }
    record["evidence_artifacts"] = list(major.get("evidence_artifacts", []))
    record["evidence_artifacts"].append(
        {
            "path": FULL_REL,
            "sha256": full_hash,
            "summary": {
                "projection": "Topic 13 Ding figure-derived normalized comparison lane",
                "raw_author_numeric_source_present": False,
                "full_core_unlock": False,
            },
        }
    )
    return record


def main() -> int:
    register = load(REGISTER_REL)
    full = load(FULL_REL)
    del full
    lane = load(LANE_REL)
    major = lane.get("major_result")
    if not isinstance(major, dict) or major.get("major_result_id") != LANE_ID:
        raise SystemExit("Ding figure-derived lane identity mismatch")

    full_hash = digest(FULL_REL)
    entries = register["entries"]
    record = lane_record(major, full_hash)
    existing = next(
        (item for item in entries if item.get("major_result_id") == LANE_ID),
        None,
    )
    if existing is None:
        anchor_index = next(
            index
            for index, item in enumerate(entries)
            if item.get("major_result_id") == ANCHOR_ID
        )
        entries.insert(anchor_index + 1, record)
    else:
        existing.update(record)

    register["generated_at"] = date.today().isoformat()
    register["claim_promotion"] = False
    register.setdefault("topic13_lane_sync", {})[
        "ding_fig1d_normalized_source_lane"
    ] = {
        "major_result_id": LANE_ID,
        "lane_artifact": {"path": LANE_REL, "sha256": digest(LANE_REL)},
        "full_gate": {"path": FULL_REL, "sha256": full_hash},
        "raw_author_numeric_source_present": False,
        "full_core_unlock": False,
    }
    (ROOT / REGISTER_REL).write_text(
        json.dumps(register, indent=2, ensure_ascii=True) + chr(10),
        encoding="utf-8",
    )

    dependency = load(DEPENDENCY_REL)
    register_hash = digest(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = register_hash
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["register_sha256"] = register_hash
    partial["full_core_unlock"] = False
    partial.setdefault("lane_extensions", {})[
        "ding_fig1d_normalized_source_lane"
    ] = {
        "major_result_id": LANE_ID,
        "closure_level": major.get("closure_level"),
        "status": lane.get("status"),
        "raw_author_numeric_source_present": False,
        "full_core_unlock": False,
        "audit": {"path": LANE_REL, "sha256": digest(LANE_REL)},
    }
    (ROOT / DEPENDENCY_REL).write_text(
        json.dumps(dependency, indent=2, ensure_ascii=True) + chr(10),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS_TOPIC13_DING_FIG1D_SOURCE_LANE_MAJOR_RESULT_SYNC",
                "major_result_id": LANE_ID,
                "full_gate_sha256": full_hash,
                "register_sha256": register_hash,
                "raw_author_numeric_source_present": False,
                "full_core_unlock": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
