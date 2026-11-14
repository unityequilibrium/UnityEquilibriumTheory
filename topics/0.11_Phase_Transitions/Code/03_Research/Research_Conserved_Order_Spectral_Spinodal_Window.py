"""
Wave 19 conserved-order spectral spinodal-window diagnostic.

Wave 18 showed a tradeoff: kappa can lift xi/L, but the strongest xi/L case
erased the order signal. This verifier tests a narrower repair hypothesis:
near the spinodal-access boundary, can the opt-in spectral conserved-order core
produce xi/L >= 0.20 while preserving order amplitude?

This is a single-grid diagnostic. It can narrow the window blocker, but it does
not validate finite-size scaling, RG closure, universality shift, or material
claims.
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
    CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
    dynamics_step_complete,
)
from docs.core.uet_parameters import UETParameters  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_spinodal_window.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_spinodal_window_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE18_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_window_repair.json"


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def axis_correlation_length_proxy(C: np.ndarray, dx: float) -> float:
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


def spinodal_margin(temperature: float, kappa: float, grid_L: int, dx: float) -> float:
    """Positive margin means the longest lattice mode is inside the unstable band."""
    longest_mode_k = 2.0 * math.pi / (grid_L * dx)
    return abs(temperature - 1.0) - kappa * longest_mode_k**2


def run_case(
    *,
    label: str,
    repair_family: str,
    replicate_group: str,
    grid_L: int,
    temperature: float,
    steps: int,
    dt: float,
    dx: float,
    kappa: float,
    seed: int,
) -> dict[str, float | int | str | bool]:
    rng = np.random.default_rng(seed)
    C = rng.normal(0.0, 0.01, (grid_L, grid_L, grid_L))
    initial_mean = float(np.mean(C))
    params = UETParameters(
        alpha=temperature - 1.0,
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
    order_parameter = float(np.mean(np.abs(C))) if np.all(np.isfinite(C)) else float("nan")
    xi_over_l = float(xi / domain_length) if math.isfinite(xi) else float("nan")
    margin = spinodal_margin(temperature, kappa, grid_L, dx)
    return {
        "label": label,
        "repair_family": repair_family,
        "replicate_group": replicate_group,
        "grid_L": grid_L,
        "domain_length": float(domain_length),
        "temperature": float(temperature),
        "delta_t": float(1.0 - temperature),
        "steps": steps,
        "dt": float(dt),
        "dx": float(dx),
        "kappa": float(kappa),
        "spinodal_margin": float(margin),
        "seed": seed,
        "status": status,
        "mass_drift_abs": abs(final_mean - initial_mean) if math.isfinite(final_mean) else float("nan"),
        "order_parameter": order_parameter,
        "xi_proxy": float(xi),
        "xi_over_L": xi_over_l,
        "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
        "order_preserving_xi_pass": bool(status == "OK" and xi_over_l >= 0.20 and order_parameter >= 0.005),
    }


def summarize_group(rows: list[dict[str, float | int | str | bool]]) -> dict[str, Any]:
    xi_values = np.array([float(row["xi_over_L"]) for row in rows], dtype=float)
    order_values = np.array([float(row["order_parameter"]) for row in rows], dtype=float)
    pass_count = sum(1 for row in rows if bool(row["order_preserving_xi_pass"]))
    return {
        "case_count": len(rows),
        "pass_count": pass_count,
        "pass_fraction": float(pass_count / len(rows)) if rows else 0.0,
        "min_xi_over_L": float(np.min(xi_values)) if len(xi_values) else float("nan"),
        "median_xi_over_L": float(np.median(xi_values)) if len(xi_values) else float("nan"),
        "max_xi_over_L": float(np.max(xi_values)) if len(xi_values) else float("nan"),
        "min_order_parameter": float(np.min(order_values)) if len(order_values) else float("nan"),
        "median_order_parameter": float(np.median(order_values)) if len(order_values) else float("nan"),
    }


def run_spinodal_window_diagnostic() -> dict[str, Any]:
    grid_L = 16
    dx = 1.0
    dt = 0.05
    xi_threshold = 0.20
    order_floor = 0.005
    target_group = "t0900_k0100_steps2400"

    cases = [
        ("t0890_k0100", "spinodal_window_probe", "adjacent_window", 0.890, 0.100, 1700, 19000),
        ("t0895_k0100", "spinodal_window_probe", "adjacent_window", 0.895, 0.100, 1700, 19001),
        ("t0900_k0100", "spinodal_window_probe", "adjacent_window", 0.900, 0.100, 1700, 19002),
        ("t0905_k0100", "spinodal_window_probe", "adjacent_window", 0.905, 0.100, 1700, 19003),
        ("t0895_k0105", "spinodal_window_probe", "adjacent_window", 0.895, 0.105, 1700, 19004),
        ("t0900_k0105", "spinodal_window_probe", "adjacent_window", 0.900, 0.105, 1700, 19005),
        ("t0900_k0110", "spinodal_window_probe", "adjacent_window", 0.900, 0.110, 1700, 19006),
        ("t0905_k0110", "spinodal_window_probe", "adjacent_window", 0.905, 0.110, 1700, 19007),
        ("t0900_k0100_seed19008", "spinodal_window_replicate", target_group, 0.900, 0.100, 2400, 19008),
        ("t0900_k0100_seed19108", "spinodal_window_replicate", target_group, 0.900, 0.100, 2400, 19108),
        ("t0900_k0100_seed19208", "spinodal_window_replicate", target_group, 0.900, 0.100, 2400, 19208),
        ("t0900_k0100_seed19308", "spinodal_window_replicate", target_group, 0.900, 0.100, 2400, 19308),
    ]
    rows = [
        run_case(
            label=label,
            repair_family=family,
            replicate_group=group,
            grid_L=grid_L,
            temperature=temperature,
            steps=steps,
            dt=dt,
            dx=dx,
            kappa=kappa,
            seed=seed,
        )
        for label, family, group, temperature, kappa, steps, seed in cases
    ]

    stable_rows = [row for row in rows if row["status"] == "OK"]
    positive_margin_rows = [row for row in stable_rows if float(row["spinodal_margin"]) > 0.0]
    viable_rows = [row for row in stable_rows if bool(row["order_preserving_xi_pass"])]
    order_preserving_rows = [row for row in stable_rows if float(row["order_parameter"]) >= order_floor]
    target_rows = [row for row in stable_rows if row["replicate_group"] == target_group]
    best_viable_row = max(viable_rows, key=lambda row: float(row["xi_over_L"])) if viable_rows else None
    best_order_preserving_row = max(order_preserving_rows, key=lambda row: float(row["xi_over_L"]))
    target_summary = summarize_group(target_rows)
    wave18 = load_json(WAVE18_ARTIFACT_PATH) if WAVE18_ARTIFACT_PATH.exists() else {}

    wave18_chain_gate = {
        "status": (
            "PASS"
            if wave18.get("blocker_label") == "spectral_core_xi_window_only_via_low_signal_smoothing"
            else "BLOCKED"
        ),
        "required_condition": "Wave 19 must start from the Wave 18 low-signal smoothing blocker.",
        "wave18_status": wave18.get("status"),
        "wave18_blocker_label": wave18.get("blocker_label"),
    }
    spinodal_access_gate = {
        "status": "PASS" if len(positive_margin_rows) == len(stable_rows) and len(stable_rows) == len(rows) else "BLOCKED",
        "required_condition": "All tested cases should be stable and inside the positive spinodal-access margin.",
        "positive_margin_case_count": len(positive_margin_rows),
        "stable_case_count": len(stable_rows),
        "case_count": len(rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    order_signal_window_gate = {
        "status": "PASS" if viable_rows else "BLOCKED",
        "required_condition": "At least one targeted spinodal-window case must satisfy xi/L and order-signal thresholds together.",
        "xi_threshold": xi_threshold,
        "order_floor": order_floor,
        "viable_case_count": len(viable_rows),
        "best_viable_case": best_viable_row,
        "best_order_preserving_case": best_order_preserving_row,
    }
    seed_margin_gate = {
        "status": "PASS" if target_summary["pass_fraction"] >= 0.75 and target_summary["min_xi_over_L"] >= xi_threshold else "BLOCKED",
        "required_condition": "The candidate window should pass in at least 75% of target-seed replicates and keep every replicate above xi/L threshold.",
        "target_group": target_group,
        "target_summary": target_summary,
        "xi_threshold": xi_threshold,
    }
    finite_size_claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "A single-grid spinodal-window diagnostic cannot validate finite-size scaling or universality.",
        "claim_boundary": "Use this artifact only to choose the next finite-size replication window.",
    }

    if order_signal_window_gate["status"] != "PASS":
        blocker_label = "spectral_core_order_signal_window_not_found"
    elif seed_margin_gate["status"] != "PASS":
        blocker_label = "spectral_core_spinodal_window_seed_margin_not_robust"
    else:
        blocker_label = "spectral_core_spinodal_window_needs_finite_size_replication"

    status = "PASS" if all(
        gate["status"] == "PASS"
        for gate in [wave18_chain_gate, spinodal_access_gate, order_signal_window_gate, seed_margin_gate]
    ) else "WARN"

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
        }
    ]
    if WAVE18_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE18_ARTIFACT_PATH),
                "sha256": hash_file(WAVE18_ARTIFACT_PATH),
                "role": "Wave 18 signal-preservation controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 19 conserved_order_spectral_v1 spinodal-window diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Spinodal_Window.py",
        "status": status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_spinodal_window_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_L": grid_L,
            "dx": dx,
            "dt": dt,
            "xi_threshold": xi_threshold,
            "order_floor": order_floor,
            "case_count": len(rows),
            "target_replicate_group": target_group,
        },
        "metrics": {
            "viable_signal_case_count": len(viable_rows),
            "best_viable_case": best_viable_row,
            "best_order_preserving_case": best_order_preserving_row,
            "target_replicate_summary": target_summary,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave18_chain_gate": wave18_chain_gate,
            "spinodal_access_gate": spinodal_access_gate,
            "order_signal_window_gate": order_signal_window_gate,
            "seed_margin_gate": seed_margin_gate,
            "finite_size_claim_boundary_gate": finite_size_claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted single-grid diagnostic, not a full finite-size scaling sweep.",
            "A single passing seed near the xi/L threshold is only a candidate window, not robust scaling evidence.",
            "The result narrows the next window design; it does not validate material, RG, or universality claims.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims until the spinodal window passes seed-margin and finite-size replication gates.",
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
    result = run_spinodal_window_diagnostic()
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
