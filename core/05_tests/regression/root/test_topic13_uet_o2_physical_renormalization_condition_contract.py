from __future__ import annotations

import pytest

from docs.core.uet_o2_physical_renormalization_condition_contract import (
    physical_renormalization_condition_contract,
    physical_renormalization_condition_state,
)


@pytest.fixture(scope="module")
def state():
    return physical_renormalization_condition_state(0.5, 0.75, 0.12, 0.08)


def test_below_threshold_on_shell_conditions_close_formal_witness(state):
    assert state.below_threshold_domain
    assert state.inverse_propagator_pole_residual <= 1.0e-12
    assert state.inverse_propagator_residue_residual <= 1.0e-12


def test_counterterms_keep_distinct_units(state):
    assert state.mass_counterterm == pytest.approx(0.12)
    assert state.wavefunction_counterterm == pytest.approx(-0.08)


def test_external_anchor_and_physical_match_remain_open():
    contract = physical_renormalization_condition_contract()
    assert contract["included"]["external_anchor_acceptance_schema"]
    assert contract["excluded"]["physical_anchor_match"]
    assert "Xie 2026 numeric holdout" in contract["forbidden_inputs"]
