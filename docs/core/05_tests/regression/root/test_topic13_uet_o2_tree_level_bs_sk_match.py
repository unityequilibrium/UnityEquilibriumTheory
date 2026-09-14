"""Regression tests for the Topic 13 tree-level/formal SK lane."""

from __future__ import annotations

from functools import lru_cache

from docs.core.uet_o2_tree_level_bs_sk_match import (
    tree_level_bs_sk_match_contract,
    tree_level_bs_sk_match_state,
)


@lru_cache(maxsize=1)
def _state():
    return tree_level_bs_sk_match_state(0.22, 0.35, 0.15)


def test_tree_level_action_vertex_and_kinematic_interfaces_are_resolved():
    state = _state()

    assert state.action_vertex_cross_section_residual <= 1.0e-12
    assert state.exact_channel_kinematic_residual <= 1.0e-10
    assert state.exact_channel_detailed_balance_residual <= 1.0e-10
    assert state.action_width_vertex_decomposition_residual <= 1.0e-12
    assert state.algebraic_bethe_salpeter_residual <= 1.0e-10


def test_formal_sk_kms_fdt_and_entropy_interfaces_are_resolved():
    state = _state()

    assert state.formal_sk_action_kms_match_completed is True
    assert state.formal_sk_action_kms_residual <= 1.0e-12
    assert state.formal_sk_noise_fdt_residual <= 1.0e-12
    assert state.formal_sk_entropy_witness > 0.0


def test_tree_level_lane_keeps_continuum_and_external_boundaries_open():
    state = _state()
    contract = tree_level_bs_sk_match_contract()

    assert len(state.continuum_sequence_relative_changes) == 3
    assert state.continuum_sequence_max_relative_change > 1.0e-2
    assert state.continuum_limit_completed is False
    assert state.microscopic_bethe_salpeter_match_completed is False
    assert state.microscopic_sk_kms_match_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert contract["excluded"]["continuum_limit"] is True
    assert contract["excluded"]["alpha_Phi_K"] is True
    assert contract["excluded"]["TTG_validation"] is True
