"""Tests for the fixed-background first-order theory spine control."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_theory_spine import (
    Covariant3p1State, TheorySpineConfig, characteristic_analysis,
    recommended_max_dt, theory_spine_contract, theory_spine_step,
)


def _config() -> TheorySpineConfig:
    return TheorySpineConfig(0.7, 0.5, 0.1, 0.2, 0.4, "periodic", "natural", "minkowski_1p1_fixed", "locked_wave5_control")


def _state(cells: int = 128) -> tuple[Covariant3p1State, float]:
    x = np.linspace(0.0, 2.0 * np.pi, cells, endpoint=False)
    dx = float(x[1] - x[0])
    matter = np.sin(x)
    response = 0.4 * np.cos(2.0 * x)
    derivative = lambda value: (np.roll(value, -1) - np.roll(value, 1)) / (2.0 * dx)
    return Covariant3p1State(matter, np.zeros(cells), derivative(matter), response, np.zeros(cells), derivative(response), np.diag([-1.0, 1.0])), dx


def test_characteristics_are_real_complete_and_subluminal() -> None:
    result = characteristic_analysis(_config())
    assert result["status"] == "PASS_STRONG_HYPERBOLIC_LINEAR_CONTROL"
    assert result["maximum_characteristic_speed"] <= 1.0
    assert result["curved_3p1"] == "NOT_IMPLEMENTED"


def test_superluminal_and_curved_requests_are_rejected() -> None:
    with pytest.raises(ValueError, match="causal cone"):
        TheorySpineConfig(1.1, 0.5, 0.0, 0.0, 0.4, "periodic", "natural", "minkowski_1p1_fixed", "x")
    with pytest.raises(NotImplementedError, match=r"curved 3\+1"):
        TheorySpineConfig(0.7, 0.5, 0.0, 0.0, 0.4, "periodic", "natural", "curved_3p1", "x")


def test_cfl_preflight_rejects_large_step_without_clipping() -> None:
    state, dx = _state()
    limit = recommended_max_dt(dx, _config())
    with pytest.raises(ValueError, match="recommended_max_dt"):
        theory_spine_step(state, limit * 1.01, dx, _config())


def test_step_reports_constraint_energy_and_trace_ledgers() -> None:
    state, dx = _state()
    result = theory_spine_step(state, 0.1 * recommended_max_dt(dx, _config()), dx, _config())
    assert result.constraints.matter_gradient_constraint_max_abs <= 1e-12
    assert result.constraints.response_gradient_constraint_max_abs <= 1e-12
    assert result.generated_trace >= 0.0
    assert result.diagnostics["field_clipping"] is False
    assert result.stress_energy.shape == (2, 2, state.matter_coordinate.size)


def test_zero_state_is_exact_fixed_point() -> None:
    cells = 32
    zero = np.zeros(cells)
    state = Covariant3p1State(zero, zero, zero, zero, zero, zero, np.diag([-1.0, 1.0]))
    result = theory_spine_step(state, 0.01, 0.1, _config())
    assert np.max(np.abs(result.physical_state.matter_coordinate)) == 0.0
    assert np.max(np.abs(result.physical_state.response)) == 0.0
    assert result.generated_trace == 0.0


def test_contract_blocks_curved_gr_claim() -> None:
    contract = theory_spine_contract()
    assert contract["curved_3p1"] == "BLOCKED"
    assert contract["dynamical_metric"] == "BLOCKED"
