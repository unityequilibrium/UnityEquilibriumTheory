from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_regularized_lane_is_integrated_without_downstream_unlock() -> None:
    full = load(FULL)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    lane = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_regularized_continuum_heat_current_lane"
    ]
    entry = next(
        item
        for item in register["entries"]
        if item["major_result_id"]
        == "T13_UET_O2_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE"
    )
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["full_core_unlock"] is False
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    assert any(
        item["path"]
        == "docs/core/artifacts/t13_uet_o2_regularized_continuum_heat_current_audit.json"
        for item in entry["evidence_artifacts"]
    )
    assert (
        dependency["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]["status"]
        == "UNLOCKED"
    )
