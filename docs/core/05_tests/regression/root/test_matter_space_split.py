"""Tests for the opt-in changing-C split bridge."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from docs.core.uet_matter_space import MatterSpaceConfig, MatterSpaceState
from docs.core.uet_matter_space_split import (
    causal_matter_space_split_step,
    causal_split_energy,
)


def _config(**changes: object) -> MatterSpaceConfig:
    base = MatterSpaceConfig(
        a_matter=-0.2,
        b_matter=1.0,
        kappa_matter=0.02,
        mobility_matter=0.04,
        a_space=0.8,
        b_space=0.6,
        kappa_space=0.2,
        mobility_space=0.5,
        tau_space=0.7,
        coupling_g=0.15,
        matter_dynamics="conserved",
        boundary_condition="periodic",
        unit_lane="normalized",
        stability_safety=0.2,
    )
    return replace(base, **changes)


def _state(n: int = 32, dx: float = 0.25) -> tuple[MatterSpaceState, float]:
    x = np.arange(n, dtype=float) * dx
    length = n * dx
    C = 0.2 + 0.03 * np.cos(2.0 * np.pi * x / length)
    phi = 0.03 * np.sin(2.0 * np.pi * x / length)
    pi = 0.01 * np.cos(4.0 * np.pi * x / length)
    return MatterSpaceState(C, phi, pi), dx


def test_changing_c_split_conserves_mass_and_reports_shared_ledger() -> None:
    state, dx = _state()
    cfg = _config()
    dt = dx / cfg.space_speed
    previous = state.space_response - dt * state.space_rate
    before_energy = causal_split_energy(state, previous, dt, dx, cfg)
    old_C = state.C.copy()
    updated, old_phi, ledger = causal_matter_space_split_step(
        state, previous, dt, dx, cfg
    )
    after_energy = causal_split_energy(updated, old_phi, dt, dx, cfg)
    scale = max(abs(before_energy), 1.0)
    assert np.max(np.abs(updated.C - old_C)) > 1e-8
    assert ledger["mass_relative_drift"] <= 1e-10
    assert abs(ledger["shared_ledger_residual"]) / scale <= 1e-6
    assert abs(ledger["matter_ledger_residual"]) / scale <= 1e-6
    assert after_energy - before_energy <= 1e-9 * scale
    assert ledger["trace_feedback"] is False


def test_split_subcycles_are_deterministic_and_cfl_is_exact() -> None:
    state, dx = _state()
    cfg = _config()
    dt = dx / cfg.space_speed
    previous = state.space_response - dt * state.space_rate
    first, old_first, ledger_first = causal_matter_space_split_step(
        state, previous, dt, dx, cfg
    )
    second, old_second, ledger_second = causal_matter_space_split_step(
        state, previous, dt, dx, cfg
    )
    np.testing.assert_allclose(first.C, second.C, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(first.space_response, second.space_response, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(old_first, old_second, rtol=0.0, atol=0.0)
    assert ledger_first["matter_substeps"] == ledger_second["matter_substeps"]
    assert ledger_first["mass_relative_drift"] == ledger_second["mass_relative_drift"]


def test_nonconserved_c_lane_is_explicitly_deferred() -> None:
    state, dx = _state()
    cfg = _config(matter_dynamics="nonconserved")
    dt = dx / cfg.space_speed
    previous = state.space_response - dt * state.space_rate
    with pytest.raises(NotImplementedError, match="requires conserved C"):
        causal_matter_space_split_step(state, previous, dt, dx, cfg)
