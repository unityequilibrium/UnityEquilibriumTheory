"""
Wave 9 critical-window and relaxation sensitivity diagnostic.

Wave 8 showed that finite-size coverage and a Binder-style proxy are available,
but xi/L remains too small and the spatial lane does not separate from baseline.
This diagnostic asks whether moving closer to Tc and running longer is enough
to expose correlation growth without changing the operator form.

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
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_critical_window_relaxation_diagnostics.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_critical_window_relaxation_diagnostics_stats.csv"
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


def run_lane(
    *,
    lane: str,
    L: int,
    temperature: float,
    steps: int,
    temp_index: int,
    step_index: int,
    dx: float,
    dt: float,
) -> dict[str, float]:
    grid_points = L**3
    critical_temperature = 1.0
    b = 1.0
    kappa = 1.0
    gamma_mobility = 0.1
    thermal_noise_strength = 0.05
    phi_noise = 0.05

    a_t = (temperature - critical_temperature) / critical_temperature
    eq_val = math.sqrt(max(0.0, -a_t / b))
    init_rng = np.random.default_rng(21000 + temp_index)
    step_rng = np.random.default_rng(22000 + 100 * step_index + 10 * temp_index + (0 if lane == "baseline_tdgl" else 1))
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

    sample_points = {max(1, steps // 2), steps}
    last_order = 0.0
    last_xi = 0.0
    for step in range(1, steps + 1):
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
        if step in sample_points:
            last_order = float(np.mean(np.abs(C)))
            last_xi = axis_correlation_length_proxy(C, L, dx)

    return {
        "lane": lane,
        "grid_L": float(L),
        "temperature": float(temperature),
        "delta_t": float(critical_temperature - temperature),
        "steps": float(steps),
        "order_parameter": last_order,
        "xi_proxy": float(last_xi),
        "xi_over_L": float(last_xi / L),
        "susceptibility_proxy": float(np.var(C) * grid_points),
    }


def run_critical_window_diagnostic() -> dict[str, Any]:
    L = 12
    dx = 1.0
    dt = 0.02
    temperatures = [0.970, 0.985, 0.992, 0.996]
    step_counts = [700, 1400, 2800]

    rows: list[dict[str, float]] = []
    for temp_index, temperature in enumerate(temperatures):
        for step_index, steps in enumerate(step_counts):
            for lane in ["baseline_tdgl", "spatial_coupled_v1"]:
                rows.append(
                    run_lane(
                        lane=lane,
                        L=L,
                        temperature=temperature,
                        steps=steps,
                        temp_index=temp_index,
                        step_index=step_index,
                        dx=dx,
                        dt=dt,
                    )
                )

    def subset(lane: str, steps: int) -> list[dict[str, float]]:
        return [row for row in rows if row["lane"] == lane and int(row["steps"]) == steps]

    max_steps = max(step_counts)
    min_steps = min(step_counts)
    spatial_long = subset("spatial_coupled_v1", max_steps)
    spatial_short = subset("spatial_coupled_v1", min_steps)
    baseline_long = subset("baseline_tdgl", max_steps)

    max_spatial_xi_over_l = max(row["xi_over_L"] for row in spatial_long)
    max_baseline_xi_over_l = max(row["xi_over_L"] for row in baseline_long)
    short_near = [row for row in spatial_short if row["temperature"] == temperatures[-1]][0]
    long_near = [row for row in spatial_long if row["temperature"] == temperatures[-1]][0]
    relaxation_gain_near = float(long_near["xi_over_L"] - short_near["xi_over_L"])

    by_steps: dict[str, Any] = {}
    for steps in step_counts:
        by_steps[str(steps)] = {
            "max_spatial_xi_over_L": float(max(row["xi_over_L"] for row in subset("spatial_coupled_v1", steps))),
            "max_baseline_xi_over_L": float(max(row["xi_over_L"] for row in subset("baseline_tdgl", steps))),
            "near_T_spatial_xi_over_L": float(
                [row for row in rows if row["lane"] == "spatial_coupled_v1" and int(row["steps"]) == steps and row["temperature"] == temperatures[-1]][0]["xi_over_L"]
            ),
        }

    critical_window_extension_gate = {
        "status": "PASS" if max_spatial_xi_over_l >= 0.20 else "BLOCKED",
        "max_spatial_xi_over_L": float(max_spatial_xi_over_l),
        "max_baseline_xi_over_L": float(max_baseline_xi_over_l),
        "required_condition": "closer-to-Tc and longer relaxation should lift spatial xi/L above 0.20",
    }
    relaxation_sensitivity_gate = {
        "status": "PASS" if relaxation_gain_near >= 0.05 else "BLOCKED",
        "near_T_short_steps_xi_over_L": float(short_near["xi_over_L"]),
        "near_T_long_steps_xi_over_L": float(long_near["xi_over_L"]),
        "relaxation_gain_near_T": relaxation_gain_near,
        "required_condition": "longer relaxation at the nearest-T point should increase xi/L by at least 0.05",
    }
    operator_separation_gate = {
        "status": "PASS" if max_spatial_xi_over_l - max_baseline_xi_over_l >= 0.05 else "BLOCKED",
        "max_spatial_xi_over_L": float(max_spatial_xi_over_l),
        "max_baseline_xi_over_L": float(max_baseline_xi_over_l),
        "spatial_minus_baseline": float(max_spatial_xi_over_l - max_baseline_xi_over_l),
        "required_condition": "spatial lane should separate from baseline in xi/L by at least 0.05",
    }

    overall_status = (
        "PASS"
        if all(
            gate["status"] == "PASS"
            for gate in [
                critical_window_extension_gate,
                relaxation_sensitivity_gate,
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
        "wave": "Wave 9 critical-window relaxation diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Critical_Window_Relaxation_Diagnostics.py",
        "status": overall_status,
        "blocker_label": "critical_window_extension_still_local",
        "claim_class": "diagnostic_window_only",
        "inputs": [
            {
                "path": str(CORE_ENGINE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "sha256": hash_file(CORE_ENGINE_PATH),
                "role": "core candidate operator implementation",
            }
        ],
        "parameters": {
            "grid_L": L,
            "grid_points": L**3,
            "dt": dt,
            "dx": dx,
            "temperature_points": temperatures,
            "step_counts": step_counts,
        },
        "metrics": {
            "by_steps": by_steps,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "critical_window_extension_gate": critical_window_extension_gate,
            "relaxation_sensitivity_gate": relaxation_sensitivity_gate,
            "operator_separation_gate": operator_separation_gate,
        },
        "limitations": [
            "This is a single-grid diagnostic intended to separate window/relaxation effects from operator-form effects.",
            "A blocked result does not prove no critical behavior exists; it blocks claims from this synthetic window.",
            "A passing result would still require a multi-grid finite-size scaling rerun.",
        ],
        "claim_boundary": "Do not claim the current operator escapes mean-field unless closer-to-Tc relaxation and finite-size gates both pass.",
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
    result = run_critical_window_diagnostic()
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
