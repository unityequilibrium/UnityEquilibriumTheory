from __future__ import annotations

import pytest

from docs.core.uet_o2_contact_sk_transition_vertex_match import (
    CONTACT_SK_TRANSITION_VERTEX_STATUS,
    contact_sk_transition_vertex_match_contract,
    contact_sk_transition_vertex_match_state,
)


def test_contact_sk_vertex_matches_declared_transition_cross_section() -> None:
    state = contact_sk_transition_vertex_match_state(0.35, 0.1, 0.8)

    assert state.contact_vertex_amplitude == pytest.approx(state.quartic_coupling)
    assert state.r3a_vertex_coefficient == pytest.approx(state.quartic_coupling)
    assert state.ra3_vertex_coefficient == pytest.approx(state.quartic_coupling / 4.0)
    assert state.action_cross_section == pytest.approx(state.kernel_cross_section)
    assert state.cross_section_match_residual < 1.0e-15
    assert state.max_channel_detailed_balance_residual < 1.0e-12
    assert state.max_channel_invariant_residual < 1.0e-12


def test_contact_sk_vertex_keeps_physical_transport_open() -> None:
    state = contact_sk_transition_vertex_match_state(0.35, 0.1, 0.8)

    assert not state.microscopic_offshell_self_energy_completed
    assert not state.physical_kubo_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted
    assert not state.target_data_used
    assert not state.xie_2026_accessed


def test_contact_sk_contract_is_lane_scoped() -> None:
    contract = contact_sk_transition_vertex_match_contract()

    assert contract["status"] == CONTACT_SK_TRANSITION_VERTEX_STATUS
    assert contract["equations"]["contact_scattering_amplitude"] == "M_22=lambda for the declared contact channel"
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["physical_current_correlator_kubo"]
