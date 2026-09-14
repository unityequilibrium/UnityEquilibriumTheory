from __future__ import annotations

from docs.core.uet_o2_finite_temperature_full_sunset_sk_kms import (
    finite_temperature_full_sunset_sk_kms_contract,
    finite_temperature_full_sunset_sk_kms_state,
)


def test_declared_full_sunset_composition_matches_both_channel_sum_and_signs():
    state = finite_temperature_full_sunset_sk_kms_state(0.35, 0.5, 0.8)
    assert state.same_invariant_and_normalization_witness
    assert state.one_to_three_channel_completed
    assert state.two_to_two_channel_completed
    assert state.declared_timelike_order_lambda2_cut_partition_completed
    assert state.combined_greater_measure == (
        state.one_to_three_greater_measure + state.two_to_two_greater_measure
    )
    assert state.combined_lesser_measure == (
        state.one_to_three_lesser_measure + state.two_to_two_lesser_measure
    )
    assert state.combined_spectral_measure > 0.0
    assert state.combined_retarded_imaginary_part < 0.0


def test_declared_full_sunset_composition_closes_combined_kms_fdt_and_pv_interface():
    state = finite_temperature_full_sunset_sk_kms_state(0.35, 0.5, 0.8)
    assert state.combined_channel_sk_kms_match_completed
    assert state.combined_kms_log_ratio_residual <= 2.0e-2
    assert state.combined_fdt_residual <= 2.0e-2
    assert state.combined_retarded_i0_completed
    assert state.combined_pole_subtracted_real_part_completed
    assert state.combined_principal_value_real_part != 0.0
    assert state.combined_pv_inner_convergence_residual <= 2.0e-2
    assert state.combined_pv_outer_convergence_residual <= 2.0e-2


def test_declared_full_sunset_contract_keeps_physical_closure_open():
    contract = finite_temperature_full_sunset_sk_kms_contract()
    assert contract["included"]["declared_timelike_order_lambda2_cut_partition"]
    assert contract["included"]["combined_channel_sk_kms_match"]
    assert contract["included"]["compositional_pole_subtracted_real_part"]
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert contract["excluded"]["alpha_Phi_K"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
