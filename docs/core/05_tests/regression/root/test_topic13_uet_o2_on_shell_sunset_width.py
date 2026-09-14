from __future__ import annotations

import pytest

from docs.core.uet_o2_on_shell_sunset_width import (
    ON_SHELL_SUNSET_WIDTH_STATUS,
    on_shell_sunset_collision_width_contract,
    on_shell_sunset_collision_width_state,
)


def test_action_matched_neutral_sunset_width_is_positive_and_composed() -> None:
    state = on_shell_sunset_collision_width_state(0.35, 0.5, 0.8)

    assert state.combined_collision_width == pytest.approx(
        state.one_to_three_collision_width + state.two_to_two_collision_width
    )
    assert state.width_is_positive
    assert state.retarded_sign_is_dissipative
    assert state.combined_kms_log_ratio_residual < 1.0e-12
    assert state.combined_fdt_residual < 1.0e-12
    assert state.cut_convergence_bound <= 2.0e-2
    assert not state.physical_transport_coefficient_emitted
    assert not state.numeric_alpha_Phi_K_emitted


def test_width_scope_rejects_unmatched_chemical_potential() -> None:
    with pytest.raises(ValueError, match="chemical_potential=0"):
        on_shell_sunset_collision_width_state(0.35, 0.5, 0.8, chemical_potential=0.1)


def test_contract_keeps_physical_boundaries_open() -> None:
    contract = on_shell_sunset_collision_width_contract()

    assert contract["status"] == ON_SHELL_SUNSET_WIDTH_STATUS
    assert contract["unit_contract"]["on_shell_collision_width"] == "energy/inverse time"
    assert contract["excluded"]["complete_off_shell_finite_temperature_1pi_self_energy"]
    assert contract["excluded"]["physical_kubo_coefficient"]
    assert contract["excluded"]["alpha_Phi_K"]
