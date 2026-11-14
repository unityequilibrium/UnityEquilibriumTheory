from __future__ import annotations

from docs.core.uet_o2_continuum_collision_operator import (
    continuum_collision_operator_contract,
    continuum_collision_operator_state,
)


def test_continuum_collocation_connects_basis_and_preserves_five_moments() -> None:
    state = continuum_collision_operator_state(0.22, 0.35, 0.15)

    assert state.transition_support_connected is True
    assert state.transition_support_component_count == 1
    assert state.basis_coverage_count == state.state_count
    assert state.invariant_rank == 5
    assert state.null_mode_count == 5
    assert state.projected_mapped_invariant_residual <= 1.0e-10
    assert state.collision_conservation_residual <= 1.0e-10


def test_continuum_collocation_matches_transition_and_vertex_contracts() -> None:
    state = continuum_collision_operator_state(0.22, 0.35, 0.15)

    assert max(max(abs(value) for value in row) for row in state.exact_channel_invariant_residuals) <= 1.0e-10
    assert max(state.exact_channel_detailed_balance_residuals) <= 1.0e-10
    assert state.transition_vertex_trace_ratio > 0.0
    assert state.vertex_decomposition_residual <= 1.0e-12
    assert max(state.bs_match_residuals) <= 1.0e-10


def test_continuum_collocation_kms_entropy_and_claim_boundaries() -> None:
    state = continuum_collision_operator_state(0.22, 0.35, 0.15)
    contract = continuum_collision_operator_contract()

    assert all(value > 0.0 for value in state.kms_spectral_density)
    assert all(
        abs(value - target) / target <= 1.0e-12
        for value, target in zip(state.kms_ratio, state.kms_target_ratio)
    )
    assert state.entropy_production_witness > 0.0
    assert state.continuum_limit_completed is False
    assert state.microscopic_bethe_salpeter_match_completed is False
    assert state.microscopic_sk_kms_match_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.xie_2026_accessed is False
    assert contract["excluded"]["continuum_limit"] is True
    assert contract["excluded"]["microscopic_sk_action_match"] is True
