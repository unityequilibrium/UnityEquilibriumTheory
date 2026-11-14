from __future__ import annotations

import numpy as np

from docs.core.uet_o2_continuum_relative_flow_kubo import (
    continuum_relative_flow_state,
)


def test_continuum_relative_flow_is_converged_and_conservative() -> None:
    state = continuum_relative_flow_state(
        0.20,
        1.28,
        0.15,
        radial_orders=(20, 28, 36),
        angular_order=20,
        angular_refined_order=28,
    )
    assert state.continuum_integrals_finite
    assert state.continuum_convergence_passes
    assert state.dc_relative_response > 0.0
    assert state.relative_collision_rate > 0.0
    assert state.common_flow_conservation_residual <= 1.0e-12
    assert state.source_common_mode_residual <= 1.0e-12
    assert min(state.collision_eigenvalues) >= -1.0e-12


def test_continuum_relative_flow_preserves_kms_entropy_and_scope() -> None:
    state = continuum_relative_flow_state(
        0.20,
        1.28,
        0.15,
        radial_orders=(20, 28, 36),
        angular_order=20,
        angular_refined_order=28,
    )
    assert state.kms_residual <= 1.0e-12
    assert state.fdt_residual <= 1.0e-12
    assert state.entropy_production_at_unit_force >= 0.0
    assert state.finite_cutoff_used is False
    assert state.loop_renormalized_vertex_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_phi_k_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
