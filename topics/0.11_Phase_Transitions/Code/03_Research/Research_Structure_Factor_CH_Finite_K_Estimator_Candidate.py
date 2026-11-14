"""
Wave 48 Cahn-Hilliard finite-k estimator candidate.

Wave 47 closed only the lattice q-grid convention and kept estimator
acceptance blocked. This verifier implements a conservative diagnostic
candidate from the CH finite-k source lane:

    C_centered -> S(q) = |FFT(C_centered)|^2
    q_peak = argmax S(q) inside an explicit finite-k window
    xi_peak = 2*pi / q_peak

The candidate excludes q=0 and records low-mode/domain-scale diagnostics. It
does not accept a critical correlation length, exponent rerun, RG closure, or
Tier A claim.
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
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"

WAVE47_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_normalization_preflight_gate.json"
WAVE47_MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_normalization_preflight.json"
WAVE25_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_Structure_Factor_Multigrid_Calibration.py"
)
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"

ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_estimator_candidate_gate.json"
CSV_PATH = TOPIC_DIR / "Result" / "gl_structure_factor_ch_finite_k_estimator_candidate_stats.csv"


def load_wave25_helpers():
    spec = importlib.util.spec_from_file_location("wave25_multigrid_calibration", WAVE25_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Wave 25 helper script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def source_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
    }


def artifact_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    data = load_json(path) if exists else {}
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
        "status": data.get("status"),
        "blocker_label": data.get("blocker_label"),
        "claim_class": data.get("claim_class"),
    }


def gate_status(artifact: dict[str, Any], gate_name: str) -> str | None:
    gate = artifact.get("gates", {}).get(gate_name, {})
    return gate.get("status") if isinstance(gate, dict) else None


def ch_finite_k_peak_estimator(
    C: np.ndarray,
    dx: float,
    *,
    low_mode_cut_multiplier: float = 2.0,
) -> dict[str, float | bool | str]:
    field = np.asarray(C, dtype=float)
    centered = field - float(np.mean(field))
    variance = float(np.mean(centered**2))
    if variance <= 1e-14:
        return {
            "valid": False,
            "invalid_reason": "zero_centered_variance",
            "xi_peak": 0.0,
            "q_peak": float("nan"),
            "q_min": float("nan"),
            "q_window_min": float("nan"),
            "q_window_max": float("nan"),
            "window_power_fraction": 0.0,
            "low_mode_power_fraction": 0.0,
            "zero_mode_power_fraction": 0.0,
            "peak_hits_low_window_edge": False,
        }

    spectrum = np.fft.fftn(centered)
    power = np.abs(spectrum) ** 2
    total_power_with_zero = float(np.sum(power))
    zero_index = (0,) * field.ndim
    zero_power = float(power[zero_index])
    power[zero_index] = 0.0
    total_nonzero_power = float(np.sum(power))
    if total_nonzero_power <= 1e-30:
        return {
            "valid": False,
            "invalid_reason": "no_nonzero_power",
            "xi_peak": 0.0,
            "q_peak": float("nan"),
            "q_min": float("nan"),
            "q_window_min": float("nan"),
            "q_window_max": float("nan"),
            "window_power_fraction": 0.0,
            "low_mode_power_fraction": 0.0,
            "zero_mode_power_fraction": zero_power / max(total_power_with_zero, 1e-30),
            "peak_hits_low_window_edge": False,
        }

    q2 = np.zeros(field.shape, dtype=float)
    for axis, size in enumerate(field.shape):
        freq = 2.0 * math.pi * np.fft.fftfreq(size, d=dx)
        shape = [1] * field.ndim
        shape[axis] = size
        q2 += freq.reshape(shape) ** 2
    q = np.sqrt(q2)
    nonzero_q = q[q > 0.0]
    q_min = float(np.min(nonzero_q))
    q_nyquist = float(math.pi / dx)
    q_window_min = float(low_mode_cut_multiplier * q_min)
    q_window_max = q_nyquist
    low_mode_mask = (q > 0.0) & (q < q_window_min)
    window_mask = (q >= q_window_min) & (q <= q_window_max)
    low_mode_power = float(np.sum(power[low_mode_mask]))
    window_power = float(np.sum(power[window_mask]))
    if window_power <= 1e-30:
        return {
            "valid": False,
            "invalid_reason": "no_power_in_finite_k_window",
            "xi_peak": 0.0,
            "q_peak": float("nan"),
            "q_min": q_min,
            "q_window_min": q_window_min,
            "q_window_max": q_window_max,
            "window_power_fraction": 0.0,
            "low_mode_power_fraction": low_mode_power / total_nonzero_power,
            "zero_mode_power_fraction": zero_power / max(total_power_with_zero, 1e-30),
            "peak_hits_low_window_edge": False,
        }

    masked_power = np.where(window_mask, power, -1.0)
    peak_index = np.unravel_index(int(np.argmax(masked_power)), masked_power.shape)
    q_peak = float(q[peak_index])
    xi_peak = float(2.0 * math.pi / q_peak) if q_peak > 0.0 else 0.0
    peak_hits_low_window_edge = bool(q_peak <= q_window_min * (1.0 + 1e-9))
    return {
        "valid": bool(math.isfinite(xi_peak) and xi_peak > 0.0),
        "invalid_reason": "none",
        "xi_peak": xi_peak,
        "q_peak": q_peak,
        "q_min": q_min,
        "q_window_min": q_window_min,
        "q_window_max": q_window_max,
        "window_power_fraction": window_power / total_nonzero_power,
        "low_mode_power_fraction": low_mode_power / total_nonzero_power,
        "zero_mode_power_fraction": zero_power / max(total_power_with_zero, 1e-30),
        "peak_hits_low_window_edge": peak_hits_low_window_edge,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    xi_over_l = np.array([float(row["ch_finite_k_xi_over_L"]) for row in rows], dtype=float)
    xi_abs = np.array([float(row["ch_finite_k_xi_peak"]) for row in rows], dtype=float)
    window_power = np.array([float(row["window_power_fraction"]) for row in rows], dtype=float)
    low_power = np.array([float(row["low_mode_power_fraction"]) for row in rows], dtype=float)
    pass_count = sum(1 for row in rows if bool(row["ch_finite_k_candidate_pass"]))
    low_edge_count = sum(1 for row in rows if bool(row["peak_hits_low_window_edge"]))
    return {
        "case_count": len(rows),
        "pass_count": pass_count,
        "pass_fraction": float(pass_count / len(rows)) if rows else 0.0,
        "median_xi_over_L": float(np.median(xi_over_l)) if len(xi_over_l) else float("nan"),
        "min_xi_over_L": float(np.min(xi_over_l)) if len(xi_over_l) else float("nan"),
        "max_xi_over_L": float(np.max(xi_over_l)) if len(xi_over_l) else float("nan"),
        "median_xi_peak": float(np.median(xi_abs)) if len(xi_abs) else float("nan"),
        "median_window_power_fraction": float(np.median(window_power)) if len(window_power) else float("nan"),
        "median_low_mode_power_fraction": float(np.median(low_power)) if len(low_power) else float("nan"),
        "peak_low_window_edge_count": low_edge_count,
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


def run_ch_finite_k_estimator_candidate() -> dict[str, Any]:
    wave25_helpers = load_wave25_helpers()
    wave24_helpers = wave25_helpers.load_wave24_helpers()
    wave23_helpers = wave24_helpers.load_wave23_helpers()
    wave47 = load_json(WAVE47_ARTIFACT_PATH) if WAVE47_ARTIFACT_PATH.exists() else {}
    wave47_manifest = load_json(WAVE47_MANIFEST_PATH) if WAVE47_MANIFEST_PATH.exists() else {}

    grid_sizes = [12, 16, 20]
    seed_sets = {
        "fresh_seed_set": [21001, 21002, 21003],
        "probe_seed_set": [22001, 22002, 22003],
    }
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    steps = 4000
    low_mode_cut_multiplier = 2.0
    xi_over_l_floor = 0.10
    xi_over_l_domain_scale_ceiling = 0.75
    min_window_power_fraction = 0.05
    max_low_mode_power_fraction = 0.90
    order_floor = 0.005

    rows: list[dict[str, Any]] = []
    for grid_L in grid_sizes:
        for seed_set, seeds in seed_sets.items():
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
                domain_length = float(grid_L * dx)
                candidate = ch_finite_k_peak_estimator(
                    C,
                    dx,
                    low_mode_cut_multiplier=low_mode_cut_multiplier,
                )
                rms = wave24_helpers.structure_factor_rms_length(C, dx)
                xi_peak = finite_float(candidate.get("xi_peak"))
                xi_over_l = xi_peak / domain_length if math.isfinite(xi_peak) else float("nan")
                valid_candidate = bool(candidate.get("valid"))
                candidate_pass = bool(
                    status == "OK"
                    and valid_candidate
                    and xi_over_l >= xi_over_l_floor
                    and xi_over_l < xi_over_l_domain_scale_ceiling
                    and float(candidate["window_power_fraction"]) >= min_window_power_fraction
                    and float(candidate["low_mode_power_fraction"]) <= max_low_mode_power_fraction
                    and order_parameter >= order_floor
                )
                rows.append(
                    {
                        "label": f"L{grid_L}_{seed_set}_seed{seed}",
                        "grid_L": grid_L,
                        "domain_length": domain_length,
                        "seed_set": seed_set,
                        "seed": seed,
                        "temperature": float(temperature),
                        "steps": steps,
                        "dx": float(dx),
                        "dt": float(dt),
                        "kappa": float(kappa),
                        "status": status,
                        "mass_drift_abs": float(mass_drift),
                        "order_parameter": float(order_parameter),
                        "spinodal_margin": float(wave23_helpers.spinodal_margin(temperature, kappa, grid_L, dx)),
                        "q_min": finite_float(candidate.get("q_min")),
                        "q_window_min": finite_float(candidate.get("q_window_min")),
                        "q_window_max": finite_float(candidate.get("q_window_max")),
                        "q_peak": finite_float(candidate.get("q_peak")),
                        "ch_finite_k_xi_peak": xi_peak,
                        "ch_finite_k_xi_over_L": float(xi_over_l),
                        "ch_finite_k_valid": valid_candidate,
                        "ch_finite_k_invalid_reason": str(candidate.get("invalid_reason")),
                        "window_power_fraction": finite_float(candidate.get("window_power_fraction")),
                        "low_mode_power_fraction": finite_float(candidate.get("low_mode_power_fraction")),
                        "zero_mode_power_fraction": finite_float(candidate.get("zero_mode_power_fraction")),
                        "peak_hits_low_window_edge": bool(candidate.get("peak_hits_low_window_edge")),
                        "structure_factor_rms_xi_proxy": finite_float(rms.get("xi_proxy")),
                        "structure_factor_rms_xi_over_L": (
                            finite_float(rms.get("xi_proxy")) / domain_length
                            if math.isfinite(finite_float(rms.get("xi_proxy")))
                            else float("nan")
                        ),
                        "ch_finite_k_candidate_pass": candidate_pass,
                    }
                )

    stable_rows = [row for row in rows if row["status"] == "OK"]
    valid_rows = [row for row in stable_rows if bool(row["ch_finite_k_valid"])]
    by_grid = {
        str(grid_L): summarize_rows([row for row in valid_rows if int(row["grid_L"]) == grid_L])
        for grid_L in grid_sizes
    }
    overall = summarize_rows(valid_rows)
    median_xi_by_grid = {
        str(grid_L): by_grid[str(grid_L)]["median_xi_peak"] for grid_L in grid_sizes
    }
    median_xi_over_l_by_grid = {
        str(grid_L): by_grid[str(grid_L)]["median_xi_over_L"] for grid_L in grid_sizes
    }
    finite_size_slope = log_slope(
        [float(grid_L) for grid_L in grid_sizes],
        [float(median_xi_by_grid[str(grid_L)]) for grid_L in grid_sizes],
    )
    adjacent_ratios = {}
    for left, right in zip(grid_sizes, grid_sizes[1:]):
        left_value = float(median_xi_by_grid[str(left)])
        right_value = float(median_xi_by_grid[str(right)])
        adjacent_ratios[f"L{right}/L{left}"] = (
            right_value / left_value if left_value > 0.0 else float("nan")
        )

    wave47_chain_gate = {
        "status": (
            "PASS"
            if wave47.get("blocker_label")
            == "ch_finite_k_normalization_preflight_written_estimator_implementation_open"
            and gate_status(wave47, "fourier_convention_gate") == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "Wave 48 must start from Wave 47 CH finite-k normalization preflight.",
        "wave47_status": wave47.get("status"),
        "wave47_blocker_label": wave47.get("blocker_label"),
        "fourier_convention_gate": gate_status(wave47, "fourier_convention_gate"),
    }
    source_formula_linkage_gate = {
        "status": (
            "PASS"
            if any("Eqn_Sqt" in item or "inline" in item for item in wave47_manifest.get("supporting_fragment_ids", []))
            else "BLOCKED"
        ),
        "required_condition": "Candidate must link to CH S(q,t) source fragments recorded in Wave 47.",
        "supporting_fragment_ids": wave47_manifest.get("supporting_fragment_ids", []),
    }
    implementation_coverage_gate = {
        "status": "PASS" if len(stable_rows) == len(rows) and len(valid_rows) == len(rows) else "BLOCKED",
        "required_condition": "All candidate cases must be stable and yield a finite-k peak measurement.",
        "case_count": len(rows),
        "stable_case_count": len(stable_rows),
        "valid_candidate_count": len(valid_rows),
    }
    q_window_diagnostic_gate = {
        "status": (
            "PASS"
            if overall["median_window_power_fraction"] >= min_window_power_fraction
            and overall["median_low_mode_power_fraction"] <= max_low_mode_power_fraction
            else "BLOCKED"
        ),
        "required_condition": "Candidate must report usable finite-k window power and low-mode/domain-scale pressure.",
        "min_window_power_fraction": min_window_power_fraction,
        "max_low_mode_power_fraction": max_low_mode_power_fraction,
        "overall": overall,
        "by_grid": by_grid,
    }
    domain_scale_guard_gate = {
        "status": (
            "PASS"
            if overall["max_xi_over_L"] < xi_over_l_domain_scale_ceiling
            else "BLOCKED"
        ),
        "required_condition": "Candidate peak length must stay below domain-scale ceiling.",
        "domain_scale_ceiling_xi_over_L": xi_over_l_domain_scale_ceiling,
        "overall": overall,
    }
    finite_size_trend_gate = {
        "status": (
            "PASS"
            if all(math.isfinite(value) and value >= 1.0 for value in adjacent_ratios.values())
            else "BLOCKED"
        ),
        "required_condition": "Median absolute finite-k length should be nondecreasing across accepted grid sizes before exponent use.",
        "median_xi_peak_by_grid": median_xi_by_grid,
        "median_xi_over_L_by_grid": median_xi_over_l_by_grid,
        "adjacent_median_xi_ratios": adjacent_ratios,
        "log_xi_vs_log_L": finite_size_slope,
    }
    coefficient_policy_gate = {
        "status": "BLOCKED",
        "required_condition": "Source coefficient mapping remains unresolved, so the candidate is measurement-only and not source-dynamics acceptance.",
        "wave47_coefficient_mapping_gate": gate_status(wave47, "coefficient_mapping_gate"),
        "policy": "exclude source coefficient claims from this candidate; measure S(q) on existing UET fields only",
    }
    estimator_acceptance_gate = {
        "status": "BLOCKED",
        "required_condition": "A candidate implementation plus q-window diagnostics is not enough to accept estimator replacement.",
        "blocking_gates": [
            "field_normalization_gate=WARN",
            "coefficient_mapping_gate=BLOCKED",
            "finite_size_admissibility_gate remains a draft policy",
            "finite-size/exponent gates not rerun",
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until candidate acceptance gates are closed.",
        "next_controller": "derive_or_accept_ch_finite_k_xi_rule_and_admissibility_policy",
        "next_artifacts_required": [
            "accepted field-normalization policy for centered C",
            "accepted q-window/domain-scale thresholds",
            "source coefficient inclusion/exclusion decision",
            "finite-size/exponent rerun using only accepted candidate rows",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Candidate implementation cannot promote estimator, exponent, universality, material, RG, or Tier A claims.",
        "claim_boundary": "Wave 48 is a source-linked finite-k estimator candidate only.",
    }

    if wave47_chain_gate["status"] != "PASS":
        blocker_label = "ch_finite_k_candidate_chain_missing_wave47_preflight"
    elif implementation_coverage_gate["status"] != "PASS":
        blocker_label = "ch_finite_k_candidate_implementation_incomplete"
    elif estimator_acceptance_gate["status"] == "BLOCKED":
        blocker_label = "ch_finite_k_candidate_implemented_acceptance_policy_open"
    else:
        blocker_label = "ch_finite_k_candidate_ready_for_exponent_rerun"

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 48 Cahn-Hilliard finite-k estimator candidate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Estimator_Candidate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_linked_estimator_candidate_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": [
            artifact_record(WAVE47_ARTIFACT_PATH, "Wave 47 CH finite-k normalization preflight"),
            source_record(WAVE47_MANIFEST_PATH, "Wave 47 CH finite-k normalization preflight manifest"),
            source_record(WAVE25_SCRIPT_PATH, "Wave 25 helper chain for fields and prior structure-factor diagnostics"),
            source_record(CORE_ENGINE_PATH, "core spectral conserved-order implementation"),
        ],
        "parameters": {
            "grid_sizes": grid_sizes,
            "seed_sets": seed_sets,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "steps": steps,
            "low_mode_cut_multiplier": low_mode_cut_multiplier,
            "xi_over_l_floor": xi_over_l_floor,
            "xi_over_l_domain_scale_ceiling": xi_over_l_domain_scale_ceiling,
            "min_window_power_fraction": min_window_power_fraction,
            "max_low_mode_power_fraction": max_low_mode_power_fraction,
            "order_floor": order_floor,
            "candidate_formula": "xi_peak = 2*pi / argmax_q S(q) inside q >= 2*q_min finite-k window",
        },
        "metrics": {
            "overall": overall,
            "by_grid": by_grid,
            "finite_size_trend": {
                "median_xi_peak_by_grid": median_xi_by_grid,
                "median_xi_over_L_by_grid": median_xi_over_l_by_grid,
                "adjacent_median_xi_ratios": adjacent_ratios,
                "log_xi_vs_log_L": finite_size_slope,
            },
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave47_chain_gate": wave47_chain_gate,
            "source_formula_linkage_gate": source_formula_linkage_gate,
            "implementation_coverage_gate": implementation_coverage_gate,
            "q_window_diagnostic_gate": q_window_diagnostic_gate,
            "domain_scale_guard_gate": domain_scale_guard_gate,
            "finite_size_trend_gate": finite_size_trend_gate,
            "coefficient_policy_gate": coefficient_policy_gate,
            "estimator_acceptance_gate": estimator_acceptance_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This uses centered UET C as a diagnostic concentration-fluctuation proxy.",
            "The finite-k peak rule is source-linked but not yet source-derived as an accepted xi estimator.",
            "Source coefficients from the CH paper are not mapped to UETParameters.",
            "No exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "claim_boundary": (
            "Wave 48 implements a source-linked CH finite-k estimator candidate with q-window diagnostics. "
            "It does not accept estimator replacement or rerun scaling claims."
        ),
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
    result = run_ch_finite_k_estimator_candidate()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "artifact": relpath(ARTIFACT_PATH),
                "csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
            },
            indent=2,
            sort_keys=True,
        )
    )
