"""Verification tests for the opt-in causal Phi/Pi discrete-gradient lane."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_matter_space import MatterSpaceConfig, MatterSpaceState
from docs.core.uet_matter_space_causal import (
    causal_space_discrete_energy,
    causal_space_discrete_gradient_step,
)


def _config(**changes: object) -> MatterSpaceConfig:
    base = MatterSpaceConfig(
        a_matter=-0.2,
        b_matter=1.0,
        kappa_matter=0.1,
        mobility_matter=0.4,
        a_space=0.8,
        b_space=0.6,
        kappa_space=0.2,
        mobility_space=0.5,
        tau_space=0.7,
        coupling_g=0.15,
        boundary_condition="periodic",
        unit_lane="normalized",
        stability_safety=0.2,
    )
    from dataclasses import replace

    return replace(base, **changes)


def _state(n: int = 32, dx: float = 0.25) -> tuple[MatterSpaceState, float]:
    x = np.arange(n, dtype=float) * dx
    length = n * dx
    C = 0.2 + 0.03 * np.cos(2.0 * np.pi * x / length)
    phi = 0.03 * np.sin(2.0 * np.pi * x / length)
    pi = 0.01 * np.cos(4.0 * np.pi * x / length)
    return MatterSpaceState(C, phi, pi), dx


@pytest.mark.parametrize("boundary", ["periodic", "zero_flux"])
def test_discrete_gradient_closes_coupled_source_ledger(boundary: str) -> None:
    state, dx = _state()
    cfg = _config(boundary_condition=boundary)
    dt = dx / cfg.space_speed
    previous = state.space_response - dt * state.space_rate
    source = 0.01 * np.cos(np.linspace(0.0, 2.0 * np.pi, state.C.size, endpoint=False))
    before = causal_space_discrete_energy(
        state.space_response, previous, state.C, dt, dx, cfg
    )
    updated, old_phi, ledger = causal_space_discrete_gradient_step(
        state, previous, dt, dx, cfg, space_source=source
    )
    after = causal_space_discrete_energy(
        updated.space_response, old_phi, state.C, dt, dx, cfg
    )
    damping = (
        np.sum((updated.space_response - previous) ** 2)
        * dx
        / (4.0 * cfg.mobility_space * dt)
    )
    residual = after - before + damping - ledger["source_work"]
    assert abs(residual) / max(abs(before), 1.0) <= 1e-10
    assert ledger["max_root_residual"] <= 1e-10
    assert ledger["cfl"] == pytest.approx(1.0)


def test_reference_lane_has_compact_support_and_descending_two_level_energy() -> None:
    n = 161
    dx = 0.0125
    center = n // 2
    cfg = _config(
        a_matter=0.0,
        kappa_matter=1.0e-8,
        mobility_matter=1.0e-8,
        a_space=0.0,
        b_space=1.0e-12,
        kappa_space=5.0,
        mobility_space=1.0,
        tau_space=5.0,
        coupling_g=0.0,
        boundary_condition="zero_flux",
    )
    dt = dx / cfg.space_speed
    C = np.zeros(n)
    phi = np.zeros(n)
    pi = np.zeros(n)
    pi[center] = 1.0 / dx
    previous = phi - dt * pi
    state = MatterSpaceState(C, phi, pi)
    previous_energy = causal_space_discrete_energy(phi, previous, C, dt, dx, cfg)
    max_increase = 0.0
    max_leakage = 0.0
    for step in range(1, 41):
        state, old_phi, ledger = causal_space_discrete_gradient_step(
            state, previous, dt, dx, cfg
        )
        current = state.space_response
        energy = causal_space_discrete_energy(current, old_phi, C, dt, dx, cfg)
        max_increase = max(max_increase, energy - previous_energy)
        radius = step - 1
        outside = np.ones(n, dtype=bool)
        outside[max(0, center - radius) : min(n, center + radius + 1)] = False
        max_leakage = max(max_leakage, float(np.max(np.abs(current[outside]))))
        previous_energy = energy
        previous = old_phi
    assert max_increase <= 1e-10
    assert max_leakage == 0.0
