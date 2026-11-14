from docs.core.uet_o2_finite_temperature_all_onshell_cut_response import (
    finite_temperature_all_onshell_cut_response_contract,
    finite_temperature_all_onshell_cut_response_state,
)


def _state():
    return finite_temperature_all_onshell_cut_response_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(4.75, 5.0, 5.5),
    )


def test_all_positive_energy_cut_response_uses_complete_signed_partition():
    state = _state()
    assert state.all_positive_energy_signed_cuts_completed
    assert state.all_positive_energy_on_shell_spectral_response_completed
    assert state.signed_cut_taxonomy.allowed_assignment_count == 4
    assert state.cut_multiplicity.two_to_two_graph_weight == 0.5
    assert state.cut_multiplicity.current_factor_matches_two_to_two_graph_weight


def test_all_onshell_response_grid_passes_retarded_kms_fdt_and_pv_checks():
    state = _state()
    assert state.on_shell_retarded_grid_completed
    assert state.response_grid.max_kms_log_ratio_residual <= 2.0e-2
    assert state.response_grid.max_fdt_residual <= 2.0e-2
    assert state.response_grid.max_pv_inner_convergence_residual <= 2.0e-2
    assert state.response_grid.max_pv_outer_convergence_residual <= 2.0e-2
    assert state.response_grid.max_retarded_i0_consistency_residual <= 1.0e-12


def test_all_onshell_lane_keeps_offshell_and_physical_claims_open():
    state = _state()
    contract = finite_temperature_all_onshell_cut_response_contract()
    assert not state.full_finite_temperature_1pi_self_energy_completed
    assert not state.unique_physical_renormalization_scheme_match_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["physical_scattering_normalization_identity"]
    assert contract["excluded"]["Xie_2026_holdout"]
