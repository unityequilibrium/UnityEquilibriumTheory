"""Add the source-locked c_p anchor to the major-result register."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"


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
                "temperature_K": audit["row_identity"]["temperature_K"],
                "uncertainty_confidence": audit["reported_values"]["uncertainty_confidence"],
                "c_v_status": "OPEN",
            },
        },
        *audit["major_result"]["evidence_artifacts"][1:],
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
            if item.get("major_result_id") == "T13_PHI_E_TTG_BRIDGE_CONDITIONAL"
        ),
        len(entries),
    )
    entries.insert(insert_at, entry)
    register["entries"] = entries
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": rel(REGISTER), "entries": len(entries), "added": entry["major_result_id"], "closure_level": entry["closure_level"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
