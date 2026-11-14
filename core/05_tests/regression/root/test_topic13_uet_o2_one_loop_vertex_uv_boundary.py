"""Regression tests for the Topic 13 one-loop vertex UV boundary."""

from __future__ import annotations

from functools import lru_cache

from docs.core.uet_o2_one_loop_vertex_uv_boundary import (
    one_loop_vertex_uv_contract,
    one_loop_vertex_uv_state,
)


@lru_cache(maxsize=1)
def _state():
    return one_loop_vertex_uv_state(0.22, 0.0, 0.15)


def test_o2_tensor_and_tree_level_sk_contour_identity_are_closed():
    state = _state()

    assert state.tree_vertex_symmetry_residual <= 1.0e-12
    assert state.tree_vertex_o2_rotation_residual <= 1.0e-12
    assert state.contour_action_identity_residual <= 1.0e-12


def test_one_loop_bubble_separates_finite_thermal_and_growing_vacuum_parts():
    state = _state()

    assert state.thermal_cutoff_relative_change <= 1.0e-10
    assert state.vacuum_growth_ratio > 1.5
    assert state.one_loop_correction_growth_ratio > 1.5
    assert all(value > 0.0 for value in state.bubble_thermal_values)
    assert all(value > 0.0 for value in state.bubble_vacuum_values)


def test_one_loop_vertex_boundary_keeps_renormalization_and_external_claims_open():
    state = _state()
    contract = one_loop_vertex_uv_contract()

    assert state.one_loop_renormalized_vertex_completed is False
    assert state.full_interacting_sk_kms_match_completed is False
    assert state.physical_kubo_coefficient_emitted is False
    assert state.numeric_alpha_Phi_K_emitted is False
    assert state.parameter_fitting_performed is False
    assert state.target_data_used is False
    assert state.xie_2026_accessed is False
    assert contract["excluded"]["vacuum_counterterm"] is True
    assert contract["excluded"]["finite_chemical_potential_vertex"] is True
    assert contract["excluded"]["alpha_Phi_K"] is True
