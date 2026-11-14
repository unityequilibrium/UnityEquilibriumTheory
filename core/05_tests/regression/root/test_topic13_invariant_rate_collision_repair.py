"""Tests for the invariant-rate finite collision-operator repair."""
import pytest

from docs.core.uet_o2_invariant_rate_collision_operator import (
    _action_amplitude,
    invariant_rate_collision_contract,
    invariant_rate_collision_state,
)
from docs.scripts.audit import audit_topic13_invariant_rate_collision_repair as audit
from docs.scripts.audit.audit_topic13_action_normalized_elastic_scattering import (
    ActionInputs,
    amplitude,
)


def test_rate_dimension_contract_and_operator_invariants():
    state = invariant_rate_collision_state(0.25, 0.1, 0.0, audit.config())
    assert invariant_rate_collision_contract()["unit_contract"]["collision_operator"] == 1
    assert state.operator_symmetry_residual <= 1.0e-12
    assert state.positive_semidefinite_min_eigenvalue >= -10.0 * state.relative_eigenvalue_tolerance
    assert state.collision_conservation_residual <= 1.0e-9
    assert state.maximum_channel_invariant_residual <= 1.0e-10
    assert not state.connected_continuum_operator_completed
    assert not state.self_consistent_width_completed
    assert not state.xie_2026_accessed


@pytest.mark.parametrize(
    "charges", [(-1, 1, -1, 1), (1, 1, 1, 1)]
)
def test_charge_resolved_amplitude_matches_production_evaluator(charges):
    cfg = audit.config()
    expected = amplitude(6.0, 0.23, charges, ActionInputs())
    actual = _action_amplitude(6.0, 0.23, charges, cfg)
    assert actual == pytest.approx(float(expected), rel=1.0e-14)


@pytest.mark.parametrize("scale", [1.5, 2.0, 3.0])
def test_whole_action_scaling_is_a_rate(scale):
    row = audit.scale_witness(scale)
    assert row["measured_energy_exponent"] == pytest.approx(1.0, abs=1.0e-10)
    assert row["operator_trace_ratio"] == pytest.approx(scale, rel=1.0e-10)


@pytest.mark.parametrize("scale", [-1.0, 0.0, 1.0])
def test_invalid_scale_witness(scale):
    with pytest.raises(ValueError):
        audit.scale_witness(scale)
