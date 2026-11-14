"""
Wave 11 spatial_coupled_v2 diagnostic.

Wave 10 required the next candidate to be opt-in, core-engine exposed, and more
than coefficient-only tuning. This diagnostic tests the first v2 candidate:
screened nonlocal space-memory contrast plus a conserved interface/game drive.

The output is diagnostic only. It does not validate a universality-class shift.
"""

from __future__ import annotations

import csv
import json
import math
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET docs root not found")


ROOT = _bootstrap()

from docs.core.uet_master_equation import (  # noqa: E402
    SPATIAL_COUPLED_OPERATOR_MODE,
    SPATIAL_COUPLED_V2_OPERATOR_MODE,
    SUPPORTED_OPERATOR_MODES,
    game_theory_force,
    information_dynamics_source,
    spatial_interface_activity,
    spatial_memory_contrast,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_spatial_coupled_v2_diagnostic.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_spatial_coupled_v2_diagnostic_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
PARAMS_PATH = ROOT / "docs" / "core" / "uet_parameters.py"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def laplacian_3d(C: np.ndarray, L: int, dx: float) -> np.ndarray:
    field = C.reshape((L, L, L))
    lap = (
        np.roll(field, 1, axis=0)
        + np.roll(field, -1, axis=0)
        + np.roll(field, 1, axis=1)
        + np.roll(field, -1, axis=1)
        + np.roll(field, 1, axis=2)
        + np.roll(field, -1, axis=2)
        - 6 * field
    )
    return lap.reshape(-1) / dx**2


def axis_correlation_length_proxy(C: np.ndarray, L: int, dx: float) -> float:
    field = C.reshape((L, L, L)).astype(float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return 0.0

    spectrum = np.fft.fftn(centered)
    autocorr = np.fft.ifftn(np.abs(spectrum) ** 2).real / centered.size
    autocorr = autocorr / max(float(autocorr[0, 0, 0]), 1e-14)
    threshold = math.exp(-1.0)

    axis_corr = []
    for r in range(L // 2 + 1):
        axis_corr.append(
            float(
                np.mean(
                    [
                        autocorr[r, 0, 0],
                        autocorr[0, r, 0],
                        autocorr[0, 0, r],
                    ]
                )
            )
        )

    for r in range(1, len(axis_corr)):
        if axis_corr[r] <= threshold:
            prev_corr = axis_corr[r - 1]
            curr_corr = axis_corr[r]
            if abs(prev_corr - curr_corr) <= 1e-12:
                return r * dx
            frac = (prev_corr - threshold) / (prev_corr - curr_corr)
            return ((r - 1) + max(0.0, min(1.0, frac))) * dx
    return (L // 2) * dx


def fit_power_law(rows: list[dict[str, float]], value_key: str) -> dict[str, float | str]:
    usable = [
        row
        for row in rows
        if row["delta_t"] > 0 and row[value_key] > 0 and np.isfinite(row[value_key])
    ]
    if len(usable) < 3:
        return {"status": "INSUFFICIENT_POINTS"}

    x = np.log([row["delta_t"] for row in usable])
    y = np.log([row[value_key] for row in usable])
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    residual = y - prediction
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    stderr = math.sqrt(ss_res / max(1, len(x) - 2)) / math.sqrt(float(np.sum((x - np.mean(x)) ** 2)))
    return {
        "status": "OK",
        "exponent": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_squared),
        "stderr": float(stderr),
    }


def params_for_mode(mode: str) -> UETParameters:
    return UETParameters(
        beta=0.05,
        kappa=1.0,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=mode,
        spatial_information_coupling=0.5,
        spatial_game_coupling=0.01,
        spatial_kpz_coupling=0.25,
        spatial_v2_information_coupling=0.5,
        spatial_v2_game_coupling=0.02,
        spatial_v2_nonlocal_coupling=0.5,
        spatial_v2_memory_length=2.0,
        spatial_v2_conserved_coupling=0.05,
    )


def run_lane(
    *,
    lane: str,
    L: int,
    temperature: float,
    steps: int,
    temp_index: int,
    dx: float,
    dt: float,
) -> dict[str, float | str]:
    grid_points = L**3
    critical_temperature = 1.0
    b = 1.0
    kappa = 1.0
    gamma_mobility = 0.1
    thermal_noise_strength = 0.05
    phi_noise = 0.05

    a_t = (temperature - critical_temperature) / critical_temperature
    eq_val = math.sqrt(max(0.0, -a_t / b))
    init_rng = np.random.default_rng(31000 + temp_index)
    step_rng = np.random.default_rng(32000 + 10 * temp_index + {"baseline_tdgl": 0, "spatial_coupled_v1": 1, "spatial_coupled_v2": 2}[lane])
    C = init_rng.normal(eq_val, 0.1, grid_points)

    operator_mode = None
    params = None
    if lane == "spatial_coupled_v1":
        operator_mode = SPATIAL_COUPLED_OPERATOR_MODE
        params = params_for_mode(operator_mode)
    elif lane == "spatial_coupled_v2":
        operator_mode = SPATIAL_COUPLED_V2_OPERATOR_MODE
        params = params_for_mode(operator_mode)

    status = "OK"
    for _ in range(steps):
        lap = laplacian_3d(C, L, dx)
        dF = a_t * C + b * C**3 - kappa * lap
        noise = thermal_noise_strength * math.sqrt(float(temperature)) * step_rng.normal(0, 1, grid_points)
        force = -gamma_mobility * dF

        if operator_mode is not None and params is not None:
            C_field = C.reshape((L, L, L))
            info_field = phi_noise * step_rng.normal(0, 1, (L, L, L))
            force += information_dynamics_source(
                C_field,
                info_field,
                params,
                operator_mode=operator_mode,
                dx=dx,
            ).reshape(-1)
            force += game_theory_force(
                C_field,
                density=params.SIGMA_CRIT,
                scale=1.0,
                dx=dx,
                params=params,
                operator_mode=operator_mode,
            ).reshape(-1)

        C = C + force * dt + noise * math.sqrt(dt)
        if not np.all(np.isfinite(C)) or float(np.max(np.abs(C))) > 25.0:
            status = "UNSTABLE"
            break

    order_parameter = float(np.mean(np.abs(C))) if np.all(np.isfinite(C)) else float("nan")
    xi_proxy = axis_correlation_length_proxy(C, L, dx) if status == "OK" else float("nan")
    return {
        "lane": lane,
        "status": status,
        "grid_L": float(L),
        "temperature": float(temperature),
        "delta_t": float(critical_temperature - temperature),
        "steps": float(steps),
        "order_parameter": order_parameter,
        "xi_proxy": float(xi_proxy),
        "xi_over_L": float(xi_proxy / L) if status == "OK" else float("nan"),
        "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
    }


def direct_operator_checks() -> dict[str, Any]:
    params = params_for_mode(SPATIAL_COUPLED_V2_OPERATOR_MODE)
    uniform = np.ones((8, 8, 8))
    zero = np.zeros((8, 8, 8))
    interface = np.zeros((8, 8, 8))
    interface[:, :, 4:] = 1.0
    info = np.ones_like(interface)

    uniform_info = information_dynamics_source(
        uniform,
        info,
        params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
        dx=1.0,
    )
    zero_mass_info = information_dynamics_source(
        zero,
        info,
        params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
        dx=1.0,
    )
    zero_info = information_dynamics_source(
        interface,
        np.zeros_like(info),
        params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
        dx=1.0,
    )
    interface_info = information_dynamics_source(
        interface,
        info,
        params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
        dx=1.0,
    )
    uniform_game = game_theory_force(
        uniform,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=1.0,
        params=params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
    )
    interface_game = game_theory_force(
        interface,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=1.0,
        params=params,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
    )

    return {
        "supported_mode": SPATIAL_COUPLED_V2_OPERATOR_MODE in SUPPORTED_OPERATOR_MODES,
        "uniform_info_source_norm": float(np.linalg.norm(uniform_info)),
        "zero_mass_info_source_norm": float(np.linalg.norm(zero_mass_info)),
        "zero_info_source_norm": float(np.linalg.norm(zero_info)),
        "interface_info_source_norm": float(np.linalg.norm(interface_info)),
        "uniform_game_force_norm": float(np.linalg.norm(uniform_game)),
        "interface_game_force_norm": float(np.linalg.norm(interface_game)),
        "interface_game_force_sum": float(np.sum(interface_game)),
        "uniform_memory_contrast_norm": float(np.linalg.norm(spatial_memory_contrast(uniform, 1.0, params))),
        "interface_memory_contrast_norm": float(np.linalg.norm(spatial_memory_contrast(interface, 1.0, params))),
        "interface_activity_norm": float(np.linalg.norm(spatial_interface_activity(interface, 1.0, params))),
    }


def run_v2_diagnostic() -> dict[str, Any]:
    L = 12
    dx = 1.0
    dt = 0.02
    steps = 1200
    temperatures = [0.940, 0.970, 0.985, 0.992]
    lanes = ["baseline_tdgl", "spatial_coupled_v1", "spatial_coupled_v2"]

    rows: list[dict[str, float | str]] = []
    for temp_index, temperature in enumerate(temperatures):
        for lane in lanes:
            rows.append(
                run_lane(
                    lane=lane,
                    L=L,
                    temperature=temperature,
                    steps=steps,
                    temp_index=temp_index,
                    dx=dx,
                    dt=dt,
                )
            )

    by_lane: dict[str, Any] = {}
    for lane in lanes:
        lane_rows = [row for row in rows if row["lane"] == lane]
        stable_rows = [row for row in lane_rows if row["status"] == "OK"]
        by_lane[lane] = {
            "stable_case_count": len(stable_rows),
            "max_xi_over_L": float(max((row["xi_over_L"] for row in stable_rows), default=float("nan"))),
            "near_T_xi_over_L": float(
                [row for row in stable_rows if row["temperature"] == temperatures[-1]][0]["xi_over_L"]
            )
            if any(row["temperature"] == temperatures[-1] for row in stable_rows)
            else float("nan"),
            "max_abs_c": float(max((row["max_abs_c"] for row in stable_rows), default=float("nan"))),
            "beta_fit": fit_power_law(stable_rows, "order_parameter"),
            "nu_proxy_fit": fit_power_law(stable_rows, "xi_proxy"),
        }

    baseline_max_xi = by_lane["baseline_tdgl"]["max_xi_over_L"]
    v1_max_xi = by_lane["spatial_coupled_v1"]["max_xi_over_L"]
    v2_max_xi = by_lane["spatial_coupled_v2"]["max_xi_over_L"]
    v2_minus_baseline = float(v2_max_xi - baseline_max_xi)
    v2_minus_v1 = float(v2_max_xi - v1_max_xi)
    checks = direct_operator_checks()

    v2_core_operator_gate = {
        "status": "PASS" if checks["supported_mode"] else "BLOCKED",
        "required_condition": "spatial_coupled_v2 must be an opt-in supported core operator mode",
        "supported_mode": checks["supported_mode"],
    }
    v2_spatial_safety_gate = {
        "status": (
            "PASS"
            if checks["uniform_info_source_norm"] <= 1e-12
            and checks["zero_mass_info_source_norm"] <= 1e-12
            and checks["zero_info_source_norm"] <= 1e-12
            and checks["uniform_game_force_norm"] <= 1e-12
            and checks["interface_info_source_norm"] > 0
            and checks["interface_game_force_norm"] > 0
            and abs(checks["interface_game_force_sum"]) <= 1e-10
            else "BLOCKED"
        ),
        "required_condition": "v2 terms must be zero/reduced on uniform, C=0, and I=0 fields while remaining active and conserved at interfaces",
        **checks,
    }
    v2_stability_gate = {
        "status": "PASS" if by_lane["spatial_coupled_v2"]["stable_case_count"] == len(temperatures) else "BLOCKED",
        "required_condition": "all v2 temperature cases must remain finite under the diagnostic run",
        "stable_case_count": by_lane["spatial_coupled_v2"]["stable_case_count"],
        "expected_case_count": len(temperatures),
        "max_abs_c": by_lane["spatial_coupled_v2"]["max_abs_c"],
    }
    v2_correlation_response_gate = {
        "status": "PASS" if v2_max_xi >= 0.20 else "BLOCKED",
        "required_condition": "v2 should produce connected-correlation growth with xi/L >= 0.20 before stronger finite-size claims",
        "max_v2_xi_over_L": float(v2_max_xi),
        "max_baseline_xi_over_L": float(baseline_max_xi),
        "max_v1_xi_over_L": float(v1_max_xi),
    }
    v2_operator_separation_gate = {
        "status": "PASS" if v2_minus_baseline >= 0.05 and v2_minus_v1 >= 0.02 else "BLOCKED",
        "required_condition": "v2 should separate from baseline by xi/L >= 0.05 and from v1 by xi/L >= 0.02",
        "v2_minus_baseline_xi_over_L": v2_minus_baseline,
        "v2_minus_v1_xi_over_L": v2_minus_v1,
    }

    claim_gates = [v2_correlation_response_gate, v2_operator_separation_gate]
    overall_status = "PASS" if all(gate["status"] == "PASS" for gate in claim_gates) else "WARN"
    blocker_label = (
        "spatial_coupled_v2_requires_full_finite_size_scaling"
        if overall_status == "PASS"
        else "spatial_coupled_v2_correlation_not_yet_established"
    )

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 11 spatial_coupled_v2 diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupled_V2_Diagnostic.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_candidate_only",
        "candidate_operator_mode": SPATIAL_COUPLED_V2_OPERATOR_MODE,
        "inputs": [
            {
                "path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(CORE_ENGINE_PATH),
                "role": "core v2 candidate operator implementation",
            },
            {
                "path": str(PARAMS_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(PARAMS_PATH),
                "role": "candidate coefficient defaults",
            },
        ],
        "parameters": {
            "grid_L": L,
            "grid_points": L**3,
            "dt": dt,
            "dx": dx,
            "steps": steps,
            "temperature_points": temperatures,
            "v2_candidate_coefficients": {
                "spatial_v2_information_coupling": params_for_mode(SPATIAL_COUPLED_V2_OPERATOR_MODE).spatial_v2_information_coupling,
                "spatial_v2_game_coupling": params_for_mode(SPATIAL_COUPLED_V2_OPERATOR_MODE).spatial_v2_game_coupling,
                "spatial_v2_nonlocal_coupling": params_for_mode(SPATIAL_COUPLED_V2_OPERATOR_MODE).spatial_v2_nonlocal_coupling,
                "spatial_v2_memory_length": params_for_mode(SPATIAL_COUPLED_V2_OPERATOR_MODE).spatial_v2_memory_length,
                "spatial_v2_conserved_coupling": params_for_mode(SPATIAL_COUPLED_V2_OPERATOR_MODE).spatial_v2_conserved_coupling,
            },
        },
        "metrics": {
            "by_lane": by_lane,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "v2_core_operator_gate": v2_core_operator_gate,
            "v2_spatial_safety_gate": v2_spatial_safety_gate,
            "v2_stability_gate": v2_stability_gate,
            "v2_correlation_response_gate": v2_correlation_response_gate,
            "v2_operator_separation_gate": v2_operator_separation_gate,
        },
        "limitations": [
            "This is a first candidate diagnostic, not a full finite-size scaling verifier.",
            "The v2 operator uses screened nonlocal memory and a conserved interface drive as a heuristic bridge.",
            "A passing correlation response would still require unit closure, formula audit review, and multi-grid reruns.",
        ],
        "claim_boundary": "Do not claim spatial_coupled_v2 validates UET phase-transition dynamics unless correlation, separation, finite-size, formula-audit, and provenance gates pass together.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy_version": np.__version__,
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_v2_diagnostic()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "blocker_label": result["blocker_label"],
            },
            indent=2,
        )
    )
