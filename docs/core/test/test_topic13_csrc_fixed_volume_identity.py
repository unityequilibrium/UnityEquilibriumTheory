from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "core/artifacts/t13_csrc_fixed_volume_identity_audit.json"
GATE = ROOT / (
    "topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_fixed_volume_identity_audit_passes_without_numeric_C_src() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["numeric_C_src_emitted"] is False
    assert audit["numeric_alpha_Phi_K_emitted"] is False
    assert audit["holdout_accessed"] is False
    assert audit["numerical_identity_witness"]["relative_error"] <= 1.0e-8


def test_identity_lane_preserves_Ding_and_UET_ontology_boundary() -> None:
    audit = load(AUDIT)
    equation = audit["major_result"]["equation_or_mapping"]
    assert equation["fixed_volume_identity"].startswith("C_src(T,V)")
    assert "not used to manufacture Ding C_src" in equation["cp_cv_boundary"]
    assert "numeric Ding source" in audit["major_result"]["dependency_unlocked"]


def test_full_gate_and_dependency_register_expose_lane_without_unlock() -> None:
    gate = load(GATE)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    lane = gate["verification_status"]["source_package"][
        "ding_c_src_fixed_volume_identity"
    ]
    assert lane["status"] == "PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert gate["verification_status"]["holdout_integrity"]["holdout_consumed"] is False
    result_ids = {entry["major_result_id"] for entry in register["entries"]}
    assert "T13_DING_C_SRC_FIXED_VOLUME_THERMODYNAMIC_IDENTITY" in result_ids
    partial = dependency["topic13_partial_evidence"]["source_lanes"][
        "ding_c_src_fixed_volume_identity"
    ]
    assert partial["status"] == "PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY"
    assert dependency["topic13_partial_evidence"]["full_core_unlock"] is False
