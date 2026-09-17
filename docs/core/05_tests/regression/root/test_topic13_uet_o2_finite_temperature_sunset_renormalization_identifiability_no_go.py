from __future__ import annotations

import pytest

from docs.core.uet_o2_finite_temperature_sunset_renormalization_identifiability_no_go import (
    sunset_renormalization_identifiability_no_go_contract,
    sunset_renormalization_identifiability_no_go_state,
)


@pytest.fixture(scope="module")
def no_go_state():
    return sunset_renormalization_identifiability_no_go_state(0.35, 0.5, 0.8)


def test_reference_change_moves_pv_real_part(no_go_state):
    state = no_go_state
    assert state.reference_dependence_witness
    assert state.principal_value_relative_span >= 1.0e-2
    assert len(set(state.combined_principal_value_real_parts)) == 3


def test_reference_change_preserves_cut_kms_and_fdt(no_go_state):
    state = no_go_state
    assert state.cut_invariance_witness
    assert state.spectral_invariance_residual <= 1.0e-10
    assert state.kms_invariance_residual <= 1.0e-10
    assert state.fdt_invariance_residual <= 1.0e-10


def test_no_go_contract_keeps_physical_scheme_open():
    contract = sunset_renormalization_identifiability_no_go_contract()
    assert contract["included"]["scoped_physical_scheme_identifiability_no_go"]
    assert contract["excluded"]["physical_renormalization_scheme_selection"]
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["alpha_Phi_K"]
