"""Tests for the same-kernel dressed RA charge-current ladder."""
import numpy as np
import pytest

from docs.core.uet_o2_dressed_ra_charge_current_ladder import (
    dressed_ra_charge_current_ladder_contract,
    dressed_ra_charge_current_ladder_state,
)
from docs.scripts.audit.audit_topic13_invariant_rate_collision_repair import config


def _state(radial_order=6):
    return dressed_ra_charge_current_ladder_state(
        0.25,
        0.1,
        0.0,
        config(),
        radial_order=radial_order,
        incoming_angular_order=4,
        outgoing_angular_order=4,
        outgoing_azimuth_order=4,
        feature_order=3,
    )


def test_kms_retarded_width_is_used_in_ra_diagonal():
    state = _state()
    loss = np.asarray(state.tagged_loss_widths_by_species_and_momentum)
    retarded = np.asarray(state.retarded_widths_by_species_and_momentum)
    assert np.all(loss >= retarded)
    assert np.any(loss > retarded)
    assert np.all(retarded > 0.0)
    assert state.maximum_kms_gain_loss_residual <= 1.0e-12
    assert state.retarded_width_used_in_ra_pair
    assert not state.tagged_out_rate_used_as_ra_width
    assert not state.fitted_relaxation_time_used


def test_d_minus_gain_rung_matches_collision_and_kinetic_solution():
    state = _state()
    assert state.d_minus_k_collision_relative_residual <= 1.0e-12
    assert state.rung_symmetry_residual <= 1.0e-12
    assert state.collision_null_residual <= 1.0e-10
    assert state.preconditioned_null_count == 1
    assert state.ladder_kinetic_response_relative_residual <= 1.0e-10
    assert state.ladder_kinetic_solution_relative_residual <= 1.0e-10
    assert state.equation_residual <= 1.0e-10


def test_event_and_width_loss_blocks_converge_together():
    coarse = _state(6)
    fine = _state(12)
    assert fine.event_width_loss_relative_residual < coarse.event_width_loss_relative_residual
    assert fine.event_width_loss_relative_residual <= 5.0e-3


def test_contract_excludes_heat_and_physical_kubo_claims():
    contract = dressed_ra_charge_current_ladder_contract()
    assert contract["included"]["kinetic_galerkin_equivalence"]
    assert contract["excluded"]["independent_heat_channel"]
    assert contract["excluded"]["physical_kubo_or_si_coefficient"]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"neumann_relative_tolerance": 0.0},
        {"neumann_relative_tolerance": 1.0},
        {"neumann_max_iterations": 0},
    ],
)
def test_invalid_ladder_controls(kwargs):
    with pytest.raises(ValueError):
        dressed_ra_charge_current_ladder_state(
            0.25, 0.1, 0.0, config(), **kwargs
        )
