from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_full_gate_exposes_kubo_provenance_without_physical_unlock() -> None:
    full = load(FULL)
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    result = transport["physical_kubo_coefficient_provenance"]
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert result["synthetic_controls_physical"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_and_dependency_keep_result_level_boundaries() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_PHYSICAL_KUBO_COEFFICIENT_PROVENANCE_GATE"]["closure_level"] == "CLOSED_FOR_LANE"
    assert register["claim_promotion"] is False
    partial = dependency["topic13_partial_evidence"]
    assert partial["physical_kubo_coefficient_controller"] == "physical_Kubo_coefficient_record_missing"
    assert partial["full_core_unlock"] is False
