"""Regression tests for the Topic 13 exact-kinematic transition lane."""

from __future__ import annotations

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)


def _state():
    return action_derived_transition_kernel_state(
        0.22,
        0.35,
        0.15,
        quadrature_order=24,
        channel_count=4,
        cutoff_factor=36.0,
    )


def test_exact_kinematics_and_detailed_balance_are_preserved():
    state = _state()

    assert state.state_count == 16
    assert state.invariant_matrix_rank == 5
    assert max(max(abs(value) for value in residual) for residual in state.channel_invariant_residuals) <= 1.0e-10
    assert max(state.channel_detailed_balance_residuals) <= 1.0e-10
    assert all(value > 0.0 for value in state.channel_rates)


def test_channel_operator_and_algebraic_interfaces_are_valid():
    state = _state()
    eigenvalues = np.asarray(state.collision_operator_eigenvalues)

    assert np.min(eigenvalues) >= -1.0e-12
    assert state.collision_conservation_residual <= 1.0e-10
    assert max(state.bs_match_residuals) <= 1.0e-10
    assert np.allclose(state.kms_ratio, state.kms_target_ratio, rtol=1.0e-12)
    assert np.allclose(state.kms_noise, state.kms_noise_target, rtol=1.0e-12)
    assert state.entropy_production_witness > 0.0


def test_transition_lane_does_not_promote_microscopic_or_external_claims():
    state = _state()

    assert state.exact_kinematics_declared is True
    assert state.detailed_balance_checked is True
    assert state.finite_channel_boundary_declared is True
    assert state.microscopic_bethe_salpeter_match_completed is False
    assert state.microscopic_sk_kms_match_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
