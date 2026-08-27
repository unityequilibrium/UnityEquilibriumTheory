from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def test_curved_parent_work_unlocks_after_topic13_core_ready() -> None:
    artifact = json.loads(GATE.read_text(encoding="utf-8-sig"))
    assert artifact["claim_promotion"] is False
    assert artifact["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"
    curved = artifact["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]
    assert curved["status"] == "UNLOCKED"
    assert curved["depends_on"] == ["T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"]
    assert artifact["topic13_core_ready"]["full_core_unlock"] is True
    assert artifact["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"] == "BLOCKED_DEPENDENCY"
    assert artifact["decisions"]["CONSTITUTIVE_TRANSPORT_CORE_LANE"]["status"] == "BLOCKED_DEPENDENCY"
    assert artifact["decisions"]["GALAXY_COMPATIBILITY_TRACK"]["status"] == "BLOCKED_DEPENDENCY"
