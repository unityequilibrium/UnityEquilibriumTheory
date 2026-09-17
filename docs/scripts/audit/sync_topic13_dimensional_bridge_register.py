"""Add the conditional Topic 13 dimensional bridge result to the register."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_dimensional_bridge_contract_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    entry = dict(audit["major_result"])
    entry["evidence_artifacts"] = [
        {
            "path": rel(AUDIT),
            "sha256": sha256(AUDIT),
            "summary": {
                "status": audit["status"],
                "conditional_formula_status": "CLOSED_FOR_LANE",
                "independent_calibration": False,
            },
        }
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
            if item.get("major_result_id") == "T13_ALPHA_PHI_K_NORMALIZED_SCALE_NO_GO"
        ),
        len(entries),
    )
    entries.insert(insert_at, entry)
    register["entries"] = entries
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "artifact": rel(REGISTER),
                "entries": len(entries),
                "added": entry["major_result_id"],
                "closure_level": entry["closure_level"],
                "evidence_sha256": sha256(AUDIT),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
