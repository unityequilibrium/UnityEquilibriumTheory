"""Generate deterministic verification artifacts for matter_space_coupled_v1.

This audit measures numerical and ontology gates. It does not validate a physical
interpretation or promote any downstream UET topic.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from docs.core.uet_matter_space import (  # noqa: E402
    MATTER_SPACE_OPERATOR_MODE,
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_chemical_potentials,
    matter_space_dissipation,
    matter_space_free_energy,
    matter_space_stability_limit,
    matter_space_step,
)
from docs.core.uet_spatial import integral_1d, laplacian_1d  # noqa: E402
from docs.core.uet_trace import TraceKernelConfig  # noqa: E402
from docs.core.core_paths import canonical_artifact_path  # noqa: E402

ARTIFACT_DIR = REPO_ROOT / "docs" / "core" / "07_artifacts"
VERIFICATION_PATH = canonical_artifact_path("matter_space_variational_verification.json", "verification")
DEPENDENCY_PATH = canonical_artifact_path("matter_space_dependency_gate.json", "gates")
ALIGNMENT_PATH = canonical_artifact_path("master_equation_alignment_gate_v2.json", "gates")
FORMULA_AUDIT_PATH = canonical_artifact_path("matter_space_formula_audit.json", "correspondence")

THRESHOLDS = {
    "local_derivative_absolute_residual_max": 1e-10,
    "discrete_directional_derivative_relative_error_max": 1e-6,
    "conserved_matter_relative_drift_max": 1e-10,
    "minimum_dissipation_density_min": -1e-12,
    "closed_energy_relative_increase_max": 1e-9,
    "ledger_closure_relative_residual_max": 1e-6,
    "open_space_ledger_closure_relative_residual_max": 1e-6,
    "decoupled_baseline_absolute_error_max": 1e-10,
    "trace_switch_physical_absolute_error_max": 1e-12,
    "physical_history_signal_to_discretization_min": 10.0,
    "trace_history_physical_absolute_error_max": 1e-12,
    "causal_arrival_speed_relative_error_max": 0.05,
    "prearrival_leakage_fraction_max": 1e-6,
    "temporal_convergence_order_min": 1.5,
    "spatial_convergence_order_min": 1.5,
    "adiabatic_local_equilibrium_relative_error_max": 0.05,
}


def _metric(value: float, threshold: float, comparator: str, detail: str = "") -> dict[str, Any]:
    if comparator == "le":
        passed = value <= threshold
    elif comparator == "ge":
        passed = value >= threshold
    else:
        raise ValueError(comparator)
    return {
        "value": float(value),
        "threshold": float(threshold),
        "comparator": comparator,
        "gate": "PASS" if passed else "FAIL",
        "detail": detail,
    }


def _base_config(**changes: object) -> MatterSpaceConfig:
    config = MatterSpaceConfig(
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
        matter_dynamics="conserved",
        boundary_condition="periodic",
        unit_lane="normalized",
        stability_safety=0.2,
        ledger_tolerance=1e-6,
    )
    return replace(config, **changes)


def _base_state(n: int = 32, dx: float = 0.25) -> MatterSpaceState:
    x = np.arange(n, dtype=float) * dx
    length = n * dx
    return MatterSpaceState(
        0.25 + 0.04 * np.cos(2.0 * np.pi * x / length),
        0.03 * np.sin(2.0 * np.pi * x / length),
        0.01 * np.cos(4.0 * np.pi * x / length),
    )


def local_derivative_residual() -> float:
    rng = np.random.default_rng(2207)
    C = rng.normal(scale=0.3, size=17)
    Phi = rng.normal(scale=0.2, size=17)
    dC = rng.normal(size=17)
    dPhi = rng.normal(size=17)
    cfg = _base_config()

    def energy(epsilon: float) -> float:
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
        -energy(2.0 * h) + 8.0 * energy(h) - 8.0 * energy(-h) + energy(-2.0 * h)
    ) / (12.0 * h)
    d_local_C = cfg.a_matter * C + cfg.b_matter * C**3 - cfg.coupling_g * C * Phi
    d_local_Phi = (
        cfg.a_space * Phi + cfg.b_space * Phi**3 - 0.5 * cfg.coupling_g * C**2
    )
    analytical = float(np.sum(d_local_C * dC + d_local_Phi * dPhi))
    return abs(finite_difference - analytical)


def directional_derivative_error(boundary: str) -> float:
    rng = np.random.default_rng(3319)
    state = _base_state(n=36, dx=0.2)
    cfg = _base_config(boundary_condition=boundary)
    dC = rng.normal(size=state.C.size)
    dPhi = rng.normal(size=state.C.size)
    dC /= np.linalg.norm(dC)
    dPhi /= np.linalg.norm(dPhi)
    mu_C, mu_Phi = matter_space_chemical_potentials(state, 0.2, cfg)
    analytical = integral_1d(mu_C * dC + mu_Phi * dPhi, 0.2)

    def energy(epsilon: float) -> float:
        return matter_space_free_energy(
            MatterSpaceState(
                state.C + epsilon * dC,
                state.space_response + epsilon * dPhi,
                state.space_rate,
            ),
            0.2,
            cfg,
        )

    h = 2e-4
    numerical = (
        -energy(2.0 * h) + 8.0 * energy(h) - 8.0 * energy(-h) + energy(-2.0 * h)
    ) / (12.0 * h)
    return abs(numerical - analytical) / max(abs(numerical), abs(analytical), 1e-12)


def closed_trajectory_metrics() -> dict[str, float]:
    state = _base_state()
    cfg = _base_config()
    initial_matter = integral_1d(state.C, 0.25)
    dt = 0.05 * matter_space_stability_limit(state, 0.25, cfg)
    max_relative_increase = 0.0
    max_closure = 0.0
    minimum_sigma = np.inf
    finite = True
    clipping = False
    fitting = False
    current = state
    for _ in range(80):
        result = matter_space_step(current, dt, 0.25, cfg)
        before = float(result.energy_ledger["free_plus_space_kinetic_before"])
        delta = float(result.energy_ledger["actual_delta"])
        max_relative_increase = max(max_relative_increase, delta / max(abs(before), 1.0))
        max_closure = max(max_closure, float(result.energy_ledger["closure_relative"]))
        minimum_sigma = min(
            minimum_sigma, float(np.min(np.asarray(result.diagnostics["source_snapshot"])))
        )
        finite = finite and all(
            np.all(np.isfinite(field))
            for field in (result.C, result.space_response, result.space_rate)
        )
        clipping = clipping or bool(result.diagnostics["field_clipping_applied"])
        fitting = fitting or bool(result.diagnostics["parameter_fitting_applied"])
        current = MatterSpaceState(result.C, result.space_response, result.space_rate)
    relative_drift = abs(integral_1d(current.C, 0.25) - initial_matter) / max(
        abs(initial_matter), 1e-12
    )
    return {
        "relative_matter_drift": relative_drift,
        "max_relative_energy_increase": max_relative_increase,
        "max_ledger_closure_relative": max_closure,
        "minimum_dissipation_density": minimum_sigma,
        "all_finite": float(finite),
        "field_clipping_applied": float(clipping),
        "parameter_fitting_applied": float(fitting),
        "dt": dt,
    }


def open_drive_metrics() -> dict[str, float]:
    state = _base_state()
    cfg = _base_config()
    dt = 0.02 * matter_space_stability_limit(state, 0.25, cfg)
    drive = 0.03 * np.cos(np.linspace(0.0, 2.0 * np.pi, state.C.size, endpoint=False))
    result = matter_space_step(state, dt, 0.25, cfg, space_source=drive)
    return {
        "space_input_power": float(result.energy_ledger["space_input_power"]),
        "closure_relative": float(result.energy_ledger["closure_relative"]),
        "joule_claim": float(bool(result.energy_ledger["joule_claim"])),
    }


def _physical_difference(left: Any, right: Any) -> float:
    return max(
        float(np.max(np.abs(left.C - right.C))),
        float(np.max(np.abs(left.space_response - right.space_response))),
        float(np.max(np.abs(left.space_rate - right.space_rate))),
    )


def decoupling_and_history_metrics() -> dict[str, float]:
    state = _base_state()
    altered = MatterSpaceState(
        state.C,
        state.space_response + 0.15 * np.cos(np.linspace(0.0, 2.0 * np.pi, state.C.size)),
        state.space_rate + 0.08,
    )
    decoupled = _base_config(coupling_g=0.0)
    dt_decoupled = 0.04 * min(
        matter_space_stability_limit(state, 0.25, decoupled),
        matter_space_stability_limit(altered, 0.25, decoupled),
    )
    decoupled_a = matter_space_step(state, dt_decoupled, 0.25, decoupled)
    decoupled_b = matter_space_step(altered, dt_decoupled, 0.25, decoupled)
    decoupled_matter_error = float(np.max(np.abs(decoupled_a.C - decoupled_b.C)))

    coupled = _base_config(coupling_g=0.3)
    dt = 0.04 * min(
        matter_space_stability_limit(state, 0.25, coupled),
        matter_space_stability_limit(altered, 0.25, coupled),
    )
    coarse_a = matter_space_step(state, dt, 0.25, coupled)
    coarse_b = matter_space_step(altered, dt, 0.25, coupled)
    physical_signal = _physical_difference(coarse_a, coarse_b)

    half_a_1 = matter_space_step(state, 0.5 * dt, 0.25, coupled)
    half_a_2 = matter_space_step(
        MatterSpaceState(half_a_1.C, half_a_1.space_response, half_a_1.space_rate),
        0.5 * dt,
        0.25,
        coupled,
    )
    discretization_error = _physical_difference(coarse_a, half_a_2)
    signal_ratio = physical_signal / max(discretization_error, np.finfo(float).eps)

    trace_cfg = TraceKernelConfig(D_trace=0.05, tau_trace=0.2, lambda_trace=0.1)
    quiet = matter_space_step(
        state,
        dt,
        0.25,
        coupled,
        trace_history=[np.zeros_like(state.C)],
        trace_config=trace_cfg,
    )
    active = matter_space_step(
        state,
        dt,
        0.25,
        coupled,
        trace_history=[np.ones_like(state.C)],
        trace_config=trace_cfg,
    )
    no_trace = matter_space_step(state, dt, 0.25, coupled, trace_config=None)
    trace_history_physical_error = _physical_difference(quiet, active)
    trace_switch_physical_error = _physical_difference(no_trace, active)
    trace_observable_difference = float(
        np.max(np.abs(quiet.trace_observable - active.trace_observable))
    )
    return {
        "decoupled_matter_absolute_error": decoupled_matter_error,
        "physical_history_signal": physical_signal,
        "discretization_error": discretization_error,
        "physical_history_signal_to_discretization": signal_ratio,
        "trace_history_physical_absolute_error": trace_history_physical_error,
        "trace_switch_physical_absolute_error": trace_switch_physical_error,
        "trace_observable_history_difference": trace_observable_difference,
    }


def temporal_convergence() -> dict[str, Any]:
    tau = 0.8
    pi0 = 0.2
    final_time = 0.4
    cfg = MatterSpaceConfig(
        a_matter=0.0,
        b_matter=1.0,
        kappa_matter=1e-8,
        mobility_matter=1e-8,
        a_space=0.0,
        b_space=1e-14,
        kappa_space=0.1,
        mobility_space=1.0,
        tau_space=tau,
        coupling_g=0.0,
        matter_dynamics="conserved",
        boundary_condition="periodic",
        stability_safety=0.5,
    )
    errors: list[float] = []
    steps_list = [10, 20, 40]
    exact_pi = pi0 * np.exp(-final_time / tau)
    exact_phi = pi0 * tau * (1.0 - np.exp(-final_time / tau))
    for steps in steps_list:
        dt = final_time / steps
        state = MatterSpaceState(np.zeros(8), np.zeros(8), np.full(8, pi0))
        for _ in range(steps):
            result = matter_space_step(state, dt, 1.0, cfg)
            state = MatterSpaceState(result.C, result.space_response, result.space_rate)
        errors.append(
            max(
                float(np.max(np.abs(state.space_response - exact_phi))),
                float(np.max(np.abs(state.space_rate - exact_pi))),
            )
        )
    orders = [float(np.log(errors[i] / errors[i + 1]) / np.log(2.0)) for i in range(2)]
    return {"steps": steps_list, "errors": errors, "orders": orders, "minimum_order": min(orders)}


def spatial_convergence() -> dict[str, Any]:
    errors: list[float] = []
    cells = [32, 64, 128]
    length = 2.0 * np.pi
    for n in cells:
        dx = length / n
        x = np.arange(n, dtype=float) * dx
        field = np.sin(2.0 * x)
        exact = -4.0 * field
        numerical = laplacian_1d(field, dx, "periodic")
        errors.append(float(np.sqrt(np.mean(np.square(numerical - exact)))))
    orders = [float(np.log(errors[i] / errors[i + 1]) / np.log(2.0)) for i in range(2)]
    return {"cells": cells, "errors": errors, "orders": orders, "minimum_order": min(orders)}


def _positive_local_root(a_space: float, b_space: float, source: float) -> float:
    roots = np.roots([b_space, 0.0, a_space, -source])
    real = [float(root.real) for root in roots if abs(root.imag) <= 1e-10 and root.real >= 0.0]
    if not real:
        raise RuntimeError("no nonnegative local equilibrium root")
    return min(real, key=lambda value: abs(a_space * value + b_space * value**3 - source))


def adiabatic_limit_metrics() -> dict[str, Any]:
    a_values = [10.0, 40.0, 160.0]
    records: list[dict[str, float]] = []
    C_value = 1.0
    coupling = 0.4
    for a_space in a_values:
        tau = 0.01 / a_space
        kappa = 1e-6
        cfg = MatterSpaceConfig(
            a_matter=0.0,
            b_matter=1.0,
            kappa_matter=0.01,
            mobility_matter=0.1,
            a_space=a_space,
            b_space=1.0,
            kappa_space=kappa,
            mobility_space=1.0,
            tau_space=tau,
            coupling_g=coupling,
            matter_dynamics="conserved",
            boundary_condition="periodic",
            stability_safety=0.5,
        )
        state = MatterSpaceState(np.full(8, C_value), np.zeros(8), np.zeros(8))
        final_time = 8.0 / a_space
        dt = 0.8 * matter_space_stability_limit(state, 1.0, cfg)
        steps = int(np.ceil(final_time / dt))
        dt = final_time / steps
        for _ in range(steps):
            result = matter_space_step(state, dt, 1.0, cfg)
            state = MatterSpaceState(result.C, result.space_response, result.space_rate)
        root = _positive_local_root(a_space, cfg.b_space, 0.5 * coupling * C_value**2)
        relative_error = float(np.max(np.abs(state.space_response - root)) / max(abs(root), 1e-15))
        records.append(
            {
                "a_space": a_space,
                "tau_space": tau,
                "response_time": 1.0 / (cfg.mobility_space * a_space),
                "correlation_length": float(np.sqrt(kappa / a_space)),
                "local_root": root,
                "final_response": float(np.mean(state.space_response)),
                "relative_error": relative_error,
                "steps": float(steps),
            }
        )
    all_three_shrink = all(
        records[i + 1][key] < records[i][key]
        for key in ("tau_space", "response_time", "correlation_length")
        for i in range(len(records) - 1)
    )
    return {
        "records": records,
        "all_three_limit_scales_shrink": all_three_shrink,
        "highest_refinement_relative_error": records[-1]["relative_error"],
    }


def causal_pulse_metrics() -> dict[str, Any]:
    n = 1601
    dx = 0.0125
    center = n // 2
    distance = 1.0
    cfg = MatterSpaceConfig(
        a_matter=0.0,
        b_matter=1.0,
        kappa_matter=1e-8,
        mobility_matter=1e-8,
        a_space=0.0,
        b_space=1e-12,
        kappa_space=5.0,
        mobility_space=1.0,
        tau_space=5.0,
        coupling_g=0.0,
        matter_dynamics="conserved",
        boundary_condition="zero_flux",
        stability_safety=0.2,
    )
    pi = np.zeros(n)
    pi[center] = 1.0 / dx
    state = MatterSpaceState(np.zeros(n), np.zeros(n), pi)
    dt = 0.8 * matter_space_stability_limit(state, dx, cfg)
    expected_arrival = distance / cfg.space_speed
    final_time = 1.3 * expected_arrival
    target = center + int(round(distance / dx))
    times: list[float] = []
    detector: list[float] = []
    steps = int(np.ceil(final_time / dt))
    for step in range(1, steps + 1):
        result = matter_space_step(state, dt, dx, cfg)
        state = MatterSpaceState(result.C, result.space_response, result.space_rate)
        times.append(step * dt)
        detector.append(float(state.space_response[target]))
    time_array = np.asarray(times)
    signal = np.abs(np.asarray(detector))
    peak = float(np.max(signal))
    arrival_indices = np.flatnonzero(signal >= 0.2 * peak)
    arrival_time = float(time_array[arrival_indices[0]])
    measured_speed = distance / arrival_time
    speed_error = abs(measured_speed - cfg.space_speed) / cfg.space_speed
    guarded_prearrival = time_array <= 0.95 * expected_arrival
    prearrival_leakage = float(np.max(signal[guarded_prearrival]) / max(peak, 1e-300))
    return {
        "grid_cells": n,
        "dx": dx,
        "dt": dt,
        "declared_speed": cfg.space_speed,
        "detector_distance": distance,
        "expected_arrival": expected_arrival,
        "arrival_threshold_fraction": 0.2,
        "arrival_time": arrival_time,
        "measured_speed": measured_speed,
        "speed_relative_error": speed_error,
        "prearrival_guard_fraction": 0.05,
        "prearrival_leakage_fraction": prearrival_leakage,
        "peak_detector_response": peak,
        "interpretation": "compact initial-rate pulse; leakage is measured before 95% of the declared arrival time",
    }


def build_verification() -> dict[str, Any]:
    trajectory = closed_trajectory_metrics()
    open_drive = open_drive_metrics()
    history = decoupling_and_history_metrics()
    temporal = temporal_convergence()
    spatial = spatial_convergence()
    adiabatic = adiabatic_limit_metrics()
    causal = causal_pulse_metrics()

    metrics = {
        "local_derivative": _metric(
            local_derivative_residual(),
            THRESHOLDS["local_derivative_absolute_residual_max"],
            "le",
        ),
        "directional_derivative_periodic": _metric(
            directional_derivative_error("periodic"),
            THRESHOLDS["discrete_directional_derivative_relative_error_max"],
            "le",
        ),
        "directional_derivative_zero_flux": _metric(
            directional_derivative_error("zero_flux"),
            THRESHOLDS["discrete_directional_derivative_relative_error_max"],
            "le",
        ),
        "conserved_matter_drift": _metric(
            trajectory["relative_matter_drift"],
            THRESHOLDS["conserved_matter_relative_drift_max"],
            "le",
        ),
        "minimum_dissipation_density": _metric(
            trajectory["minimum_dissipation_density"],
            THRESHOLDS["minimum_dissipation_density_min"],
            "ge",
        ),
        "closed_energy_increase": _metric(
            trajectory["max_relative_energy_increase"],
            THRESHOLDS["closed_energy_relative_increase_max"],
            "le",
        ),
        "ledger_closure": _metric(
            trajectory["max_ledger_closure_relative"],
            THRESHOLDS["ledger_closure_relative_residual_max"],
            "le",
        ),
        "open_space_ledger_closure": _metric(
            open_drive["closure_relative"],
            THRESHOLDS["open_space_ledger_closure_relative_residual_max"],
            "le",
        ),
        "g_zero_decoupling": _metric(
            history["decoupled_matter_absolute_error"],
            THRESHOLDS["decoupled_baseline_absolute_error_max"],
            "le",
        ),
        "trace_switch_invariance": _metric(
            history["trace_switch_physical_absolute_error"],
            THRESHOLDS["trace_switch_physical_absolute_error_max"],
            "le",
        ),
        "physical_history_signal": _metric(
            history["physical_history_signal_to_discretization"],
            THRESHOLDS["physical_history_signal_to_discretization_min"],
            "ge",
        ),
        "trace_history_no_backreaction": _metric(
            history["trace_history_physical_absolute_error"],
            THRESHOLDS["trace_history_physical_absolute_error_max"],
            "le",
        ),
        "causal_arrival_speed": _metric(
            causal["speed_relative_error"],
            THRESHOLDS["causal_arrival_speed_relative_error_max"],
            "le",
        ),
        "prearrival_leakage": _metric(
            causal["prearrival_leakage_fraction"],
            THRESHOLDS["prearrival_leakage_fraction_max"],
            "le",
            "hard falsification/numerics gate; no cone-padding is applied",
        ),
        "temporal_convergence": _metric(
            temporal["minimum_order"],
            THRESHOLDS["temporal_convergence_order_min"],
            "ge",
        ),
        "spatial_convergence": _metric(
            spatial["minimum_order"],
            THRESHOLDS["spatial_convergence_order_min"],
            "ge",
        ),
        "adiabatic_local_equilibrium": _metric(
            adiabatic["highest_refinement_relative_error"],
            THRESHOLDS["adiabatic_local_equilibrium_relative_error_max"],
            "le",
            "requires tau, response time, and correlation length to shrink together",
        ),
    }
    failed = [name for name, entry in metrics.items() if entry["gate"] == "FAIL"]
    if not adiabatic["all_three_limit_scales_shrink"]:
        failed.append("adiabatic_three_scale_contract")
    if not trajectory["all_finite"] or trajectory["field_clipping_applied"] or trajectory["parameter_fitting_applied"]:
        failed.append("run_integrity")
    status = "PASS" if not failed else "FAIL"
    controlling = failed[0] if failed else "none"
    if "prearrival_leakage" in failed:
        controlling = "prearrival_leakage"
    return {
        "schema_version": "1.0",
        "artifact": "matter_space_variational_verification",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_status": "candidate_normalized_effective_model",
        "operator_mode": MATTER_SPACE_OPERATOR_MODE,
        "controlling_blocker": controlling,
        "failed_gates": failed,
        "thresholds": THRESHOLDS,
        "metrics": metrics,
        "raw_diagnostics": {
            "closed_trajectory": trajectory,
            "open_space_drive": open_drive,
            "history_separation": history,
            "temporal_convergence": temporal,
            "spatial_convergence": spatial,
            "adiabatic_limit": adiabatic,
            "causal_pulse": causal,
        },
        "run_contract": {
            "unit_lane": "normalized",
            "dimension": "1D",
            "integrator": "Heun/RK2",
            "random_seeds": [2207, 3319],
            "parameter_fitting": False,
            "field_clipping": False,
            "external_validation": False,
            "trace_backreaction": False,
            "deterministic": True,
        },
        "falsification_state": (
            "NUMERICAL_CAUSALITY_REPAIR_REQUIRED"
            if "prearrival_leakage" in failed
            else "NO_CORE_FALSIFICATION_TRIGGERED"
        ),
        "claim_boundary": [
            "This artifact verifies only the normalized discrete candidate.",
            "A failed causal-cone gate blocks downstream physical interpretation.",
            "Phi is not established as geometry, ether, antimatter, or a particle.",
            "R remains a derived observable with no feedback path.",
            "No SI, galaxy, particle, or external-validation claim is supported.",
        ],
    }


def build_dependency_gate(verification: dict[str, Any]) -> dict[str, Any]:
    core_pass = verification["status"] == "PASS"
    status = "PASS" if core_pass else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "matter_space_dependency_gate",
        "generated_at": verification["generated_at"],
        "status": status,
        "core_verification_status": verification["status"],
        "controlling_blocker": verification["controlling_blocker"],
        "diagnostic_pilot_execution": (
            "ALLOWED" if core_pass else "ALLOWED_WITH_BLOCKED_PHYSICAL_INTERPRETATION"
        ),
        "claim_promotion": "BLOCKED" if not core_pass else "NOT_AUTOMATIC",
        "active_pilots": {
            "0.13_Thermodynamic_Bridge": "DIAGNOSTIC_ONLY",
            "0.11_Phase_Transitions": "DIAGNOSTIC_ONLY",
        },
        "dependency_gate_only": [
            "0.10_Fluid_Dynamics_Chaos",
            "0.12_Vacuum_Energy_Casimir",
            "0.19_Gravity_GR",
            "0.23_Unity_Scale_Link",
            "0.1_Galaxy_Rotation_Problem",
            "0.26_Cosmic_Dynamic_Frame",
        ],
        "deferred_foundation": [
            "0.5_Nuclear_Binding_Hadrons",
            "0.6_Electroweak_Physics",
            "0.7_Neutrino_Physics",
            "0.9_Quantum_Nonlocality",
            "0.17_Mass_Generation",
            "0.20_Atomic_Physics",
        ],
        "blocked_claims": [
            "space response as established spacetime geometry",
            "antimatter, positron, neutrino, or Dirac derivation",
            "galaxy dynamics or dark-matter replacement",
            "external thermodynamic validation",
        ],
        "next_controller": (
            "repair or replace the explicit physical-response discretization so compact support satisfies the declared cone"
            if not core_pass
            else "run diagnostic pilots without claim promotion"
        ),
    }


def update_alignment_gate(verification: dict[str, Any]) -> dict[str, Any]:
    current = json.loads(ALIGNMENT_PATH.read_text(encoding="utf-8"))
    current["status"] = "WARN" if verification["status"] == "PASS" else "BLOCKED"
    current["controlling_blocker"] = verification["controlling_blocker"]
    contract = current["matter_space_contract"]
    contract["functional_derivative_contract_gate"] = "PASS"
    contract["normalized_units_contract_gate"] = "PASS"
    contract["implementation_gate"] = "PASS"
    contract["numerical_verification_gate"] = verification["status"]
    contract["SI_gate"] = "BLOCKED"
    current["next_required_artifact"] = (
        "causal_discretization_repair_artifact.json"
        if verification["status"] != "PASS"
        else "matter_space_thermal_control.json"
    )
    current["last_verifier_artifact"] = str(VERIFICATION_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    current["claim_impact"] = "no_status_upgrade"
    return current


def update_formula_audit(verification: dict[str, Any]) -> dict[str, Any]:
    audit = json.loads(FORMULA_AUDIT_PATH.read_text(encoding="utf-8"))
    for entry in audit.get("formula_registry", []):
        implementation = entry.get("implementation")
        if isinstance(implementation, str):
            entry["implementation"] = implementation.replace(" (target)", "")
        entry["implementation_status"] = "PRESENT"
        entry["last_verifier"] = "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
    audit["status"] = "WARN"
    audit["verification_status"] = verification["status"]
    audit["next_controller"] = verification["controlling_blocker"]
    audit["implementation_status"] = "PRESENT"
    return audit


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-summary", action="store_true")
    parser.add_argument("--strict", action="store_true", help="return nonzero when a hard gate fails")
    args = parser.parse_args()
    verification = build_verification()
    dependency = build_dependency_gate(verification)
    alignment = update_alignment_gate(verification)
    formula_audit = update_formula_audit(verification)
    write_json(VERIFICATION_PATH, verification)
    write_json(DEPENDENCY_PATH, dependency)
    write_json(ALIGNMENT_PATH, alignment)
    write_json(FORMULA_AUDIT_PATH, formula_audit)
    if args.print_summary:
        print(json.dumps({
            "status": verification["status"],
            "controlling_blocker": verification["controlling_blocker"],
            "failed_gates": verification["failed_gates"],
            "dependency_status": dependency["status"],
        }, indent=2))
    return 2 if args.strict and verification["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
