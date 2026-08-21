from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_full_lbte_boundary_is_archived_without_transport_promotion() -> None:
    audit = load(AUDIT_REL)
    assert audit["status"] == "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN"
    assert audit["major_result"]["major_result_id"] == "T13_CALORINE_FULL_LBTE_NUMERICAL_STABILITY_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["acceptance_for_full_topic13"] is False
    assert audit["checks"]["method0_negative_in_plane_kappa_at_300K"] is True
    assert audit["checks"]["method1_collision_spectrum_positive_semidefinite"] is False
    assert audit["checks"]["method1_and_method0_collision_spectrum_match_at_high_mesh"] is True
    assert audit["checks"]["method1_in_plane_response_positive"] is True
    assert audit["checks"]["latest_method1_mesh_pair_converged"] is False
    assert audit["numerical_contract"]["holdout_accessed"] is False
    assert audit["numerical_contract"]["alpha_Phi_K_fit_performed"] is False


def test_full_gate_and_register_preserve_the_new_boundary() -> None:
    audit = load(AUDIT_REL)
    full = load(FULL_REL)
    register = load(REGISTER_REL)
    lane = full["verification_status"]["source_package"]["calorine_full_lbte_numerical_stability_boundary"]
    assert lane["major_result_id"] == audit["major_result"]["major_result_id"]
    assert lane["status"] == audit["status"]
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["audit"]["path"] == AUDIT_REL
    assert lane["audit"]["sha256"] == sha256(AUDIT_REL)
    assert any(item["path"] == AUDIT_REL for item in full["evidence_artifacts"])
    assert any(
        item.get("major_result_id") == audit["major_result"]["major_result_id"]
        for item in register["entries"]
    )
    assert full["claim_promotion"] is False
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
