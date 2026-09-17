"""Generate the isolated normalized matter-space coupling diagnostic for Topic 0.11."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
TOPIC = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
PREREG_PATH = TOPIC / "Data" / "03_Research" / "matter_space_coupled_preregistration.json"
AMENDMENT_PATH = TOPIC / "Data" / "03_Research" / "matter_space_coupled_numerical_amendment_001.json"
CORE_PATH = ROOT / "docs" / "core" / "07_artifacts" / "verification" / "matter_space_variational_verification.json"
TOPIC_GATE_PATH = TOPIC / "Result" / "artifacts" / "0_11_closure_status_audit.json"
ARTIFACT_PATH = TOPIC / "Result" / "artifacts" / "0_11_matter_space_coupled_diagnostic.json"
RESULT_DIR = TOPIC / "Result" / "03_show_Result"
CSV_PATH = RESULT_DIR / "matter_space_coupled_profiles.csv"

from docs.core.uet_master_equation import LEGACY_OPERATOR_MODE, dynamics_step_complete  # noqa: E402
from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_extended_energy,
    matter_space_stability_limit,
    matter_space_step,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402
from docs.core.uet_spatial import integral_1d, laplacian_1d  # noqa: E402
from docs.core.uet_trace import TraceKernelConfig  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()




def sha256_text_file(path: Path) -> str:
    """Hash text payloads with repository-stable LF line endings."""
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
def rms(field: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(np.asarray(field, dtype=float)))))


def physical_difference(left: MatterSpaceState, right: MatterSpaceState) -> float:
    return float(
        max(
            np.max(np.abs(left.C - right.C)),
            np.max(np.abs(left.space_response - right.space_response)),
            np.max(np.abs(left.space_rate - right.space_rate)),
        )
    )


def config_from(record: dict[str, Any], coupling: float | None = None) -> MatterSpaceConfig:
    return MatterSpaceConfig(
        a_matter=float(record["a_matter"]),
        b_matter=float(record["b_matter"]),
        kappa_matter=float(record["kappa_matter"]),
        mobility_matter=float(record["mobility_matter"]),
        a_space=float(record["a_space"]),
        b_space=float(record["b_space"]),
        kappa_space=float(record["kappa_space"]),
        mobility_space=float(record["mobility_space"]),
        tau_space=float(record["tau_space"]),
        coupling_g=float(record["coupling_g"] if coupling is None else coupling),
        matter_dynamics=str(record["matter_dynamics"]),
        boundary_condition=str(record["boundary_condition"]),
        unit_lane="normalized",
        stability_safety=float(record["stability_safety"]),
        ledger_tolerance=float(record["ledger_tolerance"]),
    )


def local_equilibrium_phi(C: np.ndarray, config: MatterSpaceConfig) -> np.ndarray:
    source = 0.5 * config.coupling_g * np.square(C)
    half = source / (2.0 * config.b_space)
    discriminant = np.square(half) + (config.a_space / (3.0 * config.b_space)) ** 3
    return np.cbrt(half + np.sqrt(discriminant)) + np.cbrt(half - np.sqrt(discriminant))


def initial_field(name: str, cells: int, length: float, controls: dict[str, Any], seed: int | None = None) -> np.ndarray:
    x = np.arange(cells, dtype=float) * (length / cells)
    if name == "uniform":
        return np.full(cells, float(controls["uniform_C"]))
    if name == "localized":
        distance = np.minimum(np.abs(x - 0.5 * length), length - np.abs(x - 0.5 * length))
        return float(controls["localized_mean"]) + float(controls["localized_amplitude"]) * np.exp(
            -0.5 * np.square(distance / float(controls["localized_sigma"]))
        )
    if name == "two_domain":
        phase = np.sin(2.0 * np.pi * x / length)
        width = max(float(controls["domain_interface_width"]), 1e-12)
        return float(controls["domain_amplitude"]) * np.tanh(phase * length / (2.0 * np.pi * width))
    if name == "spinodal":
        if seed is None:
            raise ValueError("spinodal initial condition requires a locked seed")
        return np.random.default_rng(seed).normal(
            0.0, float(controls["spinodal_noise_sigma"]), size=cells
        )
    raise ValueError(f"unknown initial condition: {name}")


def trace_config(record: dict[str, Any]) -> TraceKernelConfig:
    return TraceKernelConfig(
        D_trace=float(record["D_trace"]),
        tau_trace=float(record["tau_trace"]),
        lambda_trace=float(record["lambda_trace"]),
        source_normalization=str(record["source_normalization"]),
        boundary_condition=str(record["boundary_condition"]),
    )


def run_coupled(
    C0: np.ndarray,
    dx: float,
    config: MatterSpaceConfig,
    duration: float,
    dt_fraction: float,
    output_interval: float,
    Phi0: np.ndarray | None = None,
    Pi0: np.ndarray | None = None,
    trace: TraceKernelConfig | None = None,
) -> dict[str, Any]:
    zeros = np.zeros_like(C0)
    state = MatterSpaceState(C0, zeros if Phi0 is None else Phi0, zeros if Pi0 is None else Pi0)
    target_dt = float(dt_fraction) * matter_space_stability_limit(state, dx, config)
    steps = max(1, int(np.ceil(float(duration) / target_dt)))
    dt = float(duration) / steps
    stride = max(1, int(round(float(output_interval) / dt)))
    initial_mass = integral_1d(state.C, dx)
    initial_energy = matter_space_extended_energy(state, dx, config)
    trace_history: list[np.ndarray] = []
    records = [{
        "time": 0.0,
        "energy": initial_energy,
        "mass": initial_mass,
        "closure": 0.0,
    }]
    max_mass_drift = 0.0
    max_energy_increase = 0.0
    max_closure = 0.0
    minimum_source = np.inf
    final_trace = None
    for step_index in range(1, steps + 1):
        current_limit = matter_space_stability_limit(state, dx, config)
        if dt > current_limit * (1.0 + 1e-12):
            raise RuntimeError(
                f"fixed dt {dt} exceeded current preflight {current_limit} at step {step_index}"
            )
        result = matter_space_step(
            state,
            dt,
            dx,
            config,
            trace_history=trace_history if trace is not None else None,
            trace_config=trace,
        )
        updated = MatterSpaceState(result.C, result.space_response, result.space_rate)
        source = np.asarray(result.diagnostics["source_snapshot"], dtype=float)
        if trace is not None:
            trace_history.append(source.copy())
            final_trace = None if result.trace_observable is None else np.asarray(result.trace_observable).copy()
        mass = integral_1d(updated.C, dx)
        max_mass_drift = max(
            max_mass_drift, abs(mass - initial_mass) / max(abs(initial_mass), 1.0)
        )
        before = float(result.energy_ledger["free_plus_space_kinetic_before"])
        delta = float(result.energy_ledger["actual_delta"])
        max_energy_increase = max(max_energy_increase, delta / max(abs(before), 1.0))
        max_closure = max(max_closure, float(result.energy_ledger["closure_relative"]))
        minimum_source = min(minimum_source, float(np.min(source)))
        if step_index % stride == 0 or step_index == steps:
            records.append({
                "time": step_index * dt,
                "energy": float(result.energy_ledger["free_plus_space_kinetic_after"]),
                "mass": mass,
                "closure": float(result.energy_ledger["closure_relative"]),
            })
        state = updated
    return {
        "state": state,
        "trace": final_trace,
        "trace_history": trace_history,
        "dt": dt,
        "steps": steps,
        "records": {key: np.asarray([row[key] for row in records]) for key in records[0]},
        "metrics": {
            "matter_relative_drift": float(max_mass_drift),
            "max_relative_energy_increase": float(max_energy_increase),
            "max_ledger_closure_relative": float(max_closure),
            "minimum_dissipation_density": float(minimum_source),
            "all_finite": bool(
                np.all(np.isfinite(state.C))
                and np.all(np.isfinite(state.space_response))
                and np.all(np.isfinite(state.space_rate))
            ),
        },
    }


def reduced_rhs(C: np.ndarray, dx: float, config: MatterSpaceConfig) -> np.ndarray:
    Phi = local_equilibrium_phi(C, config)
    mu = (
        config.a_matter * C
        + config.b_matter * C**3
        - config.kappa_matter * laplacian_1d(C, dx, config.boundary_condition)
        - config.coupling_g * C * Phi
    )
    return config.mobility_matter * laplacian_1d(mu, dx, config.boundary_condition)


def run_reduced(C0: np.ndarray, dx: float, config: MatterSpaceConfig, duration: float, dt: float) -> dict[str, Any]:
    steps = max(1, int(round(float(duration) / float(dt))))
    actual_dt = float(duration) / steps
    C = np.asarray(C0, dtype=float).copy()
    initial_mass = integral_1d(C, dx)
    for _ in range(steps):
        k1 = reduced_rhs(C, dx, config)
        predictor = C + actual_dt * k1
        k2 = reduced_rhs(predictor, dx, config)
        C = C + 0.5 * actual_dt * (k1 + k2)
        if not np.all(np.isfinite(C)):
            raise RuntimeError("adiabatic reduced model produced a non-finite field")
    return {
        "C": C,
        "Phi": local_equilibrium_phi(C, config),
        "matter_relative_drift": abs(integral_1d(C, dx) - initial_mass) / max(abs(initial_mass), 1.0),
        "dt": actual_dt,
    }


def morphology_metrics(C: np.ndarray, dx: float) -> dict[str, float]:
    centered = C - np.mean(C)
    spectrum = np.square(np.abs(np.fft.rfft(centered)))
    wave_numbers = 2.0 * np.pi * np.fft.rfftfreq(C.size, d=dx)
    nonzero = wave_numbers > 0.0
    if not np.any(nonzero) or float(np.sum(spectrum[nonzero])) <= 1e-30:
        peak = 0.0
        correlation = 0.0
    else:
        selected = spectrum[nonzero]
        selected_k = wave_numbers[nonzero]
        peak = float(selected_k[int(np.argmax(selected))])
        correlation = float(np.sqrt(np.sum(selected) / np.sum(np.square(selected_k) * selected)))
    gradient = (np.roll(C, -1) - C) / dx
    width = float((np.max(C) - np.min(C)) / max(float(np.max(np.abs(gradient))), 1e-15))
    return {
        "interface_width_proxy": width,
        "structure_factor_peak_q": peak,
        "spectral_correlation_length_proxy": correlation,
        "variance": float(np.var(C)),
    }


def run_legacy(C0: np.ndarray, dx: float, record: dict[str, Any]) -> dict[str, Any]:
    params = UETParameters(
        alpha=float(record["alpha"]),
        gamma=float(record["gamma"]),
        C0=float(record["C0"]),
        kappa=float(record["kappa"]),
        beta=float(record["beta"]),
        W_N=float(record["W_N"]),
        a0_viscosity=float(record["a0_viscosity"]),
    )
    dt = float(record["dt"])
    steps = int(round(float(record["duration"]) / dt))
    C = C0.copy()
    initial_mass = integral_1d(C, dx)
    for _ in range(steps):
        C = np.asarray(
            dynamics_step_complete(
                C, dx=dx, dt=dt, params=params, operator_mode=LEGACY_OPERATOR_MODE
            ),
            dtype=float,
        )
    return {
        "C": C,
        "all_finite": bool(np.all(np.isfinite(C))),
        "matter_relative_drift": abs(integral_1d(C, dx) - initial_mass) / max(abs(initial_mass), 1.0),
        "parameters": record,
        "role": "descriptive nonconserved legacy comparator",
    }


def run_trace_invariance(
    C0: np.ndarray,
    dx: float,
    config: MatterSpaceConfig,
    trace: TraceKernelConfig,
    steps: int,
) -> dict[str, float]:
    zero = np.zeros_like(C0)
    plain_state = MatterSpaceState(C0, zero, zero)
    traced_state = plain_state.copy()
    dt = 0.02 * min(
        matter_space_stability_limit(plain_state, dx, config),
        matter_space_stability_limit(traced_state, dx, config),
    )
    history: list[np.ndarray] = []
    max_switch_difference = 0.0
    final_trace = None
    for _ in range(steps):
        plain = matter_space_step(plain_state, dt, dx, config)
        traced = matter_space_step(
            traced_state, dt, dx, config, trace_history=history, trace_config=trace
        )
        plain_state = MatterSpaceState(plain.C, plain.space_response, plain.space_rate)
        traced_state = MatterSpaceState(traced.C, traced.space_response, traced.space_rate)
        max_switch_difference = max(
            max_switch_difference, physical_difference(plain_state, traced_state)
        )
        history.append(np.asarray(traced.diagnostics["source_snapshot"]).copy())
        final_trace = traced.trace_observable

    common = traced_state.copy()
    zero_history = [np.zeros_like(C0) for _ in range(4)]
    active_history = [
        0.02 * (index + 1) * np.exp(-np.square(np.arange(C0.size) - C0.size / 2.0) / 32.0)
        for index in range(4)
    ]
    left = matter_space_step(common, dt, dx, config, trace_history=zero_history, trace_config=trace)
    right = matter_space_step(common, dt, dx, config, trace_history=active_history, trace_config=trace)
    history_physical_difference = physical_difference(
        MatterSpaceState(left.C, left.space_response, left.space_rate),
        MatterSpaceState(right.C, right.space_response, right.space_rate),
    )
    trace_observable_difference = float(
        np.max(np.abs(np.asarray(left.trace_observable) - np.asarray(right.trace_observable)))
    )
    return {
        "trace_switch_physical_difference": float(max_switch_difference),
        "different_history_physical_difference": float(history_physical_difference),
        "different_history_trace_observable_difference": trace_observable_difference,
        "final_trace_peak": float(np.max(np.abs(final_trace))) if final_trace is not None else 0.0,
        "dt": dt,
    }


def save_figure(fig: plt.Figure, path: Path, caption: str, caveat: str, manifest: list[dict[str, str]]) -> None:
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    manifest.append({
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "caption": caption,
        "caveat": caveat,
    })


def write_outputs(
    x: np.ndarray,
    localized_initial: np.ndarray,
    localized: dict[str, Any],
    trace_run: dict[str, Any],
    reduced: dict[str, Any],
    legacy: dict[str, Any],
    interface_initial: np.ndarray,
    interface: dict[str, Any],
    resolution: list[dict[str, float]],
    adiabatic: list[dict[str, float]],
    history: dict[str, float],
    thresholds: dict[str, float],
) -> list[dict[str, str]]:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "x_normalized", "localized_initial_C", "canonical_C", "canonical_trace_C",
            "coupled_C", "coupled_Phi", "coupled_Pi", "adiabatic_C", "legacy_C",
        ])
        canonical = localized["canonical"]["state"]
        coupled = localized["coupled"]["state"]
        for index, position in enumerate(x):
            writer.writerow([
                float(position), float(localized_initial[index]), float(canonical.C[index]),
                float(trace_run["state"].C[index]), float(coupled.C[index]),
                float(coupled.space_response[index]), float(coupled.space_rate[index]),
                float(reduced["C"][index]), float(legacy["C"][index]),
            ])

    manifest: list[dict[str, str]] = []
    path = RESULT_DIR / "matter_space_coupled_profiles.png"
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for axis, initial, runs, title in (
        (axes[0], localized_initial, localized, "Localized matter pulse"),
        (axes[1], interface_initial, interface, "Periodic two-domain interface"),
    ):
        axis.plot(x, initial, color="black", ls="--", label="initial C")
        axis.plot(x, runs["canonical"]["state"].C, label="canonical conserved C")
        axis.plot(x, runs["coupled"]["state"].C, label="coupled C")
        axis.set(ylabel="normalized C", title=title)
        axis.legend(fontsize=8)
    axes[1].set_xlabel("normalized x")
    fig.text(0.01, 0.01, "Internal 1D normalized diagnostic; profiles are not material predictions.", fontsize=8)
    save_figure(fig, path, "Canonical and coupled final profiles for two locked initial conditions.", "Morphology is diagnostic only.", manifest)

    path = RESULT_DIR / "matter_space_coupled_ledger.png"
    records = localized["coupled"]["records"]
    initial_mass = float(records["mass"][0])
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    axes[0].plot(records["time"], records["energy"], color="#003f5c")
    axes[0].set(ylabel="extended energy", title="Closed coupled-lane ledger")
    axes[1].plot(records["time"], np.abs(records["mass"] - initial_mass), color="#bc5090", label="absolute matter drift")
    axes[1].plot(records["time"], records["closure"], color="#ffa600", label="ledger residual")
    axes[1].axhline(float(thresholds["ledger_closure_relative_max"]), color="black", ls="--", label="ledger gate")
    axes[1].set(xlabel="normalized time", ylabel="absolute / relative diagnostic", yscale="log")
    axes[1].legend(fontsize=8)
    fig.text(0.01, 0.01, "Locked-dt residual is retained here; the separately disclosed refined ledger gate is reported in JSON.", fontsize=8)
    save_figure(fig, path, "Extended-energy and conservation account for the locked localized coupled lane.", "Normalized internal ledger, not SI energy; this panel intentionally preserves the pre-amendment residual.", manifest)

    path = RESULT_DIR / "matter_space_adiabatic_limit.png"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].plot([row["cells"] for row in resolution], [row["coupling_effect_rms"] for row in resolution], marker="o")
    axes[0].set(xlabel="cells over fixed domain", ylabel="RMS coupled-minus-canonical C", title="Resolution persistence")
    axes[1].loglog([row["scale"] for row in adiabatic], [row["relative_error"] for row in adiabatic], marker="o")
    axes[1].axhline(float(thresholds["adiabatic_finest_relative_error_max"]), color="black", ls="--", label="finest gate")
    axes[1].set(xlabel="adiabatic scale", ylabel="full-versus-reduced relative error", title="Three-condition adiabatic sequence")
    axes[1].legend(fontsize=8)
    fig.text(0.01, 0.01, "The sequence changes tau, relaxation time, and correlation length together; it is not a material fit.", fontsize=8)
    save_figure(fig, path, "Coupling-effect persistence and adiabatic-reduction convergence.", "Normalized numerical controls only.", manifest)

    path = RESULT_DIR / "matter_space_history_invariance.png"
    labels = ["trace switch", "different R history", "same C / different Phi,Pi"]
    values = [
        max(history["trace_switch_physical_difference"], 1e-18),
        max(history["different_history_physical_difference"], 1e-18),
        max(history["same_C_different_state_response"], 1e-18),
    ]
    fig, axis = plt.subplots(figsize=(9, 4.8))
    axis.bar(labels, values, color=["#58508d", "#bc5090", "#ff6361"])
    axis.axhline(float(thresholds["trace_physical_difference_max"]), color="black", ls="--", label="trace invariance gate")
    axis.set(yscale="log", ylabel="maximum physical-state difference", title="Physical state versus derived history")
    axis.legend(fontsize=8)
    fig.text(0.01, 0.01, "Trace history must not change physics; Phi and Pi are physical state variables and may change the response.", fontsize=8)
    save_figure(fig, path, "Trace-history invariance contrasted with physical-state sensitivity.", "R is derived and has no backreaction.", manifest)

    for entry in manifest:
        entry["sha256"] = sha256_file(ROOT / entry["path"])
    return manifest


def main() -> int:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    amendment = json.loads(AMENDMENT_PATH.read_text(encoding="utf-8"))
    core = json.loads(CORE_PATH.read_text(encoding="utf-8"))
    topic_gate = json.loads(TOPIC_GATE_PATH.read_text(encoding="utf-8"))
    if prereg.get("status") != "LOCKED_BEFORE_EXECUTION":
        raise RuntimeError("matter-space phase pilot requires a locked preregistration")
    if prereg.get("external_numeric_inputs") or prereg.get("parameter_fitting"):
        raise RuntimeError("matter-space phase pilot must remain synthetic and unfitted")
    if amendment.get("status") != "POST_DIAGNOSTIC_NUMERICAL_AMENDMENT":
        raise RuntimeError("matter-space phase pilot requires the disclosed numerical amendment")
    forbidden_changes = (
        "physical_parameters_changed", "initial_conditions_changed", "seeds_changed",
        "thresholds_changed", "external_data_added", "parameter_fitting",
    )
    if any(bool(amendment["amendment"][key]) for key in forbidden_changes):
        raise RuntimeError("the numerical amendment may refine only the ledger time step")

    primary = prereg["primary"]
    controls = prereg["initial_conditions"]
    length = float(primary["domain_length"])
    cells = int(primary["cells"])
    dx = length / cells
    dt_fraction = float(primary["dt_fraction_of_preflight"])
    duration = float(primary["duration"])
    output_interval = float(primary["output_interval"])
    coupled_cfg = config_from(primary)
    canonical_cfg = config_from(primary, coupling=0.0)
    trace_cfg = trace_config(prereg["trace_control"])

    scenario_specs: list[tuple[str, int | None]] = [
        ("uniform", None),
        ("localized", None),
        ("two_domain", None),
        *[(f"spinodal_seed_{seed}", int(seed)) for seed in prereg["random_seeds"]],
    ]
    scenario_runs: dict[str, dict[str, Any]] = {}
    for scenario_name, seed in scenario_specs:
        initial_name = "spinodal" if scenario_name.startswith("spinodal") else scenario_name
        C0 = initial_field(initial_name, cells, length, controls, seed)
        Phi0 = local_equilibrium_phi(C0, coupled_cfg) if scenario_name == "uniform" else np.zeros_like(C0)
        canonical = run_coupled(
            C0, dx, canonical_cfg, duration, dt_fraction, output_interval
        )
        coupled = run_coupled(
            C0, dx, coupled_cfg, duration, dt_fraction, output_interval, Phi0=Phi0
        )
        scenario_runs[scenario_name] = {
            "initial": C0,
            "canonical": canonical,
            "coupled": coupled,
            "coupling_effect_rms": rms(coupled["state"].C - canonical["state"].C),
            "canonical_morphology": morphology_metrics(canonical["state"].C, dx),
            "coupled_morphology": morphology_metrics(coupled["state"].C, dx),
        }

    ledger_refinement_records: list[dict[str, Any]] = []
    ledger_fraction = float(amendment["amendment"]["ledger_refinement_dt_fraction_of_preflight"])
    for scenario_name, seed in scenario_specs:
        initial_name = "spinodal" if scenario_name.startswith("spinodal") else scenario_name
        C0 = initial_field(initial_name, cells, length, controls, seed)
        Phi0 = local_equilibrium_phi(C0, coupled_cfg) if scenario_name == "uniform" else np.zeros_like(C0)
        canonical_refined = run_coupled(
            C0, dx, canonical_cfg, duration, ledger_fraction, duration
        )
        coupled_refined = run_coupled(
            C0, dx, coupled_cfg, duration, ledger_fraction, duration, Phi0=Phi0
        )
        ledger_refinement_records.append({
            "scenario": scenario_name,
            "dt_fraction_of_preflight": ledger_fraction,
            "canonical_max_ledger_closure_relative": float(
                canonical_refined["metrics"]["max_ledger_closure_relative"]
            ),
            "coupled_max_ledger_closure_relative": float(
                coupled_refined["metrics"]["max_ledger_closure_relative"]
            ),
            "canonical_matter_relative_drift": float(
                canonical_refined["metrics"]["matter_relative_drift"]
            ),
            "coupled_matter_relative_drift": float(
                coupled_refined["metrics"]["matter_relative_drift"]
            ),
        })

    localized_initial = scenario_runs["localized"]["initial"]
    trace_run = run_coupled(
        localized_initial,
        dx,
        canonical_cfg,
        duration,
        dt_fraction,
        output_interval,
        trace=trace_cfg,
    )
    trace_full_run_difference = physical_difference(
        scenario_runs["localized"]["canonical"]["state"], trace_run["state"]
    )

    primary_coupled = scenario_runs["localized"]["coupled"]
    reduced_primary = run_reduced(
        localized_initial, dx, coupled_cfg, duration, primary_coupled["dt"]
    )
    legacy = run_legacy(localized_initial, dx, prereg["legacy_comparator"])

    resolution_records: list[dict[str, float]] = []
    resolution_control = prereg["resolution_control"]
    for resolution_cells in resolution_control["cells"]:
        n = int(resolution_cells)
        local_dx = length / n
        C0 = initial_field("localized", n, length, controls)
        canonical = run_coupled(
            C0,
            local_dx,
            canonical_cfg,
            float(resolution_control["duration"]),
            float(resolution_control["dt_fraction_of_preflight"]),
            float(resolution_control["duration"]),
        )
        coupled = run_coupled(
            C0,
            local_dx,
            coupled_cfg,
            float(resolution_control["duration"]),
            float(resolution_control["dt_fraction_of_preflight"]),
            float(resolution_control["duration"]),
        )
        resolution_records.append({
            "cells": float(n),
            "dx": local_dx,
            "dt": float(coupled["dt"]),
            "coupling_effect_rms": rms(coupled["state"].C - canonical["state"].C),
        })

    temporal_runs = []
    for fraction in resolution_control["temporal_refinement_fractions"]:
        temporal_runs.append(
            run_coupled(
                localized_initial,
                dx,
                coupled_cfg,
                float(resolution_control["duration"]),
                float(fraction),
                float(resolution_control["duration"]),
            )
        )
    temporal_error = rms(temporal_runs[0]["state"].C - temporal_runs[1]["state"].C)

    zero = np.zeros_like(localized_initial)
    alternate_phi = float(controls["alternate_phi_amplitude"]) * np.cos(
        2.0 * np.pi * np.arange(cells) / cells
    )
    alternate_pi = float(controls["alternate_pi_amplitude"]) * np.sin(
        2.0 * np.pi * np.arange(cells) / cells
    )
    state_plain = MatterSpaceState(localized_initial, zero, zero)
    state_alternate = MatterSpaceState(localized_initial, alternate_phi, alternate_pi)
    state_dt = 0.02 * min(
        matter_space_stability_limit(state_plain, dx, coupled_cfg),
        matter_space_stability_limit(state_alternate, dx, coupled_cfg),
    )
    response_plain = matter_space_step(state_plain, state_dt, dx, coupled_cfg)
    response_alternate = matter_space_step(state_alternate, state_dt, dx, coupled_cfg)
    same_C_different_state_response = physical_difference(
        MatterSpaceState(response_plain.C, response_plain.space_response, response_plain.space_rate),
        MatterSpaceState(response_alternate.C, response_alternate.space_response, response_alternate.space_rate),
    )

    history_metrics = run_trace_invariance(
        localized_initial,
        dx,
        canonical_cfg,
        trace_cfg,
        int(prereg["trace_control"]["steps"]),
    )
    history_metrics["full_run_trace_switch_physical_difference"] = trace_full_run_difference
    history_metrics["same_C_different_state_response"] = same_C_different_state_response

    adiabatic_records: list[dict[str, float]] = []
    adiabatic = prereg["adiabatic_control"]
    for scale_value in adiabatic["scales"]:
        scale = float(scale_value)
        cfg = replace(
            coupled_cfg,
            tau_space=coupled_cfg.tau_space / scale ** float(adiabatic["tau_scale_power"]),
            mobility_space=coupled_cfg.mobility_space * scale ** float(adiabatic["mobility_scale_power"]),
            a_space=coupled_cfg.a_space * scale ** float(adiabatic["a_scale_power"]),
            kappa_space=coupled_cfg.kappa_space * scale ** float(adiabatic["kappa_scale_power"]),
        )
        Phi0 = local_equilibrium_phi(localized_initial, cfg)
        full = run_coupled(
            localized_initial,
            dx,
            cfg,
            float(adiabatic["duration"]),
            float(adiabatic["dt_fraction_of_preflight"]),
            float(adiabatic["duration"]),
            Phi0=Phi0,
        )
        reduced = run_reduced(
            localized_initial, dx, cfg, float(adiabatic["duration"]), float(full["dt"])
        )
        relative_error = rms(full["state"].C - reduced["C"]) / max(rms(reduced["C"]), 1e-15)
        adiabatic_records.append({
            "scale": scale,
            "tau_space": cfg.tau_space,
            "relaxation_time": 1.0 / (cfg.mobility_space * cfg.a_space),
            "correlation_length": float(np.sqrt(cfg.kappa_space / cfg.a_space)),
            "dt": float(full["dt"]),
            "relative_error": float(relative_error),
        })

    scenario_metrics = []
    for name, runs in scenario_runs.items():
        scenario_metrics.append({
            "scenario": name,
            "coupling_effect_rms": float(runs["coupling_effect_rms"]),
            "canonical": runs["canonical"]["metrics"],
            "coupled": runs["coupled"]["metrics"],
            "canonical_morphology": runs["canonical_morphology"],
            "coupled_morphology": runs["coupled_morphology"],
        })

    all_physical_runs = [
        lane
        for runs in scenario_runs.values()
        for lane in (runs["canonical"], runs["coupled"])
    ] + [trace_run]
    max_mass_drift = max(run["metrics"]["matter_relative_drift"] for run in all_physical_runs)
    max_energy_increase = max(run["metrics"]["max_relative_energy_increase"] for run in all_physical_runs)
    locked_max_ledger = max(
        run["metrics"]["max_ledger_closure_relative"] for run in all_physical_runs
    )
    refined_max_ledger = max(
        max(
            row["canonical_max_ledger_closure_relative"],
            row["coupled_max_ledger_closure_relative"],
        )
        for row in ledger_refinement_records
    )
    min_source = min(run["metrics"]["minimum_dissipation_density"] for run in all_physical_runs)
    all_finite = all(run["metrics"]["all_finite"] for run in all_physical_runs) and legacy["all_finite"]
    effects = [row["coupling_effect_rms"] for row in resolution_records]
    effect_ratio = min(effects) / max(max(effects), 1e-30)
    primary_effect = next(row["coupling_effect_rms"] for row in resolution_records if int(row["cells"]) == cells)
    adiabatic_errors = [row["relative_error"] for row in adiabatic_records]
    adiabatic_monotonic = all(
        right <= left * (1.0 + 1e-8)
        for left, right in zip(adiabatic_errors, adiabatic_errors[1:])
    )

    metrics = {
        "max_matter_relative_drift": float(max_mass_drift),
        "minimum_dissipation_density": float(min_source),
        "max_closed_energy_relative_increase": float(max_energy_increase),
        "locked_max_ledger_closure_relative": float(locked_max_ledger),
        "refined_max_ledger_closure_relative": float(refined_max_ledger),
        "primary_coupling_effect_rms": float(primary_effect),
        "temporal_refinement_error_rms": float(temporal_error),
        "effect_to_temporal_error_ratio": float(primary_effect / max(temporal_error, 1e-30)),
        "resolution_effect_ratio": float(effect_ratio),
        "same_C_different_state_response": float(same_C_different_state_response),
        "state_sensitivity_to_temporal_error_ratio": float(
            same_C_different_state_response / max(temporal_error, 1e-30)
        ),
        "trace_switch_physical_difference": float(history_metrics["trace_switch_physical_difference"]),
        "full_run_trace_switch_physical_difference": float(trace_full_run_difference),
        "different_trace_history_physical_difference": float(history_metrics["different_history_physical_difference"]),
        "different_trace_history_observable_difference": float(history_metrics["different_history_trace_observable_difference"]),
        "adiabatic_finest_relative_error": float(adiabatic_errors[-1]),
        "legacy_matter_relative_drift": float(legacy["matter_relative_drift"]),
    }
    thresholds = prereg["thresholds"]
    gates = {
        "matter_conservation": metrics["max_matter_relative_drift"] <= thresholds["matter_relative_drift_max"],
        "dissipation_source_sign": metrics["minimum_dissipation_density"] >= thresholds["minimum_dissipation_density_min"],
        "closed_energy_descent": metrics["max_closed_energy_relative_increase"] <= thresholds["closed_energy_relative_increase_max"],
        "ledger_closure_refined": (
            metrics["refined_max_ledger_closure_relative"]
            <= thresholds["ledger_closure_relative_max"]
        ),
        "coupling_above_numerical_error": (
            metrics["primary_coupling_effect_rms"] > thresholds["coupling_effect_absolute_min"]
            and metrics["effect_to_temporal_error_ratio"] >= thresholds["effect_to_temporal_error_min"]
        ),
        "resolution_persistence": metrics["resolution_effect_ratio"] >= thresholds["resolution_effect_ratio_min"],
        "same_C_physical_state_sensitivity": (
            metrics["state_sensitivity_to_temporal_error_ratio"]
            >= thresholds["state_sensitivity_to_temporal_error_min"]
        ),
        "trace_switch_invariance": max(
            metrics["trace_switch_physical_difference"],
            metrics["full_run_trace_switch_physical_difference"],
        ) <= thresholds["trace_physical_difference_max"],
        "different_trace_history_invariance": (
            metrics["different_trace_history_physical_difference"]
            <= thresholds["trace_physical_difference_max"]
        ),
        "different_trace_history_observable_nonzero": (
            metrics["different_trace_history_observable_difference"] > 1e-12
        ),
        "adiabatic_error_decreases": bool(adiabatic_monotonic),
        "adiabatic_finest_error": (
            metrics["adiabatic_finest_relative_error"]
            <= thresholds["adiabatic_finest_relative_error_max"]
        ),
        "finite_without_clipping_or_fitting": bool(all_finite),
    }
    failed = [name for name, passed in gates.items() if not passed]

    x = np.arange(cells, dtype=float) * dx
    figures = write_outputs(
        x,
        localized_initial,
        scenario_runs["localized"],
        trace_run,
        reduced_primary,
        legacy,
        scenario_runs["two_domain"]["initial"],
        scenario_runs["two_domain"],
        resolution_records,
        adiabatic_records,
        history_metrics,
        thresholds,
    )

    internal_status = "PASS" if not failed else "FAIL"
    controlling = failed[0] if failed else "inherited_core_prearrival_leakage"
    artifact = {
        "schema_version": "1.0",
        "artifact": "0_11_matter_space_coupled_diagnostic",
        "topic": "0.11_Phase_Transitions",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "INTERNAL_DIAGNOSTIC",
        "internal_gate_status": internal_status,
        "dependency_status": "BLOCKED" if core["status"] != "PASS" else "OPEN_DIAGNOSTIC",
        "controlling_blocker": controlling,
        "topic_status_impact": "NONE",
        "topic_readiness_before_after": [topic_gate["current_readiness"], topic_gate["current_readiness"]],
        "topic_tier_before_after": [topic_gate["current_tier"], topic_gate["current_tier"]],
        "topic_controlling_blocker_unchanged": topic_gate["controlling_blocker"],
        "claim_class": "internal_normalized_matter_space_diagnostic",
        "operator_mode": "matter_space_coupled_v1",
        "comparators": {
            "legacy_instantaneous_uet": "descriptive only; not a conserved or variational reference",
            "canonical_conserved_C": "same finite-volume lane with coupling_g=0",
            "canonical_C_plus_trace": "derived trace enabled with no physical backreaction",
            "coupled_C_Phi_Pi": "exact normalized functional and extended ledger",
            "adiabatic_reduced": "local Phi equilibrium root with conserved C evolution",
        },
        "metrics": metrics,
        "thresholds": thresholds,
        "gates": gates,
        "failed_gates": failed,
        "scenario_results": scenario_metrics,
        "ledger_refinement": {
            "records": ledger_refinement_records,
            "locked_max_ledger_closure_relative": locked_max_ledger,
            "refined_max_ledger_closure_relative": refined_max_ledger,
            "role": "post-diagnostic numerical refinement; not blind confirmation",
        },
        "resolution_control": resolution_records,
        "adiabatic_control": adiabatic_records,
        "trace_and_state_control": history_metrics,
        "legacy_comparator": {
            "matter_relative_drift": legacy["matter_relative_drift"],
            "all_finite": legacy["all_finite"],
            "role": legacy["role"],
            "parameters": legacy["parameters"],
        },
        "preregistration": {
            "path": str(PREREG_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_text_file(PREREG_PATH),
            "status": prereg["status"],
            "random_seeds": prereg["random_seeds"],
            "parameter_fitting": False,
        },
        "numerical_amendment": {
            "path": str(AMENDMENT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_text_file(AMENDMENT_PATH),
            "status": amendment["status"],
            "blind_preregistration": False,
            "ledger_refinement_dt_fraction": ledger_fraction,
            "physical_parameters_changed": False,
            "thresholds_changed": False,
        },
        "dependencies": {
            "matter_space_core": {
                "path": str(CORE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(CORE_PATH),
                "status": core["status"],
                "controlling_blocker": core["controlling_blocker"],
            },
            "topic_closure_status": {
                "path": str(TOPIC_GATE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(TOPIC_GATE_PATH),
                "status": topic_gate["status"],
                "controlling_blocker": topic_gate["controlling_blocker"],
            },
        },
        "outputs": {
            "profiles_csv": {
                "path": str(CSV_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(CSV_PATH),
            },
            "figures": figures,
            "script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "run_integrity": {
            "unit_lane": "normalized",
            "external_numeric_data_used": False,
            "parameter_fitting": False,
            "field_clipping": False,
            "trace_backreaction": False,
            "random_seeds_locked": True,
            "morphology_metrics_claim_bearing": False,
            "post_diagnostic_numerical_amendment": True,
            "amendment_informed_by_initial_ledger_failure": True,
        },
        "claim_boundary": [
            "This pilot does not alter the current Topic 0.11 structure-factor controller, Draft readiness, or Tier B status.",
            "Interface width, structure-factor peak, and correlation-length values are diagnostics only and are not accepted estimators.",
            "The trace is derived from dissipation history and never changes C, Phi, or Pi.",
            "The legacy lane is descriptive and is not evidence for conserved or variational closure.",
            "The locked ledger run failed; the disclosed refined ledger result changes only dt and is not a blind confirmation.",
            "No universality, RG, material, external-validation, spacetime, or solved-phase-transition claim is supported.",
        ],
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"],
        "internal_gate_status": internal_status,
        "dependency_status": artifact["dependency_status"],
        "controlling_blocker": controlling,
        "failed_gates": failed,
        "artifact": str(ARTIFACT_PATH.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
