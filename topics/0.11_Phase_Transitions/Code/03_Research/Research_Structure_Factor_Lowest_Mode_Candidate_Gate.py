"""
Wave 32 lowest-mode second-moment estimator candidate gate.

Wave 31 extracted the source-family second-moment formula and rejected the
current all-nonzero-mode RMS inverse-k proxy for source-backed claim use. This
verifier implements a literal lowest-mode estimator candidate on the same
conserved-order fields used by the existing L16 and L20 diagnostics.

The gate is intentionally conservative. It checks whether the source-family
observable is available on the current single-snapshot, near-zero-mean
conserved-order lane. A failed candidate is progress: it narrows the next
blocker to the missing observable lane rather than letting a surrogate estimator
quietly replace the formula.
"""

from __future__ import annotations

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
TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_lowest_mode_candidate_gate.json"
WAVE31_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_formula_boundary_gate.json"
FORMULA_BOUNDARY_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_formula_boundary.json"
)
WAVE24_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py"
)
WAVE26_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_Structure_Factor_L20_Probe.py"
)


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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load helper script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def lowest_mode_second_moment_length(field: np.ndarray, dx: float) -> dict[str, Any]:
    """
    Literal single-snapshot version of xi_2nd.

    This uses the source-family algebra on one field snapshot. It is expected to
    fail for conserved near-zero-mean fields when the zero mode is not a
    susceptibility observable.
    """
    C = np.asarray(field, dtype=float)
    if C.ndim < 1 or len(set(C.shape)) != 1:
        return {"valid": False, "invalid_reason": "field_must_be_cubic"}

    grid_l = int(C.shape[0])
    domain_length = float(grid_l * dx)
    spectrum = np.fft.fftn(C)
    power = np.abs(spectrum) ** 2
    zero_index = (0,) * C.ndim
    s0 = float(power[zero_index])

    lowest_values = []
    for axis in range(C.ndim):
        plus_index = [0] * C.ndim
        minus_index = [0] * C.ndim
        plus_index[axis] = 1
        minus_index[axis] = grid_l - 1
        lowest_values.append(float(power[tuple(plus_index)]))
        lowest_values.append(float(power[tuple(minus_index)]))

    s_kmin = float(np.mean(lowest_values)) if lowest_values else float("nan")
    k_min = float(2.0 * math.pi / domain_length)
    lattice_denominator = float(2.0 * math.sin(math.pi / grid_l))
    ratio = float(s0 / s_kmin) if s_kmin > 0.0 else float("nan")
    radicand = float(ratio - 1.0) if math.isfinite(ratio) else float("nan")
    valid = bool(s0 > 0.0 and s_kmin > 0.0 and radicand > 0.0)
    xi_lattice = (
        float(math.sqrt(radicand) / lattice_denominator)
        if valid and lattice_denominator > 0.0
        else float("nan")
    )
    xi_proxy = float(xi_lattice * dx) if math.isfinite(xi_lattice) else float("nan")
    if not valid:
        if s0 <= 0.0:
            invalid_reason = "zero_mode_nonpositive"
        elif s_kmin <= 0.0:
            invalid_reason = "lowest_mode_nonpositive"
        else:
            invalid_reason = "zero_mode_not_larger_than_lowest_mode"
    else:
        invalid_reason = None

    return {
        "valid": valid,
        "invalid_reason": invalid_reason,
        "S0_raw": s0,
        "S_kmin_axis_average": s_kmin,
        "S0_over_S_kmin": ratio,
        "radicand": radicand,
        "k_min": k_min,
        "lattice_denominator": lattice_denominator,
        "xi_proxy": xi_proxy,
        "xi_over_L": float(xi_proxy / domain_length) if math.isfinite(xi_proxy) else float("nan"),
    }


def summarize_metric(rows: list[dict[str, Any]], *, xi_key: str, pass_key: str) -> dict[str, Any]:
    finite_rows = [row for row in rows if math.isfinite(finite_float(row.get(xi_key)))]
    xi_values = np.array([float(row[xi_key]) for row in finite_rows], dtype=float)
    order_values = np.array([float(row["order_parameter"]) for row in rows], dtype=float)
    valid_count = sum(1 for row in rows if bool(row.get("lowest_mode_valid")))
    pass_count = sum(1 for row in rows if bool(row.get(pass_key)))
    return {
        "case_count": len(rows),
        "finite_case_count": len(finite_rows),
        "valid_count": valid_count,
        "valid_fraction": float(valid_count / len(rows)) if rows else 0.0,
        "pass_count": pass_count,
        "pass_fraction": float(pass_count / len(rows)) if rows else 0.0,
        "min_xi_over_L": float(np.min(xi_values)) if len(xi_values) else float("nan"),
        "median_xi_over_L": float(np.median(xi_values)) if len(xi_values) else float("nan"),
        "max_xi_over_L": float(np.max(xi_values)) if len(xi_values) else float("nan"),
        "min_order_parameter": float(np.min(order_values)) if len(order_values) else float("nan"),
        "median_order_parameter": float(np.median(order_values)) if len(order_values) else float("nan"),
        "invalid_reasons": sorted(
            {
                str(row.get("lowest_mode_invalid_reason"))
                for row in rows
                if row.get("lowest_mode_invalid_reason")
            }
        ),
    }


def run_case_rows() -> list[dict[str, Any]]:
    wave24_helpers = load_module(WAVE24_SCRIPT_PATH, "wave24_structure_factor_estimator")
    wave26_helpers = load_module(WAVE26_SCRIPT_PATH, "wave26_l20_probe")
    wave23_helpers = wave24_helpers.load_wave23_helpers()

    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    xi_gate_threshold = 0.20
    order_floor = 0.005

    case_specs: list[dict[str, Any]] = []
    for steps in [4000, 4800, 5600]:
        for seed in [21001, 21002, 21003]:
            case_specs.append(
                {
                    "label": f"L16_s{steps}_fresh_seed{seed}",
                    "grid_L": 16,
                    "steps": steps,
                    "seed_set": "wave24_fresh_seed_set",
                    "seed": seed,
                }
            )
    for seed_set_label, seeds in {
        "wave25_fresh_seed_set": [21001, 21002, 21003],
        "l20_probe_seed_set": [22001, 22002, 22003],
    }.items():
        for seed in seeds:
            case_specs.append(
                {
                    "label": f"L20_{seed_set_label}_seed{seed}",
                    "grid_L": 20,
                    "steps": 4000,
                    "seed_set": seed_set_label,
                    "seed": seed,
                }
            )

    rows: list[dict[str, Any]] = []
    for spec in case_specs:
        grid_l = int(spec["grid_L"])
        steps = int(spec["steps"])
        seed = int(spec["seed"])
        status, C, mass_drift, order_parameter = wave23_helpers.simulate_final_field(
            grid_L=grid_l,
            temperature=temperature,
            steps=steps,
            dt=dt,
            dx=dx,
            kappa=kappa,
            seed=seed,
        )
        domain_length = float(grid_l * dx)
        rms = wave24_helpers.structure_factor_rms_length(C, dx)
        lowest = lowest_mode_second_moment_length(C, dx)
        rms_xi = finite_float(rms.get("xi_proxy"))
        lowest_xi = finite_float(lowest.get("xi_proxy"))
        rows.append(
            {
                "label": spec["label"],
                "grid_L": grid_l,
                "domain_length": domain_length,
                "seed_set": spec["seed_set"],
                "seed": seed,
                "temperature": float(temperature),
                "delta_t": float(1.0 - temperature),
                "steps": steps,
                "dt": float(dt),
                "dx": float(dx),
                "kappa": float(kappa),
                "spinodal_margin": float(
                    wave23_helpers.spinodal_margin(temperature, kappa, grid_l, dx)
                ),
                "status": status,
                "mass_drift_abs": mass_drift,
                "order_parameter": order_parameter,
                "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
                "rms_inverse_k_xi_proxy": rms_xi,
                "rms_inverse_k_xi_over_L": float(rms_xi / domain_length)
                if math.isfinite(rms_xi)
                else float("nan"),
                "rms_inverse_k_valid": bool(rms.get("valid")),
                "lowest_mode_xi_proxy": lowest_xi,
                "lowest_mode_xi_over_L": float(lowest_xi / domain_length)
                if math.isfinite(lowest_xi)
                else float("nan"),
                "lowest_mode_valid": bool(lowest.get("valid")),
                "lowest_mode_invalid_reason": lowest.get("invalid_reason"),
                "lowest_mode_S0_raw": finite_float(lowest.get("S0_raw")),
                "lowest_mode_S_kmin_axis_average": finite_float(
                    lowest.get("S_kmin_axis_average")
                ),
                "lowest_mode_S0_over_S_kmin": finite_float(lowest.get("S0_over_S_kmin")),
                "lowest_mode_radicand": finite_float(lowest.get("radicand")),
                "lowest_mode_k_min": finite_float(lowest.get("k_min")),
                "lowest_mode_lattice_denominator": finite_float(
                    lowest.get("lattice_denominator")
                ),
                "lowest_mode_pass": bool(
                    status == "OK"
                    and bool(lowest.get("valid"))
                    and math.isfinite(lowest_xi)
                    and lowest_xi / domain_length >= xi_gate_threshold
                    and order_parameter >= order_floor
                ),
            }
        )
    return rows


def run_lowest_mode_candidate_gate() -> dict[str, Any]:
    wave31 = load_json(WAVE31_ARTIFACT_PATH) if WAVE31_ARTIFACT_PATH.exists() else {}
    formula_boundary = load_json(FORMULA_BOUNDARY_PATH) if FORMULA_BOUNDARY_PATH.exists() else {}
    rows = run_case_rows()
    stable_rows = [row for row in rows if row["status"] == "OK"]
    l16_rows = [row for row in stable_rows if int(row["grid_L"]) == 16]
    l20_rows = [row for row in stable_rows if int(row["grid_L"]) == 20]
    lowest_summary = summarize_metric(
        stable_rows,
        xi_key="lowest_mode_xi_over_L",
        pass_key="lowest_mode_pass",
    )
    rms_summary = summarize_metric(
        stable_rows,
        xi_key="rms_inverse_k_xi_over_L",
        pass_key="rms_inverse_k_valid",
    )
    l16_lowest_summary = summarize_metric(
        l16_rows,
        xi_key="lowest_mode_xi_over_L",
        pass_key="lowest_mode_pass",
    )
    l20_lowest_summary = summarize_metric(
        l20_rows,
        xi_key="lowest_mode_xi_over_L",
        pass_key="lowest_mode_pass",
    )

    thresholds = {
        "minimum_valid_fraction_for_candidate_use": 0.75,
        "minimum_grid_groups": 2,
        "minimum_order_preserving_pass_fraction": 0.75,
        "minimum_xi_over_l": 0.20,
        "minimum_abs_xi_l20_over_l16": 1.0,
    }
    l16_median_xi = finite_float(l16_lowest_summary.get("median_xi_over_L")) * 16.0
    l20_median_xi = finite_float(l20_lowest_summary.get("median_xi_over_L")) * 20.0
    lowest_l20_over_l16 = (
        float(l20_median_xi / l16_median_xi)
        if math.isfinite(l16_median_xi) and math.isfinite(l20_median_xi) and l16_median_xi > 0.0
        else float("nan")
    )

    wave31_chain_gate = {
        "status": (
            "PASS"
            if wave31.get("blocker_label")
            == "structure_factor_source_formula_extracted_current_rms_proxy_mismatch"
            else "BLOCKED"
        ),
        "required_condition": "Wave 32 must start from the Wave 31 source-formula/current-proxy mismatch blocker.",
        "wave31_status": wave31.get("status"),
        "wave31_blocker_label": wave31.get("blocker_label"),
    }
    formula_boundary_gate = {
        "status": (
            "PASS"
            if formula_boundary.get("mapping_decision", {}).get("current_proxy_matches_source_second_moment")
            is False
            else "BLOCKED"
        ),
        "required_condition": "The Wave 31 formula boundary must reject the current RMS inverse-k proxy before this replacement candidate is evaluated.",
        "formula_boundary_path": relpath(FORMULA_BOUNDARY_PATH),
        "formula_boundary_sha256": hash_file(FORMULA_BOUNDARY_PATH)
        if FORMULA_BOUNDARY_PATH.exists()
        else None,
    }
    lowest_mode_implementation_gate = {
        "status": "PASS",
        "required_condition": "The candidate must implement xi_2nd = sqrt(S(0)/S(k_min)-1)/(2 sin(k_min/2)) and expose S(0), S(k_min), k_min, and denominator diagnostics.",
        "implemented_observables": [
            "S0_raw",
            "S_kmin_axis_average",
            "S0_over_S_kmin",
            "k_min",
            "lattice_denominator",
        ],
        "claim_boundary": "This implementation is a literal single-snapshot candidate, not an accepted ensemble susceptibility estimator.",
    }
    lowest_mode_observable_gate = {
        "status": (
            "PASS"
            if lowest_summary["valid_fraction"]
            >= thresholds["minimum_valid_fraction_for_candidate_use"]
            else "BLOCKED"
        ),
        "required_condition": "The source-family lowest-mode estimator must produce valid positive lengths in enough current field cases before it can replace the RMS proxy.",
        "valid_fraction": lowest_summary["valid_fraction"],
        "valid_count": lowest_summary["valid_count"],
        "case_count": lowest_summary["case_count"],
        "minimum_valid_fraction": thresholds["minimum_valid_fraction_for_candidate_use"],
        "invalid_reasons": lowest_summary["invalid_reasons"],
        "interpretation": "A near-zero conserved snapshot zero mode is not the same observable as an ensemble susceptibility S(0).",
    }
    finite_size_trend_gate = {
        "status": (
            "PASS"
            if math.isfinite(lowest_l20_over_l16)
            and lowest_l20_over_l16 >= thresholds["minimum_abs_xi_l20_over_l16"]
            else "BLOCKED"
        ),
        "required_condition": "If the lowest-mode candidate is valid, absolute length should not decline from L16 to L20 before exponent gates.",
        "lowest_mode_l20_over_l16": lowest_l20_over_l16,
        "minimum_abs_xi_l20_over_l16": thresholds["minimum_abs_xi_l20_over_l16"],
    }
    replacement_acceptance_gate = {
        "status": (
            "PASS"
            if lowest_mode_observable_gate["status"] == "PASS"
            and finite_size_trend_gate["status"] == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "The lowest-mode candidate can only replace the RMS proxy if observable validity and finite-size trend both pass.",
        "blocking_reasons": [
            name
            for name, gate in {
                "lowest_mode_observable_gate": lowest_mode_observable_gate,
                "finite_size_trend_gate": finite_size_trend_gate,
            }.items()
            if gate["status"] == "BLOCKED"
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until an ensemble/connected S(0) lane is derived for the conserved-order field or the window/dynamics path repairs accepted-estimator lengths.",
        "next_controller": "derive_ensemble_susceptibility_second_moment_lane_or_repair_window_dynamics",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "A lowest-mode candidate diagnostic cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 32 tests replacement feasibility only; it does not accept the estimator.",
    }

    if wave31_chain_gate["status"] != "PASS":
        blocker_label = "lowest_mode_second_moment_candidate_chain_missing"
    elif lowest_mode_observable_gate["status"] == "BLOCKED":
        blocker_label = "lowest_mode_second_moment_candidate_blocked_by_zero_mode_snapshot_observable"
    else:
        blocker_label = "lowest_mode_second_moment_candidate_requires_finite_size_acceptance"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 32 lowest-mode second-moment estimator candidate gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Lowest_Mode_Candidate_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_formula_candidate_diagnostic_only",
        "inputs": [
            artifact_record(WAVE31_ARTIFACT_PATH, "Wave 31 source-formula/current-proxy mismatch controller"),
            source_record(FORMULA_BOUNDARY_PATH, "Wave 31 formula-boundary manifest"),
            source_record(WAVE24_SCRIPT_PATH, "L16 RMS proxy and field helper source"),
            source_record(WAVE26_SCRIPT_PATH, "L20 probe parameter source"),
        ],
        "parameters": thresholds,
        "metrics": {
            "case_count": len(rows),
            "stable_case_count": len(stable_rows),
            "lowest_mode_overall": lowest_summary,
            "lowest_mode_L16": l16_lowest_summary,
            "lowest_mode_L20": l20_lowest_summary,
            "rms_inverse_k_overall": rms_summary,
            "lowest_mode_l20_over_l16": lowest_l20_over_l16,
        },
        "gates": {
            "wave31_chain_gate": wave31_chain_gate,
            "formula_boundary_gate": formula_boundary_gate,
            "lowest_mode_implementation_gate": lowest_mode_implementation_gate,
            "lowest_mode_observable_gate": lowest_mode_observable_gate,
            "finite_size_trend_gate": finite_size_trend_gate,
            "replacement_acceptance_gate": replacement_acceptance_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "sample_rows": rows[:6],
        "limitations": [
            "The literal source-family formula is evaluated on single snapshots, not on a derived ensemble susceptibility observable.",
            "Conserved-order fields are near zero-mean, so the raw zero mode can be smaller than the lowest nonzero mode.",
            "No surrogate S(0) is accepted by this gate.",
            "No exponent, universality, material, or RG claim may be upgraded from this diagnostic.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 32 implements a literal lowest-mode estimator candidate and blocks replacement because the current snapshot lane lacks a valid source-family S(0) observable.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_lowest_mode_candidate_gate()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "artifact": relpath(ARTIFACT_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )
