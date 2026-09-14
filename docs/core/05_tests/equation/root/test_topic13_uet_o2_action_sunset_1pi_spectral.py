"""Regression tests for the action-normalized Topic 13 sunset lane."""

from __future__ import annotations

import pytest

from docs.core.uet_o2_action_sunset_1pi_spectral import (
    ACTION_SUNSET_CONVERGENCE_THRESHOLD,
    action_matrix_element_squared,
    action_sunset_spectral_contract,
    action_sunset_spectral_state,
    action_vertex_component,
)


@pytest.fixture(scope="module")
def state():
    return action_sunset_spectral_state(
        0.22,
        0.0,
        0.15,
        radial_order=16,
        center_of_mass_order=16,
        frequency_order=8,
        cutoff_factor=12.0,
        frequency_cutoff_factor=4.0,
        probe_energies=(0.60, 0.76),
    )


def test_action_vertex_and_species_sum_are_explicit():
    assert abs(action_vertex_component(0, 0, 0, 0, 0.8) - 4.8) <= 1.0e-12
    assert abs(action_vertex_component(0, 0, 1, 1, 0.8) - 1.6) <= 1.0e-12
    assert abs(action_vertex_component(0, 1, 0, 1, 0.8) - 1.6) <= 1.0e-12
    assert abs(action_matrix_element_squared(0.8, 0) - 17.92) <= 1.0e-12
    assert abs(action_matrix_element_squared(0.8, 1) - 17.92) <= 1.0e-12


def test_action_sunset_interface_passes_internal_controls(state):
    assert state.action_vertex_normalization_completed is True
    assert state.action_continuum_cut_completed is True
    assert state.twice_subtracted_dispersion_interface_completed is True
    assert abs(state.action_to_comparator_matrix_element_ratio - 28.0) <= 1.0e-12
    assert state.kms_max_residual <= 1.0e-12
    assert state.spectral_positivity_witness is True
    assert state.retarded_imaginary_sign_witness is True
    assert state.reference_subtraction_residual <= 1.0e-24
    assert state.reference_first_s_derivative_residual <= 5.0e-3
    assert state.dispersion_convergence_residual <= ACTION_SUNSET_CONVERGENCE_THRESHOLD


def test_action_sunset_interface_does_not_promote_claims():
    contract = action_sunset_spectral_contract()
    assert contract["excluded"]["full_1PI_retarded_self_energy"] is True
    assert contract["excluded"]["alpha_Phi_K"] is True
    assert contract["excluded"]["Xie_2026_holdout"] is True
