from __future__ import annotations

import pytest

from docs.core.uet_o2_charge_conserving_ladder_response import (
    charge_conserving_ladder_response_state,
)


def test_conserving_response_has_zero_mode_and_positive_relative_mode() -> None:
    state = charge_conserving_ladder_response_state(0.22, 0.35, 0.15)
    assert state.collision_operator_eigenvalues[0] == pytest.approx(0.0, abs=1.0e-15)
    assert state.collision_operator_eigenvalues[1] > 0.0
    assert state.conservation_residual <= 1.0e-12
    assert state.positive_semidefinite_min_eigenvalue >= -1.0e-12
    assert state.source_norm_squared > 0.0


def test_retarded_response_matches_dc_and_has_declared_frequency_behavior() -> None:
    state = charge_conserving_ladder_response_state(0.22, 0.35, 0.15)
    assert state.dc_response == pytest.approx(state.dc_closed_form, rel=1.0e-12)
    assert all(
        later <= earlier + 1.0e-12
        for earlier, later in zip(
            state.retarded_response_real,
            state.retarded_response_real[1:],
        )
    )
    assert all(value > 0.0 for value in state.retarded_response_imag[1:])


def test_lane_requires_quantum_width_and_does_not_emit_physical_kubo() -> None:
    with pytest.raises(ValueError, match="corrected quantum collision width"):
        charge_conserving_ladder_response_state(
            0.22,
            0.35,
            0.15,
            include_final_state_bose_enhancement=False,
        )
    state = charge_conserving_ladder_response_state(0.22, 0.35, 0.15)
    assert state.final_state_bose_enhancement_included is True
    assert state.ladder_vertex_resummation_included is True
    assert state.physical_kubo_coefficient_emitted is False
