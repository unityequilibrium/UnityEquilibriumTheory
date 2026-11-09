"""
Wave 14 conserved_order_v1 core-candidate diagnostic.

Wave 13 showed that Model C / Cahn-Hilliard conserved-order dynamics is the
strongest current mechanism-level repair direction. This diagnostic checks the
next required step: exposing the conserved-order structure through the core
master equation as an opt-in operator mode while preserving legacy defaults.

This remains a core-integration and mechanism diagnostic, not a universality or
publication verifier.
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
    CONSERVED_ORDER_OPERATOR_MODE,
    LEGACY_OPERATOR_MODE,
    SUPPORTED_OPERATOR_MODES,
    conserved_laplacian,
    dynamics_step_complete,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_core_candidate.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_core_candidate_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
PARAMS_PATH = ROOT / "docs" / "core" / "uet_parameters.py"
CORE_TEST_PATH = ROOT / "docs" / "core" / "test" / "test_spatial_coupling.py"
WAVE13_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_model_c_conserved_order_diagnostic.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def axis_correlation_length_proxy_2d(C: np.ndarray, dx: float) -> float:
    field = np.asarray(C, dtype=float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return 0.0

    spectrum = np.fft.fftn(centered)
    autocorr = np.fft.ifftn(np.abs(spectrum) ** 2).real / centered.size
    autocorr = autocorr / max(float(autocorr[0, 0]), 1e-14)
    threshold = math.exp(-1.0)
    max_r = min(field.shape) // 2

    axis_corr = []
    for r in range(max_r + 1):
        axis_corr.append(float(np.mean([autocorr[r, 0], autocorr[0, r]])))

    for r in range(1, len(axis_corr)):
        if axis_corr[r] <= threshold:
            prev_corr = axis_corr[r - 1]
            curr_corr = axis_corr[r]
            if abs(prev_corr - curr_corr) <= 1e-12:
                return r * dx
            frac = (prev_corr - threshold) / (prev_corr - curr_corr)
            return ((r - 1) + max(0.0, min(1.0, frac))) * dx
    return max_r * dx


def domain_boundary_count(C: np.ndarray) -> int:
    binary = (C > float(np.mean(C))).astype(int)
    h_cross = np.sum(np.abs(np.diff(binary, axis=0)))
    v_cross = np.sum(np.abs(np.diff(binary, axis=1)))
    return int(h_cross + v_cross)


def params_for_candidate(mode: str) -> UETParameters:
    return UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.1,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=mode,
        conserved_order_mobility=1.0,
    )


def run_lane(
    *,
    lane: str,
    initial: np.ndarray,
    dx: float,
    dt: float,
    steps: int,
) -> np.ndarray:
    mode = CONSERVED_ORDER_OPERATOR_MODE if lane == "core_conserved_order_v1" else LEGACY_OPERATOR_MODE
    params = params_for_candidate(mode)
    C = np.array(initial, dtype=float, copy=True)
    for _ in range(steps):
        C = dynamics_step_complete(C, dx=dx, dt=dt, params=params, operator_mode=mode)
        if not np.all(np.isfinite(C)) or float(np.max(np.abs(C))) > 25.0:
            break
    return C


def summarize_lane(lane: str, seed: int, initial: np.ndarray, final: np.ndarray, dx: float) -> dict[str, float | int | str]:
    initial_mean = float(np.mean(initial))
    final_mean = float(np.mean(final))
    initial_xi = axis_correlation_length_proxy_2d(initial, dx)
    final_xi = axis_correlation_length_proxy_2d(final, dx)
    initial_order = float(np.mean(np.abs(initial)))
    final_order = float(np.mean(np.abs(final)))
    return {
        "lane": lane,
        "seed": seed,
        "initial_mean": initial_mean,
        "final_mean": final_mean,
        "mass_drift_abs": abs(final_mean - initial_mean),
        "initial_order": initial_order,
        "final_order": final_order,
        "order_growth_ratio": final_order / max(initial_order, 1e-14),
        "initial_xi": float(initial_xi),
        "final_xi": float(final_xi),
        "xi_growth_ratio": final_xi / max(initial_xi, 1e-14),
        "xi_over_L_final": float(final_xi / initial.shape[0]),
        "initial_domain_boundary_count": domain_boundary_count(initial),
        "final_domain_boundary_count": domain_boundary_count(final),
        "max_abs_c": float(np.max(np.abs(final))) if np.all(np.isfinite(final)) else float("nan"),
        "status": "OK" if np.all(np.isfinite(final)) else "UNSTABLE",
    }


def aggregate(rows: list[dict[str, float | int | str]]) -> dict[str, Any]:
    by_lane: dict[str, Any] = {}
    for lane in sorted({str(row["lane"]) for row in rows}):
        lane_rows = [row for row in rows if row["lane"] == lane and row["status"] == "OK"]
        by_lane[lane] = {
            "stable_case_count": len(lane_rows),
            "max_mass_drift_abs": float(max((row["mass_drift_abs"] for row in lane_rows), default=float("nan"))),
            "median_xi_growth_ratio": float(np.median([row["xi_growth_ratio"] for row in lane_rows])) if lane_rows else float("nan"),
            "median_order_growth_ratio": float(np.median([row["order_growth_ratio"] for row in lane_rows])) if lane_rows else float("nan"),
            "median_final_xi_over_L": float(np.median([row["xi_over_L_final"] for row in lane_rows])) if lane_rows else float("nan"),
            "median_final_domain_boundary_count": float(np.median([row["final_domain_boundary_count"] for row in lane_rows])) if lane_rows else float("nan"),
            "max_abs_c": float(max((row["max_abs_c"] for row in lane_rows), default=float("nan"))),
        }
    return by_lane


def legacy_compatibility_check() -> dict[str, Any]:
    params = UETParameters(beta=0.05, kappa=0.1, W_N=0.0, a0_viscosity=0.0)
    C = np.linspace(-0.2, 0.2, 16)
    I = np.linspace(0.1, 0.2, 16)
    default_state = dynamics_step_complete(C, I=I, dx=0.1, dt=0.01, params=params)
    explicit_state = dynamics_step_complete(
        C,
        I=I,
        dx=0.1,
        dt=0.01,
        params=params,
        operator_mode=LEGACY_OPERATOR_MODE,
    )
    if isinstance(default_state, tuple):
        max_abs_delta = max(float(np.max(np.abs(a - b))) for a, b in zip(default_state, explicit_state))
    else:
        max_abs_delta = float(np.max(np.abs(default_state - explicit_state)))
    return {
        "default_operator_mode": params.operator_mode,
        "explicit_operator_mode": LEGACY_OPERATOR_MODE,
        "max_abs_delta": max_abs_delta,
    }


def run_core_candidate_diagnostic() -> dict[str, Any]:
    L = 32
    dx = 1.0
    dt = 0.01
    steps = 300
    seeds = [1401, 1402, 1403]
    lanes = ["legacy_nonconserved_core", "core_conserved_order_v1"]

    rows: list[dict[str, float | int | str]] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        initial = rng.normal(0.0, 0.01, (L, L))
        for lane in lanes:
            final = run_lane(lane=lane, initial=initial, dx=dx, dt=dt, steps=steps)
            rows.append(summarize_lane(lane, seed, initial, final, dx))

    by_lane = aggregate(rows)
    legacy = by_lane["legacy_nonconserved_core"]
    conserved = by_lane["core_conserved_order_v1"]
    xi_growth_delta = float(conserved["median_xi_growth_ratio"] - legacy["median_xi_growth_ratio"])
    compatibility = legacy_compatibility_check()

    direct_field = np.zeros((8, 8))
    direct_field[:, 4:] = 0.2
    direct_force_sum = float(np.sum(conserved_laplacian(direct_field, 1.0)))

    core_conserved_alignment_gate = {
        "status": "PASS" if CONSERVED_ORDER_OPERATOR_MODE in SUPPORTED_OPERATOR_MODES else "BLOCKED",
        "required_condition": "conserved_order_v1 must be an opt-in supported core operator mode.",
        "operator_mode": CONSERVED_ORDER_OPERATOR_MODE,
        "supported_modes": sorted(SUPPORTED_OPERATOR_MODES),
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }
    legacy_compatibility_gate = {
        "status": "PASS" if compatibility["max_abs_delta"] <= 1e-14 else "BLOCKED",
        "required_condition": "default legacy behavior must match explicit legacy mode.",
        **compatibility,
    }
    conserved_mass_gate = {
        "status": "PASS" if conserved["max_mass_drift_abs"] <= 1e-10 and abs(direct_force_sum) <= 1e-12 else "BLOCKED",
        "required_condition": "core conserved-order lane must conserve mean C and use a zero-sum conserved Laplacian.",
        "core_conserved_max_mass_drift_abs": conserved["max_mass_drift_abs"],
        "legacy_max_mass_drift_abs": legacy["max_mass_drift_abs"],
        "direct_conserved_laplacian_sum": direct_force_sum,
    }
    core_mechanism_response_gate = {
        "status": "PASS" if conserved["median_xi_growth_ratio"] >= 1.5 and xi_growth_delta >= 0.25 else "BLOCKED",
        "required_condition": "core conserved-order lane should show correlation growth and separate from legacy core by xi-growth ratio >= 0.25.",
        "legacy_median_xi_growth_ratio": legacy["median_xi_growth_ratio"],
        "core_conserved_median_xi_growth_ratio": conserved["median_xi_growth_ratio"],
        "core_minus_legacy_xi_growth_ratio": xi_growth_delta,
        "core_conserved_median_order_growth_ratio": conserved["median_order_growth_ratio"],
    }
    wave13_bridge_gate = {
        "status": "PASS" if WAVE13_ARTIFACT_PATH.exists() else "BLOCKED",
        "required_condition": "core integration must cite the Wave 13 Model C mechanism artifact.",
        "wave13_artifact_path": relpath(WAVE13_ARTIFACT_PATH) if WAVE13_ARTIFACT_PATH.exists() else None,
        "wave13_sha256": hash_file(WAVE13_ARTIFACT_PATH) if WAVE13_ARTIFACT_PATH.exists() else None,
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Core integration is not a universality or publication claim.",
        "claim_boundary": "Requires finite-size/exponent gates before any dynamics or universality claim upgrade.",
    }

    overall_status = (
        "PASS"
        if all(
            gate["status"] == "PASS"
            for gate in [
                core_conserved_alignment_gate,
                legacy_compatibility_gate,
                conserved_mass_gate,
                core_mechanism_response_gate,
                wave13_bridge_gate,
            ]
        )
        else "WARN"
    )
    blocker_label = (
        "conserved_order_core_candidate_scaling_open"
        if overall_status == "PASS"
        else "conserved_order_core_candidate_needs_mechanism_tuning"
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
            "role": "core conserved-order candidate implementation",
        },
        {
            "path": relpath(PARAMS_PATH),
            "sha256": hash_file(PARAMS_PATH),
            "role": "conserved-order candidate parameter default",
        },
        {
            "path": relpath(CORE_TEST_PATH),
            "sha256": hash_file(CORE_TEST_PATH),
            "role": "core candidate unit checks",
        },
    ]
    if WAVE13_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE13_ARTIFACT_PATH),
                "sha256": hash_file(WAVE13_ARTIFACT_PATH),
                "role": "Wave 13 Model C mechanism controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 14 conserved_order_v1 core candidate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Core_Candidate.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_core_candidate_only",
        "candidate_operator_mode": CONSERVED_ORDER_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_size": [L, L],
            "dx": dx,
            "dt": dt,
            "steps": steps,
            "seeds": seeds,
            "candidate_params": {
                "alpha": -1.0,
                "gamma": 1.0,
                "C0": 0.0,
                "beta": 0.0,
                "kappa": 0.1,
                "conserved_order_mobility": 1.0,
            },
        },
        "metrics": {
            "by_lane": by_lane,
            "core_minus_legacy_xi_growth_ratio": xi_growth_delta,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "core_conserved_alignment_gate": core_conserved_alignment_gate,
            "legacy_compatibility_gate": legacy_compatibility_gate,
            "conserved_mass_gate": conserved_mass_gate,
            "core_mechanism_response_gate": core_mechanism_response_gate,
            "wave13_bridge_gate": wave13_bridge_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is an opt-in core-candidate diagnostic, not a full finite-size scaling result.",
            "Explicit core conserved-order integration uses finite-difference helpers and still needs formula/unit review.",
            "A PASS only authorizes the next scaling verifier; it does not validate a universality-class shift.",
        ],
        "claim_boundary": "Use conserved_order_v1 as a diagnostic core candidate only until finite-size/exponent gates and formula audit closure pass.",
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
    result = run_core_candidate_diagnostic()
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
