"""Add the scoped Georgia Tech source-independence no-go to the register."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_volumetric_cp_independence_audit.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    entry = dict(audit["major_result"])
    audit_path = rel(AUDIT)
    entry["evidence_artifacts"] = [
        {
            "path": audit_path,
            "sha256": sha256(AUDIT),
            "summary": {
                "status": audit["status"],
                "scope": "source dependency only",
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
            == "T13_CP_CV_CORRECTION_CONTRACT"
        ),
        len(entries),
    )
    entries.insert(insert_at, entry)
    register["entries"] = entries
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    register["claim_promotion"] = False
    REGISTER.write_text(
        json.dumps(register, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
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
