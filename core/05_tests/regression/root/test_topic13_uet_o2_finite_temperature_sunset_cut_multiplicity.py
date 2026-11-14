from docs.core.uet_o2_finite_temperature_sunset_cut_multiplicity import (
    finite_temperature_sunset_cut_multiplicity_contract,
    finite_temperature_sunset_cut_multiplicity_state,
)


def test_action_level_sunset_multiplicity_matches_signed_cut_count():
    state = finite_temperature_sunset_cut_multiplicity_state(0.5, 0.8)
    assert state.one_to_three_sign_pattern_count == 1
    assert state.two_to_two_sign_pattern_count == 3
    assert state.one_to_three_graph_weight == 1.0 / 6.0
    assert state.two_to_two_graph_weight == 0.5
    assert state.two_to_two_to_one_to_three_graph_weight_ratio == 3.0
    assert state.current_factor_matches_two_to_two_graph_weight
    assert state.action_level_signed_cut_multiplicity_completed


def test_physical_final_state_factor_is_species_resolved_and_separate():
    state = finite_temperature_sunset_cut_multiplicity_state(0.5, 0.8)
    assert state.physical_final_state_weight_formula_present
    assert state.physical_final_state_has_species_dependent_weights
    assert set(state.physical_final_state_weight_values) == {0.5, 1.0}
    assert not state.physical_scattering_normalization_match_completed


def test_multiplicity_lane_keeps_full_1pi_and_physical_claims_open():
    state = finite_temperature_sunset_cut_multiplicity_state(0.5, 0.8)
    contract = finite_temperature_sunset_cut_multiplicity_contract()
    assert not state.full_finite_temperature_1pi_self_energy_completed
    assert not state.unique_physical_renormalization_scheme_match_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["physical_scattering_normalization_identity"]
    assert contract["excluded"]["complete_finite_temperature_1pi_self_energy"]
