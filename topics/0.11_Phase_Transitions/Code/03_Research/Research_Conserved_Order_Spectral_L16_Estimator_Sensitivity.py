"""
Wave 23 conserved-order spectral L16 estimator-sensitivity diagnostic.

Wave 22 showed that longer L16 relaxation preserves order amplitude but leaves
the fresh-seed xi/L margin below the declared threshold. This verifier asks a
narrower question before changing dynamics: how much of that blocker depends on
the current axis-autocorrelation crossing threshold?

This is an estimator-design diagnostic only. A threshold-sensitive pass is not a
physics pass unless the estimator threshold is independently derived and then
rerun through finite-size, exponent, material, and RG gates.
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
ARTIFACT_PATH = (
    TOPIC_DIR
    / "Result"
    / "artifacts"
    / "0_11_conserved_order_spectral_l16_estimator_sensitivity.json"
)
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_l16_estimator_sensitivity_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE19_SCRIPT_PATH = (
    TOPIC_DIR / "Code" / "03_Research" / "Research_Conserved_Order_Spectral_Spinodal_Window.py"
)
WAVE22_ARTIFACT_PATH = (
    TOPIC_DIR / "Result" / "artifacts" / "0_11_conserved_order_spectral_l16_relaxation_repair.json"
)


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def axis_correlation_length_proxy(
    C: np.ndarray,
    dx: float,
    *,
    threshold: float,
) -> tuple[float, bool, list[float]]:
    field = np.asarray(C, dtype=float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return 0.0, True, [0.0]

    spectrum = np.fft.fftn(centered)
    autocorr = np.fft.ifftn(np.abs(spectrum) ** 2).real / centered.size
    autocorr = autocorr / max(float(autocorr[(0,) * field.ndim]), 1e-14)
    max_r = min(field.shape) // 2

    axis_corr: list[float] = []
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
                return radius * dx, True, axis_corr
            fraction = (previous - threshold) / (previous - current)
            return ((radius - 1) + max(0.0, min(1.0, fraction))) * dx, True, axis_corr
    return max_r * dx, False, axis_corr


def spinodal_margin(temperature: float, kappa: float, grid_L: int, dx: float) -> float:
    longest_mode_k = 2.0 * math.pi / (grid_L * dx)
    return abs(temperature - 1.0) - kappa * longest_mode_k**2


def simulate_final_field(
    *,
    grid_L: int,
    temperature: float,
    steps: int,
    dt: float,
    dx: float,
    kappa: float,
    seed: int,
) -> tuple[str, np.ndarray, float, float]:
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
    mass_drift = abs(final_mean - initial_mean) if math.isfinite(final_mean) else float("nan")
    order_parameter = float(np.mean(np.abs(C))) if np.all(np.isfinite(C)) else float("nan")
    return status, C, mass_drift, order_parameter


def summarize_rows(rows: list[dict[str, float | int | str | bool]]) -> dict[str, Any]:
    xi_values = np.array([float(row["xi_over_L"]) for row in rows], dtype=float)
    order_values = np.array([float(row["order_parameter"]) for row in rows], dtype=float)
    pass_count = sum(1 for row in rows if bool(row["order_preserving_xi_pass"]))
    crossed_count = sum(1 for row in rows if bool(row["threshold_crossed"]))
    return {
        "case_count": len(rows),
        "pass_count": pass_count,
        "pass_fraction": float(pass_count / len(rows)) if rows else 0.0,
        "threshold_crossed_count": crossed_count,
        "threshold_saturated_count": len(rows) - crossed_count,
        "min_xi_over_L": float(np.min(xi_values)) if len(xi_values) else float("nan"),
        "median_xi_over_L": float(np.median(xi_values)) if len(xi_values) else float("nan"),
        "max_xi_over_L": float(np.max(xi_values)) if len(xi_values) else float("nan"),
        "min_order_parameter": float(np.min(order_values)) if len(order_values) else float("nan"),
        "median_order_parameter": float(np.median(order_values)) if len(order_values) else float("nan"),
    }


def run_l16_estimator_sensitivity_diagnostic() -> dict[str, Any]:
    wave22 = load_json(WAVE22_ARTIFACT_PATH) if WAVE22_ARTIFACT_PATH.exists() else {}

    grid_L = 16
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    seeds = [21001, 21002, 21003]
    step_groups = [4000, 4800, 5600]
    xi_gate_threshold = 0.20
    order_floor = 0.005
    estimator_thresholds = [
        ("default_exp_minus_1", math.exp(-1.0)),
        ("lower_0_30", 0.30),
        ("lower_0_25", 0.25),
        ("lower_0_20", 0.20),
    ]

    rows: list[dict[str, float | int | str | bool]] = []
    case_records: list[dict[str, Any]] = []
    for steps in step_groups:
        for seed in seeds:
            status, C, mass_drift, order_parameter = simulate_final_field(
                grid_L=grid_L,
                temperature=temperature,
                steps=steps,
                dt=dt,
                dx=dx,
                kappa=kappa,
                seed=seed,
            )
            domain_length = grid_L * dx
            max_abs_c = float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan")
            margin = spinodal_margin(temperature, kappa, grid_L, dx)
            case_record = {
                "label": f"L16_s{steps}_fresh_seed{seed}",
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
                "mass_drift_abs": mass_drift,
                "order_parameter": order_parameter,
                "max_abs_c": max_abs_c,
            }
            case_records.append(case_record)

            for threshold_label, threshold in estimator_thresholds:
                xi, threshold_crossed, axis_corr = (
                    axis_correlation_length_proxy(C, dx, threshold=threshold)
                    if np.all(np.isfinite(C))
                    else (float("nan"), False, [])
                )
                xi_over_l = float(xi / domain_length) if math.isfinite(xi) else float("nan")
                rows.append(
                    {
                        **case_record,
                        "threshold_label": threshold_label,
                        "estimator_threshold": float(threshold),
                        "axis_corr_radius_1": float(axis_corr[1]) if len(axis_corr) > 1 else float("nan"),
                        "axis_corr_radius_2": float(axis_corr[2]) if len(axis_corr) > 2 else float("nan"),
                        "axis_corr_radius_3": float(axis_corr[3]) if len(axis_corr) > 3 else float("nan"),
                        "axis_corr_radius_4": float(axis_corr[4]) if len(axis_corr) > 4 else float("nan"),
                        "threshold_crossed": bool(threshold_crossed),
                        "xi_proxy": float(xi),
                        "xi_over_L": xi_over_l,
                        "order_preserving_xi_pass": bool(
                            status == "OK"
                            and xi_over_l >= xi_gate_threshold
                            and order_parameter >= order_floor
                        ),
                    }
                )

    stable_case_count = sum(1 for case in case_records if case["status"] == "OK")
    positive_margin_count = sum(1 for case in case_records if float(case["spinodal_margin"]) > 0.0)
    by_threshold = {
        threshold_label: summarize_rows([row for row in rows if row["threshold_label"] == threshold_label])
        for threshold_label, _ in estimator_thresholds
    }
    by_steps_and_threshold = {
        str(steps): {
            threshold_label: summarize_rows(
                [
                    row
                    for row in rows
                    if int(row["steps"]) == steps and row["threshold_label"] == threshold_label
                ]
            )
            for threshold_label, _ in estimator_thresholds
        }
        for steps in step_groups
    }
    default_summary = by_threshold["default_exp_minus_1"]
    default_by_steps = {
        str(steps): by_steps_and_threshold[str(steps)]["default_exp_minus_1"]
        for steps in step_groups
    }
    nondefault_summaries = {
        label: summary
        for label, summary in by_threshold.items()
        if label != "default_exp_minus_1"
    }
    best_nondefault_label = max(
        nondefault_summaries,
        key=lambda label: (
            nondefault_summaries[label]["pass_fraction"],
            nondefault_summaries[label]["min_xi_over_L"],
        ),
    )
    best_nondefault_summary = nondefault_summaries[best_nondefault_label]
    sensitivity_detected = any(
        summary["pass_count"] != default_summary["pass_count"]
        or abs(float(summary["min_xi_over_L"]) - float(default_summary["min_xi_over_L"])) >= 0.002
        for summary in nondefault_summaries.values()
    )

    wave22_by_steps = wave22.get("metrics", {}).get("by_steps", {})
    reproduced_steps = {}
    for steps in step_groups:
        key = str(steps)
        current = default_by_steps[key]
        previous = wave22_by_steps.get(key, {})
        reproduced_steps[key] = {
            "current_pass_count": current["pass_count"],
            "wave22_pass_count": previous.get("pass_count"),
            "current_min_xi_over_L": current["min_xi_over_L"],
            "wave22_min_xi_over_L": previous.get("min_xi_over_L"),
            "matches_pass_count": current["pass_count"] == previous.get("pass_count"),
            "matches_min_xi_over_L": (
                abs(float(current["min_xi_over_L"]) - float(previous.get("min_xi_over_L", float("nan"))))
                <= 1e-9
            ),
        }
    default_reproduces_wave22 = all(
        bool(record["matches_pass_count"]) and bool(record["matches_min_xi_over_L"])
        for record in reproduced_steps.values()
    )

    wave22_chain_gate = {
        "status": (
            "PASS"
            if wave22.get("blocker_label") == "spectral_core_l16_relaxation_only_repair_blocked"
            else "BLOCKED"
        ),
        "required_condition": "Wave 23 must start from the Wave 22 relaxation-only blocker.",
        "wave22_status": wave22.get("status"),
        "wave22_blocker_label": wave22.get("blocker_label"),
    }
    engine_path_gate = {
        "status": "PASS",
        "required_condition": "The diagnostic must generate fields through docs.core.uet_master_equation.dynamics_step_complete.",
        "operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }
    estimator_case_coverage_gate = {
        "status": (
            "PASS"
            if stable_case_count == len(case_records) and positive_margin_count == len(case_records)
            else "BLOCKED"
        ),
        "required_condition": "All L16 fresh-seed cases must remain stable and inside the positive spinodal-margin window.",
        "case_count": len(case_records),
        "stable_case_count": stable_case_count,
        "positive_margin_case_count": positive_margin_count,
        "minimum_spinodal_margin": float(min(float(case["spinodal_margin"]) for case in case_records)),
    }
    default_estimator_reproduction_gate = {
        "status": "PASS" if default_reproduces_wave22 else "BLOCKED",
        "required_condition": "The default e^-1 estimator threshold must reproduce the Wave 22 blocker before threshold sensitivity is interpreted.",
        "threshold_label": "default_exp_minus_1",
        "threshold": math.exp(-1.0),
        "reproduced_steps": reproduced_steps,
        "default_by_steps": default_by_steps,
    }
    threshold_sensitivity_gate = {
        "status": "PASS" if sensitivity_detected else "BLOCKED",
        "required_condition": "Changing only the autocorrelation crossing threshold should be recorded if it alters the L16 xi/L gate outcome.",
        "default_summary": default_summary,
        "best_nondefault_threshold_label": best_nondefault_label,
        "best_nondefault_summary": best_nondefault_summary,
        "by_threshold": by_threshold,
        "interpretation": (
            "Threshold sensitivity is an estimator-design finding only; it does not validate the dynamics claim."
        ),
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not accept a non-default threshold until it has a derivation or calibration and is rerun through finite-size/exponent gates.",
        "claim_boundary": "Next work should derive/calibrate the correlation estimator or redesign the finite-size window before universality tests.",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic cannot validate exponent, material, RG, or universality claims.",
        "claim_boundary": "Estimator sensitivity can narrow the blocker but cannot upgrade the spectral core candidate.",
    }

    blocker_label = (
        "spectral_core_l16_xi_gate_threshold_sensitive"
        if sensitivity_detected
        else "spectral_core_l16_estimator_threshold_sensitivity_not_sufficient"
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
        },
        {
            "path": relpath(WAVE19_SCRIPT_PATH),
            "sha256": hash_file(WAVE19_SCRIPT_PATH),
            "role": "source of the default axis-autocorrelation estimator formula",
        },
    ]
    if WAVE22_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE22_ARTIFACT_PATH),
                "sha256": hash_file(WAVE22_ARTIFACT_PATH),
                "role": "Wave 22 relaxation-only controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 23 conserved_order_spectral_v1 L16 estimator-sensitivity diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_L16_Estimator_Sensitivity.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_l16_estimator_sensitivity_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_L": grid_L,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "seeds": seeds,
            "step_groups": step_groups,
            "xi_gate_threshold": xi_gate_threshold,
            "order_floor": order_floor,
            "estimator_thresholds": [
                {"label": label, "threshold": value} for label, value in estimator_thresholds
            ],
            "case_count": len(case_records),
            "csv_row_count": len(rows),
        },
        "metrics": {
            "by_threshold": by_threshold,
            "by_steps_and_threshold": by_steps_and_threshold,
            "default_summary": default_summary,
            "best_nondefault_threshold_label": best_nondefault_label,
            "best_nondefault_summary": best_nondefault_summary,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave22_chain_gate": wave22_chain_gate,
            "engine_path_gate": engine_path_gate,
            "estimator_case_coverage_gate": estimator_case_coverage_gate,
            "default_estimator_reproduction_gate": default_estimator_reproduction_gate,
            "threshold_sensitivity_gate": threshold_sensitivity_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted L16 estimator-threshold diagnostic, not a finite-size scaling rerun.",
            "A non-default threshold cannot be accepted from this artifact alone; it needs derivation or calibration.",
            "The result must not be used as material validation, RG closure, or a universality-class claim.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims from estimator-threshold sensitivity.",
        "environment": {
            "python_version": sys.version.split()[0],
            "numpy_version": np.__version__,
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_l16_estimator_sensitivity_diagnostic()
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"Wrote {ARTIFACT_PATH}")
