"""Run the isolated normalized matter-space/phase diagnostic for Topic 0.11.

This runner is intentionally separate from the current structure-factor
controller.  It produces internal/simulation-only evidence and never promotes
the topic status or feeds a trace/observer record back into physical fields.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

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
TOPIC = ROOT / "docs/topics/0.11_Phase_Transitions"
PREREG_PATH = TOPIC / "Data/03_Research/matter_space_phase_coupling.json"
PARENT_PREREG_PATH = TOPIC / "Data/03_Research/matter_space_coupled_preregistration.json"
CORE_PATH = ROOT / "docs/core/07_artifacts/verification/matter_space_variational_verification.json"
OUTPUT_PATH = TOPIC / "Result/artifacts/0_11_matter_space_phase_coupling_diagnostic.json"

from docs.core.uet_impact_effect import (  # noqa: E402
    COUPLED_RECEIVER_MODE,
    CarrierRecord,
    ImpactRecord,
    ReceiverDynamics,
    apply_receiver_effect,
    impact_to_effect,
)
from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_extended_energy,
    matter_space_stability_limit,
    matter_space_step,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402
from docs.core.uet_spatial import integral_1d, laplacian_1d  # noqa: E402
from docs.core.uet_master_equation import LEGACY_OPERATOR_MODE, dynamics_step_complete  # noqa: E402
from docs.core.uet_trace import TraceKernelConfig  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rms(value: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(np.asarray(value, dtype=float)))))


def prereg() -> dict[str, Any]:
    return json.loads(PREREG_PATH.read_text(encoding="utf-8"))


def config(parent: dict[str, Any], coupling: float) -> MatterSpaceConfig:
    p = parent["primary"]
    return MatterSpaceConfig(
        a_matter=float(p["a_matter"]),
        b_matter=float(p["b_matter"]),
        kappa_matter=float(p["kappa_matter"]),
        mobility_matter=float(p["mobility_matter"]),
        a_space=float(p["a_space"]),
        b_space=float(p["b_space"]),
        kappa_space=float(p["kappa_space"]),
        mobility_space=float(p["mobility_space"]),
        tau_space=float(p["tau_space"]),
        coupling_g=float(coupling),
        matter_dynamics="conserved",
        boundary_condition="periodic",
        unit_lane="normalized",
        stability_safety=float(p["stability_safety"]),
        ledger_tolerance=float(p["ledger_tolerance"]),
    )


def initial_field(name: str, cells: int, length: float, controls: dict[str, Any], seed: int | None = None) -> np.ndarray:
    x = np.arange(cells, dtype=float) * length / cells
    if name == "uniform":
        return np.full(cells, float(controls["uniform_C"]))
    if name == "localized":
        distance = np.minimum(np.abs(x - 0.5 * length), length - np.abs(x - 0.5 * length))
        return float(controls["localized_mean"]) + float(controls["localized_amplitude"]) * np.exp(
            -0.5 * np.square(distance / float(controls["localized_sigma"]))
        )
    if name == "two_domain":
        return float(controls["domain_amplitude"]) * np.tanh(
            np.sin(2.0 * np.pi * x / length) * length / (2.0 * np.pi * float(controls["domain_interface_width"]))
        )
    if name == "spinodal":
        if seed is None:
            raise ValueError("spinodal initial condition requires a locked seed")
        return np.random.default_rng(seed).normal(0.0, float(controls["spinodal_noise_sigma"]), cells)
    raise ValueError(f"unknown initial condition {name}")


def trace_config(parent: dict[str, Any]) -> TraceKernelConfig:
    p = parent["trace_control"]
    return TraceKernelConfig(
        D_trace=float(p["D_trace"]),
        tau_trace=float(p["tau_trace"]),
        lambda_trace=float(p["lambda_trace"]),
        source_normalization="normalized",
        boundary_condition="periodic",
    )


def phase_proxy(initial: np.ndarray, final: MatterSpaceState) -> float:
    cost = rms(final.C - initial) / max(rms(initial), 1.0) + rms(final.space_response) + rms(final.space_rate)
    return float(np.exp(-cost))


def morphology(field: np.ndarray, dx: float) -> dict[str, float]:
    centered = field - np.mean(field)
    spectrum = np.square(np.abs(np.fft.rfft(centered)))
    wavenumbers = 2.0 * np.pi * np.fft.rfftfreq(field.size, d=dx)
    nonzero = wavenumbers > 0.0
    if not np.any(nonzero) or float(np.sum(spectrum[nonzero])) <= 1e-30:
        peak = 0.0
        correlation = 0.0
    else:
        selected = spectrum[nonzero]
        selected_k = wavenumbers[nonzero]
        peak = float(selected_k[int(np.argmax(selected))])
        correlation = float(np.sqrt(np.sum(selected) / np.sum(np.square(selected_k) * selected)))
    gradient = (np.roll(field, -1) - field) / dx
    return {
        "interface_width_proxy": float((np.max(field) - np.min(field)) / max(np.max(np.abs(gradient)), 1e-15)),
        "structure_factor_peak_q_diagnostic": peak,
        "correlation_length_proxy_diagnostic": correlation,
        "variance": float(np.var(field)),
    }


def run_physical(
    initial: np.ndarray,
    dx: float,
    cfg: MatterSpaceConfig,
    duration: float,
    dt_fraction: float,
    *,
    phi0: np.ndarray | None = None,
    pi0: np.ndarray | None = None,
    trace: TraceKernelConfig | None = None,
    receiver: bool = False,
) -> dict[str, Any]:
    zeros = np.zeros_like(initial)
    state = MatterSpaceState(initial.copy(), zeros if phi0 is None else phi0.copy(), zeros if pi0 is None else pi0.copy())
    dt = float(duration) / max(1, int(np.ceil(duration / (dt_fraction * matter_space_stability_limit(state, dx, cfg)))))
    steps = max(1, int(np.ceil(duration / dt)))
    history: list[np.ndarray] = []
    initial_mass = integral_1d(state.C, dx)
    initial_energy = matter_space_extended_energy(state, dx, cfg)
    max_mass_drift = 0.0
    max_energy_increase = 0.0
    max_ledger = 0.0
    receiver_state = np.zeros(1)
    receiver_response = 0.0
    c_phase_time = None
    for step in range(steps):
        result = matter_space_step(
            state,
            dt,
            dx,
            cfg,
            trace_history=history if trace is not None else None,
            trace_config=trace,
        )
        state = MatterSpaceState(result.C, result.space_response, result.space_rate)
        source = np.asarray(result.diagnostics["source_snapshot"], dtype=float)
        if trace is not None:
            history.append(source.copy())
        if receiver:
            payload = np.asarray([rms(np.maximum(source, 0.0))])
            carrier = CarrierRecord(
                carrier_type="carrier_neutral_pilot",
                source_id="matter-system",
                receiver_id="phase-receiver",
                energy=float(np.sum(np.maximum(source, 0.0)) * dx),
                propagation_speed=1.0,
                rest_mass_status="unspecified",
                carrier_id=f"carrier-{step}",
                payload=payload,
            )
            impact = ImpactRecord(
                source_id="matter-system",
                receiver_id="phase-receiver",
                interaction_type="phase-diagnostic_input",
                energy_transfer=carrier.energy,
                mass_transfer=0.0,
                impact_id=f"impact-{step}",
            )
            effect = impact_to_effect(
                impact,
                carrier,
                generated_trace=np.asarray([rms(source)]),
                mode=COUPLED_RECEIVER_MODE,
            )
            update = apply_receiver_effect(
                receiver_state,
                effect,
                ReceiverDynamics(gain=1.0, feedback_enabled=True),
            )
            receiver_state = update.state
            receiver_response = max(receiver_response, float(np.sum(np.abs(update.delta))))
        before = float(result.energy_ledger["free_plus_space_kinetic_before"])
        max_energy_increase = max(max_energy_increase, float(result.energy_ledger["actual_delta"]) / max(abs(before), 1.0))
        max_ledger = max(max_ledger, float(result.energy_ledger["closure_relative"]))
        max_mass_drift = max(max_mass_drift, abs(integral_1d(state.C, dx) - initial_mass) / max(abs(initial_mass), 1.0))
        if c_phase_time is None and phase_proxy(initial, state) < 0.5:
            c_phase_time = (step + 1) * dt
    final_energy = matter_space_extended_energy(state, dx, cfg)
    return {
        "state": state,
        "trace": None if result.trace_observable is None else np.asarray(result.trace_observable),
        "dt": dt,
        "steps": steps,
        "metrics": {
            "C_phase_persistence_proxy": phase_proxy(initial, state),
            "interface_width_proxy": morphology(state.C, dx)["interface_width_proxy"],
            "structure_factor_peak_q_diagnostic": morphology(state.C, dx)["structure_factor_peak_q_diagnostic"],
            "phase_transition_time_proxy": c_phase_time if c_phase_time is not None else duration,
            "persistence_time_proxy": c_phase_time if c_phase_time is not None else duration,
            "energy_dissipation_proxy": initial_energy - final_energy,
            "matter_relative_drift": max_mass_drift,
            "max_relative_energy_increase": max_energy_increase,
            "max_ledger_closure_relative": max_ledger,
            "receiver_effect_response_proxy": receiver_response,
            "all_finite": bool(np.all(np.isfinite(state.C)) and np.all(np.isfinite(state.space_response)) and np.all(np.isfinite(state.space_rate))),
        },
    }


def run_legacy(initial: np.ndarray, dx: float, record: dict[str, Any]) -> dict[str, Any]:
    params = UETParameters(
        alpha=float(record["alpha"]), gamma=float(record["gamma"]), C0=float(record["C0"]),
        kappa=float(record["kappa"]), beta=float(record["beta"]), W_N=float(record["W_N"]),
        a0_viscosity=float(record["a0_viscosity"]),
    )
    steps = int(round(float(record["duration"]) / float(record["dt"])))
    current = initial.copy()
    for _ in range(steps):
        current = np.asarray(dynamics_step_complete(current, dx=dx, dt=float(record["dt"]), params=params, operator_mode=LEGACY_OPERATOR_MODE), dtype=float)
    return {"all_finite": bool(np.all(np.isfinite(current))), "matter_relative_drift": abs(integral_1d(current, dx) - integral_1d(initial, dx)) / max(abs(integral_1d(initial, dx)), 1.0), "final_rms": rms(current)}


def local_phi(C: np.ndarray, cfg: MatterSpaceConfig) -> np.ndarray:
    source = 0.5 * cfg.coupling_g * C**2
    half = source / (2.0 * cfg.b_space)
    discriminant = half**2 + (cfg.a_space / (3.0 * cfg.b_space))**3
    return np.cbrt(half + np.sqrt(discriminant)) + np.cbrt(half - np.sqrt(discriminant))


def run_adiabatic(initial: np.ndarray, dx: float, cfg: MatterSpaceConfig, duration: float) -> dict[str, Any]:
    dt = min(0.0005, duration / 10.0)
    steps = max(1, int(np.ceil(duration / dt)))
    dt = duration / steps
    current = initial.copy()
    for _ in range(steps):
        phi = local_phi(current, cfg)
        mu = cfg.a_matter * current + cfg.b_matter * current**3 - cfg.kappa_matter * laplacian_1d(current, dx, "periodic") - cfg.coupling_g * current * phi
        k1 = cfg.mobility_matter * laplacian_1d(mu, dx, "periodic")
        predictor = current + dt * k1
        phi_predictor = local_phi(predictor, cfg)
        mu_predictor = cfg.a_matter * predictor + cfg.b_matter * predictor**3 - cfg.kappa_matter * laplacian_1d(predictor, dx, "periodic") - cfg.coupling_g * predictor * phi_predictor
        k2 = cfg.mobility_matter * laplacian_1d(mu_predictor, dx, "periodic")
        current = current + 0.5 * dt * (k1 + k2)
    return {"C": current, "Phi": local_phi(current, cfg), "all_finite": bool(np.all(np.isfinite(current)))}


def main() -> int:
    locked = prereg()
    parent = json.loads(PARENT_PREREG_PATH.read_text(encoding="utf-8"))
    controls = locked["initial_conditions"]
    p = locked
    dx = float(p["domain_length"]) / int(p["cells"])
    cfgs = {
        "standard_conserved_gradient_flow": config(parent, 0.0),
        "C_plus_trace_only": config(parent, 0.0),
        "coupled_C_Phi_Pi": config(parent, float(parent["primary"]["coupling_g"])),
        "coupled_receiver_effect": config(parent, float(parent["primary"]["coupling_g"])),
        "adiabatic_reduced_model": config(parent, float(parent["primary"]["coupling_g"])),
    }
    initials: list[tuple[str, np.ndarray]] = [
        ("uniform", initial_field("uniform", int(p["cells"]), float(p["domain_length"]), controls)),
        ("localized", initial_field("localized", int(p["cells"]), float(p["domain_length"]), controls)),
        ("two_domain", initial_field("two_domain", int(p["cells"]), float(p["domain_length"]), controls)),
    ] + [(f"spinodal_{seed}", initial_field("spinodal", int(p["cells"]), float(p["domain_length"]), controls, seed)) for seed in controls["spinodal_seeds"]]
    comparator_results: dict[str, Any] = {}
    trace = trace_config(parent)
    for name, initial in initials:
        comparator_results[name] = {}
        for comparator, cfg in cfgs.items():
            if comparator == "C_plus_trace_only":
                run = run_physical(initial, dx, cfg, float(p["duration"]), float(p["dt_fraction_of_preflight"]), trace=trace)
            elif comparator == "coupled_receiver_effect":
                run = run_physical(initial, dx, cfg, float(p["duration"]), float(p["dt_fraction_of_preflight"]), receiver=True)
            elif comparator == "adiabatic_reduced_model":
                reduced = run_adiabatic(initial, dx, cfg, float(p["duration"]))
                comparator_results[name][comparator] = {"metrics": {"all_finite": reduced["all_finite"], "C_phase_persistence_proxy": float(np.exp(-rms(reduced["C"] - initial) / max(rms(initial), 1.0))), "matter_relative_drift": abs(integral_1d(reduced["C"], dx) - integral_1d(initial, dx)) / max(abs(integral_1d(initial, dx)), 1.0)}}
                continue
            else:
                run = run_physical(initial, dx, cfg, float(p["duration"]), float(p["dt_fraction_of_preflight"]))
            comparator_results[name][comparator] = {"metrics": run["metrics"], "dt": run["dt"], "steps": run["steps"]}
        comparator_results[name]["legacy_instantaneous_comparator"] = {"metrics": run_legacy(initial, dx, parent["legacy_comparator"])}

    reference = initials[1][1]
    coupled_cfg = cfgs["coupled_C_Phi_Pi"]
    zeros = np.zeros_like(reference)
    alt_phi = float(controls["alternate_phi_amplitude"]) * np.sin(np.linspace(0, 2 * np.pi, reference.size, endpoint=False))
    alt_pi = float(controls["alternate_pi_amplitude"]) * np.cos(np.linspace(0, 2 * np.pi, reference.size, endpoint=False))
    same_C_a = run_physical(reference, dx, coupled_cfg, 0.05, 0.05)
    same_C_b = run_physical(reference, dx, coupled_cfg, 0.05, 0.05, phi0=alt_phi, pi0=alt_pi)
    same_state = MatterSpaceState(reference.copy(), zeros.copy(), zeros.copy())
    dt = 0.05 * matter_space_stability_limit(same_state, dx, coupled_cfg)
    history_a = matter_space_step(same_state, dt, dx, coupled_cfg, trace_history=[np.zeros_like(reference)], trace_config=trace)
    history_b = matter_space_step(same_state, dt, dx, coupled_cfg, trace_history=[np.ones_like(reference)], trace_config=trace)
    same_history_difference = max(rms(history_a.C - history_b.C), rms(history_a.space_response - history_b.space_response), rms(history_a.space_rate - history_b.space_rate))

    convergence = {}
    for cells in (32, 64):
        local_dx = float(p["domain_length"]) / cells
        local_initial = initial_field("localized", cells, float(p["domain_length"]), controls)
        local_run = run_physical(local_initial, local_dx, coupled_cfg, 0.1, 0.05)
        convergence[str(cells)] = {"mean_C": float(np.mean(local_run["state"].C)), "variance_C": float(np.var(local_run["state"].C)), "energy_dissipation_proxy": local_run["metrics"]["energy_dissipation_proxy"]}
    scalar_error = max(abs(convergence["32"][key] - convergence["64"][key]) for key in ("mean_C", "variance_C"))
    core = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    local_checks = {
        "all_comparator_fields_finite": all(result[comp]["metrics"].get("all_finite", False) for result in comparator_results.values() for comp in result),
        "same_C_different_space_state_signal": max(rms(same_C_a["state"].C - same_C_b["state"].C), rms(same_C_a["state"].space_response - same_C_b["state"].space_response), rms(same_C_a["state"].space_rate - same_C_b["state"].space_rate)) >= float(p["thresholds"]["same_C_space_signal_min"]),
        "same_complete_state_different_trace_history_invariant": same_history_difference <= float(p["thresholds"]["trace_history_physical_difference_max"]),
        "receiver_effect_explicit_and_nonzero": any(result["coupled_receiver_effect"]["metrics"]["receiver_effect_response_proxy"] > float(p["thresholds"]["receiver_response_min"]) for result in comparator_results.values()),
        "resolution_scalar_difference_recorded": bool(np.isfinite(scalar_error)),
        "core_causal_dependency_not_hidden": core["controlling_blocker"] == "prearrival_leakage",
    }
    local_status = "PASS" if all(local_checks.values()) else "FAIL"
    artifact = {
        "schema_version": "matter-space-phase-coupling-diagnostic-v1",
        "artifact": "0_11_matter_space_phase_coupling_diagnostic",
        "generated_at": date.today().isoformat(),
        "status": "INTERNAL_DIAGNOSTIC",
        "verification_status": local_status,
        "simulation_status": "SIMULATION_ONLY",
        "dependency_status": "BLOCKED",
        "topic_status_impact": "NONE",
        "controller": "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open",
        "operator_mode": "matter_space_coupled_v1",
        "unit_lane": "normalized",
        "preregistration": {"path": str(PREREG_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PREREG_PATH), "parameter_fitting": False, "external_numeric_inputs": []},
        "parent_preregistration": {"path": str(PARENT_PREREG_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PARENT_PREREG_PATH)},
        "comparators": locked["comparators"],
        "initial_conditions": [name for name, _ in initials],
        "results": comparator_results,
        "same_C_different_space_state": {"physical_difference": max(rms(same_C_a["state"].C - same_C_b["state"].C), rms(same_C_a["state"].space_response - same_C_b["state"].space_response), rms(same_C_a["state"].space_rate - same_C_b["state"].space_rate))},
        "same_complete_state_different_trace_history": {"physical_difference": same_history_difference, "trace_history_changes_physical_state": False},
        "resolution_control": {"scalar_observables": convergence, "max_scalar_difference": scalar_error},
        "causal_arrival": {"status": "INHERITED_BLOCKED_CORE_CONTROLLER", "core_artifact": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"), "controller": core["controlling_blocker"], "new_causal_claim": False},
        "local_checks": local_checks,
        "claim_boundary": ["internal normalized diagnostic only", "C_phase is a lane-specific persistence/compatibility proxy", "morphology metrics are not accepted structure-factor estimators", "no universality, mass, particle, GR, or cosmological claim"],
        "falsification_state": "core_causal_support_and_topic_structure_factor_controllers_remain_blocking",
        "next_controller": "repair inherited causal-support discretization and separately execute Topic 0.11 replicate/temporal acquisition",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"verification_status={local_status}")
    print("dependency_status=BLOCKED")
    print(f"topic_status_impact={artifact['topic_status_impact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
