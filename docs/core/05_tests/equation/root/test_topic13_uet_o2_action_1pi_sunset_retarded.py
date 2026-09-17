from __future__ import annotations

from docs.core.uet_o2_action_1pi_sunset_euclidean import (
    euclidean_1pi_sunset_state,
)
from docs.core.uet_o2_action_1pi_sunset_retarded import (
    retarded_vacuum_sunset_contract,
    retarded_vacuum_sunset_state,
    three_body_phase_space,
)


def test_three_body_cut_has_threshold_support():
    assert three_body_phase_space(4.0, 0.5) == 0.0
    assert three_body_phase_space(5.0, 0.5) > 0.0


def test_retarded_sunset_matches_euclidean_and_has_negative_imaginary_part():
    euclidean = euclidean_1pi_sunset_state(0.5, 0.8)
    state = retarded_vacuum_sunset_state(
        0.5,
        0.8,
        euclidean.twice_subtracted_self_energy_values,
    )
    assert state.euclidean_dispersion_match_residual <= 2.0e-2
    assert state.below_threshold_zero_witness
    assert state.above_threshold_nonzero_witness
    assert state.retarded_imaginary_part_at_timelike_probe < 0.0
    assert state.above_threshold_principal_value_real_part_completed
    assert state.above_threshold_principal_value_real_part > 0.0
    assert state.above_threshold_pv_inner_convergence_residual <= 2.0e-2
    assert state.above_threshold_pv_outer_convergence_residual <= 2.0e-2


def test_retarded_contract_keeps_full_finite_temperature_closure_open():
    contract = retarded_vacuum_sunset_contract()
    assert contract["included"]["retarded_i0_discontinuity"]
    assert contract["included"]["above_threshold_principal_value_real_part"]
    assert contract["excluded"]["finite_temperature_self_energy"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "derived history trace" in contract["unit_contract"]["R_gen"]
