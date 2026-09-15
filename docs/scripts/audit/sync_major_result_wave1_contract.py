"""Attach the major-result contract and register to the Wave 1 contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WAVE1 = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
CONTRACT = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_contract.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    wave1 = json.loads(WAVE1.read_text(encoding="utf-8-sig"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    wave1["major_result_reporting"] = {
        "contract": {
            "path": rel(CONTRACT),
            "sha256": sha256(CONTRACT),
            "schema_version": contract["schema_version"],
        },
        "register": {
            "path": rel(REGISTER),
            "sha256": sha256(REGISTER),
            "generated_at": register["generated_at"],
        },
        "required_fields": contract["required_fields"],
        "closure_levels": contract["closure_levels"],
        "claim_promotion": False,
        "rule": "major result closure is progress evidence; PASS/WARN/BLOCKED remains verification state",
    }
    wave1["generated_at"] = date.today().isoformat()
    WAVE1.write_text(json.dumps(wave1, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": rel(WAVE1), "major_result_reporting": wave1["major_result_reporting"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
