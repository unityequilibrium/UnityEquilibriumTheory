from __future__ import annotations

from docs.core.uet_o2_heat_current_kubo_match import (
    HEAT_CURRENT_KUBO_MATCH_STATUS,
    heat_current_kubo_match_state,
)


def test_heat_current_kubo_match_is_state_matched_and_finite_cutoff() -> None:
    state = heat_current_kubo_match_state(0.22, 0.35, 0.15)
    assert state.branch == "normal"
    assert state.same_operator_state_verified
    assert state.retarded_heat_current_match_completed
    assert state.dc_matrix_relative_residual <= 1.0e-10
    assert state.dc_scalar_relative_residual <= 1.0e-10
    assert state.kms_ratio_residual <= 1.0e-10
    assert state.fdt_residual <= 1.0e-10
    assert state.physical_kubo_coefficient_emitted is False
    assert state.continuum_limit_completed is False
    assert HEAT_CURRENT_KUBO_MATCH_STATUS.startswith("PASS_")
