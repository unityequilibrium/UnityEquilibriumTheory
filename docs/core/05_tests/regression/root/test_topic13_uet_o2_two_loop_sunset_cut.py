"""Regression tests for the Topic 13 two-loop sunset-cut lane."""

from __future__ import annotations

from docs.core.uet_o2_two_loop_sunset_cut import two_loop_sunset_cut_state


def _state():
    return two_loop_sunset_cut_state(
        0.22,
        0.25,
        0.15,
        quadrature_order=24,
        channel_count=4,
        cutoff_factor=20.0,
    )


def test_forward_reverse_sunset_cut_is_positive_and_balanced():
    state = _state()

    assert state.finite_channel_sunset_cut_completed is True
    assert state.symmetric_cut_total > 0.0
    assert state.nonzero_cut_channel_count == state.channel_count
    assert state.detailed_balance_max_residual <= 1.0e-10
    assert abs(state.forward_cut_total - state.reverse_cut_total) / state.symmetric_cut_total <= 1.0e-10


def test_sunset_cut_inherits_conservative_response_witnesses():
    state = _state()

    assert state.positive_semidefinite_min_eigenvalue >= -1.0e-12
    assert state.collision_conservation_residual <= 1.0e-10
    assert state.entropy_production_witness > 0.0
    assert state.response_kms_max_residual <= 1.0e-12
    assert state.response_fdt_max_residual <= 1.0e-12


def test_sunset_cut_does_not_promote_full_self_energy_or_external_claims():
    state = _state()

    assert state.continuum_sunset_self_energy_completed is False
    assert state.physical_retarded_self_energy_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
