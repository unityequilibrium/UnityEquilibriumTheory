from functools import lru_cache

from docs.core.uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi import (
    finite_temperature_declared_channel_reta_keldysh_1pi_contract,
    finite_temperature_declared_channel_reta_keldysh_1pi_state,
)


@lru_cache(maxsize=1)
def _state():
    return finite_temperature_declared_channel_reta_keldysh_1pi_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(4.75, 5.0, 5.5),
    )


def test_declared_channel_real_time_components_are_complete_on_grid():
    state = _state()
    assert state.declared_channel_retarded_advanced_keldysh_1pi_completed
    assert all(point.component_triplet_completed for point in state.points)
    assert state.max_retarded_advanced_conjugacy_residual <= 1.0e-12
    assert state.max_retarded_discontinuity_residual <= 1.0e-12
    assert state.max_keldysh_component_residual <= 1.0e-12


def test_declared_channel_keldysh_component_matches_fdt():
    state = _state()
    assert state.max_keldysh_fdt_residual <= 2.0e-2
    assert state.source_response_grid.max_kms_log_ratio_residual <= 2.0e-2
    assert state.source_response_grid.max_pv_inner_convergence_residual <= 2.0e-2
    assert state.source_response_grid.max_pv_outer_convergence_residual <= 2.0e-2


def test_declared_channel_keeps_physical_and_full_offshell_boundaries_open():
    state = _state()
    contract = finite_temperature_declared_channel_reta_keldysh_1pi_contract()
    assert not state.complete_off_shell_finite_temperature_1pi_self_energy_completed
    assert not state.all_finite_temperature_sunset_channels_completed
    assert not state.unique_physical_renormalization_scheme_match_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert contract["excluded"]["Xie_2026_holdout"]
