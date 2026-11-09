"""
Wave 17 conserved-order spectral finite-size scaling diagnostic.

Wave 16 exposed an opt-in semi-implicit conserved-order core path and showed
that it bridges the topic spectral Cahn-Hilliard engine. This diagnostic asks
the next narrower question: does the new core candidate already provide enough
finite-size and exponent evidence to support a stronger dynamics claim?

The answer is recorded as machine-readable gates. A passing implementation
bridge is not treated as a universality, RG-closure, or material-validation
claim.
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
    CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    dynamics_step_complete,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_scaling.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_scaling_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
PARAMS_PATH = ROOT / "docs" / "core" / "uet_parameters.py"
WAVE16_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_core_candidate.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def axis_correlation_length_proxy(C: np.ndarray, dx: float) -> float:
    """Estimate connected xi from the average axis autocorrelation crossing."""
    field = np.asarray(C, dtype=float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return 0.0

    spectrum = np.fft.fftn(centered)
    autocorr = np.fft.ifftn(np.abs(spectrum) ** 2).real / centered.size
    autocorr = autocorr / max(float(autocorr[(0,) * field.ndim]), 1e-14)
    threshold = math.exp(-1.0)
    max_r = min(field.shape) // 2

    axis_corr = []
    for radius in range(max_r + 1):
        samples = []
        for axis in range(field.ndim):
            index = [0] * field.ndim
            index[axis] = radius
            samples.append(float(autocorr[tuple(index)]))
        axis_corr.append(float(np.mean(samples)))

    for radius in range(1, len(axis_corr)):
        if axis_corr[radius] <= threshold:
            previous = axis_corr[radius - 1]
            current = axis_corr[radius]
            if abs(previous - current) <= 1e-12:
                return radius * dx
            fraction = (previous - threshold) / (previous - current)
            return ((radius - 1) + max(0.0, min(1.0, fraction))) * dx
    return max_r * dx


def binder_proxy(C: np.ndarray) -> float:
    second = float(np.mean(C**2))
    fourth = float(np.mean(C**4))
    if second <= 1e-14:
        return 0.0
    return float(1.0 - fourth / (3.0 * second**2))


def fit_power(rows: list[dict[str, float | int | str]], value_key: str, exponent_sign: float = 1.0) -> dict[str, float]:
    delta_t = np.array([float(row["delta_t"]) for row in rows], dtype=float)
    values = np.array([max(float(row[value_key]), 1e-12) for row in rows], dtype=float)
    fit = linregress(np.log(delta_t), np.log(values))
    return {
        "exponent": float(exponent_sign * fit.slope),
        "slope": float(fit.slope),
        "intercept": float(fit.intercept),
        "r_squared": float(fit.rvalue**2),
        "stderr": float(fit.stderr),
        "p_value": float(fit.pvalue),
    }


def run_single_case(
    *,
    grid_L: int,
    grid_index: int,
    temperature: float,
    temp_index: int,
    steps: int,
    dt: float,
    dx: float,
    kappa: float,
) -> dict[str, float | int | str]:
    critical_temperature = 1.0
    alpha_t = temperature - critical_temperature
    seed = 17000 + 100 * grid_index + temp_index
    rng = np.random.default_rng(seed)
    C = rng.normal(0.0, 0.01, (grid_L, grid_L, grid_L))
    initial_mean = float(np.mean(C))

    params = UETParameters(
        alpha=alpha_t,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=kappa,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        conserved_order_mobility=1.0,
    )

    status = "OK"
    for _ in range(steps):
        C = dynamics_step_complete(
            C,
            dx=dx,
            dt=dt,
            params=params,
            operator_mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        )
        if not np.all(np.isfinite(C)) or float(np.max(np.abs(C))) > 25.0:
            status = "UNSTABLE"
            break

    final_mean = float(np.mean(C)) if np.all(np.isfinite(C)) else float("nan")
    xi = axis_correlation_length_proxy(C, dx) if np.all(np.isfinite(C)) else float("nan")
    domain_length = grid_L * dx
    return {
        "lane": "core_conserved_order_spectral_v1",
        "grid_L": grid_L,
        "grid_points": grid_L**3,
        "domain_length": float(domain_length),
        "temperature": float(temperature),
        "delta_t": float(critical_temperature - temperature),
        "steps": steps,
        "dt": float(dt),
        "dx": float(dx),
        "seed": seed,
        "status": status,
        "mass_drift_abs": abs(final_mean - initial_mean) if math.isfinite(final_mean) else float("nan"),
        "order_parameter": float(np.mean(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
        "xi_proxy": float(xi),
        "xi_over_L": float(xi / domain_length) if math.isfinite(xi) else float("nan"),
        "susceptibility_proxy": float(np.var(C) * C.size) if np.all(np.isfinite(C)) else float("nan"),
        "binder_proxy": binder_proxy(C) if np.all(np.isfinite(C)) else float("nan"),
        "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
    }


def run_spectral_scaling_diagnostic() -> dict[str, Any]:
    grid_sizes = [8, 12, 16]
    temperatures = [0.90, 0.94, 0.97, 0.985]
    steps_by_grid = {8: 500, 12: 650, 16: 850}
    dt = 0.05
    dx = 1.0
    kappa = 0.002

    rows: list[dict[str, float | int | str]] = []
    for grid_index, grid_L in enumerate(grid_sizes):
        for temp_index, temperature in enumerate(temperatures):
            rows.append(
                run_single_case(
                    grid_L=grid_L,
                    grid_index=grid_index,
                    temperature=temperature,
                    temp_index=temp_index,
                    steps=steps_by_grid[grid_L],
                    dt=dt,
                    dx=dx,
                    kappa=kappa,
                )
            )

    by_grid: dict[str, Any] = {}
    beta_values = []
    beta_r2_values = []
    near_xi_over_l = []
    near_rows = [row for row in rows if float(row["temperature"]) == temperatures[-1]]
    for row in near_rows:
        near_xi_over_l.append(float(row["xi_over_L"]))

    for grid_L in grid_sizes:
        subset = [row for row in rows if int(row["grid_L"]) == grid_L and row["status"] == "OK"]
        beta_fit = fit_power(subset, "order_parameter", exponent_sign=1.0)
        nu_fit = fit_power(subset, "xi_proxy", exponent_sign=-1.0)
        beta_values.append(beta_fit["exponent"])
        beta_r2_values.append(beta_fit["r_squared"])
        by_grid[str(grid_L)] = {
            "beta": beta_fit,
            "nu_proxy": nu_fit,
            "xi_near_over_far": float(subset[-1]["xi_proxy"]) / max(float(subset[0]["xi_proxy"]), 1e-12),
            "xi_over_L_near": float(subset[-1]["xi_over_L"]),
            "binder_near": float(subset[-1]["binder_proxy"]),
            "max_mass_drift_abs": float(max(row["mass_drift_abs"] for row in subset)),
            "max_abs_c": float(max(row["max_abs_c"] for row in subset)),
        }

    binder_spreads: dict[str, float] = {}
    for temperature in temperatures:
        temp_rows = [row for row in rows if float(row["temperature"]) == temperature and row["status"] == "OK"]
        binders = [float(row["binder_proxy"]) for row in temp_rows]
        binder_spreads[f"{temperature:.3f}"] = float(max(binders) - min(binders))
    best_binder_spread = float(min(binder_spreads.values()))

    wave16 = load_json(WAVE16_ARTIFACT_PATH) if WAVE16_ARTIFACT_PATH.exists() else {}
    stable_rows = [row for row in rows if row["status"] == "OK"]
    max_mass_drift = float(max(row["mass_drift_abs"] for row in stable_rows))
    max_abs_c = float(max(row["max_abs_c"] for row in stable_rows))
    median_beta = float(np.median(beta_values))
    beta_range = [float(min(beta_values)), float(max(beta_values))]
    median_beta_r2 = float(np.median(beta_r2_values))
    beta_ising = 0.3265
    beta_tolerance = 0.08

    wave16_bridge_gate = {
        "status": (
            "PASS"
            if wave16.get("status") == "PASS"
            and wave16.get("candidate_operator_mode") == CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE
            else "BLOCKED"
        ),
        "required_condition": "Wave 17 scaling must use the Wave 16 opt-in spectral core candidate as its source.",
        "wave16_status": wave16.get("status"),
        "wave16_blocker_label": wave16.get("blocker_label"),
        "wave16_candidate_operator_mode": wave16.get("candidate_operator_mode"),
    }
    finite_size_coverage_gate = {
        "status": "PASS" if len(grid_sizes) >= 3 and len(temperatures) >= 4 else "FAIL",
        "grid_sizes": grid_sizes,
        "temperature_points": temperatures,
        "required_condition": "at least three grid sizes and four temperatures for a diagnostic finite-size sweep",
    }
    spectral_stability_gate = {
        "status": (
            "PASS"
            if len(stable_rows) == len(rows) and max_mass_drift <= 1e-8 and max_abs_c <= 2.0
            else "BLOCKED"
        ),
        "required_condition": "all spectral core scaling cases must remain finite and conserve mean C.",
        "stable_case_count": len(stable_rows),
        "required_case_count": len(rows),
        "max_mass_drift_abs": max_mass_drift,
        "max_abs_c": max_abs_c,
    }
    correlation_window_gate = {
        "status": "PASS" if max(near_xi_over_l) >= 0.20 and max(near_xi_over_l) < 0.80 else "BLOCKED",
        "required_condition": "near-critical xi/L must be large enough to show finite-size effects without saturating the grid",
        "xi_over_L_near_values": near_xi_over_l,
        "max_xi_over_L_near": float(max(near_xi_over_l)),
    }
    binder_crossing_gate = {
        "status": "PASS" if best_binder_spread <= 0.05 else "BLOCKED",
        "required_condition": "Binder-style proxy curves should show at least one crossing-like spread <= 0.05",
        "binder_spread_by_temperature": binder_spreads,
        "best_binder_spread": best_binder_spread,
    }
    universality_exponent_gate = {
        "status": (
            "PASS"
            if abs(median_beta - beta_ising) <= beta_tolerance
            and min(beta_r2_values) >= 0.80
            and correlation_window_gate["status"] == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "median beta must be near 3D Ising and paired with a passing correlation window before any universality claim.",
        "beta_ising_reference": beta_ising,
        "beta_tolerance": beta_tolerance,
        "beta_by_grid": beta_values,
        "beta_range": beta_range,
        "median_beta": median_beta,
        "beta_r_squared_by_grid": beta_r2_values,
        "median_beta_r_squared": median_beta_r2,
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Finite-size diagnostics do not replace material validation or RG closure.",
        "claim_boundary": "Keep the spectral core candidate diagnostic-only until correlation-window and exponent gates pass together.",
    }

    pass_gates = [
        wave16_bridge_gate,
        finite_size_coverage_gate,
        spectral_stability_gate,
        correlation_window_gate,
        binder_crossing_gate,
        universality_exponent_gate,
    ]
    overall_status = "PASS" if all(gate["status"] == "PASS" for gate in pass_gates) else "WARN"
    if correlation_window_gate["status"] != "PASS":
        blocker_label = "spectral_core_finite_size_window_not_established"
    elif universality_exponent_gate["status"] != "PASS":
        blocker_label = "spectral_core_exponent_scaling_not_established"
    else:
        blocker_label = "spectral_core_scaling_claim_boundary_open"

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    inputs = [
        {
            "path": relpath(CORE_ENGINE_PATH),
            "sha256": hash_file(CORE_ENGINE_PATH),
            "role": "core spectral conserved-order implementation",
        },
        {
            "path": relpath(PARAMS_PATH),
            "sha256": hash_file(PARAMS_PATH),
            "role": "candidate parameter source",
        },
    ]
    if WAVE16_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE16_ARTIFACT_PATH),
                "sha256": hash_file(WAVE16_ARTIFACT_PATH),
                "role": "Wave 16 core spectral bridge controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 17 conserved_order_spectral_v1 finite-size scaling diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Scaling.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_finite_size_exponent_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_sizes": grid_sizes,
            "temperature_points": temperatures,
            "steps_by_grid": steps_by_grid,
            "dt": dt,
            "dx": dx,
            "kappa": kappa,
            "domain_policy": "lattice_unit_dx_1_finite_size_sweep",
        },
        "metrics": {
            "by_grid": by_grid,
            "max_xi_over_L_near": float(max(near_xi_over_l)),
            "median_beta": median_beta,
            "beta_range": beta_range,
            "median_beta_r_squared": median_beta_r2,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave16_bridge_gate": wave16_bridge_gate,
            "finite_size_coverage_gate": finite_size_coverage_gate,
            "spectral_stability_gate": spectral_stability_gate,
            "correlation_window_gate": correlation_window_gate,
            "binder_crossing_gate": binder_crossing_gate,
            "universality_exponent_gate": universality_exponent_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a deterministic normalized 3D lattice-unit diagnostic, not an equilibrium ensemble or material-data result.",
            "A blocked correlation-window or exponent gate prevents universality-class promotion even when the spectral core is stable.",
            "The finite-size sweep uses proxy xi and Binder measurements; RG closure remains external to this artifact.",
        ],
        "claim_boundary": "Do not claim a universality shift or phase-transition solution from conserved_order_spectral_v1 until finite-size, exponent, material, and RG gates pass.",
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
    result = run_spectral_scaling_diagnostic()
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
