"""
Wave 7 correlation-length and estimator adequacy diagnostic.

This script asks a narrower question than the Wave 5 scaling verifier:
does the current synthetic dynamics window show enough correlation-length
structure to support a universality claim, and does the spatial-coupled
candidate separate from the baseline beyond a mean-field order-parameter fit?

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
    LEGACY_OPERATOR_MODE,
    SPATIAL_COUPLED_OPERATOR_MODE,
    game_theory_force,
    information_dynamics_source,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_correlation_length_diagnostics.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_correlation_length_diagnostics_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def laplacian_3d(C: np.ndarray, L: int, dx: float) -> np.ndarray:
    C_3d = C.reshape((L, L, L))
    lap = (
        np.roll(C_3d, 1, axis=0)
        + np.roll(C_3d, -1, axis=0)
        + np.roll(C_3d, 1, axis=1)
        + np.roll(C_3d, -1, axis=1)
        + np.roll(C_3d, 1, axis=2)
        + np.roll(C_3d, -1, axis=2)
        - 6 * C_3d
    )
    return lap.reshape(-1) / dx**2


def axis_correlation_length_proxy(C: np.ndarray, L: int, dx: float) -> float:
    """Estimate a connected correlation-length proxy from axis autocorrelation."""
    field = C.reshape((L, L, L)).astype(float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return 0.0

    spectrum = np.fft.fftn(centered)
    autocorr = np.fft.ifftn(np.abs(spectrum) ** 2).real / centered.size
    autocorr = autocorr / max(float(autocorr[0, 0, 0]), 1e-14)

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

    threshold = math.exp(-1.0)
    for r in range(1, len(axis_corr)):
        if axis_corr[r] <= threshold:
            prev_corr = axis_corr[r - 1]
            curr_corr = axis_corr[r]
            if abs(prev_corr - curr_corr) <= 1e-12:
                return r * dx
            frac = (prev_corr - threshold) / (prev_corr - curr_corr)
            return ((r - 1) + max(0.0, min(1.0, frac))) * dx
    return max_r * dx


def fit_power(rows: list[dict[str, float]], value_key: str, exponent_sign: float = 1.0) -> dict[str, float]:
    delta_t = np.array([row["delta_t"] for row in rows], dtype=float)
    values = np.array([max(row[value_key], 1e-12) for row in rows], dtype=float)
    fit = linregress(np.log(delta_t), np.log(values))
    return {
        "exponent": float(exponent_sign * fit.slope),
        "slope": float(fit.slope),
        "intercept": float(fit.intercept),
        "r_squared": float(fit.rvalue**2),
        "stderr": float(fit.stderr),
        "p_value": float(fit.pvalue),
    }


def run_dynamics() -> dict[str, Any]:
    grid_L = 16
    grid_points = grid_L**3
    dx = 1.0
    dt = 0.02
    steps = 800
    b = 1.0
    kappa = 1.0
    gamma_mobility = 0.1
    critical_temperature = 1.0
    thermal_noise_strength = 0.05
    phi_noise = 0.05
    gamma_n = 0.1
    mu_g = 0.05
    eta_u = 0.5
    temperatures = np.linspace(0.80, 0.98, 8)

    legacy_params = UETParameters(
        beta=0.05,
        kappa=kappa,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=LEGACY_OPERATOR_MODE,
    )
    spatial_params = UETParameters(
        beta=0.05,
        kappa=kappa,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
        spatial_information_coupling=0.5,
        spatial_game_coupling=0.01,
        spatial_kpz_coupling=0.25,
    )

    rows: list[dict[str, float]] = []
    for index, temperature in enumerate(temperatures):
        a_t = (temperature - critical_temperature) / critical_temperature
        eq_val = math.sqrt(max(0.0, -a_t / b))
        init_rng = np.random.default_rng(4200 + index)
        C_init = init_rng.normal(eq_val, 0.1, grid_points)
        C_base = C_init.copy()
        C_legacy = C_init.copy()
        C_spatial = C_init.copy()

        base_rng = np.random.default_rng(5200 + index)
        legacy_rng = np.random.default_rng(6200 + index)
        spatial_rng = np.random.default_rng(7200 + index)

        for _ in range(steps):
            lap_base = laplacian_3d(C_base, grid_L, dx)
            dF_base = a_t * C_base + b * C_base**3 - kappa * lap_base
            noise_base = thermal_noise_strength * math.sqrt(float(temperature)) * base_rng.normal(
                0, 1, grid_points
            )
            C_base += -gamma_mobility * dF_base * dt + noise_base * math.sqrt(dt)

            lap_legacy = laplacian_3d(C_legacy, grid_L, dx)
            dF_legacy = a_t * C_legacy + b * C_legacy**3 - kappa * lap_legacy
            noise_legacy = thermal_noise_strength * math.sqrt(float(temperature)) * legacy_rng.normal(
                0, 1, grid_points
            )
            phi_legacy = gamma_n * phi_noise * legacy_rng.normal(0, 1, grid_points) * (1 - C_legacy**2)
            info_field_legacy = -phi_legacy / max(legacy_params.beta, 1e-12)
            legacy_info = information_dynamics_source(
                C_legacy,
                info_field_legacy,
                legacy_params,
                operator_mode=LEGACY_OPERATOR_MODE,
            )
            payoff_legacy = -(0.5 * a_t * C_legacy**2 + 0.25 * b * C_legacy**4)
            legacy_game = mu_g * C_legacy * (payoff_legacy - np.mean(payoff_legacy)) * eta_u
            C_legacy += (-gamma_mobility * dF_legacy + legacy_info + legacy_game) * dt + noise_legacy * math.sqrt(dt)

            lap_spatial = laplacian_3d(C_spatial, grid_L, dx)
            dF_spatial = a_t * C_spatial + b * C_spatial**3 - kappa * lap_spatial
            noise_spatial = thermal_noise_strength * math.sqrt(float(temperature)) * spatial_rng.normal(
                0, 1, grid_points
            )
            info_field_spatial = phi_noise * spatial_rng.normal(0, 1, grid_points)
            spatial_info = information_dynamics_source(
                C_spatial,
                info_field_spatial,
                spatial_params,
                operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
            )
            spatial_game = game_theory_force(
                C_spatial,
                density=spatial_params.SIGMA_CRIT,
                scale=1.0,
                dx=dx,
                params=spatial_params,
                operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
            )
            C_spatial += (-gamma_mobility * dF_spatial + spatial_info + spatial_game) * dt + noise_spatial * math.sqrt(dt)

        rows.append(
            {
                "temperature": float(temperature),
                "delta_t": float(critical_temperature - temperature),
                "order_baseline": float(np.mean(np.abs(C_base))),
                "order_legacy": float(np.mean(np.abs(C_legacy))),
                "order_spatial": float(np.mean(np.abs(C_spatial))),
                "xi_baseline": axis_correlation_length_proxy(C_base, grid_L, dx),
                "xi_legacy": axis_correlation_length_proxy(C_legacy, grid_L, dx),
                "xi_spatial": axis_correlation_length_proxy(C_spatial, grid_L, dx),
                "susceptibility_baseline": float(np.var(C_base) * grid_points),
                "susceptibility_legacy": float(np.var(C_legacy) * grid_points),
                "susceptibility_spatial": float(np.var(C_spatial) * grid_points),
            }
        )

    fits = {}
    for lane, order_key, xi_key in [
        ("baseline_tdgl", "order_baseline", "xi_baseline"),
        ("legacy_local_uet", "order_legacy", "xi_legacy"),
        ("spatial_coupled_v1", "order_spatial", "xi_spatial"),
    ]:
        lane_rows = rows
        fits[lane] = {
            "beta": fit_power(lane_rows, order_key, exponent_sign=1.0),
            "nu_proxy": fit_power(lane_rows, xi_key, exponent_sign=-1.0),
            "xi_ratio_near_over_far": float(lane_rows[-1][xi_key] / max(lane_rows[0][xi_key], 1e-12)),
        }

    beta_ising = 0.3265
    nu_ising = 0.630
    spatial_beta = fits["spatial_coupled_v1"]["beta"]["exponent"]
    spatial_nu = fits["spatial_coupled_v1"]["nu_proxy"]["exponent"]
    baseline_nu = fits["baseline_tdgl"]["nu_proxy"]["exponent"]
    spatial_xi_ratio = fits["spatial_coupled_v1"]["xi_ratio_near_over_far"]

    critical_window_gate = {
        "status": "PASS" if spatial_xi_ratio >= 1.5 and spatial_nu > 0 else "BLOCKED",
        "spatial_xi_ratio_near_over_far": spatial_xi_ratio,
        "spatial_nu_proxy": spatial_nu,
        "baseline_nu_proxy": baseline_nu,
        "required_condition": "spatial xi proxy grows toward Tc with xi_near/xi_far >= 1.5 and positive nu proxy",
        "claim_boundary": "A blocked gate means the current temperature/window/estimator does not expose critical correlation growth.",
    }
    estimator_adequacy_gate = {
        "status": "PASS"
        if critical_window_gate["status"] == "PASS"
        and abs(spatial_nu - nu_ising) <= 0.25
        and fits["spatial_coupled_v1"]["nu_proxy"]["r_squared"] >= 0.6
        else "BLOCKED",
        "nu_3d_ising_reference": nu_ising,
        "spatial_nu_proxy": spatial_nu,
        "spatial_nu_r_squared": fits["spatial_coupled_v1"]["nu_proxy"]["r_squared"],
        "required_condition": "correlation-length proxy must be monotonic enough and near the 3D Ising nu benchmark before beta claims are promoted",
    }
    operator_separation_gate = {
        "status": "PASS"
        if abs(spatial_beta - beta_ising) <= 0.08
        and abs(spatial_nu - baseline_nu) >= 0.1
        else "BLOCKED",
        "spatial_beta": spatial_beta,
        "beta_3d_ising_reference": beta_ising,
        "spatial_minus_ising_abs": float(abs(spatial_beta - beta_ising)),
        "spatial_nu_minus_baseline_nu_abs": float(abs(spatial_nu - baseline_nu)),
        "required_condition": "spatial lane must shift beta toward 3D Ising and separate its xi proxy from baseline",
    }

    gate_statuses = [
        critical_window_gate["status"],
        estimator_adequacy_gate["status"],
        operator_separation_gate["status"],
    ]
    overall_status = "PASS" if all(status == "PASS" for status in gate_statuses) else "WARN"

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 7 correlation-length estimator diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Correlation_Length_Diagnostics.py",
        "status": overall_status,
        "blocker_label": "critical_window_or_operator_form_not_resolved",
        "claim_class": "diagnostic_estimator_only",
        "inputs": [
            {
                "path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(CORE_ENGINE_PATH),
                "role": "core candidate operator implementation",
            }
        ],
        "parameters": {
            "grid_L": grid_L,
            "grid_points": grid_points,
            "steps": steps,
            "dt": dt,
            "dx": dx,
            "temperature_points": [float(value) for value in temperatures],
            "beta_3d_ising_reference": beta_ising,
            "nu_3d_ising_reference": nu_ising,
        },
        "metrics": {
            "fits": fits,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "critical_window_gate": critical_window_gate,
            "estimator_adequacy_gate": estimator_adequacy_gate,
            "operator_separation_gate": operator_separation_gate,
        },
        "limitations": [
            "The correlation-length estimate is a connected autocorrelation proxy, not a full finite-size scaling analysis.",
            "A blocked gate should trigger estimator/operator redesign, not stronger claims.",
            "This artifact does not replace source-locked material critical-point validation.",
        ],
        "claim_boundary": "Do not claim a universality shift until beta and correlation-length diagnostics both pass declared gates.",
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
    result = run_dynamics()
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
