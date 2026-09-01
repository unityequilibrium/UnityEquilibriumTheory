"""Tests for the charge-resolved invariant Galerkin collision operator."""
import pytest

from docs.core.uet_o2_invariant_galerkin_collision_operator import (
    invariant_galerkin_collision_contract,
    invariant_galerkin_collision_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config
from docs.scripts.audit import audit_topic13_invariant_galerkin_collision_operator as audit


def test_eventwise_invariants_and_galerkin_operator_contract():
    state = invariant_galerkin_collision_state(0.25, 0.1, 0.0, config())
    contract = invariant_galerkin_collision_contract()
    assert contract["unit_contract"]["collision_operator"] == 1
    assert state.maximum_event_charge_residual == 0.0
    assert state.maximum_event_energy_residual <= 1.0e-12
    assert state.maximum_event_momentum_residual <= 1.0e-12
    assert state.maximum_detailed_balance_residual <= 1.0e-11
    assert state.collision_invariant_residual <= 1.0e-9
    assert state.operator_symmetry_residual <= 1.0e-12
    assert state.positive_semidefinite_min_eigenvalue >= -10.0 * state.relative_eigenvalue_tolerance
    assert state.null_mode_count == 3
    assert state.dissipative_subspace_full_rank
    assert not state.posterior_conservation_projection_used
    assert not state.self_consistent_width_completed
    assert not state.xie_2026_accessed


def test_non_equilibrium_response_background_is_not_silently_relabelled():
    with pytest.raises(NotImplementedError):
        invariant_galerkin_collision_state(0.25, 0.1, 0.1, config())


@pytest.mark.parametrize("scale", [1.5, 2.0, 3.0])
def test_whole_action_scaling_has_rate_dimension(scale):
    row = audit.scale_witness(scale)
    assert row["trace_energy_exponent"] == pytest.approx(1.0, abs=1.0e-8)
    assert row["rate_energy_exponent"] == pytest.approx(1.0, abs=1.0e-8)


@pytest.mark.parametrize(
    "name,value",
    [
        ("radial_order", 3),
        ("incoming_angular_order", 3),
        ("outgoing_angular_order", 3),
        ("outgoing_azimuth_order", 3),
        ("feature_order", 2),
    ],
)
def test_invalid_discretization_controls(name, value):
    with pytest.raises(ValueError):
        invariant_galerkin_collision_state(
            0.25, 0.1, 0.0, config(), **{name: value}
        )
