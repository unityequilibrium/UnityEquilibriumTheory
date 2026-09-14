from __future__ import annotations

from docs.core.uet_o2_finite_temperature_offshell_1pi import (
    finite_temperature_offshell_1pi_contract,
    finite_temperature_offshell_1pi_state,
)


def test_formal_offshell_object_covers_all_declared_interfaces() -> None:
    state = finite_temperature_offshell_1pi_state(0.35, 0.5, 0.8)

    assert state.formal_offshell_1pi_object_completed
    assert state.one_loop_tadpole_sum_integral_closed
    assert state.two_loop_sunset_sum_integral_closed
    assert state.all_signed_cut_assignments_included
    assert state.retarded_continuation_contract_closed
    assert state.kms_relation_contract_closed


def test_species_prefactors_match_declared_o2_action() -> None:
    state = finite_temperature_offshell_1pi_state(0.35, 0.5, 0.8)

    assert state.tadpole_prefactor == 3.2
    assert abs(state.sunset_prefactor - 5.12) <= 1.0e-12
    assert state.species_diagonal_structure_closed


def test_physical_boundaries_remain_open() -> None:
    state = finite_temperature_offshell_1pi_state(0.35, 0.5, 0.8)
    contract = finite_temperature_offshell_1pi_contract()

    assert not state.unique_physical_renormalization_scheme_match_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert contract["excluded"]["Ding_C_src_numeric_source"]
    assert not state.target_data_used
    assert not state.xie_2026_accessed
