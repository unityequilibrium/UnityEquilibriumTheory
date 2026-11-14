from __future__ import annotations

import pytest

from docs.core.uet_o2_tree_level_charged_ward_vertex import (
    TREE_LEVEL_CHARGED_WARD_STATUS,
    tree_level_charged_ward_vertex_contract,
    tree_level_charged_ward_vertex_state,
)


def test_tree_level_charged_ward_identity_matches_propagator_difference() -> None:
    state = tree_level_charged_ward_vertex_state(0.35, 0.1, 0.8)

    assert state.normal_branch
    assert state.sample_count == 3
    assert state.max_ward_residual == pytest.approx(0.0, abs=1.0e-12)
    assert state.zero_transfer_vertex_residual == pytest.approx(0.0, abs=1.0e-12)
    assert state.charge_conjugation_residual == pytest.approx(0.0, abs=1.0e-12)


def test_tree_level_ward_lane_keeps_loop_and_transport_open() -> None:
    state = tree_level_charged_ward_vertex_state(0.35, 0.1, 0.8)

    assert state.tree_level_current_vertex_completed
    assert not state.loop_renormalized_offshell_vertex_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed


def test_tree_level_ward_contract_is_natural_and_lane_scoped() -> None:
    contract = tree_level_charged_ward_vertex_contract()

    assert contract["status"] == TREE_LEVEL_CHARGED_WARD_STATUS
    assert "ward_identity" in contract["equations"]
    assert contract["units"]["Q_dot_Gamma"] == "energy^2"
    assert contract["excluded"]["loop_renormalized_current_vertex"]
    assert contract["excluded"]["physical_kubo_coefficient"]
