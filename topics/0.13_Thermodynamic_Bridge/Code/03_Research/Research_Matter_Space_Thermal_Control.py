"""Normalized thermal controls for the matter-space candidate.

Reads a locked preregistration, compares five responses, and preserves the
boundary between synthetic diagnostics and external validation.
"""
from __future__ import annotations
import csv, hashlib, json, sys
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
TOPIC = ROOT / "docs" / "topics" / "0.13_Thermodynamic_Bridge"
PREREG_PATH = TOPIC / "Data" / "03_Research" / "matter_space_thermal_preregistration.json"
SOURCE_PATH = TOPIC / "Data" / "03_Research" / "matter_space_second_sound_source_package.json"
AMENDMENT_PATH = TOPIC / "Data" / "03_Research" / "matter_space_thermal_numerical_amendment_001.json"
CORE_VERIFIER_PATH = ROOT / "docs" / "core" / "07_artifacts" / "verification" / "matter_space_variational_verification.json"
ARTIFACT_PATH = TOPIC / "Result" / "artifacts" / "matter_space_thermal_control.json"
RESULT_DIR = TOPIC / "Result" / "03_show_Result"
CSV_PATH = RESULT_DIR / "matter_space_thermal_control_timeseries.csv"

from docs.core.uet_matter_space import (  # noqa: E402
    MatterSpaceConfig, MatterSpaceState, matter_space_stability_limit, matter_space_step,
)
from docs.core.uet_trace import TraceKernelConfig, compute_spacetime_trace  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def signed_loop_area(x: np.ndarray, y: np.ndarray) -> float:
    return float(0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))


def phase_and_lag(signal: np.ndarray, times: np.ndarray, omega: float) -> tuple[float, float]:
    design = np.column_stack([np.ones_like(times), np.sin(omega * times), np.cos(omega * times)])
    coefficients, *_ = np.linalg.lstsq(design, signal, rcond=None)
    phase = float(np.arctan2(coefficients[2], coefficients[1]))
    return phase, float(-phase / omega)


def cattaneo_reference(times: np.ndarray, tau: float, conductivity: float, omega: float) -> np.ndarray:
    a = omega * tau
    return conductivity * (np.sin(omega * times) - a * np.cos(omega * times)) / (1.0 + a * a)


def integrate_cattaneo_heun(times: np.ndarray, tau: float, conductivity: float, omega: float) -> np.ndarray:
    response = np.zeros_like(times)
    response[0] = cattaneo_reference(times[:1], tau, conductivity, omega)[0]
    for i in range(len(times) - 1):
        dt = float(times[i + 1] - times[i])
        k1 = (-response[i] + conductivity * np.sin(omega * times[i])) / tau
        predictor = response[i] + dt * k1
        k2 = (-predictor + conductivity * np.sin(omega * times[i + 1])) / tau
        response[i + 1] = response[i] + 0.5 * dt * (k1 + k2)
    return response


def cattaneo_residual(tau: float, conductivity: float, omega: float) -> float:
    transfer = conductivity / (1.0 + 1j * omega * tau)
    return float(abs((1.0 + 1j * omega * tau) * transfer - conductivity))


def linear_space_response(times: np.ndarray, omega: float, control: dict[str, Any]) -> np.ndarray:
    transfer = float(control["drive_amplitude"]) / (
        float(control["mobility_space"]) * float(control["a_space"])
        - float(control["tau_space"]) * omega**2 + 1j * omega
    )
    return transfer.real * np.sin(omega * times) + transfer.imag * np.cos(omega * times)


def scalar_rhs(C: float, Phi: float, Pi: float, cfg: dict[str, float], Jc: float, Jphi: float):
    mu_C = cfg["a_matter"] * C + cfg["b_matter"] * C**3 - cfg["coupling_g"] * C * Phi
    mu_Phi = cfg["a_space"] * Phi + cfg["b_space"] * Phi**3 - 0.5 * cfg["coupling_g"] * C**2
    return (
        -cfg["mobility_matter"] * mu_C + Jc,
        Pi,
        (-Pi - cfg["mobility_space"] * mu_Phi + Jphi) / cfg["tau_space"],
        mu_C,
    )


def scalar_energy(C: float, Phi: float, Pi: float, cfg: dict[str, float]) -> float:
    omega = (
        0.5 * cfg["a_matter"] * C**2 + 0.25 * cfg["b_matter"] * C**4
        + 0.5 * cfg["a_space"] * Phi**2 + 0.25 * cfg["b_space"] * Phi**4
        - 0.5 * cfg["coupling_g"] * C**2 * Phi
    )
    return float(omega + cfg["tau_space"] * Pi**2 / (2.0 * cfg["mobility_space"]))


def scalar_dissipation(mu_C: float, Pi: float, cfg: dict[str, float]) -> float:
    return float(cfg["mobility_matter"] * mu_C**2 + Pi**2 / cfg["mobility_space"])


def scalar_step(C: float, Phi: float, Pi: float, dt: float, cfg: dict[str, float], Jc: float, Jphi: float) -> dict[str, float]:
    energy_before = scalar_energy(C, Phi, Pi, cfg)
    k1_C, k1_Phi, k1_Pi, mu1 = scalar_rhs(C, Phi, Pi, cfg, Jc, Jphi)
    sigma1 = scalar_dissipation(mu1, Pi, cfg)
    power1 = mu1 * Jc + Pi * Jphi / cfg["mobility_space"]
    pred = (C + dt * k1_C, Phi + dt * k1_Phi, Pi + dt * k1_Pi)
    k2_C, k2_Phi, k2_Pi, _ = scalar_rhs(*pred, cfg, Jc, Jphi)
    new = (
        C + 0.5 * dt * (k1_C + k2_C),
        Phi + 0.5 * dt * (k1_Phi + k2_Phi),
        Pi + 0.5 * dt * (k1_Pi + k2_Pi),
    )
    _, _, _, mu2 = scalar_rhs(*new, cfg, Jc, Jphi)
    sigma2 = scalar_dissipation(mu2, new[2], cfg)
    power2 = mu2 * Jc + new[2] * Jphi / cfg["mobility_space"]
    energy_after = scalar_energy(*new, cfg)
    sigma = 0.5 * (sigma1 + sigma2)
    power = 0.5 * (power1 + power2)
    predicted = dt * (-sigma + power)
    actual = energy_after - energy_before
    scale = max(abs(actual), abs(predicted), dt * sigma, 1e-12)
    return {
        "C": new[0], "Phi": new[1], "Pi": new[2], "energy": energy_after,
        "actual_delta": actual, "predicted_delta": predicted,
        "closure_relative": abs(actual - predicted) / scale,
        "dissipation": sigma, "input_power": power, "trace_source": sigma,
    }


def nonlinear_config(primary: dict[str, Any], coupling: float, tau: float) -> dict[str, float]:
    keys = ["a_matter", "b_matter", "kappa_matter", "mobility_matter", "a_space", "b_space", "kappa_space", "mobility_space"]
    cfg = {key: float(primary[key]) for key in keys}
    cfg.update({"coupling_g": float(coupling), "tau_space": float(tau)})
    return cfg


def simulate_nonlinear(prereg: dict[str, Any], coupling: float, tau: float, dt: float, duration: float, output_dt: float) -> dict[str, Any]:
    primary = prereg["nonlinear_primary"]
    cfg = nonlinear_config(primary, coupling, tau)
    omega = float(prereg["forcing"]["omega"])
    steps, stride = int(round(duration / dt)), max(1, int(round(output_dt / dt)))
    C, Phi, Pi = 0.3, 0.0, 0.0
    records = [{"time": 0.0, "force": 0.0, "C": C, "Phi": Phi, "Pi": Pi,
                "energy": scalar_energy(C, Phi, Pi, cfg), "actual_delta": 0.0,
                "predicted_delta": 0.0, "closure_relative": 0.0,
                "dissipation": 0.0, "input_power": 0.0, "trace_source": 0.0}]
    max_closure, source_min = 0.0, np.inf
    for step in range(1, steps + 1):
        force_mid = float(np.sin(omega * (step - 0.5) * dt))
        result = scalar_step(
            C, Phi, Pi, dt, cfg,
            float(primary["matter_drive_amplitude"]) * force_mid,
            float(primary["space_drive_amplitude"]) * force_mid,
        )
        C, Phi, Pi = result["C"], result["Phi"], result["Pi"]
        max_closure = max(max_closure, result["closure_relative"])
        source_min = min(source_min, result["trace_source"])
        if step % stride == 0 or step == steps:
            records.append({"time": step * dt, "force": float(np.sin(omega * step * dt)), **result})
    arrays = {key: np.asarray([row[key] for row in records], dtype=float) for key in records[0]}
    cutoff = min(float(prereg["analysis"]["transient_cutoff"]), 0.6 * duration)
    mask = arrays["time"] >= cutoff
    phase, lag = phase_and_lag(arrays["Phi"][mask], arrays["time"][mask], omega)
    return {
        "arrays": arrays, "config": cfg, "dt": dt, "duration": duration,
        "metrics": {
            "phase_radians": phase, "lag_time": lag,
            "hysteresis_area": signed_loop_area(arrays["force"][mask], arrays["Phi"][mask]),
            "max_ledger_closure_relative": float(max_closure),
            "minimum_trace_source": float(source_min),
            "final_C": float(C), "final_Phi": float(Phi), "final_Pi": float(Pi),
        },
    }



def homogeneous_core_crosscheck(prereg: dict[str, Any]) -> float:
    primary = prereg["nonlinear_primary"]
    cfg_dict = nonlinear_config(primary, primary["coupling_g"], primary["tau_space"])
    cfg = MatterSpaceConfig(
        **cfg_dict, matter_dynamics="nonconserved", boundary_condition="periodic",
        stability_safety=0.2, ledger_tolerance=1e-6,
    )
    cells, dx, dt = int(primary["cells"]), float(primary["dx"]), float(primary["dt"])
    force = float(np.sin(float(prereg["forcing"]["omega"]) * 0.5 * dt))
    Jc = float(primary["matter_drive_amplitude"]) * force
    Jphi = float(primary["space_drive_amplitude"]) * force
    state = MatterSpaceState(np.full(cells, 0.3), np.zeros(cells), np.zeros(cells))
    if dt > matter_space_stability_limit(state, dx, cfg):
        raise RuntimeError("pre-registered primary dt exceeds core stability limit")
    core = matter_space_step(
        state, dt, dx, cfg,
        matter_source=np.full(cells, Jc), space_source=np.full(cells, Jphi),
    )
    scalar = scalar_step(0.3, 0.0, 0.0, dt, cfg_dict, Jc, Jphi)
    return max(
        float(np.max(np.abs(core.C - scalar["C"]))),
        float(np.max(np.abs(core.space_response - scalar["Phi"]))),
        float(np.max(np.abs(core.space_rate - scalar["Pi"]))),
    )


def trace_only_control(prereg: dict[str, Any]) -> dict[str, np.ndarray]:
    control, forcing = prereg["trace_control"], prereg["forcing"]
    tau = float(prereg["cattaneo_control"]["tau_q"])
    k = float(prereg["cattaneo_control"]["conductivity_normalized"])
    omega, dt = float(forcing["omega"]), float(control["dt"])
    times = np.arange(0.0, float(forcing["duration"]) + 0.5 * dt, dt)
    a = omega * tau
    derivative = k * omega * (np.cos(omega * times) + a * np.sin(omega * times)) / (1.0 + a * a)
    source = np.square(derivative)
    cfg = TraceKernelConfig(
        D_trace=float(control["D_trace"]), tau_trace=float(control["tau_trace"]),
        lambda_trace=float(control["lambda_trace"]), source_normalization="normalized",
        boundary_condition=str(control["boundary_condition"]),
    )
    history: list[np.ndarray] = []
    trace = np.zeros_like(times)
    for i, value in enumerate(source):
        history.append(np.asarray([value], dtype=float))
        trace[i] = compute_spacetime_trace(history, dx=1.0, dt=dt, config=cfg, shape=(1,))[0]
    return {"time": times, "source": source, "trace": trace}


def causal_visual_control() -> dict[str, Any]:
    n, dx = 801, 0.025
    center = n // 2
    cfg = MatterSpaceConfig(
        a_matter=0.0, b_matter=1.0, kappa_matter=1e-8, mobility_matter=1e-8,
        a_space=0.0, b_space=1e-12, kappa_space=5.0, mobility_space=1.0,
        tau_space=5.0, coupling_g=0.0, matter_dynamics="conserved",
        boundary_condition="zero_flux", stability_safety=0.2,
    )
    rate = np.zeros(n)
    rate[center] = 1.0 / dx
    state = MatterSpaceState(np.zeros(n), np.zeros(n), rate)
    dt = 0.8 * matter_space_stability_limit(state, dx, cfg)
    distance, expected = 1.0, 1.0 / cfg.space_speed
    target = center + int(round(distance / dx))
    steps = int(np.ceil(1.3 * expected / dt))
    times, signal = np.zeros(steps), np.zeros(steps)
    for i in range(steps):
        result = matter_space_step(state, dt, dx, cfg)
        state = MatterSpaceState(result.C, result.space_response, result.space_rate)
        times[i], signal[i] = (i + 1) * dt, state.space_response[target]
    magnitude, peak = np.abs(signal), float(np.max(np.abs(signal)))
    arrival = float(times[int(np.flatnonzero(magnitude >= 0.2 * peak)[0])])
    leakage = float(np.max(magnitude[times <= 0.95 * expected]) / max(peak, 1e-300))
    speed = distance / arrival
    return {
        "time": times, "signal": signal, "expected_arrival": expected,
        "arrival_time": arrival, "measured_speed": speed, "declared_speed": cfg.space_speed,
        "speed_relative_error": abs(speed - cfg.space_speed) / cfg.space_speed,
        "prearrival_leakage_fraction": leakage, "dt": dt, "dx": dx,
    }


def normalized(signal: np.ndarray) -> np.ndarray:
    centered = signal - np.mean(signal)
    return centered / max(float(np.max(np.abs(centered))), 1e-15)


def write_timeseries(primary, fourier, cattaneo_ref, cattaneo_numeric, linear_phi, trace) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    a, times = primary["arrays"], primary["arrays"]["time"]
    trace_y = np.interp(times, trace["time"], trace["trace"])
    source = np.interp(times, trace["time"], trace["source"])
    columns = [
        "time_normalized", "thermal_force_normalized", "fourier_response_normalized",
        "cattaneo_reference_normalized", "cattaneo_numeric_normalized",
        "linear_phi_response_normalized", "nonlinear_C", "nonlinear_Phi", "nonlinear_Pi",
        "trace_source_nonnegative", "trace_observable_normalized", "extended_energy_normalized",
        "actual_delta_normalized", "predicted_delta_normalized", "ledger_closure_relative",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for i, time in enumerate(times):
            writer.writerow([
                float(time), float(a["force"][i]), float(fourier[i]), float(cattaneo_ref[i]),
                float(cattaneo_numeric[i]), float(linear_phi[i]), float(a["C"][i]),
                float(a["Phi"][i]), float(a["Pi"][i]), float(source[i]), float(trace_y[i]),
                float(a["energy"][i]), float(a["actual_delta"][i]),
                float(a["predicted_delta"][i]), float(a["closure_relative"][i]),
            ])


def _save_figure(fig, path: Path, caption: str, caveat: str, manifest: list[dict[str, str]]) -> None:
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    manifest.append({
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "caption": caption, "caveat": caveat,
    })


def create_figures(prereg, primary, fourier, cattaneo_ref, linear_phi, trace, causal):
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    a, times = primary["arrays"], primary["arrays"]["time"]
    mask = times >= float(prereg["analysis"]["transient_cutoff"])
    source = np.interp(times, trace["time"], trace["source"])
    trace_y = np.interp(times, trace["time"], trace["trace"])
    manifest: list[dict[str, str]] = []

    path = RESULT_DIR / "matter_space_thermal_phase_lag.png"
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(times[mask], normalized(a["force"][mask]), label="thermal force", color="black", lw=1.5)
    for values, label in [(fourier, "Fourier"), (cattaneo_ref, "Cattaneo"), (linear_phi, "linear Phi"), (a["Phi"], "nonlinear Phi")]:
        axes[0].plot(times[mask], normalized(values[mask]), label=label, lw=1.2)
    axes[0].set(ylabel="centered normalized response", title="Phase-lag comparison (normalized synthetic controls)")
    axes[0].legend(ncol=3, fontsize=8)
    axes[1].plot(times[mask], normalized(source[mask]), label="non-negative source", color="#7a5195")
    axes[1].plot(times[mask], normalized(trace_y[mask]), label="derived trace R", color="#ef5675")
    axes[1].set(xlabel="normalized time", ylabel="centered normalized observable")
    axes[1].legend(fontsize=8)
    fig.text(0.01, 0.01, "Synthetic normalized controls; R is not heat flux and has no backreaction.", fontsize=8)
    _save_figure(fig, path, "Fourier, Cattaneo, linear Phi, nonlinear Phi, and a separately plotted derived trace.", "Visual phase similarity is not external validation.", manifest)

    path = RESULT_DIR / "matter_space_thermal_hysteresis.png"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for values, label in [(fourier, "Fourier"), (cattaneo_ref, "Cattaneo"), (linear_phi, "linear Phi"), (a["Phi"], "nonlinear Phi")]:
        axes[0].plot(a["force"][mask], normalized(values[mask]), label=label)
    axes[0].set(xlabel="normalized thermal force", ylabel="normalized response", title="Response hysteresis")
    axes[0].legend(fontsize=8)
    axes[1].plot(source[mask], trace_y[mask], color="#ef5675")
    axes[1].set(xlabel="non-negative dissipation source", ylabel="derived trace R", title="Trace-only history loop")
    fig.text(0.01, 0.01, "Loop areas are diagnostic; axes are not W/m? or K/m.", fontsize=8)
    _save_figure(fig, path, "Physical-control loops and the source-to-trace loop are kept on separate axes.", "No material-level comparison is made.", manifest)

    path = RESULT_DIR / "matter_space_thermal_causal_arrival.png"
    fig, ax = plt.subplots(figsize=(9, 4.5))
    peak = max(float(np.max(np.abs(causal["signal"]))), 1e-15)
    ax.plot(causal["time"], causal["signal"] / peak, label="detector response / peak")
    ax.axvspan(0.0, 0.95 * causal["expected_arrival"], color="#ffa600", alpha=0.12, label="pre-arrival audit window")
    ax.axvline(causal["expected_arrival"], color="black", ls="--", label="declared arrival")
    ax.axvline(causal["arrival_time"], color="#ef5675", ls=":", label="20% measured arrival")
    ax.set(xlabel="normalized time", ylabel="normalized detector response", title="Compact-pulse causal arrival audit")
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "The early tail is retained, not clipped; it is the current blocking numerical result.", fontsize=8)
    _save_figure(fig, path, "Compact-pulse detector response against the declared Phi propagation time.", "Pre-arrival leakage blocks physical interpretation.", manifest)

    path = RESULT_DIR / "matter_space_thermal_ledger.png"
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].plot(times, a["energy"], color="#003f5c", label="extended energy")
    axes[0].set(xlabel="normalized time", ylabel="normalized extended energy", title="Driven-system energy account")
    axes[0].legend(fontsize=8)
    axes[1].semilogy(times[1:], np.maximum(a["closure_relative"][1:], 1e-18), color="#bc5090", label="closure residual")
    axes[1].axhline(float(prereg["thresholds"]["ledger_closure_relative_max"]), color="black", ls="--", label="gate")
    axes[1].set(xlabel="normalized time", ylabel="relative closure residual", title="Ledger closure")
    axes[1].legend(fontsize=8)
    fig.text(0.01, 0.01, "External drive power is recorded; energy change is not described as disappearance.", fontsize=8)
    _save_figure(fig, path, "Normalized extended energy and open-system ledger closure.", "This is not an SI heat or entropy balance.", manifest)
    return manifest



def main() -> int:
    prereg = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    sources = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    amendment = json.loads(AMENDMENT_PATH.read_text(encoding="utf-8"))
    core = json.loads(CORE_VERIFIER_PATH.read_text(encoding="utf-8"))
    if prereg.get("status") != "LOCKED_BEFORE_EXECUTION" or prereg.get("external_numeric_inputs"):
        raise RuntimeError("pilot requires a locked synthetic-only preregistration")
    if amendment.get("status") != "POST_DIAGNOSTIC_NUMERICAL_AMENDMENT":
        raise RuntimeError("pilot requires the explicit numerical-amendment record")
    if any(
        bool(amendment["amendment"][key])
        for key in ("physical_parameters_changed", "thresholds_changed", "external_data_added", "parameter_fitting", "seed_changed")
    ):
        raise RuntimeError("the numerical amendment may change only the analysis time step")

    forcing, primary_cfg = prereg["forcing"], prereg["nonlinear_primary"]
    omega, duration = float(forcing["omega"]), float(forcing["duration"])
    locked_primary = simulate_nonlinear(
        prereg, float(primary_cfg["coupling_g"]), float(primary_cfg["tau_space"]),
        float(primary_cfg["dt"]), duration, float(primary_cfg["output_dt"]),
    )
    analysis_dt = float(amendment["amendment"]["analysis_dt"])
    primary = simulate_nonlinear(
        prereg, float(primary_cfg["coupling_g"]), float(primary_cfg["tau_space"]),
        analysis_dt, duration, float(primary_cfg["output_dt"]),
    )
    convergence = simulate_nonlinear(
        prereg, float(primary_cfg["coupling_g"]), float(primary_cfg["tau_space"]),
        float(primary_cfg["convergence_dt"]), duration, float(primary_cfg["output_dt"]),
    )
    nonlinear_convergence = float(
        np.max(np.abs(primary["arrays"]["Phi"] - locked_primary["arrays"]["Phi"]))
    )
    locked_to_coarse_convergence = float(
        np.max(np.abs(locked_primary["arrays"]["Phi"] - convergence["arrays"]["Phi"]))
    )
    crosscheck = homogeneous_core_crosscheck(prereg)

    grid_records = []
    grid = prereg["sensitivity_grid"]
    for coupling in grid["coupling_g"]:
        for tau in grid["tau_space"]:
            run = simulate_nonlinear(
                prereg, float(coupling), float(tau), float(grid["dt"]),
                float(grid["duration"]), 0.02,
            )
            grid_records.append({
                "coupling_g": float(coupling), "tau_space": float(tau),
                **{key: float(value) for key, value in run["metrics"].items()},
            })

    times = primary["arrays"]["time"]
    force = np.sin(omega * times)
    tau_q = float(prereg["cattaneo_control"]["tau_q"])
    conductivity = float(prereg["cattaneo_control"]["conductivity_normalized"])
    fourier = conductivity * force
    base_dt = float(prereg["cattaneo_control"]["dt"])
    coarse_times = np.arange(0.0, duration + 0.5 * base_dt, base_dt)
    fine_times = np.arange(0.0, duration + 0.25 * base_dt, 0.5 * base_dt)
    reference_control = cattaneo_reference(coarse_times, tau_q, conductivity, omega)
    coarse = integrate_cattaneo_heun(coarse_times, tau_q, conductivity, omega)
    fine = integrate_cattaneo_heun(fine_times, tau_q, conductivity, omega)
    cattaneo_convergence = float(np.max(np.abs(coarse - fine[::2][: len(coarse)])))
    reference = cattaneo_reference(times, tau_q, conductivity, omega)
    numeric = np.interp(times, coarse_times, coarse)
    linear_phi = linear_space_response(times, omega, prereg["linear_space_control"])
    trace = trace_only_control(prereg)
    causal = causal_visual_control()

    mask = coarse_times >= float(prereg["analysis"]["transient_cutoff"])
    phase_ref, lag_ref = phase_and_lag(reference_control[mask], coarse_times[mask], omega)
    phase_num, lag_num = phase_and_lag(coarse[mask], coarse_times[mask], omega)
    phase_error = abs(float(np.angle(np.exp(1j * (phase_num - phase_ref)))))
    phase_relative = phase_error / max(abs(phase_ref), 1e-15)
    lag_relative = abs(lag_num - lag_ref) / max(abs(lag_ref), 1e-15)
    control_force = np.sin(omega * coarse_times)
    area_ref = signed_loop_area(control_force[mask], reference_control[mask])
    area_num = signed_loop_area(control_force[mask], coarse[mask])
    area_relative = abs(area_num - area_ref) / max(abs(area_ref), 1e-15)
    residual = cattaneo_residual(tau_q, conductivity, omega)

    write_timeseries(primary, fourier, reference, numeric, linear_phi, trace)
    figures = create_figures(prereg, primary, fourier, reference, linear_phi, trace, causal)
    for entry in figures:
        entry["sha256"] = sha256_file(ROOT / entry["path"])

    thresholds = prereg["thresholds"]
    core_leakage = float(core["metrics"]["prearrival_leakage"]["value"])
    core_arrival = float(core["metrics"]["causal_arrival_speed"]["value"])
    metrics = {
        "cattaneo_analytical_residual": residual,
        "cattaneo_phase_relative_error": phase_relative,
        "cattaneo_lag_relative_error": lag_relative,
        "cattaneo_hysteresis_relative_error": area_relative,
        "cattaneo_convergence_error": cattaneo_convergence,
        "nonlinear_homogeneous_core_crosscheck_error": crosscheck,
        "nonlinear_dt_convergence_error": nonlinear_convergence,
        "nonlinear_locked_to_coarse_dt_error": locked_to_coarse_convergence,
        "locked_primary_max_ledger_closure_relative": float(locked_primary["metrics"]["max_ledger_closure_relative"]),
        "nonlinear_max_ledger_closure_relative": float(primary["metrics"]["max_ledger_closure_relative"]),
        "minimum_dissipation_source": float(primary["metrics"]["minimum_trace_source"]),
        "core_causal_arrival_speed_relative_error": core_arrival,
        "core_prearrival_leakage_fraction": core_leakage,
        "pilot_visual_arrival_speed_relative_error": float(causal["speed_relative_error"]),
        "pilot_visual_prearrival_leakage_fraction": float(causal["prearrival_leakage_fraction"]),
        "trace_source_minimum": float(np.min(trace["source"])),
        "trace_lag_time": phase_and_lag(trace["trace"] - np.mean(trace["trace"]), trace["time"], 2.0 * omega)[1],
        "trace_hysteresis_area": signed_loop_area(trace["source"], trace["trace"]),
    }
    gates = {
        "cattaneo_analytical_residual": residual <= thresholds["cattaneo_analytical_residual_max"],
        "cattaneo_phase": phase_relative <= thresholds["cattaneo_phase_relative_error_max"],
        "cattaneo_lag": lag_relative <= thresholds["cattaneo_lag_relative_error_max"],
        "cattaneo_hysteresis": area_relative <= thresholds["cattaneo_hysteresis_relative_error_max"],
        "cattaneo_convergence": cattaneo_convergence <= thresholds["cattaneo_convergence_error_max"],
        "homogeneous_core_crosscheck": crosscheck <= 1e-12,
        "ledger_closure_refined": metrics["nonlinear_max_ledger_closure_relative"] <= thresholds["ledger_closure_relative_max"],
        "source_sign": metrics["minimum_dissipation_source"] >= thresholds["source_minimum"],
        "trace_source_sign": metrics["trace_source_minimum"] >= thresholds["source_minimum"],
        "causal_arrival_speed": core_arrival <= thresholds["causal_arrival_speed_relative_error_max"],
        "prearrival_leakage": core_leakage <= thresholds["prearrival_leakage_fraction_max"],
        "external_source_ready": sources["status"] == "READY",
    }
    failed = [name for name, passed in gates.items() if not passed]
    controlling = "core_prearrival_leakage" if "prearrival_leakage" in failed else (failed[0] if failed else "none")
    artifact = {
        "schema_version": "1.0", "artifact": "matter_space_thermal_control",
        "topic": "0.13_Thermodynamic_Bridge",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "SIMULATION_ONLY", "internal_gate_status": "FAIL" if failed else "PASS",
        "dependency_status": "BLOCKED" if core["status"] != "PASS" else "OPEN_DIAGNOSTIC",
        "controlling_blocker": controlling, "claim_class": "internal_synthetic_diagnostic",
        "external_validation": False,
        "operator_mode": "matter_space_coupled_v1_homogeneous_reduction_plus_spatial_causal_control",
        "controls": {
            "fourier": "q = k F(t)",
            "cattaneo": "tau_q dq/dt + q = k F(t)",
            "trace_only": "R = G_ret * sigma; no backreaction",
            "linear_space": "tau_Phi Phi_tt + Phi_t + M_Phi a_Phi Phi = J_Phi(t)",
            "nonlinear_candidate": "uniform reduction of the exact functional, cross-checked against the core operator",
        },
        "metrics": metrics, "thresholds": thresholds, "gates": gates,
        "failed_gates": failed,
        "primary_parameters": {**primary_cfg, "dt": analysis_dt},
        "locked_primary_observation": {
            "dt": float(primary_cfg["dt"]),
            "ledger_closure_relative": float(locked_primary["metrics"]["max_ledger_closure_relative"]),
            "ledger_gate_passed": bool(
                locked_primary["metrics"]["max_ledger_closure_relative"]
                <= thresholds["ledger_closure_relative_max"]
            ),
            "role": "preserved trigger for the post-diagnostic numerical amendment",
        },
        "sensitivity_grid": grid_records,
        "preregistration": {
            "path": str(PREREG_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(PREREG_PATH), "status": prereg["status"],
            "parameter_fitting": False, "seed": prereg["random_seed"],
        },
        "numerical_amendment": {
            "path": str(AMENDMENT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(AMENDMENT_PATH), "status": amendment["status"],
            "blind_preregistration": False, "analysis_dt": analysis_dt,
            "physical_parameters_changed": False, "thresholds_changed": False,
        },
        "source_package": {
            "path": str(SOURCE_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(SOURCE_PATH), "status": sources["status"],
            "numeric_rows_consumed": 0, "holdout_consumed": False,
        },
        "core_dependency": {
            "path": str(CORE_VERIFIER_PATH.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_file(CORE_VERIFIER_PATH), "status": core["status"],
            "controlling_blocker": core["controlling_blocker"],
        },
        "outputs": {
            "timeseries_csv": {"path": str(CSV_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(CSV_PATH)},
            "figures": figures, "script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "run_integrity": {
            "unit_lane": "normalized", "random_draws_used": False,
            "field_clipping": False, "parameter_fitting": False,
            "external_numeric_data_used": False, "trace_backreaction": False,
            "post_diagnostic_numerical_amendment": True,
            "amendment_informed_by_initial_ledger_failure": True,
        },
        "interpretation": [
            "Cattaneo is an analytical/numerical control, not a UET derivation.",
            "Phi and R are normalized internal variables, not temperature or heat flux.",
            "The trace-only response never changes C, Phi, or Pi.",
            "The strict physical causal-cone gate fails and blocks physical interpretation.",
            "The locked dt failed the strict per-step ledger threshold; the preserved post-diagnostic refinement passes without changing physics parameters or thresholds.",
            "The refined ledger result is a disclosed numerical repair, not an independent blind confirmation.",
            "The external source package is metadata-only and the 2026 source is an untouched holdout.",
            "Landauer k_B T ln 2 is not used to derive beta or a pilot coefficient.",
        ],
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"], "internal_gate_status": artifact["internal_gate_status"],
        "controlling_blocker": controlling, "failed_gates": failed,
        "artifact": str(ARTIFACT_PATH.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
