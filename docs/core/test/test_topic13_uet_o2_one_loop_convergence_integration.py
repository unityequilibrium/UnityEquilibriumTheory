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


def test_full_gate_exposes_convergence_without_physical_unlock() -> None:
    full = load(FULL)
    result = full["verification_status"]["eos_transport_kms_entropy"][
        "uet_o2_one_loop_convergence"
    ]
    assert result["major_result_id"] == "T13_UET_O2_ONE_LOOP_CONVERGENCE"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["reference"]["cutoff_factor"] == 70.0
    assert result["reference"]["quadrature_order"] == 256
    assert result["policy"]["vacuum_counterterm_included"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_and_dependency_preserve_convergence_boundary() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_UET_O2_ONE_LOOP_CONVERGENCE"]["closure_level"] == "CLOSED_FOR_LANE"
    assert entries["T13_UET_O2_ONE_LOOP_CONVERGENCE"]["data_role"] == "ACTION_DERIVED_NUMERICAL_CONVERGENCE_NOT_PHYSICAL_TRANSPORT"
    partial = dependency["topic13_partial_evidence"]
    assert partial["uet_o2_one_loop_convergence_controller"] == (
        "vacuum_counterterm_and_renormalized_one_loop_response_not_closed"
    )
    assert partial["uet_o2_one_loop_convergence_full_core_unlock"] is False
    assert register["claim_promotion"] is False
