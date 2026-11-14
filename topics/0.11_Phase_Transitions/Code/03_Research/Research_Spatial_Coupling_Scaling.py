"""
Wave 5 spatial-coupling scaling verifier for Topic 0.11.

This script is a diagnostic verifier. It does not promote the UET phase-transition
claim. It compares a baseline TDGL lane, the historical local-additive UET lane,
and the opt-in core spatial-coupled candidate lane, then writes a machine-readable
artifact with explicit claim gates.
"""

from __future__ import annotations

import csv
import json
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
    gradient_magnitude_squared,
    information_dynamics_source,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_spatial_coupling_scaling.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_spatial_coupling_scaling_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def laplacian_3d(C: np.ndarray, L: int, dx: float) -> np.ndarray:
    C_3d = C.reshape((L, L, L))
    lap_x = np.roll(C_3d, 1, axis=0) + np.roll(C_3d, -1, axis=0) - 2 * C_3d
    lap_y = np.roll(C_3d, 1, axis=1) + np.roll(C_3d, -1, axis=1) - 2 * C_3d
    lap_z = np.roll(C_3d, 1, axis=2) + np.roll(C_3d, -1, axis=2) - 2 * C_3d
    return (lap_x + lap_y + lap_z).reshape(-1) / dx**2


def fit_beta(rows: list[dict[str, float]], value_key: str) -> dict[str, float]:
    delta_t = np.array([row["Delta_T"] for row in rows], dtype=float)
    order = np.array([max(row[value_key], 1e-12) for row in rows], dtype=float)
    fit = linregress(np.log(delta_t), np.log(order))
    return {
        "beta": float(fit.slope),
        "intercept": float(fit.intercept),
        "r_squared": float(fit.rvalue**2),
        "p_value": float(fit.pvalue),
        "stderr": float(fit.stderr),
    }


def build_spatial_operator_gate(params: UETParameters, dx: float) -> dict[str, Any]:
    uniform = np.ones(32)
    interface = np.concatenate([np.zeros(16), np.ones(16)])
    two_d = np.zeros((8, 8))
    two_d[:, 4:] = 1.0
    info = np.ones_like(uniform)

    uniform_game = game_theory_force(
        uniform,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=dx,
        params=params,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
    )
    interface_game = game_theory_force(
        interface,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=dx,
        params=params,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
    )
    two_d_game = game_theory_force(
        two_d,
        density=params.SIGMA_CRIT,
        scale=1.0,
        dx=dx,
        params=params,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
    )
    zero_mass_source = information_dynamics_source(
        np.zeros_like(uniform), info, params, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE
    )
    zero_info_source = information_dynamics_source(
        uniform, np.zeros_like(uniform), params, operator_mode=SPATIAL_COUPLED_OPERATOR_MODE
    )

    uniform_game_norm = float(np.linalg.norm(uniform_game))
    interface_game_norm = float(np.linalg.norm(interface_game))
    zero_mass_info_source_norm = float(np.linalg.norm(zero_mass_source))
    zero_info_source_norm = float(np.linalg.norm(zero_info_source))
    two_d_shape_ok = getattr(two_d_game, "shape", None) == two_d.shape

    passed = (
        uniform_game_norm <= 1e-12
        and interface_game_norm > 1e-9
        and zero_mass_info_source_norm <= 1e-12
        and zero_info_source_norm <= 1e-12
        and two_d_shape_ok
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "blocker_label": "spatially_blind_engine_operator" if not passed else "none",
        "uniform_game_force_norm": uniform_game_norm,
        "interface_game_force_norm": interface_game_norm,
        "zero_mass_info_source_norm": zero_mass_info_source_norm,
        "zero_info_source_norm": zero_info_source_norm,
        "two_d_shape_ok": two_d_shape_ok,
        "operator_role": "candidate heuristic bridge",
    }


def run_scaling_analysis() -> dict[str, Any]:
    L = 16
    N = L**3
    dx = 1.0
    dt = 0.02
    steps = 800
    b = 1.0
    kappa = 1.0
    gamma_mobility = 0.1
    T_c = 1.0
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
    for index, T in enumerate(temperatures):
        a_T = (T - T_c) / T_c
        eq_val = np.sqrt(max(0.0, -a_T / b))
        init_rng = np.random.default_rng(4200 + index)
        C_init = init_rng.normal(eq_val, 0.1, N)
        C_base = C_init.copy()
        C_legacy = C_init.copy()
        C_spatial = C_init.copy()

        base_rng = np.random.default_rng(5200 + index)
        legacy_rng = np.random.default_rng(6200 + index)
        spatial_rng = np.random.default_rng(7200 + index)

        for _ in range(steps):
            lap_base = laplacian_3d(C_base, L, dx)
            dF_base = a_T * C_base + b * C_base**3 - kappa * lap_base
            noise_base = thermal_noise_strength * np.sqrt(T) * base_rng.normal(0, 1, N)
            C_base += -gamma_mobility * dF_base * dt + noise_base * np.sqrt(dt)

            lap_legacy = laplacian_3d(C_legacy, L, dx)
            dF_legacy = a_T * C_legacy + b * C_legacy**3 - kappa * lap_legacy
            noise_legacy = thermal_noise_strength * np.sqrt(T) * legacy_rng.normal(0, 1, N)
            phi_legacy = gamma_n * phi_noise * legacy_rng.normal(0, 1, N) * (1 - C_legacy**2)
            info_field_legacy = -phi_legacy / max(legacy_params.beta, 1e-12)
            legacy_info = information_dynamics_source(
                C_legacy, info_field_legacy, legacy_params, operator_mode=LEGACY_OPERATOR_MODE
            )
            payoff_legacy = -(0.5 * a_T * C_legacy**2 + 0.25 * b * C_legacy**4)
            legacy_game = mu_g * C_legacy * (payoff_legacy - np.mean(payoff_legacy)) * eta_u
            C_legacy += (-gamma_mobility * dF_legacy + legacy_info + legacy_game) * dt + noise_legacy * np.sqrt(dt)

            lap_spatial = laplacian_3d(C_spatial, L, dx)
            dF_spatial = a_T * C_spatial + b * C_spatial**3 - kappa * lap_spatial
            noise_spatial = thermal_noise_strength * np.sqrt(T) * spatial_rng.normal(0, 1, N)
            info_field_spatial = phi_noise * spatial_rng.normal(0, 1, N)
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
            C_spatial += (-gamma_mobility * dF_spatial + spatial_info + spatial_game) * dt + noise_spatial * np.sqrt(dt)

        rows.append(
            {
                "T": float(T),
                "Delta_T": float(T_c - T),
                "Order_Base": float(np.mean(np.abs(C_base))),
                "Var_Base": float(np.var(C_base) * N),
                "Order_Legacy_UET": float(np.mean(np.abs(C_legacy))),
                "Var_Legacy_UET": float(np.var(C_legacy) * N),
                "Order_Spatial_UET": float(np.mean(np.abs(C_spatial))),
                "Var_Spatial_UET": float(np.var(C_spatial) * N),
                "Spatial_Grad2_Mean": float(np.mean(gradient_magnitude_squared(C_spatial, dx))),
            }
        )

    fits = {
        "baseline_tdgl": fit_beta(rows, "Order_Base"),
        "legacy_local_uet": fit_beta(rows, "Order_Legacy_UET"),
        "spatial_coupled_v1": fit_beta(rows, "Order_Spatial_UET"),
    }

    beta_mean_field = 0.5
    beta_ising = 0.3265
    spatial_beta = fits["spatial_coupled_v1"]["beta"]
    legacy_beta = fits["legacy_local_uet"]["beta"]
    tolerance = 0.08
    shifted_toward_ising = (
        abs(spatial_beta - beta_ising) <= tolerance
        and abs(spatial_beta - beta_mean_field) > tolerance
        and spatial_beta < legacy_beta - 0.05
    )

    engine_alignment_gate = {
        "status": "PASS",
        "core_engine_path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "core_engine_sha256": hash_file(CORE_ENGINE_PATH),
        "core_functions_used": [
            "information_dynamics_source",
            "game_theory_force",
            "gradient_magnitude_squared",
        ],
        "claim_boundary": "The spatial candidate uses core operator helpers; the legacy comparison lane preserves the historical local-additive diagnostic shape.",
    }
    spatial_operator_gate = build_spatial_operator_gate(spatial_params, dx)
    universality_shift_gate = {
        "status": "PASS" if shifted_toward_ising else "BLOCKED",
        "beta_mean_field_reference": beta_mean_field,
        "beta_3d_ising_reference": beta_ising,
        "tolerance_to_ising": tolerance,
        "legacy_beta": legacy_beta,
        "spatial_beta": spatial_beta,
        "spatial_minus_ising_abs": float(abs(spatial_beta - beta_ising)),
        "spatial_minus_mean_field_abs": float(abs(spatial_beta - beta_mean_field)),
        "required_condition": "spatial beta within tolerance of 3D Ising, away from mean-field, and at least 0.05 below legacy beta",
        "claim_boundary": "A blocked gate means the candidate remains a mechanism diagnostic and does not establish a universality-class shift.",
    }

    gate_statuses = [
        engine_alignment_gate["status"],
        spatial_operator_gate["status"],
        universality_shift_gate["status"],
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
        "wave": "Wave 5 spatial-coupling candidate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupling_Scaling.py",
        "status": overall_status,
        "blocker_label": "spatially_blind_engine_operator",
        "operator_mode_default": LEGACY_OPERATOR_MODE,
        "candidate_operator_mode": SPATIAL_COUPLED_OPERATOR_MODE,
        "claim_class": "diagnostic_candidate_only",
        "inputs": [
            {
                "path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(CORE_ENGINE_PATH),
                "role": "core candidate operator implementation",
            }
        ],
        "parameters": {
            "grid_L": L,
            "grid_points": N,
            "steps": steps,
            "dt": dt,
            "dx": dx,
            "temperature_points": [float(T) for T in temperatures],
            "spatial_candidate_coefficients": {
                "beta": spatial_params.beta,
                "spatial_information_coupling": spatial_params.spatial_information_coupling,
                "spatial_game_coupling": spatial_params.spatial_game_coupling,
                "spatial_kpz_coupling": spatial_params.spatial_kpz_coupling,
            },
        },
        "metrics": {
            "beta_estimates": fits,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "engine_alignment_gate": engine_alignment_gate,
            "spatial_operator_gate": spatial_operator_gate,
            "universality_shift_gate": universality_shift_gate,
        },
        "limitations": [
            "This verifier is diagnostic and synthetic; it is not a material-data validation.",
            "The spatial-coupled operator is a heuristic bridge until unit closure and derivation are documented.",
            "A PASS in the selected beta JSON artifact is still separate from this dynamics-scaling artifact.",
        ],
        "claim_boundary": "Do not claim UET escaped mean-field unless universality_shift_gate is PASS and the formula audit is upgraded accordingly.",
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
    result = run_scaling_analysis()
    print(json.dumps({"status": result["status"], "artifact": str(ARTIFACT_PATH)}, indent=2))
