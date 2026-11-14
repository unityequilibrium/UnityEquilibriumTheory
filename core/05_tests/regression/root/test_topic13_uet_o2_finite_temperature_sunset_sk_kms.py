from __future__ import annotations

from docs.core.uet_o2_finite_temperature_sunset_sk_kms import (
    finite_temperature_sunset_sk_kms_contract,
    finite_temperature_sunset_sk_kms_state,
)


def test_finite_temperature_three_body_channel_has_positive_cut_and_negative_retarded_sign():
    state = finite_temperature_sunset_sk_kms_state(0.35, 0.5, 0.8)
    assert state.greater_is_positive
    assert state.lesser_is_positive
    assert state.spectral_difference_is_positive
    assert state.retarded_imaginary_sign_witness
    assert state.retarded_imaginary_part < 0.0


def test_finite_temperature_three_body_channel_matches_kms_fdt_and_converges():
    state = finite_temperature_sunset_sk_kms_state(0.35, 0.5, 0.8)
    assert state.kms_log_ratio_residual <= 2.0e-2
    assert state.fdt_residual <= 2.0e-2
    assert state.vacuum_phase_space_normalization_residual <= 2.0e-2
    assert state.inner_quadrature_convergence_residual <= 2.0e-2
    assert state.outer_quadrature_convergence_residual <= 2.0e-2
    assert state.finite_temperature_principal_value_completed
    assert state.finite_temperature_principal_value_real_part != 0.0
    assert state.thermal_pv_inner_convergence_residual <= 2.0e-2
    assert state.thermal_pv_outer_convergence_residual <= 2.0e-2


def test_finite_temperature_three_body_contract_keeps_full_closure_open():
    contract = finite_temperature_sunset_sk_kms_contract()
    assert contract["included"]["channel_level_sk_kms_match"]
    assert contract["included"]["channel_level_fdt_noise_relation"]
    assert contract["included"]["finite_temperature_principal_value_real_part"]
    assert contract["excluded"]["full_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert contract["excluded"]["alpha_Phi_K"]
    assert "not temperature" in contract["unit_contract"]["Phi"]
