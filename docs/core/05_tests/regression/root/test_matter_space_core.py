"""Numerical gates for the opt-in matter-space response candidate."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from docs.core.uet_matter_space import (
    MatterSpaceConfig,
    MatterSpaceStabilityError,
    MatterSpaceState,
    matter_space_chemical_potentials,
    matter_space_dissipation,
    matter_space_free_energy,
    matter_space_stability_limit,
    matter_space_step,
)
from docs.core.uet_spatial import integral_1d, laplacian_1d
from docs.core.uet_trace import TraceKernelConfig


def _state(n: int = 32, dx: float = 0.25) -> MatterSpaceState:
    x = np.arange(n, dtype=float) * dx
    length = n * dx
    C = 0.25 + 0.04 * np.cos(2.0 * np.pi * x / length)
    Phi = 0.03 * np.sin(2.0 * np.pi * x / length)
    Pi = 0.01 * np.cos(4.0 * np.pi * x / length)
    return MatterSpaceState(C, Phi, Pi)


def _config(**changes: object) -> MatterSpaceConfig:
    base = MatterSpaceConfig(
        a_matter=-0.5,
        b_matter=1.0,
        kappa_matter=0.1,
        mobility_matter=0.4,
        a_space=0.8,
        b_space=0.6,
        kappa_space=0.2,
        mobility_space=0.5,
        tau_space=0.7,
        coupling_g=0.15,
        stability_safety=0.2,
        ledger_tolerance=1e-6,
    )
    return replace(base, **changes)


@pytest.mark.parametrize("boundary", ["periodic", "zero_flux"])
def test_finite_volume_laplacian_has_zero_integral(boundary: str) -> None:
    rng = np.random.default_rng(1103)
    field = rng.normal(size=41)
    lap = laplacian_1d(field, 0.17, boundary)
    assert abs(integral_1d(lap, 0.17)) <= 2e-13


def test_local_polynomial_derivative_residual_is_small() -> None:
    rng = np.random.default_rng(2207)
    C = rng.normal(scale=0.3, size=17)
    Phi = rng.normal(scale=0.2, size=17)
    dC = rng.normal(size=17)
    dPhi = rng.normal(size=17)
    cfg = _config()

    def local_energy(epsilon: float) -> float:
        c = C + epsilon * dC
        phi = Phi + epsilon * dPhi
        density = (
            0.5 * cfg.a_matter * c**2
            + 0.25 * cfg.b_matter * c**4
            + 0.5 * cfg.a_space * phi**2
            + 0.25 * cfg.b_space * phi**4
            - 0.5 * cfg.coupling_g * c**2 * phi
        )
        return float(np.sum(density))

    h = 1e-3
    finite_difference = (
        -local_energy(2.0 * h)
        + 8.0 * local_energy(h)
        - 8.0 * local_energy(-h)
        + local_energy(-2.0 * h)
    ) / (12.0 * h)
    derivative_C = (
        cfg.a_matter * C
        + cfg.b_matter * C**3
        - cfg.coupling_g * C * Phi
    )
    derivative_Phi = (
        cfg.a_space * Phi
        + cfg.b_space * Phi**3
        - 0.5 * cfg.coupling_g * C**2
    )
    analytical = float(np.sum(derivative_C * dC + derivative_Phi * dPhi))
    assert abs(finite_difference - analytical) <= 1e-10


@pytest.mark.parametrize("boundary", ["periodic", "zero_flux"])
def test_full_discrete_directional_derivative_closes(boundary: str) -> None:
    rng = np.random.default_rng(3319)
    state = _state(n=36, dx=0.2)
    cfg = _config(boundary_condition=boundary)
    dC = rng.normal(size=state.C.size)
    dPhi = rng.normal(size=state.C.size)
    dC /= np.linalg.norm(dC)
    dPhi /= np.linalg.norm(dPhi)
    mu_C, mu_Phi = matter_space_chemical_potentials(state, 0.2, cfg)
    analytical = integral_1d(mu_C * dC + mu_Phi * dPhi, 0.2)

    def energy(epsilon: float) -> float:
        shifted = MatterSpaceState(
            state.C + epsilon * dC,
            state.space_response + epsilon * dPhi,
            state.space_rate,
        )
        return matter_space_free_energy(shifted, 0.2, cfg)

    h = 2e-4
    finite_difference = (
        -energy(2.0 * h)
        + 8.0 * energy(h)
        - 8.0 * energy(-h)
        + energy(-2.0 * h)
    ) / (12.0 * h)
    scale = max(abs(analytical), abs(finite_difference), 1e-12)
    assert abs(finite_difference - analytical) / scale <= 1e-6


@pytest.mark.parametrize("matter_dynamics", ["conserved", "nonconserved"])
def test_closed_step_has_nonnegative_source_and_descending_energy(
    matter_dynamics: str,
) -> None:
    state = _state()
    cfg = _config(matter_dynamics=matter_dynamics)
    dt = 0.1 * matter_space_stability_limit(state, 0.25, cfg)
    result = matter_space_step(state, dt, 0.25, cfg)
    assert result.energy_ledger["actual_delta"] <= 1e-9 * max(
        abs(result.energy_ledger["free_plus_space_kinetic_before"]), 1.0
    )
    assert result.energy_ledger["closure_relative"] <= 1e-6
    assert result.diagnostics["source_nonnegative"]
    assert result.diagnostics["field_clipping_applied"] is False


def test_conserved_lane_preserves_matter_over_many_steps() -> None:
    state = _state()
    cfg = _config(matter_dynamics="conserved")
    initial = integral_1d(state.C, 0.25)
    dt = 0.08 * matter_space_stability_limit(state, 0.25, cfg)
    current = state
    for _ in range(80):
        result = matter_space_step(current, dt, 0.25, cfg)
        current = MatterSpaceState(result.C, result.space_response, result.space_rate)
    drift = abs(integral_1d(current.C, 0.25) - initial) / max(abs(initial), 1e-12)
    assert drift <= 1e-10


def test_conserved_lane_rejects_nonzero_net_source() -> None:
    state = _state()
    cfg = _config(matter_dynamics="conserved")
    dt = 0.1 * matter_space_stability_limit(state, 0.25, cfg)
    with pytest.raises(ValueError, match="integral J_C"):
        matter_space_step(state, dt, 0.25, cfg, matter_source=np.ones(state.C.size))


def test_open_space_drive_is_explicit_in_the_ledger() -> None:
    state = _state()
    cfg = _config()
    dt = 0.02 * matter_space_stability_limit(state, 0.25, cfg)
    drive = 0.03 * np.cos(np.linspace(0.0, 2.0 * np.pi, state.C.size, endpoint=False))
    result = matter_space_step(state, dt, 0.25, cfg, space_source=drive)
    assert abs(result.energy_ledger["space_input_power"]) > 0.0
    assert result.energy_ledger["closure_relative"] <= 1e-6
    assert result.energy_ledger["joule_claim"] is False


def test_stability_preflight_rejects_oversized_step_without_clipping() -> None:
    state = _state()
    cfg = _config()
    max_dt = matter_space_stability_limit(state, 0.25, cfg)
    with pytest.raises(MatterSpaceStabilityError, match="recommended_max_dt") as captured:
        matter_space_step(state, 1.01 * max_dt, 0.25, cfg)
    assert captured.value.recommended_max_dt == pytest.approx(max_dt)


def test_v1_rejects_non_1d_state_and_si_lane() -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        MatterSpaceState(np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((4, 4)))
    with pytest.raises(NotImplementedError, match="normalized"):
        _config(unit_lane="SI")


@pytest.mark.parametrize(
    "field,value",
    [
        ("b_matter", 0.0),
        ("kappa_matter", 0.0),
        ("mobility_matter", 0.0),
        ("b_space", 0.0),
        ("kappa_space", 0.0),
        ("mobility_space", 0.0),
        ("tau_space", 0.0),
        ("a_space", -1.0),
        ("coupling_g", -1.0),
    ],
)
def test_coefficient_contract_rejects_invalid_values(field: str, value: float) -> None:
    with pytest.raises((ValueError, NotImplementedError)):
        _config(**{field: value})


def test_g_zero_matches_decoupled_matter_baseline() -> None:
    state_a = _state()
    state_b = MatterSpaceState(
        state_a.C,
        state_a.space_response + 0.4 * np.sin(np.linspace(0.0, 2.0 * np.pi, state_a.C.size)),
        state_a.space_rate + 0.2,
    )
    cfg = _config(coupling_g=0.0)
    dt = 0.05 * min(
        matter_space_stability_limit(state_a, 0.25, cfg),
        matter_space_stability_limit(state_b, 0.25, cfg),
    )
    result_a = matter_space_step(state_a, dt, 0.25, cfg)
    result_b = matter_space_step(state_b, dt, 0.25, cfg)
    np.testing.assert_allclose(result_a.C, result_b.C, rtol=0.0, atol=1e-10)


def test_same_matter_different_physical_space_state_changes_future() -> None:
    state_a = _state()
    state_b = MatterSpaceState(
        state_a.C,
        state_a.space_response + 0.15 * np.cos(np.linspace(0.0, 2.0 * np.pi, state_a.C.size)),
        state_a.space_rate + 0.08,
    )
    cfg = _config(coupling_g=0.3)
    dt = 0.05 * min(
        matter_space_stability_limit(state_a, 0.25, cfg),
        matter_space_stability_limit(state_b, 0.25, cfg),
    )
    result_a = matter_space_step(state_a, dt, 0.25, cfg)
    result_b = matter_space_step(state_b, dt, 0.25, cfg)
    difference = max(
        np.max(np.abs(result_a.C - result_b.C)),
        np.max(np.abs(result_a.space_response - result_b.space_response)),
        np.max(np.abs(result_a.space_rate - result_b.space_rate)),
    )
    assert difference > 1e-8


def test_trace_switch_and_trace_history_do_not_change_physical_future() -> None:
    state = _state()
    cfg = _config()
    dt = 0.05 * matter_space_stability_limit(state, 0.25, cfg)
    trace_cfg = TraceKernelConfig(D_trace=0.05, tau_trace=0.2, lambda_trace=0.1)
    quiet = [np.zeros_like(state.C)]
    active = [np.ones_like(state.C)]
    no_trace = matter_space_step(state, dt, 0.25, cfg, trace_config=None)
    quiet_trace = matter_space_step(
        state, dt, 0.25, cfg, trace_history=quiet, trace_config=trace_cfg
    )
    active_trace = matter_space_step(
        state, dt, 0.25, cfg, trace_history=active, trace_config=trace_cfg
    )
    for field in ("C", "space_response", "space_rate"):
        np.testing.assert_allclose(
            getattr(no_trace, field), getattr(quiet_trace, field), rtol=0.0, atol=1e-12
        )
        np.testing.assert_allclose(
            getattr(quiet_trace, field), getattr(active_trace, field), rtol=0.0, atol=1e-12
        )
    assert quiet_trace.trace_observable is not None
    assert active_trace.trace_observable is not None
    assert not np.allclose(quiet_trace.trace_observable, active_trace.trace_observable)
    assert active_trace.diagnostics["trace_backreaction"] is False


def test_dissipation_density_is_nonnegative_by_construction() -> None:
    state = _state()
    cfg = _config()
    mu_C, _ = matter_space_chemical_potentials(state, 0.25, cfg)
    sigma_C, sigma_Phi, sigma = matter_space_dissipation(state, mu_C, 0.25, cfg)
    assert min(float(np.min(sigma_C)), float(np.min(sigma_Phi)), float(np.min(sigma))) >= -1e-12
