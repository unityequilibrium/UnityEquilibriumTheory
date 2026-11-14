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


def test_full_gate_exposes_action_derived_one_loop_branch_without_unlock() -> None:
    full = load(FULL)
    result = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_one_loop_normal_branch"
    ]
    assert result["major_result_id"] == "T13_UET_O2_ONE_LOOP_NORMAL_BRANCH"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["vacuum_counterterm_included"] is False
    assert result["condensate_contribution_included"] is False
    assert result["normal_two_fluid_completion"] is False
    assert result["physical_kubo_coefficient_emitted"] is False
    assert result["alpha_Phi_K_emitted"] is False
    assert result["R_gen_used_as_state"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_and_dependency_preserve_one_loop_boundaries() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_UET_O2_ONE_LOOP_NORMAL_BRANCH"]["closure_level"] == "CLOSED_FOR_LANE"
    assert entries["T13_UET_O2_ONE_LOOP_NORMAL_BRANCH"]["data_role"] == "ACTION_DERIVED_ONE_LOOP_NORMAL_LANE_NOT_FULL_UET_THERMAL_CLOSURE"
    partial = dependency["topic13_partial_evidence"]
    assert partial["uet_o2_one_loop_normal_branch_controller"] == (
        "vacuum_counterterm_and_renormalized_one_loop_response_not_closed"
    )
    assert partial["uet_o2_one_loop_normal_branch_full_core_unlock"] is False
    assert register["claim_promotion"] is False
