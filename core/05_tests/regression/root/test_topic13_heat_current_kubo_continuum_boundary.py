from __future__ import annotations

from docs.core.uet_o2_heat_current_kubo_continuum_boundary import (
    HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS,
    heat_current_kubo_continuum_boundary_state,
)


def test_heat_current_continuum_boundary_is_a_scoped_no_go() -> None:
    state = heat_current_kubo_continuum_boundary_state(0.22, 0.35, 0.15)
    assert state.cutoff_sequence_fails_acceptance
    assert state.refinement_fails_acceptance
    assert state.cutoff_maximum_relative_change > state.acceptance_threshold
    assert state.baseline_to_refined_relative_change > state.acceptance_threshold
    assert state.extrapolated_response_emitted is False
    assert state.physical_kubo_coefficient_emitted is False
    assert HEAT_CURRENT_KUBO_CONTINUUM_BOUNDARY_STATUS.startswith("PASS_")
