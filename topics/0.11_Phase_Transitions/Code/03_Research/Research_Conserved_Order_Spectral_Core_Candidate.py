"""
Wave 16 conserved-order spectral core-candidate diagnostic.

Wave 15 showed that the explicit finite-difference conserved-order core path is
too stiff to be treated as a direct replacement for the Wave 13 spectral
Cahn-Hilliard mechanism. This diagnostic checks the next implementation step:
an opt-in semi-implicit spectral conserved-order core mode that reuses the core
master-equation force assembly while matching the topic spectral engine.

This remains an implementation/mechanism bridge, not a universality or
publication verifier.
"""

from __future__ import annotations

import csv
import importlib.util
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

from docs.core import uet_base_solver  # noqa: E402
from docs.core.uet_master_equation import (  # noqa: E402
    CONSERVED_ORDER_OPERATOR_MODE,
    CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    LEGACY_OPERATOR_MODE,
    SUPPORTED_OPERATOR_MODES,
    dynamics_step_complete,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_core_candidate.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_core_candidate_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
PARAMS_PATH = ROOT / "docs" / "core" / "uet_parameters.py"
CORE_TEST_PATH = ROOT / "docs" / "core" / "test" / "test_spatial_coupling.py"
ENGINE_PHASE_PATH = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Phase.py"
WAVE13_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_model_c_conserved_order_diagnostic.json"
WAVE15_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_numerics_gap.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_phase_engine_class():
    """Load topic Engine_Phase.py without creating run-log side effects."""
    uet_base_solver.UETBaseSolver._setup_logger = lambda self, *args, **kwargs: setattr(self, "logger", None)
    spec = importlib.util.spec_from_file_location("uet_phase_engine_wave16", ENGINE_PHASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Engine_Phase.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.UETPhaseEngine


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


def params_for_mode(mode: str) -> UETParameters:
    return UETParameters(
        alpha=-1.0,
        gamma=1.0,
        C0=0.0,
        beta=0.0,
        kappa=0.002,
        W_N=0.0,
        a0_viscosity=0.0,
        operator_mode=mode,
        conserved_order_mobility=1.0,
    )


def run_topic_reference(*, engine_cls, initial: np.ndarray, dt: float, steps: int) -> np.ndarray:
    params = params_for_mode(CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE)
    engine = engine_cls(nx=initial.shape[0], ny=initial.shape[1], dt=dt, temperature=0.0, params=params)
    engine.logger = None
    engine.C = np.array(initial, dtype=float, copy=True)
    for step in range(steps):
        engine.step(step)
        if not np.all(np.isfinite(engine.C)):
            break
    return np.array(engine.C, dtype=float, copy=True)


def run_core_lane(*, mode: str, initial: np.ndarray, dx: float, dt: float, steps: int) -> tuple[np.ndarray, str]:
    params = params_for_mode(mode)
    C = np.array(initial, dtype=float, copy=True)
    status = "OK"
    for _ in range(steps):
        C = dynamics_step_complete(C, dx=dx, dt=dt, params=params, operator_mode=mode)
        if not np.all(np.isfinite(C)) or float(np.max(np.abs(C))) > 25.0:
            status = "UNSTABLE"
            break
    return C, status


def summarize_lane(
    lane: str,
    seed: int,
    initial: np.ndarray,
    final: np.ndarray,
    dx: float,
    status: str,
    topic_delta: float | None = None,
) -> dict[str, float | int | str]:
    initial_mean = float(np.mean(initial))
    final_mean = float(np.mean(final)) if np.all(np.isfinite(final)) else float("nan")
    initial_xi = axis_correlation_length_proxy_2d(initial, dx)
    final_xi = axis_correlation_length_proxy_2d(final, dx) if np.all(np.isfinite(final)) else float("nan")
    initial_order = float(np.mean(np.abs(initial)))
    final_order = float(np.mean(np.abs(final))) if np.all(np.isfinite(final)) else float("nan")
    return {
        "lane": lane,
        "seed": seed,
        "initial_mean": initial_mean,
        "final_mean": final_mean,
        "mass_drift_abs": abs(final_mean - initial_mean) if math.isfinite(final_mean) else float("nan"),
        "initial_order": initial_order,
        "final_order": final_order,
        "order_growth_ratio": final_order / max(initial_order, 1e-14) if math.isfinite(final_order) else float("nan"),
        "initial_xi": float(initial_xi),
        "final_xi": float(final_xi),
        "xi_growth_ratio": final_xi / max(initial_xi, 1e-14) if math.isfinite(final_xi) else float("nan"),
        "xi_over_L_final": float(final_xi / initial.shape[0]) if math.isfinite(final_xi) else float("nan"),
        "initial_domain_boundary_count": domain_boundary_count(initial),
        "final_domain_boundary_count": domain_boundary_count(final) if np.all(np.isfinite(final)) else -1,
        "max_abs_c": float(np.max(np.abs(final))) if np.all(np.isfinite(final)) else float("nan"),
        "topic_reference_max_abs_delta": float(topic_delta) if topic_delta is not None else float("nan"),
        "status": status,
    }


def aggregate(rows: list[dict[str, float | int | str]]) -> dict[str, Any]:
    by_lane: dict[str, Any] = {}
    for lane in sorted({str(row["lane"]) for row in rows}):
        lane_rows = [row for row in rows if row["lane"] == lane and row["status"] == "OK"]
        deltas = [
            float(row["topic_reference_max_abs_delta"])
            for row in lane_rows
            if math.isfinite(float(row["topic_reference_max_abs_delta"]))
        ]
        by_lane[lane] = {
            "stable_case_count": len(lane_rows),
            "max_mass_drift_abs": float(max((row["mass_drift_abs"] for row in lane_rows), default=float("nan"))),
            "median_xi_growth_ratio": float(np.median([row["xi_growth_ratio"] for row in lane_rows])) if lane_rows else float("nan"),
            "median_order_growth_ratio": float(np.median([row["order_growth_ratio"] for row in lane_rows])) if lane_rows else float("nan"),
            "median_final_xi_over_L": float(np.median([row["xi_over_L_final"] for row in lane_rows])) if lane_rows else float("nan"),
            "median_final_domain_boundary_count": float(np.median([row["final_domain_boundary_count"] for row in lane_rows])) if lane_rows else float("nan"),
            "max_abs_c": float(max((row["max_abs_c"] for row in lane_rows), default=float("nan"))),
            "max_topic_reference_abs_delta": float(max(deltas, default=float("nan"))),
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


def run_spectral_core_candidate_diagnostic() -> dict[str, Any]:
    engine_cls = load_phase_engine_class()
    nx = 64
    dx = 1.0 / nx
    dt = 0.01
    steps = 500
    seeds = [1301, 1302, 1303]

    rows: list[dict[str, float | int | str]] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        initial = rng.normal(0.0, 0.01, (nx, nx))
        topic_final = run_topic_reference(engine_cls=engine_cls, initial=initial, dt=dt, steps=steps)
        rows.append(summarize_lane("topic_model_c_reference", seed, initial, topic_final, dx, "OK"))

        spectral_final, spectral_status = run_core_lane(
            mode=CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
            initial=initial,
            dx=dx,
            dt=dt,
            steps=steps,
        )
        topic_delta = float(np.max(np.abs(spectral_final - topic_final))) if spectral_status == "OK" else float("nan")
        rows.append(
            summarize_lane(
                "core_conserved_order_spectral_v1",
                seed,
                initial,
                spectral_final,
                dx,
                spectral_status,
                topic_delta,
            )
        )

        explicit_final, explicit_status = run_core_lane(
            mode=CONSERVED_ORDER_OPERATOR_MODE,
            initial=initial,
            dx=dx,
            dt=dt,
            steps=steps,
        )
        rows.append(
            summarize_lane(
                "core_conserved_order_v1_explicit",
                seed,
                initial,
                explicit_final,
                dx,
                explicit_status,
            )
        )

    by_lane = aggregate(rows)
    topic = by_lane["topic_model_c_reference"]
    spectral = by_lane["core_conserved_order_spectral_v1"]
    explicit = by_lane["core_conserved_order_v1_explicit"]
    compatibility = legacy_compatibility_check()
    wave15 = load_json(WAVE15_ARTIFACT_PATH) if WAVE15_ARTIFACT_PATH.exists() else {}

    spectral_minus_topic_xi = float(spectral["median_xi_growth_ratio"] - topic["median_xi_growth_ratio"])

    core_spectral_alignment_gate = {
        "status": "PASS" if CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE in SUPPORTED_OPERATOR_MODES else "BLOCKED",
        "required_condition": "conserved_order_spectral_v1 must be an opt-in supported core operator mode.",
        "operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "supported_modes": sorted(SUPPORTED_OPERATOR_MODES),
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }
    legacy_compatibility_gate = {
        "status": "PASS" if compatibility["max_abs_delta"] <= 1e-14 else "BLOCKED",
        "required_condition": "default legacy behavior must match explicit legacy mode.",
        **compatibility,
    }
    spectral_mass_stability_gate = {
        "status": (
            "PASS"
            if spectral["stable_case_count"] == len(seeds)
            and spectral["max_mass_drift_abs"] <= 1e-8
            and spectral["max_abs_c"] <= 2.0
            else "BLOCKED"
        ),
        "required_condition": "core spectral lane must stay finite and conserve mean C under Wave 13-like stiff settings.",
        "stable_case_count": spectral["stable_case_count"],
        "required_case_count": len(seeds),
        "max_mass_drift_abs": spectral["max_mass_drift_abs"],
        "max_abs_c": spectral["max_abs_c"],
    }
    topic_engine_bridge_gate = {
        "status": "PASS" if spectral["max_topic_reference_abs_delta"] <= 1e-8 else "BLOCKED",
        "required_condition": "core spectral lane should match the existing topic spectral engine within 1e-8 max absolute field delta.",
        "max_topic_reference_abs_delta": spectral["max_topic_reference_abs_delta"],
        "spectral_minus_topic_median_xi_growth_ratio": spectral_minus_topic_xi,
    }
    mechanism_response_gate = {
        "status": (
            "PASS"
            if spectral["median_xi_growth_ratio"] >= 1.5
            and spectral["median_order_growth_ratio"] >= 5.0
            and abs(spectral_minus_topic_xi) <= 1e-8
            else "BLOCKED"
        ),
        "required_condition": "core spectral lane should reproduce the Wave 13 mechanism response before scaling claims are rerun.",
        "topic_median_xi_growth_ratio": topic["median_xi_growth_ratio"],
        "core_spectral_median_xi_growth_ratio": spectral["median_xi_growth_ratio"],
        "core_spectral_median_order_growth_ratio": spectral["median_order_growth_ratio"],
        "spectral_minus_topic_median_xi_growth_ratio": spectral_minus_topic_xi,
    }
    wave15_repair_gate = {
        "status": (
            "PASS"
            if wave15.get("gates", {}).get("explicit_core_viability_gate", {}).get("status") == "BLOCKED"
            and spectral_mass_stability_gate["status"] == "PASS"
            and topic_engine_bridge_gate["status"] == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "Wave 15 explicit-core stiffness blocker must be addressed by a stable spectral/semi-implicit core path.",
        "wave15_blocker_label": wave15.get("blocker_label"),
        "wave15_explicit_core_viability_gate": wave15.get("gates", {}).get("explicit_core_viability_gate", {}).get("status"),
        "explicit_v1_stable_case_count_under_wave13_settings": explicit["stable_case_count"],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Core spectral integration is not a universality or publication claim.",
        "claim_boundary": "Requires finite-size/exponent gates and formula audit closure before any dynamics or universality claim upgrade.",
    }

    pass_gates = [
        core_spectral_alignment_gate,
        legacy_compatibility_gate,
        spectral_mass_stability_gate,
        topic_engine_bridge_gate,
        mechanism_response_gate,
        wave15_repair_gate,
    ]
    overall_status = "PASS" if all(gate["status"] == "PASS" for gate in pass_gates) else "WARN"
    blocker_label = (
        "conserved_order_spectral_core_candidate_scaling_open"
        if overall_status == "PASS"
        else "conserved_order_spectral_core_candidate_not_yet_bridged"
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
            "role": "core spectral conserved-order candidate implementation",
        },
        {
            "path": relpath(PARAMS_PATH),
            "sha256": hash_file(PARAMS_PATH),
            "role": "candidate mobility/default parameter source",
        },
        {"path": relpath(CORE_TEST_PATH), "sha256": hash_file(CORE_TEST_PATH), "role": "core unit checks"},
        {
            "path": relpath(ENGINE_PHASE_PATH),
            "sha256": hash_file(ENGINE_PHASE_PATH),
            "role": "topic spectral Cahn-Hilliard reference engine",
        },
    ]
    for path, role in [
        (WAVE13_ARTIFACT_PATH, "Wave 13 mechanism controller"),
        (WAVE15_ARTIFACT_PATH, "Wave 15 numerics-gap controller"),
    ]:
        if path.exists():
            inputs.append({"path": relpath(path), "sha256": hash_file(path), "role": role})

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 16 conserved_order_spectral_v1 core candidate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Core_Candidate.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_core_candidate_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_size": [nx, nx],
            "dx": dx,
            "dt": dt,
            "steps": steps,
            "seeds": seeds,
            "candidate_params": {
                "alpha": -1.0,
                "gamma": 1.0,
                "C0": 0.0,
                "beta": 0.0,
                "kappa": 0.002,
                "conserved_order_mobility": 1.0,
            },
        },
        "metrics": {
            "by_lane": by_lane,
            "core_spectral_minus_topic_median_xi_growth_ratio": spectral_minus_topic_xi,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "core_spectral_alignment_gate": core_spectral_alignment_gate,
            "legacy_compatibility_gate": legacy_compatibility_gate,
            "spectral_mass_stability_gate": spectral_mass_stability_gate,
            "topic_engine_bridge_gate": topic_engine_bridge_gate,
            "mechanism_response_gate": mechanism_response_gate,
            "wave15_repair_gate": wave15_repair_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is an opt-in core-candidate diagnostic, not a finite-size scaling result.",
            "The candidate matches the topic spectral engine under normalized 2D settings only.",
            "A PASS authorizes the next scaling verifier; it does not validate a universality-class shift.",
        ],
        "claim_boundary": "Use conserved_order_spectral_v1 as a diagnostic core candidate only until finite-size/exponent gates and formula audit closure pass.",
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
    result = run_spectral_core_candidate_diagnostic()
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
