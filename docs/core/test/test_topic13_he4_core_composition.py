from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_he4_core_thermodynamic_bridge_composition_audit.json"


def test_he4_thermodynamic_bridge_composition_is_core_ready() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_CORE"
    assert audit["major_result"]["open_blockers"] == []
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_composition_keeps_state_and_claim_boundaries_explicit() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    interface = audit["state_interface"]
    assert interface["natural_action_state"]["temperature"] != interface["physical_he4_state"]["temperature_K"]
    assert all(interface["natural_state_checks"].values())
    assert all(interface["physical_state_checks"].values())
    assert all(interface["mapping_checks"].values())
    assert "not graphite TTG validation" in audit["major_result"]["claim_boundary"]
