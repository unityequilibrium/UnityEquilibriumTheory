"""
Wave 25 conserved-order spectral structure-factor multi-grid calibration.

Wave 24 showed that a threshold-free structure-factor RMS length sees
long-wavelength structure in the L=16 fresh-seed fields, but the value is near
the single-grid domain scale. This verifier reruns the same normalized target
window over L=8, 12, and 16 with the Wave 20 and fresh seed sets.

The goal is not to promote the estimator. The goal is to decide whether the
structure-factor length behaves like a calibratable finite-size diagnostic or a
domain-scale/saturation proxy that still needs a larger-grid or source-backed
estimator benchmark before exponent claims.
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
    / "0_11_conserved_order_spectral_structure_factor_multigrid_calibration.json"
)
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_structure_factor_multigrid_calibration_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE24_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py"
)
WAVE24_ARTIFACT_PATH = (
    TOPIC_DIR
    / "Result"
    / "artifacts"
    / "0_11_conserved_order_spectral_l16_structure_factor_estimator.json"
)
INBOX_ALIGNMENT_ARTIFACT_PATH = ROOT / "docs" / "core" / "artifacts" / "inbox_research_alignment_gate.json"


def load_wave24_helpers():
    spec = importlib.util.spec_from_file_location("wave24_structure_factor_estimator", WAVE24_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Wave 24 helper script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_metric(rows: list[dict[str, Any]], *, xi_key: str, pass_key: str) -> dict[str, Any]:
    xi_values = np.array([float(row[xi_key]) for row in rows], dtype=float)
    xi_abs_values = np.array(
        [float(row[xi_key.replace("_over_L", "_proxy")]) for row in rows],
        dtype=float,
    )
    order_values = np.array([float(row["order_parameter"]) for row in rows], dtype=float)
    pass_count = sum(1 for row in rows if bool(row[pass_key]))
    return {
        "case_count": len(rows),
        "pass_count": pass_count,
        "pass_fraction": float(pass_count / len(rows)) if rows else 0.0,
        "min_xi_over_L": float(np.min(xi_values)) if len(xi_values) else float("nan"),
        "median_xi_over_L": float(np.median(xi_values)) if len(xi_values) else float("nan"),
        "max_xi_over_L": float(np.max(xi_values)) if len(xi_values) else float("nan"),
        "median_xi_proxy": float(np.median(xi_abs_values)) if len(xi_abs_values) else float("nan"),
        "min_order_parameter": float(np.min(order_values)) if len(order_values) else float("nan"),
        "median_order_parameter": float(np.median(order_values)) if len(order_values) else float("nan"),
    }


def log_slope(xs: list[float], ys: list[float]) -> dict[str, float]:
    x = np.log(np.asarray(xs, dtype=float))
    y = np.log(np.asarray(ys, dtype=float))
    coeffs = np.polyfit(x, y, 1)
    pred = coeffs[0] * x + coeffs[1]
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
    return {
        "slope": float(coeffs[0]),
        "intercept": float(coeffs[1]),
        "r2": float(1.0 - ss_res / ss_tot) if ss_tot > 1e-14 else 1.0,
    }


def run_structure_factor_multigrid_calibration() -> dict[str, Any]:
    wave24_helpers = load_wave24_helpers()
    wave23_helpers = wave24_helpers.load_wave23_helpers()
    wave24 = load_json(WAVE24_ARTIFACT_PATH) if WAVE24_ARTIFACT_PATH.exists() else {}
    inbox_alignment = (
        load_json(INBOX_ALIGNMENT_ARTIFACT_PATH) if INBOX_ALIGNMENT_ARTIFACT_PATH.exists() else {}
    )

    grid_sizes = [8, 12, 16]
    seed_sets = {
        "wave20_seed_set": [20001, 20002, 20003],
        "fresh_seed_set": [21001, 21002, 21003],
    }
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    steps = 4000
    xi_gate_threshold = 0.20
    order_floor = 0.005
    domain_scale_warning_threshold = 0.50
    lower_axis_threshold = 0.30

    rows: list[dict[str, Any]] = []
    for grid_L in grid_sizes:
        for seed_set_label, seeds in seed_sets.items():
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
                sf = wave24_helpers.structure_factor_rms_length(C, dx)
                axis_default_xi_over_l = float(axis_default_xi / domain_length)
                axis_lower_xi_over_l = float(axis_lower_xi / domain_length)
                sf_xi = float(sf["xi_proxy"])
                sf_xi_over_l = float(sf_xi / domain_length) if math.isfinite(sf_xi) else float("nan")
                rows.append(
                    {
                        "label": f"L{grid_L}_{seed_set_label}_seed{seed}",
                        "grid_L": grid_L,
                        "domain_length": float(domain_length),
                        "seed_set": seed_set_label,
                        "seed": seed,
                        "temperature": float(temperature),
                        "delta_t": float(1.0 - temperature),
                        "steps": steps,
                        "dt": float(dt),
                        "dx": float(dx),
                        "kappa": float(kappa),
                        "spinodal_margin": float(
                            wave23_helpers.spinodal_margin(temperature, kappa, grid_L, dx)
                        ),
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
                )

    stable_rows = [row for row in rows if row["status"] == "OK"]
    positive_margin_rows = [row for row in stable_rows if float(row["spinodal_margin"]) > 0.0]
    sf_valid_rows = [row for row in stable_rows if bool(row["structure_factor_valid"])]

    by_grid: dict[str, Any] = {}
    for grid_L in grid_sizes:
        grid_rows = [row for row in stable_rows if int(row["grid_L"]) == grid_L]
        by_grid[str(grid_L)] = {
            "axis_default": summarize_metric(
                grid_rows,
                xi_key="axis_default_xi_over_L",
                pass_key="axis_default_pass",
            ),
            "axis_lower_0_30": summarize_metric(
                grid_rows,
                xi_key="axis_lower_xi_over_L",
                pass_key="axis_lower_pass",
            ),
            "structure_factor_rms": summarize_metric(
                grid_rows,
                xi_key="structure_factor_xi_over_L",
                pass_key="structure_factor_pass",
            ),
            "seed_sets": {
                seed_set_label: {
                    "axis_default": summarize_metric(
                        [row for row in grid_rows if row["seed_set"] == seed_set_label],
                        xi_key="axis_default_xi_over_L",
                        pass_key="axis_default_pass",
                    ),
                    "axis_lower_0_30": summarize_metric(
                        [row for row in grid_rows if row["seed_set"] == seed_set_label],
                        xi_key="axis_lower_xi_over_L",
                        pass_key="axis_lower_pass",
                    ),
                    "structure_factor_rms": summarize_metric(
                        [row for row in grid_rows if row["seed_set"] == seed_set_label],
                        xi_key="structure_factor_xi_over_L",
                        pass_key="structure_factor_pass",
                    ),
                }
                for seed_set_label in seed_sets
            },
        }

    by_seed_set = {
        seed_set_label: {
            "axis_default": summarize_metric(
                [row for row in stable_rows if row["seed_set"] == seed_set_label],
                xi_key="axis_default_xi_over_L",
                pass_key="axis_default_pass",
            ),
            "axis_lower_0_30": summarize_metric(
                [row for row in stable_rows if row["seed_set"] == seed_set_label],
                xi_key="axis_lower_xi_over_L",
                pass_key="axis_lower_pass",
            ),
            "structure_factor_rms": summarize_metric(
                [row for row in stable_rows if row["seed_set"] == seed_set_label],
                xi_key="structure_factor_xi_over_L",
                pass_key="structure_factor_pass",
            ),
        }
        for seed_set_label in seed_sets
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

    sf_grid_medians = [
        float(by_grid[str(grid_L)]["structure_factor_rms"]["median_xi_proxy"])
        for grid_L in grid_sizes
    ]
    sf_grid_over_l_medians = [
        float(by_grid[str(grid_L)]["structure_factor_rms"]["median_xi_over_L"])
        for grid_L in grid_sizes
    ]
    sf_scaling = log_slope([float(grid_L) for grid_L in grid_sizes], sf_grid_medians)
    sf_over_l_spread = float(max(sf_grid_over_l_medians) - min(sf_grid_over_l_medians))
    sf_domain_scale_risk = any(
        float(by_grid[str(grid_L)]["structure_factor_rms"]["median_xi_over_L"])
        >= domain_scale_warning_threshold
        for grid_L in grid_sizes
    )
    sf_linear_domain_tracking = sf_scaling["slope"] >= 0.75 and sf_scaling["r2"] >= 0.90

    wave24_chain_gate = {
        "status": (
            "PASS"
            if wave24.get("blocker_label")
            == "spectral_core_l16_structure_factor_domain_scale_needs_multigrid_calibration"
            else "BLOCKED"
        ),
        "required_condition": "Wave 25 must start from the Wave 24 structure-factor domain-scale calibration blocker.",
        "wave24_status": wave24.get("status"),
        "wave24_blocker_label": wave24.get("blocker_label"),
    }
    inbox_chain_gate = {
        "status": (
            "PASS"
            if inbox_alignment.get("blocker_label")
            == "inbox_claims_mapped_current_controller_multigrid_calibration"
            else "BLOCKED"
        ),
        "required_condition": "The inbox alignment gate must point to multi-grid structure-factor calibration.",
        "inbox_status": inbox_alignment.get("status"),
        "inbox_blocker_label": inbox_alignment.get("blocker_label"),
    }
    engine_path_gate = {
        "status": "PASS",
        "required_condition": "The diagnostic must generate fields through docs.core.uet_master_equation via Wave 23/24 helpers.",
        "operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }
    multigrid_coverage_gate = {
        "status": (
            "PASS"
            if len(stable_rows) == len(rows)
            and len(positive_margin_rows) == len(rows)
            and len(sf_valid_rows) == len(rows)
            else "BLOCKED"
        ),
        "required_condition": "All grid/seed cases must be stable, positive-margin, and structure-factor measurable.",
        "grid_sizes": grid_sizes,
        "seed_sets": seed_sets,
        "case_count": len(rows),
        "stable_case_count": len(stable_rows),
        "positive_margin_case_count": len(positive_margin_rows),
        "structure_factor_valid_case_count": len(sf_valid_rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    structure_factor_margin_replication_gate = {
        "status": (
            "PASS"
            if all(
                by_grid[str(grid_L)]["structure_factor_rms"]["pass_fraction"] >= 0.75
                and by_grid[str(grid_L)]["structure_factor_rms"]["min_xi_over_L"] >= xi_gate_threshold
                and by_grid[str(grid_L)]["structure_factor_rms"]["min_order_parameter"] >= order_floor
                for grid_L in grid_sizes
            )
            and all(
                by_seed_set[seed_set_label]["structure_factor_rms"]["pass_fraction"] >= 0.75
                for seed_set_label in seed_sets
            )
            else "BLOCKED"
        ),
        "required_condition": "The structure-factor margin should replicate across every grid and both seed sets before it can be used as a candidate finite-size estimator.",
        "xi_gate_threshold": xi_gate_threshold,
        "order_floor": order_floor,
        "by_grid": by_grid,
        "by_seed_set": by_seed_set,
    }
    domain_scale_calibration_gate = {
        "status": "BLOCKED" if sf_domain_scale_risk or sf_linear_domain_tracking else "PASS",
        "required_condition": "The structure-factor estimator should not sit near the domain scale or track grid length linearly before exponent gates use it.",
        "domain_scale_warning_threshold": domain_scale_warning_threshold,
        "structure_factor_median_xi_over_L_by_grid": {
            str(grid_L): by_grid[str(grid_L)]["structure_factor_rms"]["median_xi_over_L"]
            for grid_L in grid_sizes
        },
        "structure_factor_median_xi_proxy_by_grid": {
            str(grid_L): by_grid[str(grid_L)]["structure_factor_rms"]["median_xi_proxy"]
            for grid_L in grid_sizes
        },
        "median_xi_over_L_spread": sf_over_l_spread,
        "log_xi_vs_log_L": sf_scaling,
        "domain_scale_risk": sf_domain_scale_risk,
        "linear_domain_tracking": sf_linear_domain_tracking,
    }
    estimator_disagreement_gate = {
        "status": "WARN",
        "required_condition": "Axis-threshold and structure-factor estimator disagreements must keep the claim boundary conservative.",
        "overall": overall,
        "interpretation": "Estimator disagreement is diagnostic; it cannot validate finite-size scaling without accepted calibration.",
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent/universality gates until domain-scale calibration is repaired or a source-backed estimator benchmark exists.",
        "claim_boundary": "Next work should calibrate the structure-factor estimator against larger grids, known benchmarks, or a derived finite-size scaling acceptance rule.",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic cannot validate exponent, material, RG, or universality claims.",
        "claim_boundary": "A replicated high structure-factor xi/L is domain-scale calibration evidence only.",
    }

    if structure_factor_margin_replication_gate["status"] != "PASS":
        blocker_label = "spectral_core_structure_factor_multigrid_margin_not_replicated"
    elif domain_scale_calibration_gate["status"] != "PASS":
        blocker_label = "spectral_core_structure_factor_multigrid_domain_scale_saturated"
    else:
        blocker_label = "spectral_core_structure_factor_multigrid_calibrated_needs_exponent_gate"

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
            "path": relpath(WAVE24_SCRIPT_PATH),
            "sha256": hash_file(WAVE24_SCRIPT_PATH),
            "role": "Wave 24 structure-factor helper and current estimator definition",
        },
    ]
    if WAVE24_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE24_ARTIFACT_PATH),
                "sha256": hash_file(WAVE24_ARTIFACT_PATH),
                "role": "Wave 24 structure-factor domain-scale controller",
            }
        )
    if INBOX_ALIGNMENT_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(INBOX_ALIGNMENT_ARTIFACT_PATH),
                "sha256": hash_file(INBOX_ALIGNMENT_ARTIFACT_PATH),
                "role": "inbox alignment controller pointing to multi-grid calibration",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 25 conserved_order_spectral_v1 structure-factor multi-grid calibration",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Structure_Factor_Multigrid_Calibration.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_structure_factor_multigrid_calibration_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_sizes": grid_sizes,
            "seed_sets": seed_sets,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "steps": steps,
            "xi_gate_threshold": xi_gate_threshold,
            "order_floor": order_floor,
            "domain_scale_warning_threshold": domain_scale_warning_threshold,
            "axis_default_threshold": math.exp(-1.0),
            "axis_lower_threshold": lower_axis_threshold,
            "structure_factor_formula": "xi_sf = 2*pi / sqrt(sum(S(k)*k^2)/sum(S(k))) over nonzero FFT modes",
            "case_count": len(rows),
        },
        "metrics": {
            "overall": overall,
            "by_grid": by_grid,
            "by_seed_set": by_seed_set,
            "structure_factor_scaling": {
                "median_xi_over_L_by_grid": domain_scale_calibration_gate[
                    "structure_factor_median_xi_over_L_by_grid"
                ],
                "median_xi_proxy_by_grid": domain_scale_calibration_gate[
                    "structure_factor_median_xi_proxy_by_grid"
                ],
                "median_xi_over_L_spread": sf_over_l_spread,
                "log_xi_vs_log_L": sf_scaling,
            },
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave24_chain_gate": wave24_chain_gate,
            "inbox_chain_gate": inbox_chain_gate,
            "engine_path_gate": engine_path_gate,
            "multigrid_coverage_gate": multigrid_coverage_gate,
            "structure_factor_margin_replication_gate": structure_factor_margin_replication_gate,
            "domain_scale_calibration_gate": domain_scale_calibration_gate,
            "estimator_disagreement_gate": estimator_disagreement_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a structure-factor estimator calibration diagnostic, not a finite-size scaling proof.",
            "A high replicated xi/L can indicate domain-scale saturation rather than a valid critical correlation length.",
            "The result must not be used as material validation, RG closure, or a universality-class claim.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims until structure-factor domain-scale calibration is repaired and exponent gates are rerun.",
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
    result = run_structure_factor_multigrid_calibration()
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"Wrote {ARTIFACT_PATH}")
