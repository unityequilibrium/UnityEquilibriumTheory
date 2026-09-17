from functools import lru_cache

from docs.core.uet_o2_finite_temperature_declared_retarded_1pi_grid import (
    finite_temperature_declared_retarded_1pi_grid_contract,
    finite_temperature_declared_retarded_1pi_grid_state,
)


@lru_cache(maxsize=1)
def _state():
    return finite_temperature_declared_retarded_1pi_grid_state(
        0.35,
        0.5,
        0.8,
        invariant_grid=(4.75, 5.0, 5.5),
    )


def test_declared_retarded_grid_matches_channels_and_has_retarded_sign():
    state = _state()
    assert state.declared_retarded_response_grid_completed
    assert state.declared_1pi_pole_subtracted_response_completed
    assert state.matched_state_witness
    assert state.positive_spectral_grid_witness
    assert state.lower_half_plane_grid_witness
    assert all(point.one_to_three_completed for point in state.points)
    assert all(point.two_to_two_completed for point in state.points)
    assert all(point.response_pair_consistent for point in state.points)


def test_declared_retarded_grid_passes_kms_fdt_pv_and_keeps_full_self_energy_open():
    state = _state()
    assert state.max_kms_log_ratio_residual <= 2.0e-2
    assert state.max_fdt_residual <= 2.0e-2
    assert state.max_pv_inner_convergence_residual <= 2.0e-2
    assert state.max_pv_outer_convergence_residual <= 2.0e-2
    assert state.max_retarded_i0_consistency_residual <= 1.0e-12
    assert not state.full_finite_temperature_1pi_self_energy_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed


def test_declared_retarded_grid_contract_preserves_claim_boundary():
    contract = finite_temperature_declared_retarded_1pi_grid_contract()
    assert contract["excluded"]["complete_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["unique_physical_renormalization"]
    assert contract["excluded"]["physical_kubo_coefficient"]
    assert contract["excluded"]["alpha_Phi_K"]
    assert contract["excluded"]["Xie_2026_holdout"]
    assert "not temperature" in contract["ontology"]["Phi"]
