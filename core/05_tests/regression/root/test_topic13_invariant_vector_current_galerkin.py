"""Tests for the invariant vector current Galerkin lane."""
import numpy as np
import pytest

from docs.core.uet_o2_invariant_vector_current_galerkin import (
    invariant_vector_current_contract,
    invariant_vector_current_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config


def test_vector_operator_preserves_momentum_and_is_dissipative():
    state = invariant_vector_current_state(0.25, 0.1, 0.0, config())
    contract = invariant_vector_current_contract()
    assert contract["unit_contract"]["collision_operator"] == 1
    assert state.maximum_event_charge_residual == 0.0
    assert state.maximum_event_energy_residual <= 1.0e-12
    assert state.maximum_event_momentum_residual <= 1.0e-12
    assert state.maximum_detailed_balance_residual <= 1.0e-10
    assert state.momentum_null_residual <= 1.0e-9
    assert state.null_mode_count == 1
    assert state.dissipative_subspace_full_rank
    assert state.operator_symmetry_residual <= 1.0e-12
    assert state.positive_semidefinite_min_eigenvalue >= -10.0 * state.relative_eigenvalue_tolerance
    assert not state.posterior_collision_projection_used


def test_landau_projected_heat_and_charge_sources_have_rank_one():
    state = invariant_vector_current_state(0.25, 0.1, 0.0, config())
    charge = np.asarray(state.landau_projected_charge_current_source)
    heat = np.asarray(state.landau_projected_grand_heat_current_source)
    assert state.projected_source_rank == 1
    assert state.projected_heat_charge_rank_residual <= 1.0e-9
    assert heat == pytest.approx(-state.chemical_potential * charge, rel=1.0e-9, abs=1.0e-12)
    assert state.charge_response_form > 0.0
    assert state.heat_response_form == pytest.approx(
        state.chemical_potential**2 * state.charge_response_form, rel=1.0e-8
    )
    assert not state.physical_kubo_coefficient_emitted


def test_zero_mu_landau_heat_source_vanishes():
    state = invariant_vector_current_state(0.25, 0.0, 0.0, config())
    assert np.linalg.norm(state.landau_projected_grand_heat_current_source) <= 1.0e-10
    assert state.projected_source_rank == 1


def test_non_equilibrium_response_background_is_rejected():
    with pytest.raises(NotImplementedError):
        invariant_vector_current_state(0.25, 0.1, 0.1, config())
