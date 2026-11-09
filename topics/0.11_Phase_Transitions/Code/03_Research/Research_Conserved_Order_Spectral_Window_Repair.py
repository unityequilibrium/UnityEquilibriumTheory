"""
Wave 18 conserved-order spectral window-repair diagnostic.

Wave 17 showed that the opt-in spectral conserved-order core is stable, but
its finite-size window remains too local for universality claims. This script
tests two narrow repair hypotheses before any new claim is promoted:

1. Longer relaxation or moving closer to Tc is enough to lift xi/L.
2. Increasing gradient stiffness (kappa) can lift xi/L without erasing the
   order-parameter signal.

The artifact records the tradeoff explicitly. It is diagnostic only.
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
ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_window_repair.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_window_repair_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE17_ARTIFACT_PATH = TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_scaling.json"


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


def run_case(
    *,
    label: str,
    repair_family: str,
    grid_L: int,
    temperature: float,
    steps: int,
    dt: float,
    dx: float,
    kappa: float,
    seed: int,
) -> dict[str, float | int | str]:
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
    return {
        "label": label,
        "repair_family": repair_family,
        "grid_L": grid_L,
        "domain_length": float(domain_length),
        "temperature": float(temperature),
        "delta_t": float(1.0 - temperature),
        "steps": steps,
        "dt": float(dt),
        "dx": float(dx),
        "kappa": float(kappa),
        "seed": seed,
        "status": status,
        "mass_drift_abs": abs(final_mean - initial_mean) if math.isfinite(final_mean) else float("nan"),
        "order_parameter": order_parameter,
        "xi_proxy": float(xi),
        "xi_over_L": float(xi / domain_length) if math.isfinite(xi) else float("nan"),
        "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
    }


def run_window_repair_diagnostic() -> dict[str, Any]:
    grid_L = 16
    dx = 1.0
    dt = 0.05
    baseline_kappa = 0.002
    xi_threshold = 0.20
    order_floor = 0.005

    cases = [
        {
            "label": "wave17_near_baseline",
            "repair_family": "relaxation_window",
            "temperature": 0.985,
            "steps": 850,
            "kappa": baseline_kappa,
            "seed": 18001,
        },
        {
            "label": "wave17_near_long_relaxation",
            "repair_family": "relaxation_window",
            "temperature": 0.985,
            "steps": 3400,
            "kappa": baseline_kappa,
            "seed": 18002,
        },
        {
            "label": "closer_tc_long_relaxation",
            "repair_family": "relaxation_window",
            "temperature": 0.995,
            "steps": 3400,
            "kappa": baseline_kappa,
            "seed": 18003,
        },
        {
            "label": "less_near_tc_long_relaxation",
            "repair_family": "relaxation_window",
            "temperature": 0.970,
            "steps": 3400,
            "kappa": baseline_kappa,
            "seed": 18004,
        },
    ]
    for index, kappa in enumerate([0.0005, 0.002, 0.01, 0.05, 0.1, 0.2], start=1):
        cases.append(
            {
                "label": f"kappa_sweep_{kappa:g}",
                "repair_family": "kappa_window",
                "temperature": 0.985,
                "steps": 1700,
                "kappa": kappa,
                "seed": 18100 + index,
            }
        )

    rows = [
        run_case(
            label=str(case["label"]),
            repair_family=str(case["repair_family"]),
            grid_L=grid_L,
            temperature=float(case["temperature"]),
            steps=int(case["steps"]),
            dt=dt,
            dx=dx,
            kappa=float(case["kappa"]),
            seed=int(case["seed"]),
        )
        for case in cases
    ]

    stable_rows = [row for row in rows if row["status"] == "OK"]
    relaxation_rows = [row for row in stable_rows if row["repair_family"] == "relaxation_window"]
    kappa_rows = [row for row in stable_rows if row["repair_family"] == "kappa_window"]
    viable_signal_rows = [
        row
        for row in stable_rows
        if float(row["xi_over_L"]) >= xi_threshold and float(row["order_parameter"]) >= order_floor
    ]
    xi_pass_rows = [row for row in stable_rows if float(row["xi_over_L"]) >= xi_threshold]

    max_relaxation_xi = float(max(row["xi_over_L"] for row in relaxation_rows))
    max_kappa_xi = float(max(row["xi_over_L"] for row in kappa_rows))
    best_xi_row = max(stable_rows, key=lambda row: float(row["xi_over_L"]))
    best_viable_row = max(
        stable_rows,
        key=lambda row: (
            float(row["xi_over_L"]) if float(row["order_parameter"]) >= order_floor else -1.0
        ),
    )
    wave17 = load_json(WAVE17_ARTIFACT_PATH) if WAVE17_ARTIFACT_PATH.exists() else {}

    wave17_chain_gate = {
        "status": (
            "PASS"
            if wave17.get("blocker_label") == "spectral_core_finite_size_window_not_established"
            else "BLOCKED"
        ),
        "required_condition": "Wave 18 must start from the Wave 17 finite-size-window blocker.",
        "wave17_status": wave17.get("status"),
        "wave17_blocker_label": wave17.get("blocker_label"),
    }
    relaxation_window_repair_gate = {
        "status": "PASS" if max_relaxation_xi >= xi_threshold else "BLOCKED",
        "required_condition": "Longer relaxation or closer-to-Tc temperature should lift xi/L above threshold without parameter changes.",
        "xi_threshold": xi_threshold,
        "max_relaxation_xi_over_L": max_relaxation_xi,
        "tested_cases": [row["label"] for row in relaxation_rows],
    }
    kappa_window_sensitivity_gate = {
        "status": "PASS" if max_kappa_xi >= xi_threshold else "BLOCKED",
        "required_condition": "A kappa sweep should identify whether gradient stiffness can lift xi/L above threshold.",
        "xi_threshold": xi_threshold,
        "max_kappa_xi_over_L": max_kappa_xi,
        "best_xi_label": best_xi_row["label"],
        "best_xi_order_parameter": best_xi_row["order_parameter"],
    }
    signal_preservation_gate = {
        "status": "PASS" if viable_signal_rows else "BLOCKED",
        "required_condition": "A window repair must lift xi/L while preserving order-parameter amplitude >= order_floor.",
        "order_floor": order_floor,
        "xi_threshold": xi_threshold,
        "viable_signal_case_count": len(viable_signal_rows),
        "best_order_preserving_label": best_viable_row["label"],
        "best_order_preserving_xi_over_L": best_viable_row["xi_over_L"],
        "best_order_preserving_order_parameter": best_viable_row["order_parameter"],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Window repair diagnostics do not validate universality or material claims.",
        "claim_boundary": "Treat xi/L gains without preserved signal as smoothing diagnostics, not scaling evidence.",
    }

    pass_gates = [
        wave17_chain_gate,
        relaxation_window_repair_gate,
        kappa_window_sensitivity_gate,
        signal_preservation_gate,
    ]
    overall_status = "PASS" if all(gate["status"] == "PASS" for gate in pass_gates) else "WARN"
    blocker_label = (
        "spectral_core_xi_window_only_via_low_signal_smoothing"
        if kappa_window_sensitivity_gate["status"] == "PASS" and signal_preservation_gate["status"] != "PASS"
        else "spectral_core_relaxation_window_still_insufficient"
        if relaxation_window_repair_gate["status"] != "PASS"
        else "spectral_core_window_repair_scaling_open"
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
            "role": "core spectral conserved-order implementation",
        }
    ]
    if WAVE17_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE17_ARTIFACT_PATH),
                "sha256": hash_file(WAVE17_ARTIFACT_PATH),
                "role": "Wave 17 finite-size-window controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 18 conserved_order_spectral_v1 window-repair diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Window_Repair.py",
        "status": overall_status,
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_window_repair_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_L": grid_L,
            "dx": dx,
            "dt": dt,
            "xi_threshold": xi_threshold,
            "order_floor": order_floor,
            "case_count": len(rows),
        },
        "metrics": {
            "max_relaxation_xi_over_L": max_relaxation_xi,
            "max_kappa_xi_over_L": max_kappa_xi,
            "best_xi_case": best_xi_row,
            "xi_pass_case_count": len(xi_pass_rows),
            "viable_signal_case_count": len(viable_signal_rows),
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave17_chain_gate": wave17_chain_gate,
            "relaxation_window_repair_gate": relaxation_window_repair_gate,
            "kappa_window_sensitivity_gate": kappa_window_sensitivity_gate,
            "signal_preservation_gate": signal_preservation_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted single-grid repair diagnostic, not a replacement for a full finite-size scaling sweep.",
            "High xi/L reached only through very low order-parameter amplitude should be treated as smoothing, not universality evidence.",
            "The result guides the next scaling-window design; it does not validate material or RG closure.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims until xi/L improvement and order-signal preservation pass together in a finite-size artifact.",
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
    result = run_window_repair_diagnostic()
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
