"""Wave 50 extended-grid coverage probe for CH finite-k acceptance.

Wave 49 defined strict row acceptance and found that only L20 rows survived.
This probe keeps the same estimator and policy, adds larger grids, and checks
whether accepted-row coverage can be repaired before any exponent rerun.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import platform
import sys
from collections import defaultdict
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET repository root not found")


ROOT = _bootstrap()
TOPIC = "0.11_Phase_Transitions"
TOPIC_DIR = ROOT / "docs" / "topics" / TOPIC
CODE_DIR = TOPIC_DIR / "Code" / "03_Research"
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
RESULT_DIR = TOPIC_DIR / "Result"
ARTIFACT_DIR = RESULT_DIR / "artifacts"

WAVE48_SCRIPT = CODE_DIR / "Research_Structure_Factor_CH_Finite_K_Estimator_Candidate.py"
WAVE48_CSV = RESULT_DIR / "gl_structure_factor_ch_finite_k_estimator_candidate_stats.csv"
WAVE49_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_acceptance_policy_gate.json"
WAVE49_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_acceptance_policy.json"

ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_extended_grid_coverage_probe.json"
CSV_PATH = RESULT_DIR / "gl_structure_factor_ch_finite_k_extended_grid_coverage_probe_stats.csv"


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bool_value(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def finite_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def load_wave48_rows() -> list[dict[str, Any]]:
    with WAVE48_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def policy_acceptance(row: dict[str, Any], policy: dict[str, Any]) -> tuple[bool, list[str]]:
    rules = policy["q_window_row_acceptance"]
    reasons: list[str] = []
    if rules["require_status_ok"] and row["status"] != "OK":
        reasons.append("status_not_ok")
    if rules["require_wave48_candidate_pass"] and not bool_value(row["ch_finite_k_candidate_pass"]):
        reasons.append("candidate_pass_false")
    if not bool_value(row["ch_finite_k_valid"]):
        reasons.append("finite_k_invalid")
    if rules["exclude_low_window_edge_peaks"] and bool_value(row["peak_hits_low_window_edge"]):
        reasons.append("peak_hits_low_window_edge")
    if finite_float(row["window_power_fraction"]) < rules["min_window_power_fraction"]:
        reasons.append("window_power_fraction_below_floor")
    if finite_float(row["low_mode_power_fraction"]) > rules["max_low_mode_power_fraction"]:
        reasons.append("low_mode_power_fraction_above_ceiling")
    xi_over_l = finite_float(row["ch_finite_k_xi_over_L"])
    if xi_over_l < rules["xi_over_l_floor"]:
        reasons.append("xi_over_l_below_floor")
    if xi_over_l >= rules["xi_over_l_domain_scale_ceiling"]:
        reasons.append("xi_over_l_at_or_above_domain_scale_ceiling")
    if finite_float(row["order_parameter"]) < rules["order_floor"]:
        reasons.append("order_below_floor")
    return not reasons, reasons


def summarize(rows: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    by_grid: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "total_rows": 0,
            "accepted_rows": 0,
            "low_window_edge_rows": 0,
            "candidate_pass_rows": 0,
            "accepted_xi_peak": [],
            "accepted_xi_over_L": [],
            "rejection_reasons": defaultdict(int),
        }
    )
    row_decisions = []
    accepted = []
    for row in rows:
        ok, reasons = policy_acceptance(row, policy)
        grid = str(int(float(row["grid_L"])))
        bucket = by_grid[grid]
        bucket["total_rows"] += 1
        bucket["accepted_rows"] += int(ok)
        bucket["candidate_pass_rows"] += int(bool_value(row["ch_finite_k_candidate_pass"]))
        bucket["low_window_edge_rows"] += int(bool_value(row["peak_hits_low_window_edge"]))
        for reason in reasons:
            bucket["rejection_reasons"][reason] += 1
        if ok:
            accepted.append(row)
            bucket["accepted_xi_peak"].append(finite_float(row["ch_finite_k_xi_peak"]))
            bucket["accepted_xi_over_L"].append(finite_float(row["ch_finite_k_xi_over_L"]))
        row_decisions.append(
            {
                "label": row["label"],
                "grid_L": int(float(row["grid_L"])),
                "policy_accepted": ok,
                "rejection_reasons": reasons,
            }
        )

    by_grid_out = {}
    for grid, bucket in sorted(by_grid.items(), key=lambda item: int(item[0])):
        by_grid_out[grid] = {
            "total_rows": bucket["total_rows"],
            "candidate_pass_rows": bucket["candidate_pass_rows"],
            "low_window_edge_rows": bucket["low_window_edge_rows"],
            "accepted_rows": bucket["accepted_rows"],
            "median_accepted_xi_peak": median(bucket["accepted_xi_peak"]) if bucket["accepted_xi_peak"] else None,
            "median_accepted_xi_over_L": median(bucket["accepted_xi_over_L"]) if bucket["accepted_xi_over_L"] else None,
            "rejection_reasons": dict(sorted(bucket["rejection_reasons"].items())),
        }
    accepted_grid_counts = {
        grid: bucket["accepted_rows"] for grid, bucket in by_grid_out.items() if bucket["accepted_rows"] > 0
    }
    return {
        "overall": {
            "total_rows": len(rows),
            "accepted_rows": len(accepted),
            "accepted_fraction": len(accepted) / len(rows) if rows else 0.0,
            "accepted_grid_count": len(accepted_grid_counts),
            "min_rows_per_accepted_grid": min(accepted_grid_counts.values()) if accepted_grid_counts else 0,
            "accepted_grid_counts": accepted_grid_counts,
            "accepted_labels": [row["label"] for row in accepted],
        },
        "by_grid": by_grid_out,
        "row_decisions": row_decisions,
    }


def make_extended_rows() -> list[dict[str, Any]]:
    wave48 = load_module(WAVE48_SCRIPT, "wave48_ch_finite_k_candidate")
    wave25 = wave48.load_wave25_helpers()
    wave24 = wave25.load_wave24_helpers()
    wave23 = wave24.load_wave23_helpers()

    grid_sizes = [24, 28]
    seed_sets = {
        "fresh_seed_set": [21001, 21002],
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
                status, C, mass_drift, order_parameter = wave23.simulate_final_field(
                    grid_L=grid_L,
                    temperature=temperature,
                    steps=steps,
                    dt=dt,
                    dx=dx,
                    kappa=kappa,
                    seed=seed,
                )
                domain_length = float(grid_L * dx)
                candidate = wave48.ch_finite_k_peak_estimator(
                    C,
                    dx,
                    low_mode_cut_multiplier=low_mode_cut_multiplier,
                )
                rms = wave24.structure_factor_rms_length(C, dx)
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
                        "spinodal_margin": float(wave23.spinodal_margin(temperature, kappa, grid_L, dx)),
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
    return rows


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> dict[str, Any]:
    wave49 = load_json(WAVE49_ARTIFACT)
    manifest = load_json(WAVE49_MANIFEST)
    policy = manifest["policy"]
    prior_rows = load_wave48_rows()
    extended_rows = make_extended_rows()
    write_csv(extended_rows)
    combined_rows = prior_rows + [{key: str(value) for key, value in row.items()} for row in extended_rows]
    prior_summary = summarize(prior_rows, policy)
    extended_summary = summarize([{key: str(value) for key, value in row.items()} for row in extended_rows], policy)
    combined_summary = summarize(combined_rows, policy)

    required_grid_count = int(policy["finite_size_coverage"]["min_accepted_grid_count"])
    required_rows_per_grid = int(policy["finite_size_coverage"]["min_accepted_rows_per_grid"])
    coverage_pass = (
        combined_summary["overall"]["accepted_grid_count"] >= required_grid_count
        and combined_summary["overall"]["min_rows_per_accepted_grid"] >= required_rows_per_grid
    )

    wave49_chain_pass = (
        wave49.get("blocker_label") == "ch_finite_k_acceptance_policy_defined_finite_size_coverage_and_normalization_open"
        and wave49.get("gates", {}).get("acceptance_policy_manifest_gate", {}).get("status") == "PASS"
    )
    extended_stable = all(row["status"] == "OK" and bool(row["ch_finite_k_valid"]) for row in extended_rows)

    gates = {
        "wave49_chain_gate": {
            "status": "PASS" if wave49_chain_pass else "BLOCKED",
            "required_condition": "Extended-grid probe must start from the Wave 49 acceptance policy.",
            "wave49_status": wave49.get("status"),
            "wave49_blocker_label": wave49.get("blocker_label"),
        },
        "extended_grid_probe_gate": {
            "status": "PASS" if extended_stable else "BLOCKED",
            "required_condition": "All extended-grid rows must run stably and yield finite-k measurements.",
            "extended_rows": len(extended_rows),
            "extended_grids": [24, 28],
        },
        "policy_application_gate": {
            "status": "PASS",
            "required_condition": "Wave 50 must apply the unchanged Wave 49 strict policy.",
            "policy_source": relpath(WAVE49_MANIFEST),
            "policy_sha256": hash_file(WAVE49_MANIFEST),
        },
        "accepted_multi_grid_coverage_gate": {
            "status": "PASS" if coverage_pass else "BLOCKED",
            "required_condition": "Combined accepted rows must cover at least three grid sizes with at least two rows per grid.",
            "required_grid_count": required_grid_count,
            "required_rows_per_grid": required_rows_per_grid,
            "accepted_grid_count": combined_summary["overall"]["accepted_grid_count"],
            "min_rows_per_accepted_grid": combined_summary["overall"]["min_rows_per_accepted_grid"],
            "accepted_grid_counts": combined_summary["overall"]["accepted_grid_counts"],
        },
        "field_normalization_policy_gate": {
            "status": "WARN",
            "required_condition": "Extended-grid coverage does not resolve centered-C source-equivalence.",
            "inherited_from_wave49": "field_normalization_policy_gate=WARN",
        },
        "source_dynamics_coefficient_mapping_gate": {
            "status": "BLOCKED",
            "required_condition": "Extended-grid coverage does not map source CH dynamics coefficients.",
            "inherited_from_wave49": "source_dynamics_coefficient_mapping_gate=BLOCKED",
        },
        "estimator_acceptance_gate": {
            "status": "BLOCKED",
            "required_condition": "Estimator acceptance still requires field normalization, source coefficient mapping, and exponent rerun policy.",
            "blocking_gates": [
                "field_normalization_policy_gate=WARN",
                "source_dynamics_coefficient_mapping_gate=BLOCKED",
                "exponent_rerun_gate=BLOCKED",
            ],
        },
        "exponent_rerun_gate": {
            "status": "BLOCKED",
            "required_condition": "Do not rerun exponent gates until estimator acceptance gates pass.",
        },
    }

    blocker_label = (
        "ch_finite_k_extended_grid_coverage_repaired_normalization_and_coefficients_open"
        if coverage_pass
        else "ch_finite_k_extended_grid_coverage_still_insufficient"
    )
    artifact = {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 50 CH finite-k extended-grid coverage probe",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Extended_Grid_Coverage_Probe.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "coverage_probe_only",
        "claim_boundary": (
            "Wave 50 tests whether larger-grid rows can repair Wave 49 accepted-row coverage. "
            "It does not accept estimator replacement or rerun exponent/universality claims."
        ),
        "inputs": [
            {
                "path": relpath(WAVE49_ARTIFACT),
                "role": "Wave 49 strict acceptance policy artifact",
                "sha256": hash_file(WAVE49_ARTIFACT),
                "status": wave49.get("status"),
                "blocker_label": wave49.get("blocker_label"),
            },
            {
                "path": relpath(WAVE49_MANIFEST),
                "role": "Wave 49 strict acceptance policy manifest",
                "sha256": hash_file(WAVE49_MANIFEST),
            },
            {
                "path": relpath(WAVE48_CSV),
                "role": "Wave 48 baseline candidate rows",
                "sha256": hash_file(WAVE48_CSV),
            },
        ],
        "parameters": {
            "extended_grid_sizes": [24, 28],
            "seed_sets": {
                "fresh_seed_set": [21001, 21002],
            },
            "temperature": 0.900,
            "steps": 4000,
            "dx": 1.0,
            "dt": 0.05,
            "kappa": 0.100,
            "policy": policy,
        },
        "metrics": {
            "prior_wave48_summary": prior_summary,
            "extended_grid_summary": extended_summary,
            "combined_summary": combined_summary,
            "extended_csv": relpath(CSV_PATH),
        },
        "gates": gates,
        "limitations": [
            "This is an extended-grid coverage probe only.",
            "The estimator and strict policy are unchanged from Waves 48-49.",
            "Centered UET C remains proxy-normalized.",
            "Source dynamics coefficients remain unmapped.",
            "No exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "environment": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "platform": platform.platform(),
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = main()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "accepted_grid_counts": result["metrics"]["combined_summary"]["overall"]["accepted_grid_counts"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
            },
            indent=2,
            sort_keys=True,
        )
    )
