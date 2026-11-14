"""Regression tests for the Topic 13 finite-channel entropy balance lane."""

from __future__ import annotations

from docs.core.uet_o2_finite_channel_entropy_balance import (
    finite_channel_entropy_balance_state,
)


def _state():
    return finite_channel_entropy_balance_state(
        0.22,
        0.25,
        0.15,
        quadrature_order=24,
        channel_count=4,
        cutoff_factor=20.0,
        affinity_scale=0.05,
    )


def test_finite_channel_h_theorem_is_nonnegative():
    state = _state()

    assert state.positive_affinity_witness is True
    assert state.minimum_channel_entropy_production >= -1.0e-30
    assert state.perturbed_entropy_production > 0.0
    assert state.equilibrium_entropy_production >= -1.0e-30


def test_entropy_balance_identity_and_inherited_controls_hold():
    state = _state()

    assert state.entropy_balance_residual <= 1.0e-30
    assert state.detailed_balance_max_residual <= 1.0e-10
    assert state.collision_conservation_residual <= 1.0e-10
    assert state.response_kms_max_residual <= 1.0e-12
    assert state.response_fdt_max_residual <= 1.0e-12


def test_entropy_lane_does_not_promote_physical_transport_or_external_claims():
    state = _state()

    assert state.physical_entropy_current_completed is False
    assert state.physical_heat_flux_balance_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
