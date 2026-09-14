from __future__ import annotations

import pytest

from docs.core.uet_o2_charged_current_correlator import (
    CHARGED_CURRENT_CORRELATOR_STATUS,
    charged_current_correlator_contract,
    charged_current_correlator_state,
)


def test_charged_current_source_and_kms_interface() -> None:
    state = charged_current_correlator_state(0.35, 0.1, 0.8)

    assert state.current_source_formula_residual < 1.0e-12
    assert state.current_ward_projection_residual < 1.0e-12
    assert state.collision_conservation_residual < 1.0e-12
    assert state.contact_cross_section_match_residual < 1.0e-15
    assert state.kms_ratio_max_residual < 1.0e-12
    assert state.fdt_max_residual < 1.0e-12
    assert state.entropy_production_witness > 0.0


def test_current_correlator_keeps_microscopic_and_physical_scopes_open() -> None:
    state = charged_current_correlator_state(0.35, 0.1, 0.8)

    assert not state.microscopic_offshell_self_energy_completed
    assert not state.microscopic_current_vertex_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed


def test_current_correlator_contract_is_lane_scoped() -> None:
    contract = charged_current_correlator_contract()

    assert contract["status"] == CHARGED_CURRENT_CORRELATOR_STATUS
    assert contract["equations"]["current_source"] == "b_Jx(s,k,n)=q_s*(p_x/E_s)*sqrt(w_s)"
    assert contract["excluded"]["physical_Kubo_coefficient"]
    assert contract["excluded"]["loop_renormalized_offshell_self_energy"]
