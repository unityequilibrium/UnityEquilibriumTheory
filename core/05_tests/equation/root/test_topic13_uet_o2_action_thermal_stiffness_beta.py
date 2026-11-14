"""Regression tests for the non-Landauer action thermal stiffness lane."""

from __future__ import annotations

from docs.core.uet_o2_action_thermal_stiffness_beta import (
    action_thermal_stiffness_beta_contract,
    action_thermal_stiffness_beta_state,
)


def _state():
    return action_thermal_stiffness_beta_state()


def test_action_thermal_stiffness_beta_has_a_stable_natural_derivation():
    state = _state()

    assert state.branch == "normal"
    assert state.response_epsilon_nc > 0.0
    assert state.response_coupling > 0.0
    assert state.beta_phi_natural != 0.0
    assert state.curvature_relative_change <= 1.0e-3
    assert state.beta_relative_change <= 1.0e-3


def test_action_beta_lane_does_not_emit_normalized_or_si_quantities():
    state = _state()
    contract = action_thermal_stiffness_beta_contract()

    assert state.normalized_beta_T13_emitted is False
    assert state.numeric_e0_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.landauer_identity_used is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert contract["excluded"]["normalized_beta_T13"] is True
    assert contract["excluded"]["SI_Phi_normalization"] is True
    assert contract["excluded"]["alpha_Phi_K"] is True


def test_action_beta_ontology_and_claim_boundary_are_explicit():
    contract = action_thermal_stiffness_beta_contract()

    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
    assert "derived history trace" in contract["unit_contract"]["R_gen"]
    assert "separate observer" in contract["unit_contract"]["R_obs"]
    assert "Full Topic 13 closure" in contract["claim_boundary"]
