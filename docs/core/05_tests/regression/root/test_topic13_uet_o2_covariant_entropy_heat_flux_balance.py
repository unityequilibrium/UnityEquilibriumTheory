"""Regression tests for the Topic 13 covariant entropy/heat-flux lane."""

from __future__ import annotations

import numpy as np

from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    covariant_entropy_heat_flux_balance_contract,
    covariant_entropy_heat_flux_balance_state,
)


def _state():
    return covariant_entropy_heat_flux_balance_state(0.22, 0.35, 0.15)


def test_action_derived_heat_response_is_positive_and_balanced():
    state = _state()
    response = np.asarray(state.heat_response_matrix, dtype=float)

    assert state.eos_branch == "normal"
    assert state.kappa_natural > 0.0
    assert np.min(np.linalg.eigvalsh(response)) >= -1.0e-8
    assert state.heat_response_isotropy_residual <= 1.0e-8
    assert state.entropy_production > 0.0
    assert state.entropy_balance_residual <= 1.0e-7
    assert state.kinetic_equation_residual <= 1.0e-10


def test_covariant_heat_flux_preserves_orthogonality_and_conserved_moments():
    state = _state()

    assert state.force_orthogonality_residual <= 1.0e-12
    assert state.heat_flux_orthogonality_residual <= 1.0e-12
    assert state.projector_orthogonality_residual <= 1.0e-12
    assert state.charge_balance_residual <= 1.0e-10
    assert state.energy_balance_residual <= 1.0e-10
    assert state.momentum_balance_residual <= 1.0e-10
    assert state.lorentz_covariance_residual <= 1.0e-10
    assert state.equilibrium_heat_flux_norm <= 1.0e-12


def test_heat_flux_lane_does_not_promote_physical_transport_or_alpha():
    state = _state()
    contract = covariant_entropy_heat_flux_balance_contract()

    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert contract["excluded"]["physical_Kubo_coefficient"] is True
    assert contract["excluded"]["SI_heat_flux"] is True
    assert contract["excluded"]["alpha_Phi_K"] is True
    assert contract["excluded"]["TTG_validation"] is True
