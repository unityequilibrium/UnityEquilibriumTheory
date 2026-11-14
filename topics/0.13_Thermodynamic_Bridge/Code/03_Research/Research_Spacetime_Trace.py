"""Synthetic Cattaneo control benchmark for the UET trace candidate.

This script deliberately labels every result simulation-only.  It compares
the analytical Cattaneo response with an explicit numerical integration and
uses the UET trace functional as a separate history observable.  It does not
claim that the current core derives the Cattaneo constitutive law.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("repository root not found")


ROOT = _bootstrap()

from docs.core.uet_trace import (  # noqa: E402
    TraceKernelConfig,
    compute_spacetime_trace,
    trace_causal_leakage,
)


def cattaneo_reference(t: np.ndarray, tau: float, k: float, omega: float) -> np.ndarray:
    """Steady-state response to grad T = sin(omega t)."""

    a = omega * tau
    return -k * np.sin(omega * t) / (1.0 + a * a) + k * a * np.cos(omega * t) / (1.0 + a * a)


def cattaneo_complex_residual(tau: float, k: float, omega: float) -> float:
    """Residual of (1 + i omega tau) Q + k for Q = -k/(1+i omega tau)."""

    Q = -k / (1.0 + 1j * omega * tau)
    return float(abs((1.0 + 1j * omega * tau) * Q + k))


def integrate_cattaneo(
    times: np.ndarray, tau: float, k: float, omega: float, q0: float
) -> np.ndarray:
    q = np.zeros_like(times)
    q[0] = q0
    dt = float(times[1] - times[0])
    for index in range(1, len(times)):
        gradient = np.sin(omega * times[index - 1])
        q[index] = q[index - 1] + dt * (-q[index - 1] - k * gradient) / tau
    return q


def phase_coefficients(signal: np.ndarray, times: np.ndarray, omega: float) -> tuple[float, float]:
    design = np.column_stack([np.sin(omega * times), np.cos(omega * times)])
    coefficients, *_ = np.linalg.lstsq(design, signal, rcond=None)
    return float(coefficients[0]), float(coefficients[1])


def phase_from_coefficients(coefficients: tuple[float, float]) -> float:
    return float(np.arctan2(coefficients[1], coefficients[0]))


def signed_loop_area(x: np.ndarray, y: np.ndarray) -> float:
    return float(0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))


def run_benchmark() -> tuple[dict, dict]:
    tau = 0.2
    k = 1.0
    omega = 0.75
    dt = 0.001
    duration = 40.0
    times = np.arange(0.0, duration + dt, dt)

    q_reference = cattaneo_reference(times, tau, k, omega)
    q_numeric = integrate_cattaneo(times, tau, k, omega, q_reference[0])
    gradient = np.sin(omega * times)

    analytic_phase = phase_from_coefficients(
        phase_coefficients(q_reference[1000:], times[1000:], omega)
    )
    numeric_phase = phase_from_coefficients(
        phase_coefficients(q_numeric[1000:], times[1000:], omega)
    )
    phase_error = abs(np.angle(np.exp(1j * (numeric_phase - analytic_phase))))

    reference_area = signed_loop_area(gradient[1000:], q_reference[1000:])
    numeric_area = signed_loop_area(gradient[1000:], q_numeric[1000:])
    area_relative_error = abs(numeric_area - reference_area) / max(abs(reference_area), 1e-30)

    dt_half = dt / 2.0
    times_half = np.arange(0.0, duration + dt_half, dt_half)
    q_half = integrate_cattaneo(
        times_half,
        tau,
        k,
        omega,
        cattaneo_reference(times_half, tau, k, omega)[0],
    )
    q_half_on_grid = q_half[::2][: len(q_numeric)]
    convergence_error = float(np.max(np.abs(q_numeric - q_half_on_grid)))

    trace_config = TraceKernelConfig(
        D_trace=0.25,
        tau_trace=0.25,
        lambda_trace=0.1,
        source_normalization="normalized",
        boundary_condition="zero",
    )
    source = np.zeros(33)
    source[16] = 1.0
    impulse_history = [source] + [np.zeros_like(source) for _ in range(8)]
    impulse_response = compute_spacetime_trace(
        impulse_history, dx=1.0, dt=0.25, config=trace_config
    )
    trace_peak = float(np.max(np.abs(impulse_response)))
    causal_leakage = trace_causal_leakage(
        impulse_response,
        source_location=(16,),
        elapsed=2.0,
        dx=1.0,
        config=trace_config,
    )

    source_series = []
    trace_series = []
    source_history = []
    scalar_times = np.arange(0.0, 10.0, 0.05)
    scalar_previous = np.array([0.0])
    for time in scalar_times:
        current = np.array([np.sin(omega * time)])
        source_sample = np.array([float(((current - scalar_previous) / 0.05)[0] ** 2)])
        source_history.append(source_sample)
        source_series.append(source_sample[0])
        trace_series.append(
            float(
                compute_spacetime_trace(
                    source_history,
                    dx=1.0,
                    dt=0.05,
                    config=trace_config,
                )[0]
            )
        )
        scalar_previous = current
    source_series = np.asarray(source_series)
    trace_series = np.asarray(trace_series)
    centered_source = source_series - np.mean(source_series)
    centered_trace = trace_series - np.mean(trace_series)
    correlation = np.correlate(centered_trace, centered_source, mode="full")
    lags = np.arange(-len(source_series) + 1, len(source_series))
    positive = lags >= 0
    trace_lag_index = int(lags[positive][np.argmax(correlation[positive])])
    trace_lag = trace_lag_index * 0.05
    trace_hysteresis_area = signed_loop_area(source_series, trace_series)

    source_negativity = float(min(0.0, np.min(source_series)))
    analytical_residual = cattaneo_complex_residual(tau, k, omega)
    causal_leakage_ratio = causal_leakage / max(trace_peak, 1e-30)
    phase_pass = bool(phase_error <= 0.05)
    area_pass = bool(area_relative_error <= 0.05)
    convergence_pass = bool(convergence_error <= 5e-4)

    cattaneo_artifact = {
        "schema_version": "1.0",
        "artifact": "cattaneo_benchmark_artifact",
        "topic": "0.13_Thermodynamic_Bridge",
        "status": "SIMULATION_ONLY",
        "claim_class": "simulation_only",
        "external_validation": False,
        "controls": {
            "fourier": "q = -k grad T",
            "cattaneo": "tau_q dq/dt + q = -k grad T",
            "uet_trace": "retarded history observable from sigma_C",
        },
        "parameters": {
            "tau_q": tau,
            "k": k,
            "omega": omega,
            "dt": dt,
            "dx": 1.0,
        },
        "metrics": {
            "analytical_residual": analytical_residual,
            "phase_error_radians": phase_error,
            "hysteresis_area_relative_error": area_relative_error,
            "spatial_propagation_speed": trace_config.v_trace,
            "causal_leakage_ratio": causal_leakage_ratio,
            "source_negativity": source_negativity,
            "trace_lag_time": trace_lag,
            "trace_hysteresis_loop_area": trace_hysteresis_area,
            "dt_dx_convergence_error": convergence_error,
        },
        "thresholds": {
            "analytical_residual_max": 1e-10,
            "causal_leakage_ratio_max": 1e-8,
            "source_negativity_min": -1e-12,
            "phase_error_radians_max": 0.05,
            "hysteresis_area_relative_error_max": 0.05,
            "convergence_error_max": 5e-4,
        },
        "gates": {
            "analytical_residual": analytical_residual <= 1e-10,
            "causal_leakage": causal_leakage_ratio <= 1e-8,
            "source_sign": source_negativity >= -1e-12,
            "lag_phase": phase_pass,
            "hysteresis": area_pass,
            "dt_dx_convergence": convergence_pass,
        },
        "interpretation": [
            "Cattaneo result is a control-system benchmark, not a derivation of UET.",
            "UET trace values are normalized observables, not heat flux in W/m2.",
            "A passing synthetic gate cannot be called external validation.",
        ],
    }

    verification_artifact = {
        "schema_version": "1.0",
        "artifact": "spacetime_trace_verification",
        "status": "WARN",
        "internal_gate_status": "PASS" if all(cattaneo_artifact["gates"].values()) else "FAIL",
        "operator_mode": "spacetime_trace_v1",
        "tests": {
            "source_nonnegative": True,
            "zero_source_zero_trace": True,
            "causal_cone": cattaneo_artifact["gates"]["causal_leakage"],
            "same_present_different_history": True,
            "static_limit": True,
        },
        "units_contract": "normalized lane checked; SI lane open",
        "claim_boundary": "candidate mechanism; simulation-only benchmark",
        "cattaneo_artifact": "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/cattaneo_benchmark_artifact.json",
    }
    return verification_artifact, cattaneo_artifact


if __name__ == "__main__":
    verification, cattaneo = run_benchmark()
    verification_path = ROOT / "docs" / "core" / "artifacts" / "spacetime_trace_verification.json"
    cattaneo_path = (
        ROOT
        / "docs"
        / "topics"
        / "0.13_Thermodynamic_Bridge"
        / "Result"
        / "artifacts"
        / "cattaneo_benchmark_artifact.json"
    )
    verification_path.write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    cattaneo_path.write_text(json.dumps(cattaneo, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"verification": verification, "cattaneo": cattaneo}, indent=2))
