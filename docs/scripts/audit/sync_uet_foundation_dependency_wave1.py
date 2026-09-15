"""Attach the Wave 1 contract to the generated Core dependency gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json"
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
INTEGRATION = ROOT / "docs/core/07_artifacts/gates/uet_research_room_wave1_integration_gate.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    integration = json.loads(INTEGRATION.read_text(encoding="utf-8-sig"))
    evidence = [rel(CONTRACT), rel(INTEGRATION)]
    gate["research_room_wave1"] = {
        "status": contract.get("status"),
        "integration_status": integration.get("status"),
        "claim_promotion": False,
        "contract": {"path": rel(CONTRACT), "sha256": digest(CONTRACT)},
        "integration_gate": {"path": rel(INTEGRATION), "sha256": digest(INTEGRATION)},
        "required_mapping_fields": contract.get("required_mapping_fields"),
        "rooms": {room_id: {"verification_status": room.get("verification_status"), "controlling_blocker": room.get("controlling_blocker"), "next_action": room.get("next_action"), "claim_boundary": room.get("claim_boundary")} for room_id, room in contract.get("rooms", {}).items()},
        "controlling_blockers": contract.get("integration_blockers", []),
        "next_action": integration.get("next_action"),
        "claim_boundary": contract.get("claim_boundary"),
    }
    for gate_id in ("F7_observable_mapping", "F8_data_and_claim"):
        if gate_id in gate.get("gates", {}):
            current = gate["gates"][gate_id].setdefault("evidence", [])
            for path in evidence:
                if path not in current:
                    current.append(path)
    gate.setdefault("source_and_calibration_snapshot", {})["research_room_wave1_status"] = contract.get("status")
    gate["source_and_calibration_snapshot"]["research_room_wave1_claim_promotion"] = False
    gate["source_and_calibration_snapshot"]["research_room_wave1_blockers"] = contract.get("integration_blockers", [])
    gate["claim_ceiling"] = "candidate normalized effective models and explicitly labelled internal/provisional diagnostics; Wave 1 room coordination does not promote physical closure"
    GATE.write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": gate.get("status"), "research_room_wave1": gate["research_room_wave1"]["status"], "claim_promotion": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
