"""Tests for the finite-temperature two-sector static response lane."""

from __future__ import annotations

import pytest

from docs.core.uet_o2_finite_temperature_two_fluid_response import (
    finite_temperature_two_fluid_static_contract,
    finite_temperature_two_fluid_static_state,
)


def test_normal_state_composes_sector_and_heat_balance() -> None:
    state = finite_temperature_two_fluid_static_state(
        0.22,
        0.35,
        0.15,
        include_normal_heat_flux_balance=True,
    )
    assert state.branch == "normal"
    assert state.condensate_phase_stiffness == 0.0
    assert state.normal_momentum_susceptibility > 0.0
    assert state.heat_flux_kappa_natural is not None
    assert state.entropy_balance_residual is not None
    assert state.entropy_balance_residual <= 1.0e-7


def test_condensed_state_exposes_static_response_without_dissipative_shortcut() -> None:
    state = finite_temperature_two_fluid_static_state(0.20, 1.28, 0.15)
    assert state.branch == "condensed"
    assert state.condensate_phase_stiffness > 0.0
    assert state.normal_momentum_susceptibility > 0.0
    assert state.heat_flux_kappa_natural is None


def test_heat_balance_request_rejects_condensed_branch() -> None:
    with pytest.raises(NotImplementedError, match="normal branch"):
        finite_temperature_two_fluid_static_state(
            0.20,
            1.28,
            0.15,
            include_normal_heat_flux_balance=True,
        )


def test_contract_preserves_ontology_and_physical_boundary() -> None:
    contract = finite_temperature_two_fluid_static_contract()
    assert "not temperature" in contract["unit_contract"]["Phi"]
    assert "not mass or charge" in contract["unit_contract"]["C"]
    assert "retarded physical Kubo coefficient" in contract["excluded_scope"]
    assert "numeric alpha_Phi_K" in contract["excluded_scope"]
    assert "signed derivatives" in contract["unit_contract"]["sector_derivative_sign_policy"]
    assert "not imposed on a residual sector" in contract["unit_contract"]["sector_derivative_sign_policy"]
