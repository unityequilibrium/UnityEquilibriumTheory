"""
Wave 12 spatial_coupled_v2 component-ablation diagnostic.

Wave 11 showed that the first v2 candidate is available, stable, and safety
gated, but it still does not create correlation growth or lane separation. This
diagnostic asks which v2 component is responsible by running information-only,
game-only, full, short-memory, and long-memory profiles through the same core
operator helpers.

This is blocker triage only. It does not validate a new physics operator.
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
    SPATIAL_COUPLED_V2_OPERATOR_MODE,
    game_theory_force,
    information_dynamics_source,
    spatial_interface_activity,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_spatial_coupled_v2_component_ablation.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_spatial_coupled_v2_component_ablation_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
PARAMS_PATH = ROOT / "docs" / "core" / "uet_parameters.py"
WAVE11_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_spatial_coupled_v2_diagnostic.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


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


def fit_power_law(rows: list[dict[str, float | str]], value_key: str) -> dict[str, float | str]:
    usable = [
        row
        for row in rows
        if row["delta_t"] > 0 and isinstance(row[value_key], float) and row[value_key] > 0
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


PROFILE_PARAMS: dict[str, dict[str, float | str]] = {
    "baseline_tdgl": {"operator": "baseline"},
    "v2_info_only": {
        "operator": SPATIAL_COUPLED_V2_OPERATOR_MODE,
        "info": 0.5,
        "game": 0.0,
        "nonlocal": 0.5,
        "memory": 2.0,
        "conserved": 0.0,
    },
    "v2_game_only": {
        "operator": SPATIAL_COUPLED_V2_OPERATOR_MODE,
        "info": 0.0,
        "game": 0.02,
        "nonlocal": 0.5,
        "memory": 2.0,
        "conserved": 0.05,
    },
    "v2_full": {
        "operator": SPATIAL_COUPLED_V2_OPERATOR_MODE,
        "info": 0.5,
        "game": 0.02,
        "nonlocal": 0.5,
        "memory": 2.0,
        "conserved": 0.05,
    },
    "v2_memory_short": {
        "operator": SPATIAL_COUPLED_V2_OPERATOR_MODE,
        "info": 0.5,
        "game": 0.02,
        "nonlocal": 0.5,
        "memory": 1.0,
        "conserved": 0.05,
    },
    "v2_memory_long": {
        "operator": SPATIAL_COUPLED_V2_OPERATOR_MODE,
        "info": 0.5,
        "game": 0.02,
        "nonlocal": 0.5,
        "memory": 6.0,
        "conserved": 0.05,
    },
}


def params_for_profile(profile: str) -> UETParameters | None:
    config = PROFILE_PARAMS[profile]
    if config["operator"] == "baseline":
        return None
    return UETParameters(
        beta=0.05,
        kappa=1.0,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
        spatial_v2_information_coupling=float(config["info"]),
        spatial_v2_game_coupling=float(config["game"]),
        spatial_v2_nonlocal_coupling=float(config["nonlocal"]),
        spatial_v2_memory_length=float(config["memory"]),
        spatial_v2_conserved_coupling=float(config["conserved"]),
    )


def run_profile(
    *,
    profile: str,
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
    init_rng = np.random.default_rng(41000 + temp_index)
    profile_index = list(PROFILE_PARAMS).index(profile)
    step_rng = np.random.default_rng(42000 + 100 * profile_index + 10 * temp_index)
    C = init_rng.normal(eq_val, 0.1, grid_points)
    params = params_for_profile(profile)

    status = "OK"
    mean_info_norm = 0.0
    mean_game_norm = 0.0
    sample_count = 0

    for step in range(1, steps + 1):
        lap = laplacian_3d(C, L, dx)
        dF = a_t * C + b * C**3 - kappa * lap
        noise = thermal_noise_strength * math.sqrt(float(temperature)) * step_rng.normal(0, 1, grid_points)
        force = -gamma_mobility * dF

        if params is not None:
            C_field = C.reshape((L, L, L))
            info_field = phi_noise * step_rng.normal(0, 1, (L, L, L))
            info_force = information_dynamics_source(
                C_field,
                info_field,
                params,
                operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
                dx=dx,
            )
            game_force = game_theory_force(
                C_field,
                density=params.SIGMA_CRIT,
                scale=1.0,
                dx=dx,
                params=params,
                operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
            )
            force += info_force.reshape(-1) + game_force.reshape(-1)
            if step in {steps // 2, steps}:
                mean_info_norm += float(np.linalg.norm(info_force))
                mean_game_norm += float(np.linalg.norm(game_force))
                sample_count += 1

        C = C + force * dt + noise * math.sqrt(dt)
        if not np.all(np.isfinite(C)) or float(np.max(np.abs(C))) > 25.0:
            status = "UNSTABLE"
            break

    order_parameter = float(np.mean(np.abs(C))) if np.all(np.isfinite(C)) else float("nan")
    xi_proxy = axis_correlation_length_proxy(C, L, dx) if status == "OK" else float("nan")
    return {
        "profile": profile,
        "status": status,
        "grid_L": float(L),
        "temperature": float(temperature),
        "delta_t": float(critical_temperature - temperature),
        "steps": float(steps),
        "order_parameter": order_parameter,
        "xi_proxy": float(xi_proxy),
        "xi_over_L": float(xi_proxy / L) if status == "OK" else float("nan"),
        "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
        "mean_info_force_norm": float(mean_info_norm / sample_count) if sample_count else 0.0,
        "mean_game_force_norm": float(mean_game_norm / sample_count) if sample_count else 0.0,
    }


def direct_profile_checks() -> dict[str, Any]:
    interface = np.zeros((8, 8, 8))
    interface[:, :, 4:] = 1.0
    info = np.ones_like(interface)
    checks: dict[str, Any] = {}
    for profile in PROFILE_PARAMS:
        params = params_for_profile(profile)
        if params is None:
            continue
        info_force = information_dynamics_source(
            interface,
            info,
            params,
            operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
            dx=1.0,
        )
        game_force = game_theory_force(
            interface,
            density=params.SIGMA_CRIT,
            scale=1.0,
            dx=1.0,
            params=params,
            operator_mode=SPATIAL_COUPLED_V2_OPERATOR_MODE,
        )
        activity = spatial_interface_activity(interface, 1.0, params)
        checks[profile] = {
            "interface_activity_norm": float(np.linalg.norm(activity)),
            "interface_info_force_norm": float(np.linalg.norm(info_force)),
            "interface_game_force_norm": float(np.linalg.norm(game_force)),
            "interface_game_force_sum": float(np.sum(game_force)),
        }
    return checks


def run_component_ablation() -> dict[str, Any]:
    L = 12
    dx = 1.0
    dt = 0.02
    steps = 1200
    temperatures = [0.940, 0.970, 0.985, 0.992]

    rows: list[dict[str, float | str]] = []
    for temp_index, temperature in enumerate(temperatures):
        for profile in PROFILE_PARAMS:
            rows.append(
                run_profile(
                    profile=profile,
                    L=L,
                    temperature=temperature,
                    steps=steps,
                    temp_index=temp_index,
                    dx=dx,
                    dt=dt,
                )
            )

    by_profile: dict[str, Any] = {}
    for profile in PROFILE_PARAMS:
        profile_rows = [row for row in rows if row["profile"] == profile]
        stable_rows = [row for row in profile_rows if row["status"] == "OK"]
        by_profile[profile] = {
            "stable_case_count": len(stable_rows),
            "max_xi_over_L": float(max((row["xi_over_L"] for row in stable_rows), default=float("nan"))),
            "near_T_xi_over_L": float(
                [row for row in stable_rows if row["temperature"] == temperatures[-1]][0]["xi_over_L"]
            )
            if any(row["temperature"] == temperatures[-1] for row in stable_rows)
            else float("nan"),
            "max_abs_c": float(max((row["max_abs_c"] for row in stable_rows), default=float("nan"))),
            "mean_info_force_norm": float(np.mean([row["mean_info_force_norm"] for row in stable_rows]))
            if stable_rows
            else 0.0,
            "mean_game_force_norm": float(np.mean([row["mean_game_force_norm"] for row in stable_rows]))
            if stable_rows
            else 0.0,
            "beta_fit": fit_power_law(stable_rows, "order_parameter"),
            "nu_proxy_fit": fit_power_law(stable_rows, "xi_proxy"),
        }

    baseline_xi = by_profile["baseline_tdgl"]["max_xi_over_L"]
    component_profiles = [profile for profile in PROFILE_PARAMS if profile != "baseline_tdgl"]
    improvements = {
        profile: float(by_profile[profile]["max_xi_over_L"] - baseline_xi)
        for profile in component_profiles
    }
    best_profile = max(component_profiles, key=lambda profile: improvements[profile])
    best_improvement = improvements[best_profile]
    memory_short_delta = float(by_profile["v2_memory_short"]["max_xi_over_L"] - by_profile["v2_full"]["max_xi_over_L"])
    memory_long_delta = float(by_profile["v2_memory_long"]["max_xi_over_L"] - by_profile["v2_full"]["max_xi_over_L"])
    direct_checks = direct_profile_checks()

    ablation_coverage_gate = {
        "status": "PASS"
        if all(by_profile[profile]["stable_case_count"] == len(temperatures) for profile in PROFILE_PARAMS)
        else "BLOCKED",
        "required_condition": "all ablation profiles must remain finite for all temperature points",
        "stable_case_counts": {
            profile: by_profile[profile]["stable_case_count"] for profile in PROFILE_PARAMS
        },
        "expected_case_count": len(temperatures),
    }
    component_improvement_gate = {
        "status": "PASS" if best_improvement >= 0.02 else "BLOCKED",
        "required_condition": "at least one v2 component profile should improve max xi/L over baseline by >= 0.02",
        "baseline_max_xi_over_L": float(baseline_xi),
        "profile_improvements_over_baseline": improvements,
        "best_profile": best_profile,
        "best_improvement_over_baseline": float(best_improvement),
    }
    memory_length_response_gate = {
        "status": "PASS" if max(memory_short_delta, memory_long_delta) >= 0.02 else "BLOCKED",
        "required_condition": "changing v2 memory length should improve max xi/L over the full v2 profile by >= 0.02",
        "full_v2_max_xi_over_L": float(by_profile["v2_full"]["max_xi_over_L"]),
        "short_memory_delta": memory_short_delta,
        "long_memory_delta": memory_long_delta,
    }
    force_lane_activity_gate = {
        "status": "PASS"
        if direct_checks["v2_info_only"]["interface_info_force_norm"] > 0
        and direct_checks["v2_info_only"]["interface_game_force_norm"] <= 1e-12
        and direct_checks["v2_game_only"]["interface_info_force_norm"] <= 1e-12
        and direct_checks["v2_game_only"]["interface_game_force_norm"] > 0
        and abs(direct_checks["v2_game_only"]["interface_game_force_sum"]) <= 1e-10
        else "BLOCKED",
        "required_condition": "info-only and game-only lanes must isolate the intended force components and keep the game lane conserved",
        "direct_profile_checks": direct_checks,
    }

    claim_gates = [component_improvement_gate, memory_length_response_gate]
    overall_status = "PASS" if all(gate["status"] == "PASS" for gate in claim_gates) else "WARN"
    blocker_label = (
        "v2_component_ablation_points_to_candidate_repair"
        if component_improvement_gate["status"] == "PASS"
        else "v2_components_remain_correlation_neutral_or_damping"
    )

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    inputs = [
        {
            "path": relpath(CORE_ENGINE_PATH),
            "sha256": hash_file(CORE_ENGINE_PATH),
            "role": "core v2 candidate operator implementation",
        },
        {
            "path": relpath(PARAMS_PATH),
            "sha256": hash_file(PARAMS_PATH),
            "role": "candidate coefficient defaults",
        },
    ]
    if WAVE11_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE11_ARTIFACT_PATH),
                "sha256": hash_file(WAVE11_ARTIFACT_PATH),
                "role": "Wave 11 v2 diagnostic controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 12 spatial_coupled_v2 component ablation",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupled_V2_Component_Ablation.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_ablation_only",
        "inputs": inputs,
        "parameters": {
            "grid_L": L,
            "grid_points": L**3,
            "dt": dt,
            "dx": dx,
            "steps": steps,
            "temperature_points": temperatures,
            "profiles": PROFILE_PARAMS,
        },
        "metrics": {
            "by_profile": by_profile,
            "profile_improvements_over_baseline": improvements,
            "best_profile": best_profile,
            "best_improvement_over_baseline": float(best_improvement),
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "ablation_coverage_gate": ablation_coverage_gate,
            "force_lane_activity_gate": force_lane_activity_gate,
            "component_improvement_gate": component_improvement_gate,
            "memory_length_response_gate": memory_length_response_gate,
        },
        "limitations": [
            "This ablation is a deterministic local diagnostic, not a full scaling verifier.",
            "A component improvement would identify a repair direction, not validate a universality claim.",
            "A blocked result means the tested v2 components are not sufficient under this synthetic window.",
        ],
        "claim_boundary": "Do not promote spatial_coupled_v2 claims from ablation; use this artifact only to decide the next operator redesign path.",
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
    result = run_component_ablation()
    print(
        json.dumps(
            {
                "status": result["status"],
                "artifact": str(ARTIFACT_PATH),
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "blocker_label": result["blocker_label"],
                "best_profile": result["metrics"]["best_profile"],
                "best_improvement_over_baseline": result["metrics"]["best_improvement_over_baseline"],
            },
            indent=2,
        )
    )
