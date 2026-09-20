from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

from docs.core.uet_o2_regularized_continuum_heat_current import (
    regularized_continuum_heat_current_state,
)


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_regularized_continuum_heat_current_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_regularized_continuum_heat_current_lane_passes_without_promotion() -> None:
    artifact = load(ARTIFACT)
    state = regularized_continuum_heat_current_state(0.22, 0.35, 0.15)
    assert artifact["status"] == "PASS_ACTION_DERIVED_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["claim_promotion"] is False
    assert artifact["full_core_unlock"] is False
    assert state.continuum_convergence_passes is True
    assert state.compactified_radial_domain_used is True
    assert state.finite_cutoff_used is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert state.collision_operator_min_eigenvalue >= -1.0e-10
    assert state.conservation_residual <= 1.0e-10
    assert state.source_constraint_residual <= 1.0e-10
    assert state.entropy_production > 0.0


def test_regularized_lane_does_not_replace_old_finite_cutoff_no_go() -> None:
    baseline = load(
        ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_heat_current_kubo_continuum_boundary_audit.json"
    )
    assert baseline["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert baseline["claim_promotion"] is False
