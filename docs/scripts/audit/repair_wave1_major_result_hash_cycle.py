"""Repair generated Wave 1 hash links after major-result artifact updates."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
FOUNDATION = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
BRIEF = ROOT / "docs/core/UET_RESEARCH_ROOM_BRIEF.md"
MAJOR_CONTRACT = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_contract.json"
MAJOR_REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    foundation = json.loads(FOUNDATION.read_text(encoding="utf-8-sig"))
    brief_hash = digest(BRIEF)
    contract["brief"]["sha256"] = brief_hash
    reporting = contract["major_result_reporting"]
    reporting["contract"]["sha256"] = digest(MAJOR_CONTRACT)
    reporting["register"]["sha256"] = digest(MAJOR_REGISTER)
    for room in contract.get("rooms", {}).values():
        for evidence in room.get("evidence", []):
            path_text = evidence.get("path")
            if not evidence.get("present") or not path_text:
                continue
            if "EXCLUDED" in str(evidence.get("hash_policy", "")).upper():
                evidence.pop("sha256", None)
                continue
            path = ROOT / path_text
            if path.is_file():
                evidence["sha256"] = digest(path)
    contract["generated_at"] = date.today().isoformat()
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    foundation.setdefault("research_room_wave1", {}).setdefault("contract", {})["sha256"] = digest(CONTRACT)
    FOUNDATION.write_text(json.dumps(foundation, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"contract_sha256": digest(CONTRACT), "foundation_link_updated": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
