"""
Wave 13 Model C conserved-order diagnostic.

Wave 12 showed that the current spatial_coupled_v2 components remain
correlation-neutral or damping. The inbox analysis also listed Model C
(Cahn-Hilliard conserved order-parameter dynamics) as a different operator
structure: dC/dt = nabla^2(delta Omega / delta C).

This diagnostic does not promote UET phase-transition claims. It asks whether
the existing topic Cahn-Hilliard engine provides the mechanism-level properties
needed before a core operator redesign: mass conservation, domain/correlation
growth, and separation from a nonconserved TDGL comparison lane.
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
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ENGINE_PHASE_PATH = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Phase.py"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_model_c_conserved_order_diagnostic.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_model_c_conserved_order_diagnostic_stats.csv"
WAVE12_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_spatial_coupled_v2_component_ablation.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_phase_engine_class():
    """Load the topic engine by path because the topic directory is not a package name."""
    # Avoid verifier side effects: Engine_Phase inherits UETBaseSolver, which
    # normally creates log folders on construction.
    uet_base_solver.UETBaseSolver._setup_logger = lambda self, *args, **kwargs: setattr(self, "logger", None)
    spec = importlib.util.spec_from_file_location("uet_phase_engine_wave13", ENGINE_PHASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Engine_Phase.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.UETPhaseEngine


def laplacian_2d(C: np.ndarray, dx: float) -> np.ndarray:
    return (
        np.roll(C, 1, axis=0)
        + np.roll(C, -1, axis=0)
        + np.roll(C, 1, axis=1)
        + np.roll(C, -1, axis=1)
        - 4 * C
    ) / dx**2


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


def run_nonconserved_tdgl(
    *,
    initial: np.ndarray,
    alpha: float,
    gamma: float,
    kappa: float,
    dx: float,
    dt: float,
    steps: int,
) -> np.ndarray:
    C = np.array(initial, dtype=float, copy=True)
    for _ in range(steps):
        lap = laplacian_2d(C, dx)
        chemical_potential = alpha * C + gamma * C**3 - kappa * lap
        C = C - dt * chemical_potential
        if not np.all(np.isfinite(C)):
            break
    return C


def run_model_c_engine(
    *,
    engine_cls,
    initial: np.ndarray,
    alpha: float,
    kappa: float,
    dt: float,
    steps: int,
) -> np.ndarray:
    params = UETParameters(kappa=kappa, alpha=alpha, beta=1.0, W_N=0.0, a0_viscosity=0.0)
    engine = engine_cls(nx=initial.shape[0], ny=initial.shape[1], dt=dt, temperature=0.0, params=params)
    engine.logger = None
    engine.C = np.array(initial, dtype=float, copy=True)
    for step in range(steps):
        engine.step(step)
        if not np.all(np.isfinite(engine.C)):
            break
    return np.array(engine.C, dtype=float, copy=True)


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
        "xi_over_L_final": float(final_xi),
        "initial_domain_boundary_count": domain_boundary_count(initial),
        "final_domain_boundary_count": domain_boundary_count(final),
        "max_abs_c": float(np.max(np.abs(final))) if np.all(np.isfinite(final)) else float("nan"),
        "status": "OK" if np.all(np.isfinite(final)) else "UNSTABLE",
    }


def aggregate(rows: list[dict[str, float | int | str]]) -> dict[str, Any]:
    lanes = sorted({str(row["lane"]) for row in rows})
    by_lane: dict[str, Any] = {}
    for lane in lanes:
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


def run_model_c_diagnostic() -> dict[str, Any]:
    engine_cls = load_phase_engine_class()
    nx = 64
    dx = 1.0 / nx
    dt = 0.01
    steps = 500
    seeds = [1301, 1302, 1303]
    alpha = -1.0
    gamma = 1.0
    kappa = 0.002

    rows: list[dict[str, float | int | str]] = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        initial = rng.normal(0.0, 0.01, (nx, nx))
        baseline_final = run_nonconserved_tdgl(
            initial=initial,
            alpha=alpha,
            gamma=gamma,
            kappa=kappa,
            dx=dx,
            dt=dt,
            steps=steps,
        )
        model_c_final = run_model_c_engine(
            engine_cls=engine_cls,
            initial=initial,
            alpha=alpha,
            kappa=kappa,
            dt=dt,
            steps=steps,
        )
        rows.append(summarize_lane("baseline_nonconserved_tdgl", seed, initial, baseline_final, dx))
        rows.append(summarize_lane("model_c_cahn_hilliard", seed, initial, model_c_final, dx))

    by_lane = aggregate(rows)
    baseline = by_lane["baseline_nonconserved_tdgl"]
    model_c = by_lane["model_c_cahn_hilliard"]
    xi_growth_delta = float(model_c["median_xi_growth_ratio"] - baseline["median_xi_growth_ratio"])

    model_c_engine_alignment_gate = {
        "status": "PASS" if ENGINE_PHASE_PATH.exists() else "BLOCKED",
        "required_condition": "Model C diagnostic must use the topic Cahn-Hilliard engine rather than a hidden standalone accepted-equation lane.",
        "engine_path": relpath(ENGINE_PHASE_PATH),
        "engine_class": "UETPhaseEngine",
        "engine_sha256": hash_file(ENGINE_PHASE_PATH),
    }
    mass_conservation_gate = {
        "status": "PASS" if model_c["max_mass_drift_abs"] <= 1e-8 else "BLOCKED",
        "required_condition": "Cahn-Hilliard lane should conserve mean order parameter to <= 1e-8 absolute drift.",
        "model_c_max_mass_drift_abs": model_c["max_mass_drift_abs"],
        "baseline_max_mass_drift_abs": baseline["max_mass_drift_abs"],
    }
    domain_growth_gate = {
        "status": "PASS" if model_c["median_xi_growth_ratio"] >= 1.5 and model_c["median_order_growth_ratio"] >= 5.0 else "BLOCKED",
        "required_condition": "Model C lane should show domain/correlation growth before being used as a repair direction.",
        "model_c_median_xi_growth_ratio": model_c["median_xi_growth_ratio"],
        "model_c_median_order_growth_ratio": model_c["median_order_growth_ratio"],
    }
    operator_distinction_gate = {
        "status": "PASS" if xi_growth_delta >= 0.25 else "BLOCKED",
        "required_condition": "Model C lane should separate from nonconserved TDGL by median xi-growth ratio >= 0.25.",
        "baseline_median_xi_growth_ratio": baseline["median_xi_growth_ratio"],
        "model_c_median_xi_growth_ratio": model_c["median_xi_growth_ratio"],
        "model_c_minus_baseline_xi_growth_ratio": xi_growth_delta,
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Model C mechanism evidence is not a universality or RG closure claim.",
        "claim_boundary": "Mechanism repair direction only; still requires finite-size/exponent gates and core formula integration before stronger claims.",
    }

    overall_status = (
        "PASS"
        if all(
            gate["status"] == "PASS"
            for gate in [
                model_c_engine_alignment_gate,
                mass_conservation_gate,
                domain_growth_gate,
                operator_distinction_gate,
            ]
        )
        else "WARN"
    )
    blocker_label = (
        "model_c_mechanism_promising_scaling_open"
        if overall_status == "PASS"
        else "model_c_mechanism_not_yet_separated"
    )

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    inputs = [
        {
            "path": relpath(ENGINE_PHASE_PATH),
            "sha256": hash_file(ENGINE_PHASE_PATH),
            "role": "topic Model C / Cahn-Hilliard engine",
        }
    ]
    if WAVE12_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE12_ARTIFACT_PATH),
                "sha256": hash_file(WAVE12_ARTIFACT_PATH),
                "role": "Wave 12 v2 component-ablation controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 13 Model C conserved-order diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Model_C_Conserved_Order_Diagnostic.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_mechanism_only",
        "inputs": inputs,
        "parameters": {
            "grid_size": [nx, nx],
            "dx": dx,
            "dt": dt,
            "steps": steps,
            "seeds": seeds,
            "alpha": alpha,
            "gamma": gamma,
            "kappa": kappa,
        },
        "metrics": {
            "by_lane": by_lane,
            "xi_growth_delta_model_c_minus_baseline": xi_growth_delta,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "model_c_engine_alignment_gate": model_c_engine_alignment_gate,
            "mass_conservation_gate": mass_conservation_gate,
            "domain_growth_gate": domain_growth_gate,
            "operator_distinction_gate": operator_distinction_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a normalized 2D mechanism diagnostic, not a 3D universality or material-validation result.",
            "A passing Model C mechanism gate identifies a repair direction; it does not replace finite-size scaling or exponent gates.",
            "The nonconserved TDGL lane is a local comparison lane, not a publication baseline.",
        ],
        "claim_boundary": "Use Model C results only to decide whether a conserved-order operator structure deserves a future opt-in core candidate.",
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
    result = run_model_c_diagnostic()
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
