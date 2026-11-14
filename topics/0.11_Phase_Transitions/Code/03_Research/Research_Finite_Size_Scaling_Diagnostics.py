"""
Wave 8 finite-size scaling readiness diagnostic.

This diagnostic checks whether the current synthetic phase-transition window
contains enough finite-size/correlation structure to support universality
claims. It compares baseline TDGL and the opt-in spatial-coupled UET candidate
across several grid sizes, then records xi/L and Binder-style proxy gates.

It is diagnostic only. It does not promote the phase-transition claim.
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
from scipy.stats import linregress


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
    game_theory_force,
    information_dynamics_source,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_finite_size_scaling_diagnostics.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_finite_size_scaling_diagnostics_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"


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

    max_r = L // 2
    axis_corr = []
    for r in range(max_r + 1):
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
    return max_r * dx


def binder_proxy(C: np.ndarray) -> float:
    second = float(np.mean(C**2))
    fourth = float(np.mean(C**4))
    if second <= 1e-14:
        return 0.0
    return float(1.0 - fourth / (3.0 * second**2))


def fit_exponent(rows: list[dict[str, float]], key: str, sign: float = 1.0) -> dict[str, float]:
    delta_t = np.array([row["delta_t"] for row in rows], dtype=float)
    values = np.array([max(row[key], 1e-12) for row in rows], dtype=float)
    fit = linregress(np.log(delta_t), np.log(values))
    return {
        "exponent": float(sign * fit.slope),
        "slope": float(fit.slope),
        "stderr": float(fit.stderr),
        "r_squared": float(fit.rvalue**2),
        "p_value": float(fit.pvalue),
    }


def run_single_lane(
    *,
    lane: str,
    L: int,
    temperature: float,
    temp_index: int,
    grid_index: int,
    steps: int,
    dt: float,
    dx: float,
) -> dict[str, float]:
    grid_points = L**3
    b = 1.0
    kappa = 1.0
    gamma_mobility = 0.1
    critical_temperature = 1.0
    thermal_noise_strength = 0.05
    phi_noise = 0.05

    a_t = (temperature - critical_temperature) / critical_temperature
    eq_val = math.sqrt(max(0.0, -a_t / b))
    init_rng = np.random.default_rng(13000 + 1000 * grid_index + temp_index)
    step_rng = np.random.default_rng(14000 + 1000 * grid_index + 100 * temp_index + (0 if lane == "baseline_tdgl" else 1))
    C = init_rng.normal(eq_val, 0.1, grid_points)

    params = UETParameters(
        beta=0.05,
        kappa=kappa,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
        spatial_information_coupling=0.5,
        spatial_game_coupling=0.01,
        spatial_kpz_coupling=0.25,
    )

    for _ in range(steps):
        lap = laplacian_3d(C, L, dx)
        dF = a_t * C + b * C**3 - kappa * lap
        noise = thermal_noise_strength * math.sqrt(float(temperature)) * step_rng.normal(0, 1, grid_points)
        force = -gamma_mobility * dF

        if lane == "spatial_coupled_v1":
            info_field = phi_noise * step_rng.normal(0, 1, grid_points)
            force += information_dynamics_source(
                C,
                info_field,
                params,
                operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
            )
            force += game_theory_force(
                C,
                density=params.SIGMA_CRIT,
                scale=1.0,
                dx=dx,
                params=params,
                operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
            )

        C = C + force * dt + noise * math.sqrt(dt)

    xi = axis_correlation_length_proxy(C, L, dx)
    return {
        "lane": lane,
        "grid_L": float(L),
        "grid_points": float(grid_points),
        "temperature": float(temperature),
        "delta_t": float(critical_temperature - temperature),
        "steps": float(steps),
        "order_parameter": float(np.mean(np.abs(C))),
        "xi_proxy": float(xi),
        "xi_over_L": float(xi / L),
        "susceptibility_proxy": float(np.var(C) * grid_points),
        "binder_proxy": binder_proxy(C),
    }


def run_finite_size_diagnostic() -> dict[str, Any]:
    grid_sizes = [8, 12, 16]
    temperatures = np.array([0.90, 0.94, 0.97, 0.985])
    steps_by_grid = {8: 450, 12: 550, 16: 700}
    dt = 0.02
    dx = 1.0

    rows: list[dict[str, float]] = []
    for grid_index, L in enumerate(grid_sizes):
        for temp_index, temperature in enumerate(temperatures):
            for lane in ["baseline_tdgl", "spatial_coupled_v1"]:
                rows.append(
                    run_single_lane(
                        lane=lane,
                        L=L,
                        temperature=float(temperature),
                        temp_index=temp_index,
                        grid_index=grid_index,
                        steps=steps_by_grid[L],
                        dt=dt,
                        dx=dx,
                    )
                )

    by_lane_grid: dict[str, dict[str, Any]] = {}
    for lane in ["baseline_tdgl", "spatial_coupled_v1"]:
        by_lane_grid[lane] = {}
        for L in grid_sizes:
            subset = [row for row in rows if row["lane"] == lane and int(row["grid_L"]) == L]
            by_lane_grid[lane][str(L)] = {
                "beta": fit_exponent(subset, "order_parameter", sign=1.0),
                "nu_proxy": fit_exponent(subset, "xi_proxy", sign=-1.0),
                "xi_near_over_far": float(subset[-1]["xi_proxy"] / max(subset[0]["xi_proxy"], 1e-12)),
                "xi_over_L_near": float(subset[-1]["xi_over_L"]),
                "binder_near": float(subset[-1]["binder_proxy"]),
            }

    near_rows_spatial = [
        row for row in rows if row["lane"] == "spatial_coupled_v1" and row["temperature"] == float(temperatures[-1])
    ]
    near_rows_baseline = [
        row for row in rows if row["lane"] == "baseline_tdgl" and row["temperature"] == float(temperatures[-1])
    ]
    spatial_xi_over_l = [row["xi_over_L"] for row in near_rows_spatial]
    baseline_xi_over_l = [row["xi_over_L"] for row in near_rows_baseline]

    binder_spreads = {}
    for temperature in temperatures:
        temp_rows = [
            row
            for row in rows
            if row["lane"] == "spatial_coupled_v1" and row["temperature"] == float(temperature)
        ]
        binders = [row["binder_proxy"] for row in temp_rows]
        binder_spreads[f"{temperature:.3f}"] = float(max(binders) - min(binders))
    best_binder_spread = float(min(binder_spreads.values()))

    finite_size_coverage_gate = {
        "status": "PASS" if len(grid_sizes) >= 3 and len(temperatures) >= 4 else "FAIL",
        "grid_sizes": grid_sizes,
        "temperature_points": [float(value) for value in temperatures],
        "required_condition": "at least three grid sizes and four temperatures for a diagnostic finite-size sweep",
    }
    correlation_window_gate = {
        "status": "PASS" if max(spatial_xi_over_l) >= 0.20 and max(spatial_xi_over_l) < 0.80 else "BLOCKED",
        "spatial_xi_over_L_near_values": spatial_xi_over_l,
        "baseline_xi_over_L_near_values": baseline_xi_over_l,
        "max_spatial_xi_over_L_near": float(max(spatial_xi_over_l)),
        "required_condition": "near-critical xi/L must be large enough to show finite-size effects without saturating the grid",
        "claim_boundary": "A blocked gate means the current finite-size window is not adequate for universality claims.",
    }
    binder_crossing_gate = {
        "status": "PASS" if best_binder_spread <= 0.05 else "BLOCKED",
        "binder_spread_by_temperature": binder_spreads,
        "best_binder_spread": best_binder_spread,
        "required_condition": "Binder-style proxy curves should show a crossing-like spread <= 0.05",
    }
    operator_separation_gate = {
        "status": "PASS"
        if abs(max(spatial_xi_over_l) - max(baseline_xi_over_l)) >= 0.05
        else "BLOCKED",
        "max_spatial_xi_over_L_near": float(max(spatial_xi_over_l)),
        "max_baseline_xi_over_L_near": float(max(baseline_xi_over_l)),
        "required_condition": "spatial candidate must separate from baseline in near-critical xi/L",
    }
    overall_status = (
        "PASS"
        if all(
            gate["status"] == "PASS"
            for gate in [
                finite_size_coverage_gate,
                correlation_window_gate,
                binder_crossing_gate,
                operator_separation_gate,
            ]
        )
        else "WARN"
    )

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 8 finite-size scaling readiness diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Finite_Size_Scaling_Diagnostics.py",
        "status": overall_status,
        "blocker_label": "finite_size_scaling_window_not_established",
        "claim_class": "diagnostic_finite_size_only",
        "inputs": [
            {
                "path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(CORE_ENGINE_PATH),
                "role": "core candidate operator implementation",
            }
        ],
        "parameters": {
            "grid_sizes": grid_sizes,
            "steps_by_grid": steps_by_grid,
            "dt": dt,
            "dx": dx,
            "temperature_points": [float(value) for value in temperatures],
        },
        "metrics": {
            "by_lane_grid": by_lane_grid,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "finite_size_coverage_gate": finite_size_coverage_gate,
            "correlation_window_gate": correlation_window_gate,
            "binder_crossing_gate": binder_crossing_gate,
            "operator_separation_gate": operator_separation_gate,
        },
        "limitations": [
            "Binder and xi/L values are diagnostic proxies from one deterministic run per grid/temperature.",
            "A blocked finite-size gate means stronger universality claims require a dedicated finite-size scaling design.",
            "This artifact does not replace material-data validation or RG derivation.",
        ],
        "claim_boundary": "Do not claim a universality shift until finite-size, correlation-length, and operator-separation gates pass together.",
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
    result = run_finite_size_diagnostic()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
            },
            indent=2,
        )
    )
