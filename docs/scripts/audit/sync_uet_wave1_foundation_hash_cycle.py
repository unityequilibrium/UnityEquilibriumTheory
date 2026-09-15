"""Declare the intentional contract<->foundation hash cycle explicitly."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
FOUNDATION_REL = "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    changed = False
    for evidence in contract.get("rooms", {}).get("core", {}).get("evidence", []):
        if evidence.get("path") == FOUNDATION_REL:
            evidence.pop("sha256", None)
            evidence["hash_policy"] = "LINKED_AFTER_GENERATION; excluded from fixed hash comparison because foundation embeds contract hash"
            changed = True
    contract["hash_cycle_policy"] = {
        "status": "EXPLICIT_LINKED_GENERATION_CYCLE",
        "foundation_gate_embeds_contract_hash": True,
        "contract_embeds_foundation_path_without_hash": True,
        "verification": "foundation.research_room_wave1.contract.sha256 is the controlling linkage; both JSON files are parsed and cross-linked",
    }
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS_HASH_CYCLE_EXPLICIT", "changed": changed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
