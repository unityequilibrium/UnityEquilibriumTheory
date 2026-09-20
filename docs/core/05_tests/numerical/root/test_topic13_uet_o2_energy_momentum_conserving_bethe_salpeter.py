"""Regression tests for the Topic 13 full-moment conserving interface."""

from __future__ import annotations

import numpy as np

from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import (
    energy_momentum_conserving_bs_state,
)


def _state():
    return energy_momentum_conserving_bs_state(
        0.22,
        0.35,
        0.15,
        radial_order=8,
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=36.0,
    )


def test_charge_energy_and_three_momentum_constraints_are_conserved():
    state = _state()
    eigenvalues = np.asarray(state.collision_operator_eigenvalues)

    assert state.direction_count == 6
    assert state.invariant_rank == 5
    assert sum(abs(value) <= 1.0e-12 for value in eigenvalues) == 5
    assert state.collision_conservation_residual <= 1.0e-10
    assert state.invariant_projection_residual <= 1.0e-12
    assert state.source_constraint_residual <= 1.0e-12
    assert state.positive_semidefinite_min_eigenvalue >= -1.0e-12


def test_algebraic_bethe_salpeter_and_kms_interfaces_are_consistent():
    state = _state()

    assert max(state.bs_match_residuals) <= 1.0e-10
    assert all(value > 0.0 for value in state.kms_spectral_density)
    assert np.allclose(state.kms_ratio, state.kms_target_ratio, rtol=1.0e-12)
    assert np.allclose(state.kms_noise, state.kms_noise_target, rtol=1.0e-12)
    assert state.entropy_production_witness > 0.0
    assert state.microscopic_bethe_salpeter_match_completed is False
    assert state.microscopic_sk_kms_match_completed is False


def test_response_boundary_and_claim_flags_remain_conservative():
    state = _state()

    assert state.finite_cutoff_boundary_declared is True
    assert state.full_energy_momentum_constraints_included is True
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert all(value >= 0.0 for value in state.retarded_response_real)
    assert all(
        later <= earlier + 1.0e-10
        for earlier, later in zip(
            state.retarded_response_real,
            state.retarded_response_real[1:],
        )
    )
