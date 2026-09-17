"""Add the named Topic 13 flux branch to the major-result register."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
BRANCH = ROOT / "docs/core/07_artifacts/verification/matter_space_conserved_flux_telegraph_verification.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    branch = json.loads(BRANCH.read_text(encoding="utf-8-sig"))
    entry = branch.get("major_result")
    if not isinstance(entry, dict):
        raise ValueError("flux branch has no major_result closure record")
    entry["evidence_artifacts"] = [
        {
            "path": rel(BRANCH),
            "sha256": sha256(BRANCH),
            "summary": {
                "status": branch.get("status"),
                "closure_level": entry.get("closure_level"),
            },
        }
    ]
    entries = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != entry.get("major_result_id")
    ]
    insert_at = next(
        (
            index + 1
            for index, item in enumerate(entries)
            if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
        ),
        len(entries),
    )
    entries.insert(insert_at, entry)
    register["entries"] = entries
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": rel(REGISTER),
        "entries": len(entries),
        "added": entry.get("major_result_id"),
        "closure_level": entry.get("closure_level"),
        "evidence_sha256": sha256(BRANCH),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
