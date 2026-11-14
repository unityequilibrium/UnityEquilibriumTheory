"""
Wave 6 spatial-coupling coefficient sensitivity diagnostic.

This script tests whether changing only the opt-in spatial-coupled candidate
coefficients can move the fitted beta exponent away from mean-field behavior.
It is diagnostic only; it does not promote the phase-transition claim.
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
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_spatial_coupling_sensitivity.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_spatial_coupling_sensitivity_stats.csv"
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


def fit_beta(rows: list[dict[str, float]]) -> dict[str, float]:
    delta_t = np.array([row["delta_t"] for row in rows], dtype=float)
    order = np.array([max(row["order_parameter"], 1e-12) for row in rows], dtype=float)
    fit = linregress(np.log(delta_t), np.log(order))
    return {
        "beta": float(fit.slope),
        "intercept": float(fit.intercept),
        "r_squared": float(fit.rvalue**2),
        "p_value": float(fit.pvalue),
        "stderr": float(fit.stderr),
    }


def run_candidate_case(
    *,
    info_coeff: float,
    game_coeff: float,
    kpz_coeff: float,
    case_index: int,
    grid_L: int,
    steps: int,
    dt: float,
    dx: float,
    temperatures: np.ndarray,
) -> dict[str, Any]:
    grid_points = grid_L**3
    b = 1.0
    kappa = 1.0
    gamma_mobility = 0.1
    critical_temperature = 1.0
    thermal_noise_strength = 0.05
    phi_noise = 0.05

    params = UETParameters(
        beta=0.05,
        kappa=kappa,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
        spatial_information_coupling=info_coeff,
        spatial_game_coupling=game_coeff,
        spatial_kpz_coupling=kpz_coeff,
    )

    rows: list[dict[str, float]] = []
    max_abs_c = 0.0
    for temp_index, temperature in enumerate(temperatures):
        a_t = (temperature - critical_temperature) / critical_temperature
        eq_val = math.sqrt(max(0.0, -a_t / b))
        init_rng = np.random.default_rng(9100 + 100 * case_index + temp_index)
        step_rng = np.random.default_rng(10100 + 100 * case_index + temp_index)
        C = init_rng.normal(eq_val, 0.1, grid_points)

        for _ in range(steps):
            laplacian = laplacian_3d(C, grid_L, dx)
            dF = a_t * C + b * C**3 - kappa * laplacian
            noise = thermal_noise_strength * math.sqrt(float(temperature)) * step_rng.normal(
                0, 1, grid_points
            )
            info_field = phi_noise * step_rng.normal(0, 1, grid_points)
            spatial_info = information_dynamics_source(
                C,
                info_field,
                params,
                operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
            )
            spatial_game = game_theory_force(
                C,
                density=params.SIGMA_CRIT,
                scale=1.0,
                dx=dx,
                params=params,
                operator_mode=SPATIAL_COUPLED_OPERATOR_MODE,
            )
            C = C + (-gamma_mobility * dF + spatial_info + spatial_game) * dt + noise * math.sqrt(dt)
            if not np.all(np.isfinite(C)) or float(np.max(np.abs(C))) > 1e4:
                return {
                    "status": "UNSTABLE",
                    "info_coeff": info_coeff,
                    "game_coeff": game_coeff,
                    "kpz_coeff": kpz_coeff,
                    "temperature_failed": float(temperature),
                }

        max_abs_c = max(max_abs_c, float(np.max(np.abs(C))))
        rows.append(
            {
                "temperature": float(temperature),
                "delta_t": float(critical_temperature - temperature),
                "order_parameter": float(np.mean(np.abs(C))),
            }
        )

    fit = fit_beta(rows)
    return {
        "status": "OK",
        "info_coeff": info_coeff,
        "game_coeff": game_coeff,
        "kpz_coeff": kpz_coeff,
        "beta": fit["beta"],
        "stderr": fit["stderr"],
        "r_squared": fit["r_squared"],
        "p_value": fit["p_value"],
        "max_abs_c": max_abs_c,
    }


def run_sensitivity_analysis() -> dict[str, Any]:
    grid_L = 12
    steps = 500
    dt = 0.02
    dx = 1.0
    temperatures = np.linspace(0.80, 0.98, 6)
    beta_mean_field = 0.5
    beta_ising = 0.3265
    tolerance_to_ising = 0.08

    cases = [
        (info_coeff, game_coeff, 0.25)
        for info_coeff in [0.0, 0.5, 2.0, 5.0]
        for game_coeff in [0.0, 0.01, 0.05, 0.2, 1.0]
    ]

    results = [
        run_candidate_case(
            info_coeff=info_coeff,
            game_coeff=game_coeff,
            kpz_coeff=kpz_coeff,
            case_index=index,
            grid_L=grid_L,
            steps=steps,
            dt=dt,
            dx=dx,
            temperatures=temperatures,
        )
        for index, (info_coeff, game_coeff, kpz_coeff) in enumerate(cases)
    ]

    stable_results = [result for result in results if result["status"] == "OK"]
    for result in stable_results:
        result["distance_to_ising"] = float(abs(result["beta"] - beta_ising))
        result["distance_to_mean_field"] = float(abs(result["beta"] - beta_mean_field))

    best_case = min(stable_results, key=lambda item: item["distance_to_ising"]) if stable_results else None
    near_ising_cases = [
        result for result in stable_results if result["distance_to_ising"] <= tolerance_to_ising
    ]
    beta_values = [result["beta"] for result in stable_results]

    coefficient_sensitivity_gate = {
        "status": "PASS" if near_ising_cases else "BLOCKED",
        "stable_case_count": len(stable_results),
        "unstable_case_count": len(results) - len(stable_results),
        "tested_case_count": len(results),
        "best_case": best_case,
        "near_ising_case_count": len(near_ising_cases),
        "beta_min": float(min(beta_values)) if beta_values else None,
        "beta_max": float(max(beta_values)) if beta_values else None,
        "required_condition": "at least one stable coefficient-only case within tolerance of 3D Ising beta",
        "claim_boundary": "A blocked gate means coefficient tuning alone is not evidence for a universality shift.",
    }
    operator_form_revision_gate = {
        "status": "BLOCKED" if not near_ising_cases else "WARN",
        "reason": "The current spatial-coupled operator family remains mean-field-like across the tested coefficient grid.",
        "next_evidence_required": [
            "derive a nonlocal or scale-dependent operator",
            "define a correlation-length-aware estimator",
            "rerun the full Wave 5 scaling verifier with the revised operator",
        ],
    }

    overall_status = (
        "WARN"
        if coefficient_sensitivity_gate["status"] == "BLOCKED"
        or operator_form_revision_gate["status"] == "BLOCKED"
        else "PASS"
    )

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "status",
            "info_coeff",
            "game_coeff",
            "kpz_coeff",
            "beta",
            "stderr",
            "r_squared",
            "p_value",
            "max_abs_c",
            "distance_to_ising",
            "distance_to_mean_field",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 6 spatial-coupling coefficient sensitivity",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupling_Sensitivity.py",
        "status": overall_status,
        "blocker_label": "coefficient_only_spatial_operator_still_mean_field",
        "claim_class": "diagnostic_sensitivity_only",
        "inputs": [
            {
                "path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(CORE_ENGINE_PATH),
                "role": "core candidate operator implementation",
            }
        ],
        "parameters": {
            "grid_L": grid_L,
            "grid_points": grid_L**3,
            "steps": steps,
            "dt": dt,
            "dx": dx,
            "temperature_points": [float(value) for value in temperatures],
            "info_coefficients": [0.0, 0.5, 2.0, 5.0],
            "game_coefficients": [0.0, 0.01, 0.05, 0.2, 1.0],
            "kpz_coefficients": [0.25],
            "beta_mean_field_reference": beta_mean_field,
            "beta_3d_ising_reference": beta_ising,
            "tolerance_to_ising": tolerance_to_ising,
        },
        "metrics": {
            "case_results": results,
            "best_case": best_case,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "coefficient_sensitivity_gate": coefficient_sensitivity_gate,
            "operator_form_revision_gate": operator_form_revision_gate,
        },
        "limitations": [
            "This reduced-grid sensitivity diagnostic is not the publication verifier.",
            "The result tests coefficient-only changes, not new operator derivations.",
            "Passing this diagnostic would still require rerunning the full spatial scaling verifier.",
        ],
        "claim_boundary": "Do not claim UET escaped mean-field from coefficient sweeps; use this artifact only to decide whether the operator family needs revision.",
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
    result = run_sensitivity_analysis()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "best_beta": result["metrics"]["best_case"]["beta"]
                if result["metrics"]["best_case"]
                else None,
            },
            indent=2,
        )
    )
