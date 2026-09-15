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


def test_full_gate_exposes_standard_comparator_without_core_unlock() -> None:
    full = load(FULL)
    result = full["verification_status"]["eos_transport_kms_entropy"][
        "standard_graphite_transport_comparator"
    ]
    assert result["major_result_id"] == "T13_GATECH_STANDARD_TRANSPORT_COMPARATOR"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["synthetic_controls_physical"] is False
    assert result["alpha_Phi_K_emitted"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False


def test_register_and_dependency_keep_comparator_boundary() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    entries = {item["major_result_id"]: item for item in register["entries"]}
    assert entries["T13_GATECH_STANDARD_TRANSPORT_COMPARATOR"]["closure_level"] == "CLOSED_FOR_LANE"
    assert entries["T13_GATECH_STANDARD_TRANSPORT_COMPARATOR"]["data_role"] == "STANDARD_MATERIAL_COMPARATOR_NOT_UET_CALIBRATION"
    partial = dependency["topic13_partial_evidence"]
    assert partial["standard_graphite_transport_comparator_controller"] == (
        "standard_comparator_is_not_a_UET_Phi_transport_coefficient_or_Ding_C_src"
    )
    assert partial["full_core_unlock"] is False
    assert register["claim_promotion"] is False
