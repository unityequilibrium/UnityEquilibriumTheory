from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_full_gate_exposes_transport_boundary_without_physical_unlock() -> None:
    full = load(FULL)
    result = full["verification_status"]["eos_transport_kms_entropy"][
        "covariant_transport_implementation_boundary"
    ]
    assert result["major_result_id"] == "T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert result["temperature_scope"] == "T_ZERO_PURE_SUPERFLUID_ONLY"
    assert result["si_lane"] == "BLOCKED"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_and_dependency_preserve_transport_blocker() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY"]["closure_level"] == "CLOSED_FOR_LANE"
    assert entries["T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY"]["data_role"] == "INTERNAL_IMPLEMENTATION_SCOPE_NOT_PHYSICAL_TRANSPORT"
    partial = dependency["topic13_partial_evidence"]
    assert partial["covariant_transport_implementation_controller"] == "physical_Kubo_coefficient_record_missing"
    assert partial["covariant_transport_implementation_full_core_unlock"] is False
    assert register["claim_promotion"] is False
