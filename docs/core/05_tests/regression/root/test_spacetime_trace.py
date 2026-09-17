"""Gate-level tests for the opt-in spacetime thermodynamic trace lane."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_master_equation import (
    LEGACY_OPERATOR_MODE,
    SPACETIME_TRACE_OPERATOR_MODE,
    UETMasterEquation,
    dynamics_step_complete,
    omega_functional_complete,
)
from docs.core.uet_parameters import UETParameters
from docs.core.uet_trace import (
    TraceKernelConfig,
    compute_dissipation_source,
    compute_spacetime_trace,
    markovian_trace,
    trace_causal_leakage,
)


def test_trace_config_rejects_superluminal_configured_speed() -> None:
    with pytest.raises(ValueError):
        TraceKernelConfig(D_trace=4.0, tau_trace=1.0, c_limit=1.0)


def test_dissipation_source_is_nonnegative() -> None:
    previous = np.zeros(8)
    current = np.linspace(-1.0, 1.0, 8)
    source = compute_dissipation_source(previous, current, dt=0.1)
    assert np.min(source) >= 0.0
    assert np.any(source > 0.0)


def test_no_source_gives_zero_trace() -> None:
    config = TraceKernelConfig(D_trace=1.0, tau_trace=1.0, boundary_condition="zero")
    source = np.zeros(16)
    trace = compute_spacetime_trace([source, source], dx=1.0, dt=0.1, config=config)
    np.testing.assert_allclose(trace, 0.0, atol=1e-15)


def test_causal_cone_has_no_discrete_leakage() -> None:
    config = TraceKernelConfig(D_trace=1.0, tau_trace=1.0, boundary_condition="zero")
    source = np.zeros(32)
    source[16] = 1.0
    history = [source] + [np.zeros_like(source) for _ in range(4)]
    response = compute_spacetime_trace(history, dx=1.0, dt=1.0, config=config)
    leakage = trace_causal_leakage(response, (16,), elapsed=4.0, dx=1.0, config=config)
    assert response.max() > 0.0
    assert leakage <= 1e-12


def test_same_present_source_can_have_different_trace_history() -> None:
    config = TraceKernelConfig(D_trace=1.0, tau_trace=1.0, boundary_condition="zero")
    present = np.zeros(16)
    present[8] = 1.0
    old_quiet = np.zeros_like(present)
    old_active = np.ones_like(present)
    quiet_history = compute_spacetime_trace(
        [old_quiet, present], dx=1.0, dt=0.5, config=config
    )
    active_history = compute_spacetime_trace(
        [old_active, present], dx=1.0, dt=0.5, config=config
    )
    assert not np.allclose(quiet_history, active_history)


def test_markovian_baseline_is_explicit() -> None:
    source = np.linspace(0.0, 1.0, 10)
    np.testing.assert_allclose(markovian_trace(source), source)


def test_empty_trace_history_matches_legacy_baseline() -> None:
    params = UETParameters(
        alpha=0.5,
        gamma=0.0,
        kappa=0.1,
        beta=0.0,
        W_N=0.0,
        a0_viscosity=0.0,
    )
    C = np.linspace(0.1, 0.9, 16)
    baseline = dynamics_step_complete(
        C, dt=0.01, dx=1.0, params=params, operator_mode=LEGACY_OPERATOR_MODE
    )
    trace_params = UETParameters(
        alpha=params.alpha,
        gamma=params.gamma,
        kappa=params.kappa,
        beta=params.beta,
        W_N=params.W_N,
        a0_viscosity=0.0,
        operator_mode=SPACETIME_TRACE_OPERATOR_MODE,
    )
    result = dynamics_step_complete(
        C,
        dt=0.01,
        dx=1.0,
        params=trace_params,
        operator_mode=SPACETIME_TRACE_OPERATOR_MODE,
        trace_history=[],
    )
    np.testing.assert_allclose(result.C, baseline)
    np.testing.assert_allclose(result.trace_observable, 0.0)


def test_engine_returns_structured_trace_result_and_cache_is_not_I_state() -> None:
    params = UETParameters(
        alpha=0.0,
        gamma=0.0,
        kappa=0.0,
        beta=0.0,
        W_N=0.0,
        operator_mode=SPACETIME_TRACE_OPERATOR_MODE,
        a0_viscosity=0.0,
    )
    engine = UETMasterEquation(params=params)
    C = np.zeros(16)
    C[4] = 1.0
    result = engine.step(C, dt=0.1, dx=1.0)
    assert result.C.shape == C.shape
    assert result.V is None
    assert result.trace_observable.shape == C.shape
    assert engine.I is None
    assert len(engine.trace_history) == 1
    assert result.diagnostics["ontology"].startswith("history_functional")


def test_two_dimensional_trace_preserves_shape() -> None:
    config = TraceKernelConfig(D_trace=0.25, tau_trace=0.25)
    source = np.zeros((6, 8))
    source[3, 4] = 1.0
    trace = compute_spacetime_trace([source], dx=1.0, dt=0.1, config=config)
    assert trace.shape == source.shape
    assert np.isfinite(trace).all()


def test_omega_information_gradient_and_mass_terms_are_explicit() -> None:
    params = UETParameters(kappa=0.0, beta=0.0, W_N=0.0, kappa_I=1.0)
    C = np.ones(8)
    I = np.zeros(8)
    I[4:] = 1.0
    omega_without_I = omega_functional_complete(C, dx=1.0, params=params)
    omega_with_I = omega_functional_complete(C, I=I, dx=1.0, params=params)
    assert omega_with_I > omega_without_I
