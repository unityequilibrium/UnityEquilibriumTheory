from docs.core.uet_o2_finite_temperature_all_22_permutation_identity import (
    all_22_permutation_identity_contract,
    all_22_permutation_identity_state,
)


def _state():
    return all_22_permutation_identity_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(0.25, 4.75, 5.5),
    )


def test_all_three_allowed_permutations_have_unit_jacobian_maps():
    state = _state()
    assert state.all_three_permutation_identity_completed
    assert state.signs == ((-1, 1, 1), (1, -1, 1), (1, 1, -1))
    assert {
        point.relabeling_to_reference
        for point in state.points
    } == {(2, 3, 1), (1, 3, 2), (1, 2, 3)}
    assert all(point.relabeling_jacobian_absolute == 1.0 for point in state.points)


def test_equal_mass_response_identity_and_graph_weight_hold():
    state = _state()
    assert state.max_response_identity_residual == 0.0
    assert state.single_cut_graph_weight == 1.0 / 6.0
    assert state.aggregate_graph_weight == 0.5
    assert state.action_level_multiplicity_contract_preserved
    assert state.max_pv_inner_convergence_residual <= 2.0e-2
    assert state.max_pv_outer_convergence_residual <= 2.0e-2


def test_permutation_lane_does_not_promote_physical_closure():
    state = _state()
    contract = all_22_permutation_identity_contract()
    assert contract["data_role"].endswith("NO_HOLDOUT")
    assert not state.complete_off_shell_finite_temperature_1pi_self_energy_completed
    assert not state.unique_physical_renormalization_scheme_match_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.xie_2026_accessed
