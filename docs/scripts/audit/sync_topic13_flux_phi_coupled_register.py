"""Add the Topic 13 coupled C/Phi lane to the major-result register."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
COUPLED = ROOT / "docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    coupled = json.loads(COUPLED.read_text(encoding="utf-8-sig"))
    entry = coupled.get("major_result")
    if not isinstance(entry, dict):
        raise ValueError("coupled branch has no major_result closure record")
    entry["evidence_artifacts"] = [
        {
            "path": rel(COUPLED),
            "sha256": sha256(COUPLED),
            "summary": {
                "status": coupled.get("status"),
                "closure_level": entry.get("closure_level"),
            },
        }
    ]
    entries = [
        item
        for item in register.get("entries", [])
        if item.get("major_result_id") != entry.get("major_result_id")
    ]
    insert_at = next(
        (
            index + 1
            for index, item in enumerate(entries)
            if item.get("major_result_id") == "T13_CAUSAL_FLUX_TELEGRAPH_BRANCH"
        ),
        len(entries),
    )
    entries.insert(insert_at, entry)
    register["entries"] = entries
    REGISTER.write_text(
        json.dumps(register, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "artifact": rel(REGISTER),
        "entries": len(entries),
        "added": entry.get("major_result_id"),
        "closure_level": entry.get("closure_level"),
        "evidence_sha256": sha256(COUPLED),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
