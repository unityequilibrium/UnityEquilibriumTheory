"""Add the Ding PMC OA numeric-input no-go to the major-result register."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_numeric_input_availability_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    register = load(REGISTER)
    audit = load(AUDIT)
    entry = dict(audit["major_result"])
    audit_path = rel(AUDIT)
    entry["evidence_artifacts"] = [
        {
            "path": audit_path,
            "sha256": sha256(AUDIT),
            "summary": {
                "status": audit["status"],
                "scope": "captured official PMC OA distribution only",
            },
        },
        *audit["major_result"].get("evidence_artifacts", [])[1:],
    ]
    entries = [
        item
        for item in register.get("entries", [])
        if item.get("major_result_id") != entry["major_result_id"]
    ]
    insert_at = next(
        (
            index + 1
            for index, item in enumerate(entries)
            if item.get("major_result_id")
            == "T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING"
        ),
        len(entries),
    )
    entries.insert(insert_at, entry)
    register["entries"] = entries
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    register["claim_promotion"] = False
    REGISTER.write_text(
        json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact": rel(REGISTER),
                "entries": len(entries),
                "added": entry["major_result_id"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
