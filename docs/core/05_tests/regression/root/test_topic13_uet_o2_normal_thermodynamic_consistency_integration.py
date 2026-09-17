from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_normal_consistency_is_integrated_without_unlock() -> None:
    result_id = "T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY"
    full = load(FULL)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    lane = full["verification_status"]["eos_transport_kms_entropy"]["uet_o2_normal_thermodynamic_consistency"]
    assert lane["major_result_id"] == result_id
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert any(item.get("major_result_id") == result_id for item in register["entries"])
    partial = dependency["topic13_partial_evidence"]
    assert partial["uet_o2_normal_thermodynamic_consistency"]["summary"]["major_result_id"] == result_id
    assert partial["uet_o2_normal_thermodynamic_consistency_full_core_unlock"] is False
    assert dependency["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"
    assert full["claim_promotion"] is False
