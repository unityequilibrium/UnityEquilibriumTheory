"""Regression tests for the action-derived natural Phi-to-thermal bridge."""

from __future__ import annotations

from docs.core.uet_o2_action_thermal_observable_bridge import (
    action_natural_phi_thermal_bridge_contract,
    action_natural_phi_thermal_bridge_state,
)


def test_natural_bridge_has_a_locked_normal_branch_and_stable_derivatives():
    state = action_natural_phi_thermal_bridge_state()

    assert state.branch == "normal"
    assert state.energy_temperature_susceptibility > 0.0
    assert state.refined_energy_temperature_susceptibility > 0.0
    assert state.response_refinement_relative_change <= 1.0e-3
    assert state.susceptibility_refinement_relative_change <= 1.0e-3
    assert state.coefficient_refinement_relative_change <= 1.0e-3


def test_natural_bridge_maps_energy_response_to_temperature_response():
    state = action_natural_phi_thermal_bridge_state()

    assert abs(state.thermodynamic_identity_residual) <= 1.0e-12
    assert abs(
        state.linear_energy_response
        - state.energy_temperature_susceptibility
        * state.linear_temperature_response_natural
    ) <= 1.0e-14
    assert state.linearization_relative_residual <= 1.0e-3


def test_natural_bridge_does_not_emit_physical_calibration():
    state = action_natural_phi_thermal_bridge_state()
    contract = action_natural_phi_thermal_bridge_contract()

    assert state.phi_ontology_preserved is True
    assert state.physical_cv_emitted is False
    assert state.numeric_alpha_phi_k_emitted is False
    assert state.numeric_e0_emitted is False
    assert state.normalized_beta_t13_emitted is False
    assert state.landauer_identity_used is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert "normalization-dependent" in contract["unit_contract"]["Phi"]
    assert "not source c_v" in contract["unit_contract"]["C_epsilon_T"]


def test_natural_bridge_claim_boundary_stays_lane_scoped():
    contract = action_natural_phi_thermal_bridge_contract()

    assert "alpha_Phi_K" in contract["claim_boundary"]
    assert "Full Topic 13" in contract["claim_boundary"]
