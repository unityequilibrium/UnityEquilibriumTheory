from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
AUDIT_REL = "docs/core/artifacts/t13_mp48_temperature_volume_uncertainty_boundary_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_mp48_temperature_volume_boundary_is_scoped_and_passing() -> None:
    package = load(PACKAGE_REL)
    audit = load(AUDIT_REL)
    full = load(FULL_REL)

    assert audit["status"] == "PASS_SCOPED_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["boundary_observations"]["temperature_volume_uncertainty_status"] == "OPEN"
    assert audit["boundary_observations"]["alpha_Phi_K_emitted"] is False
    assert audit["boundary_observations"]["ding_c_src_equivalence_claimed"] is False
    assert audit["boundary_observations"]["source_package_sha256"] == sha256(PACKAGE_REL)
    assert package["holdout_policy"]["xie_2026_accessed"] is False

    projected = full["verification_status"]["source_package"][
        "mp48_temperature_volume_uncertainty_boundary"
    ]
    assert projected["major_result_id"] == "T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["path"] == AUDIT_REL
    assert projected["audit"]["sha256"] == sha256(AUDIT_REL)
    assert any(item["path"] == AUDIT_REL for item in full["evidence_artifacts"])


def test_boundary_does_not_promote_full_topic13_or_downstream_dependencies() -> None:
    full = load(FULL_REL)
    register = load(REGISTER_REL)
    dependency = load(DEPENDENCY_REL)

    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "c_v_source_uncertainty_not_closed" in full["major_result"]["what_remains_open"]
    assert "direct_volumetric_c_v_or_same_state_Cp_source_missing" not in full["major_result"]["what_remains_open"]
    assert any(
        item.get("major_result_id") == "T13_MP48_TEMPERATURE_VOLUME_UNCERTAINTY_BOUNDARY"
        for item in register["entries"]
    )
    assert dependency["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]["status"] == "UNLOCKED"
    assert dependency["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"] == "BLOCKED_DEPENDENCY"
