from docs.core.uet_o2_finite_temperature_signed_cut_coverage import (
    CURRENT_LABELED_SCATTERING_SIGNS,
    SCATTERING_SIGN_PERMUTATIONS,
    finite_temperature_signed_cut_coverage_contract,
    finite_temperature_signed_cut_coverage_state,
)


def test_positive_external_signed_cut_taxonomy_enumerates_allowed_classes():
    state = finite_temperature_signed_cut_coverage_state(
        external_energy=5.0**0.5,
        mass_squared=0.5,
    )
    assert state.all_sign_assignments_enumerated
    assert state.signed_cut_kinematic_taxonomy_completed
    assert state.allowed_assignment_count == 4
    assert state.one_to_three_allowed_assignment_count == 1
    assert state.two_to_two_allowed_assignment_count == 3
    assert state.forbidden_one_plus_two_minus_count == 3


def test_current_scattering_module_is_labeled_to_one_of_three_permutations():
    state = finite_temperature_signed_cut_coverage_state(
        external_energy=5.0**0.5,
        mass_squared=0.5,
    )
    assert state.current_labeled_scattering_signs == CURRENT_LABELED_SCATTERING_SIGNS
    assert state.current_labeled_scattering_assignment_count == 1
    assert state.missing_scattering_permutation_count == 2
    assert state.two_to_two_permutations_enumerated
    assert tuple(
        assignment.signs
        for assignment in state.assignments
        if assignment.process_class == "2<->2"
    ) == SCATTERING_SIGN_PERMUTATIONS


def test_signed_cut_lane_keeps_full_1pi_and_physical_claims_open():
    state = finite_temperature_signed_cut_coverage_state(
        external_energy=5.0**0.5,
        mass_squared=0.5,
    )
    contract = finite_temperature_signed_cut_coverage_contract()
    assert not state.action_level_cut_multiplicity_completed
    assert not state.full_finite_temperature_1pi_self_energy_completed
    assert not state.all_finite_temperature_sunset_channels_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed
    assert contract["excluded"]["action_level_cut_multiplicity"]
    assert contract["excluded"]["complete_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["Xie_2026_holdout"]
