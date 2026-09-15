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


def test_full_gate_exposes_standard_finite_temperature_comparator_without_unlock() -> None:
    full = load(FULL)
    result = full["verification_status"]["eos_transport_kms_entropy"][
        "standard_o2_finite_temperature_normal_comparator"
    ]
    assert result["major_result_id"] == "T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["physical_uet_eos"] is False
    assert result["physical_kubo_coefficient_emitted"] is False
    assert result["alpha_Phi_K_emitted"] is False
    assert result["R_gen_used_as_state"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_and_dependency_preserve_comparator_boundary() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR"]["closure_level"] == "CLOSED_FOR_LANE"
    assert entries["T13_STANDARD_O2_FINITE_TEMPERATURE_NORMAL_COMPARATOR"]["data_role"] == "STANDARD_THERMAL_QFT_COMPARATOR_NOT_UET_CLOSURE"
    partial = dependency["topic13_partial_evidence"]
    assert partial["standard_o2_finite_temperature_normal_comparator_controller"] == (
        "finite_temperature_UET_effective_action_and_normal_two_fluid_sector_not_derived"
    )
    assert partial["standard_o2_finite_temperature_normal_comparator_full_core_unlock"] is False
    assert register["claim_promotion"] is False
