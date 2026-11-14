from functools import lru_cache

from docs.core.uet_o2_finite_temperature_offshell_threshold_crossing_1pi import (
    finite_temperature_offshell_threshold_crossing_1pi_contract,
    finite_temperature_offshell_threshold_crossing_1pi_state,
)


@lru_cache(maxsize=1)
def _state():
    return finite_temperature_offshell_threshold_crossing_1pi_state(
        0.35,
        0.5,
        0.8,
    )


def test_threshold_crossing_has_correct_channel_support():
    state = _state()
    assert state.offshell_threshold_crossing_response_completed
    assert state.three_body_threshold_s == 4.5
    assert state.below_threshold_one_to_three_zero_witness
    assert state.above_threshold_one_to_three_nonzero_witness
    assert state.below_threshold_two_to_two_nonzero_witness


def test_threshold_crossing_real_time_components_and_fdt_pass():
    state = _state()
    assert all(point.response_triplet_completed for point in state.points)
    assert state.max_one_to_three_pv_convergence_residual <= 2.0e-2
    assert state.max_two_to_two_pv_convergence_residual <= 2.0e-2
    assert state.max_retarded_advanced_conjugacy_residual <= 1.0e-12
    assert state.max_retarded_discontinuity_residual <= 1.0e-12
    assert state.max_keldysh_component_residual <= 1.0e-12
    assert state.max_keldysh_fdt_residual <= 2.0e-2


def test_threshold_crossing_keeps_full_physical_boundaries_open():
    state = _state()
    contract = finite_temperature_offshell_threshold_crossing_1pi_contract()
    assert not state.complete_off_shell_finite_temperature_1pi_self_energy_completed
    assert not state.unique_physical_renormalization_scheme_match_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert contract["excluded"]["Xie_2026_holdout"]
