"""
Wave 24 conserved-order spectral L16 structure-factor estimator diagnostic.

Wave 23 showed that the L16 fresh-seed xi/L gate is sensitive to the
axis-autocorrelation crossing threshold. This verifier keeps the dynamics fixed
and adds a threshold-free Fourier-domain characteristic-length proxy:

    xi_sf = 2*pi / sqrt(<k^2>_S)

where <k^2>_S is the power-spectrum-weighted mean nonzero wave-number squared.

This is an estimator-design diagnostic only. A passing structure-factor margin
does not validate finite-size scaling, exponent behavior, material calibration,
or RG closure unless it is rerun through the appropriate gates.
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

from docs.core.uet_master_equation import CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE  # noqa: E402


TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_PATH = (
    TOPIC_DIR
    / "Result"
    / "artifacts"
    / "0_11_conserved_order_spectral_l16_structure_factor_estimator.json"
)
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_l16_structure_factor_estimator_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
FORMULA_AUDIT_PATH = TOPIC_DIR / "FORMULA_AUDIT.md"
WAVE23_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_L16_Estimator_Sensitivity.py"
)
WAVE23_ARTIFACT_PATH = (
    TOPIC_DIR
    / "Result"
    / "artifacts"
    / "0_11_conserved_order_spectral_l16_estimator_sensitivity.json"
)


def load_wave23_helpers():
    spec = importlib.util.spec_from_file_location("wave23_estimator_sensitivity", WAVE23_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Wave 23 helper script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def structure_factor_rms_length(C: np.ndarray, dx: float) -> dict[str, float | bool]:
    """Return a threshold-free characteristic length from nonzero Fourier power."""
    field = np.asarray(C, dtype=float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return {
            "xi_proxy": 0.0,
            "total_power": 0.0,
            "mean_k2": float("nan"),
            "rms_k": float("nan"),
            "valid": False,
        }

    spectrum = np.fft.fftn(centered)
    power = np.abs(spectrum) ** 2
    power[(0,) * field.ndim] = 0.0
    total_power = float(np.sum(power))
    if total_power <= 1e-30:
        return {
            "xi_proxy": 0.0,
            "total_power": total_power,
            "mean_k2": float("nan"),
            "rms_k": float("nan"),
            "valid": False,
        }

    k2 = np.zeros(field.shape, dtype=float)
    for axis, size in enumerate(field.shape):
        freq = 2.0 * math.pi * np.fft.fftfreq(size, d=dx)
        shape = [1] * field.ndim
        shape[axis] = size
        k2 += freq.reshape(shape) ** 2

    mean_k2 = float(np.sum(power * k2) / total_power)
    rms_k = math.sqrt(mean_k2) if mean_k2 > 0.0 else float("nan")
    xi_proxy = float(2.0 * math.pi / rms_k) if math.isfinite(rms_k) and rms_k > 0.0 else 0.0
    return {
        "xi_proxy": xi_proxy,
        "total_power": total_power,
        "mean_k2": mean_k2,
        "rms_k": rms_k,
        "valid": bool(math.isfinite(xi_proxy) and xi_proxy > 0.0),
    }


def summarize_metric(rows: list[dict[str, Any]], *, xi_key: str, pass_key: str) -> dict[str, Any]:
    xi_values = np.array([float(row[xi_key]) for row in rows], dtype=float)
    order_values = np.array([float(row["order_parameter"]) for row in rows], dtype=float)
    pass_count = sum(1 for row in rows if bool(row[pass_key]))
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


def run_l16_structure_factor_estimator_diagnostic() -> dict[str, Any]:
    wave23_helpers = load_wave23_helpers()
    wave23 = load_json(WAVE23_ARTIFACT_PATH) if WAVE23_ARTIFACT_PATH.exists() else {}

    grid_L = 16
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    seeds = [21001, 21002, 21003]
    step_groups = [4000, 4800, 5600]
    xi_gate_threshold = 0.20
    order_floor = 0.005
    lower_axis_threshold = 0.30

    rows: list[dict[str, Any]] = []
    for steps in step_groups:
        for seed in seeds:
            status, C, mass_drift, order_parameter = wave23_helpers.simulate_final_field(
                grid_L=grid_L,
                temperature=temperature,
                steps=steps,
                dt=dt,
                dx=dx,
                kappa=kappa,
                seed=seed,
            )
            domain_length = grid_L * dx
            axis_default_xi, axis_default_crossed, _ = wave23_helpers.axis_correlation_length_proxy(
                C,
                dx,
                threshold=math.exp(-1.0),
            )
            axis_lower_xi, axis_lower_crossed, _ = wave23_helpers.axis_correlation_length_proxy(
                C,
                dx,
                threshold=lower_axis_threshold,
            )
            sf = structure_factor_rms_length(C, dx)
            sf_xi = float(sf["xi_proxy"])
            sf_xi_over_l = float(sf_xi / domain_length) if math.isfinite(sf_xi) else float("nan")
            axis_default_xi_over_l = float(axis_default_xi / domain_length)
            axis_lower_xi_over_l = float(axis_lower_xi / domain_length)
            row = {
                "label": f"L16_s{steps}_fresh_seed{seed}",
                "grid_L": grid_L,
                "domain_length": float(domain_length),
                "temperature": float(temperature),
                "delta_t": float(1.0 - temperature),
                "steps": steps,
                "dt": float(dt),
                "dx": float(dx),
                "kappa": float(kappa),
                "spinodal_margin": float(
                    wave23_helpers.spinodal_margin(temperature, kappa, grid_L, dx)
                ),
                "seed": seed,
                "status": status,
                "mass_drift_abs": mass_drift,
                "order_parameter": order_parameter,
                "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
                "axis_default_threshold": float(math.exp(-1.0)),
                "axis_default_crossed": bool(axis_default_crossed),
                "axis_default_xi_proxy": float(axis_default_xi),
                "axis_default_xi_over_L": axis_default_xi_over_l,
                "axis_default_pass": bool(
                    status == "OK"
                    and axis_default_xi_over_l >= xi_gate_threshold
                    and order_parameter >= order_floor
                ),
                "axis_lower_threshold": lower_axis_threshold,
                "axis_lower_crossed": bool(axis_lower_crossed),
                "axis_lower_xi_proxy": float(axis_lower_xi),
                "axis_lower_xi_over_L": axis_lower_xi_over_l,
                "axis_lower_pass": bool(
                    status == "OK"
                    and axis_lower_xi_over_l >= xi_gate_threshold
                    and order_parameter >= order_floor
                ),
                "structure_factor_xi_proxy": sf_xi,
                "structure_factor_xi_over_L": sf_xi_over_l,
                "structure_factor_total_power": float(sf["total_power"]),
                "structure_factor_mean_k2": float(sf["mean_k2"]),
                "structure_factor_rms_k": float(sf["rms_k"]),
                "structure_factor_valid": bool(sf["valid"]),
                "structure_factor_pass": bool(
                    status == "OK"
                    and bool(sf["valid"])
                    and sf_xi_over_l >= xi_gate_threshold
                    and order_parameter >= order_floor
                ),
            }
            rows.append(row)

    stable_rows = [row for row in rows if row["status"] == "OK"]
    positive_margin_rows = [row for row in stable_rows if float(row["spinodal_margin"]) > 0.0]
    sf_valid_rows = [row for row in stable_rows if bool(row["structure_factor_valid"])]

    by_steps = {
        str(steps): {
            "axis_default": summarize_metric(
                [row for row in stable_rows if int(row["steps"]) == steps],
                xi_key="axis_default_xi_over_L",
                pass_key="axis_default_pass",
            ),
            "axis_lower_0_30": summarize_metric(
                [row for row in stable_rows if int(row["steps"]) == steps],
                xi_key="axis_lower_xi_over_L",
                pass_key="axis_lower_pass",
            ),
            "structure_factor_rms": summarize_metric(
                [row for row in stable_rows if int(row["steps"]) == steps],
                xi_key="structure_factor_xi_over_L",
                pass_key="structure_factor_pass",
            ),
        }
        for steps in step_groups
    }
    overall = {
        "axis_default": summarize_metric(
            stable_rows,
            xi_key="axis_default_xi_over_L",
            pass_key="axis_default_pass",
        ),
        "axis_lower_0_30": summarize_metric(
            stable_rows,
            xi_key="axis_lower_xi_over_L",
            pass_key="axis_lower_pass",
        ),
        "structure_factor_rms": summarize_metric(
            stable_rows,
            xi_key="structure_factor_xi_over_L",
            pass_key="structure_factor_pass",
        ),
    }

    wave23_by_steps = wave23.get("metrics", {}).get("by_steps_and_threshold", {})
    reproduced_steps = {}
    for steps in step_groups:
        key = str(steps)
        current = by_steps[key]["axis_default"]
        previous = wave23_by_steps.get(key, {}).get("default_exp_minus_1", {})
        reproduced_steps[key] = {
            "current_pass_count": current["pass_count"],
            "wave23_pass_count": previous.get("pass_count"),
            "current_min_xi_over_L": current["min_xi_over_L"],
            "wave23_min_xi_over_L": previous.get("min_xi_over_L"),
            "matches_pass_count": current["pass_count"] == previous.get("pass_count"),
            "matches_min_xi_over_L": (
                abs(float(current["min_xi_over_L"]) - float(previous.get("min_xi_over_L", float("nan"))))
                <= 1e-9
            ),
        }
    default_reproduces_wave23 = all(
        bool(record["matches_pass_count"]) and bool(record["matches_min_xi_over_L"])
        for record in reproduced_steps.values()
    )

    sf_summary = overall["structure_factor_rms"]
    sf_margin_passes = (
        sf_summary["pass_fraction"] >= 0.75
        and sf_summary["min_xi_over_L"] >= xi_gate_threshold
        and sf_summary["min_order_parameter"] >= order_floor
    )
    sf_domain_scale_risk = float(sf_summary["max_xi_over_L"]) >= 0.50
    estimator_disagrees = (
        overall["axis_default"]["pass_count"] != sf_summary["pass_count"]
        or abs(float(overall["axis_default"]["min_xi_over_L"]) - float(sf_summary["min_xi_over_L"]))
        >= 0.02
    )

    wave23_chain_gate = {
        "status": (
            "PASS"
            if wave23.get("blocker_label") == "spectral_core_l16_xi_gate_threshold_sensitive"
            else "BLOCKED"
        ),
        "required_condition": "Wave 24 must start from the Wave 23 estimator-threshold sensitivity blocker.",
        "wave23_status": wave23.get("status"),
        "wave23_blocker_label": wave23.get("blocker_label"),
    }
    engine_path_gate = {
        "status": "PASS",
        "required_condition": "The diagnostic must generate fields through docs.core.uet_master_equation via the Wave 23 helper.",
        "operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }
    estimator_case_coverage_gate = {
        "status": (
            "PASS"
            if len(stable_rows) == len(rows)
            and len(positive_margin_rows) == len(rows)
            and len(sf_valid_rows) == len(rows)
            else "BLOCKED"
        ),
        "required_condition": "All L16 fresh-seed cases must stay stable, positive-margin, and structure-factor measurable.",
        "case_count": len(rows),
        "stable_case_count": len(stable_rows),
        "positive_margin_case_count": len(positive_margin_rows),
        "structure_factor_valid_case_count": len(sf_valid_rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    default_estimator_reproduction_gate = {
        "status": "PASS" if default_reproduces_wave23 else "BLOCKED",
        "required_condition": "The default e^-1 axis estimator must reproduce Wave 23 before the structure-factor comparison is interpreted.",
        "reproduced_steps": reproduced_steps,
        "current_default_summary": overall["axis_default"],
    }
    structure_factor_margin_gate = {
        "status": "PASS" if sf_margin_passes else "BLOCKED",
        "required_condition": "The threshold-free structure-factor RMS length should keep at least 75% of cases above xi/L and order thresholds before it can be used as a candidate estimator.",
        "xi_gate_threshold": xi_gate_threshold,
        "order_floor": order_floor,
        "structure_factor_summary": sf_summary,
    }
    domain_scale_guard_gate = {
        "status": "WARN" if sf_domain_scale_risk else "PASS",
        "required_condition": "A single-grid structure-factor length near the domain scale must be treated as finite-size calibration risk, not accepted critical scaling.",
        "warning_threshold_xi_over_L": 0.50,
        "structure_factor_summary": sf_summary,
        "interpretation": (
            "xi/L above the warning threshold can be useful for detecting long-wavelength structure, "
            "but it requires multi-grid calibration before exponent or universality claims."
        ),
    }
    estimator_disagreement_gate = {
        "status": "WARN" if estimator_disagrees else "PASS",
        "required_condition": "Estimator disagreement must keep the claim boundary conservative.",
        "axis_default_summary": overall["axis_default"],
        "axis_lower_0_30_summary": overall["axis_lower_0_30"],
        "structure_factor_summary": sf_summary,
        "interpretation": "A structure-factor margin is an estimator-design result, not a finite-size scaling proof.",
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not promote dynamics claims until the candidate estimator is documented and rerun through multi-grid finite-size/exponent gates.",
        "claim_boundary": (
            "Next work should run a multi-grid finite-size replication using the threshold-free estimator "
            "or calibrate it against a source-backed benchmark before exponent claims."
        ),
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic cannot validate exponent, material, RG, or universality claims.",
        "claim_boundary": "A threshold-free structure-factor margin narrows estimator design only.",
    }

    if sf_margin_passes and sf_domain_scale_risk:
        blocker_label = "spectral_core_l16_structure_factor_domain_scale_needs_multigrid_calibration"
    elif sf_margin_passes:
        blocker_label = "spectral_core_l16_structure_factor_margin_observed_needs_finite_size_rerun"
    else:
        blocker_label = "spectral_core_l16_structure_factor_margin_not_confirmed"

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
            "path": relpath(WAVE23_SCRIPT_PATH),
            "sha256": hash_file(WAVE23_SCRIPT_PATH),
            "role": "Wave 23 field generator and axis-estimator helper",
        },
        {
            "path": relpath(FORMULA_AUDIT_PATH),
            "sha256": hash_file(FORMULA_AUDIT_PATH),
            "role": "local audit note requiring structure-factor/correlation-length supplementation",
        },
    ]
    if WAVE23_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE23_ARTIFACT_PATH),
                "sha256": hash_file(WAVE23_ARTIFACT_PATH),
                "role": "Wave 23 estimator-threshold sensitivity controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 24 conserved_order_spectral_v1 L16 structure-factor estimator diagnostic",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_l16_structure_factor_estimator_only",
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
            "axis_default_threshold": math.exp(-1.0),
            "axis_lower_threshold": lower_axis_threshold,
            "structure_factor_formula": "xi_sf = 2*pi / sqrt(sum(S(k)*k^2)/sum(S(k))) over nonzero FFT modes",
            "case_count": len(rows),
        },
        "metrics": {
            "overall": overall,
            "by_steps": by_steps,
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave23_chain_gate": wave23_chain_gate,
            "engine_path_gate": engine_path_gate,
            "estimator_case_coverage_gate": estimator_case_coverage_gate,
            "default_estimator_reproduction_gate": default_estimator_reproduction_gate,
            "structure_factor_margin_gate": structure_factor_margin_gate,
            "domain_scale_guard_gate": domain_scale_guard_gate,
            "estimator_disagreement_gate": estimator_disagreement_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a targeted L16 threshold-free estimator diagnostic, not a finite-size scaling rerun.",
            "The structure-factor RMS length is a characteristic-length proxy and is not by itself an accepted critical correlation length.",
            "The result must not be used as material validation, RG closure, or a universality-class claim.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims from a single-grid structure-factor estimator diagnostic.",
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
    result = run_l16_structure_factor_estimator_diagnostic()
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"Wrote {ARTIFACT_PATH}")
