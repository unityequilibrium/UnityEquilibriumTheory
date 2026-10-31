from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
GATE = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def test_curved_parent_work_unlocks_after_topic13_core_ready() -> None:
    artifact = json.loads(GATE.read_text(encoding="utf-8-sig"))
    assert artifact["claim_promotion"] is False
    assert artifact["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"
    curved = artifact["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"]
    assert curved["status"] == "UNLOCKED"
    assert curved["depends_on"] == ["T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"]
    assert artifact["topic13_core_ready"]["full_core_unlock"] is True
    assert artifact["decisions"]["GR_CLASSICAL_COMPATIBILITY_LANE"]["status"] == "BLOCKED_DEPENDENCY"
    assert artifact["decisions"]["CONSTITUTIVE_TRANSPORT_CORE_LANE"]["status"] == "BLOCKED_DEPENDENCY"
    assert artifact["decisions"]["GALAXY_COMPATIBILITY_TRACK"]["status"] == "BLOCKED_DEPENDENCY"
    progress = artifact["curved_3p1_progress"]
    assert progress["generalized_harmonic_nonlinear_vacuum_rhs"]["closure_level"] == "CLOSED_FOR_LANE"
    assert progress["generalized_harmonic_periodic_vacuum_evolution"]["closure_level"] == "CLOSED_FOR_LANE"
    assert progress["generalized_harmonic_boundary_characteristics"]["closure_level"] == "CLOSED_FOR_LANE"
    assert progress["generalized_harmonic_boundary_projectors"]["closure_level"] == "CLOSED_FOR_LANE"
    boundary_residuals = progress["generalized_harmonic_linear_boundary_residuals"]
    assert boundary_residuals["closure_level"] == "CLOSED_FOR_LANE"
    assert boundary_residuals["dependency_unlocked"].startswith(
        "local boundary-residual implementation and verification only"
    )
    reduced_tt_sat = progress["generalized_harmonic_reduced_tt_sbp_sat_energy_comparator"]
    assert reduced_tt_sat["closure_level"] == "CLOSED_FOR_LANE"
    assert reduced_tt_sat["dependency_unlocked"].startswith("none;")
    assert progress["parent"]["closure_level"] == "PARTIAL"
    assert progress["topic13_prescribed_matter_wiring"]["closure_level"] == "CLOSED_FOR_LANE"
    assert progress["controlling_blocker"] == (
        "curved_3p1_constraint_preserving_boundaries_and_"
        "dimensional_observable_mapping_missing"
    )
