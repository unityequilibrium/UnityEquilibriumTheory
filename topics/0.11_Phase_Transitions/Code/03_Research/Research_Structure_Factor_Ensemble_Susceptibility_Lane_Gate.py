"""
Wave 33 ensemble/connected susceptibility lane gate.

Wave 32 implemented the source-family lowest-mode second-moment estimator but
blocked it because a single conserved-order snapshot does not provide a valid
S(0) observable. This verifier tests two explicit S(0) lanes on the same
conserved-order fields:

1. ensemble magnetization susceptibility, N * Var(<C>), which is the closer
   source-family zero-mode observable but is constrained by conserved mass;
2. spatial variance proxy, N * <Var_x(C)>, which is already used as a local
   susceptibility proxy elsewhere but is not accepted here as source-equivalent
   S(0).

The goal is to prevent a convenient surrogate from silently replacing the
source formula. Passing a diagnostic lane is not enough for exponent use.
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ensemble_susceptibility_lane_gate.json"
WAVE32_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_lowest_mode_candidate_gate.json"
WAVE24_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py"
)
WAVE32_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Structure_Factor_Lowest_Mode_Candidate_Gate.py"
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


def lowest_mode_power_norm(field: np.ndarray) -> float:
    C = np.asarray(field, dtype=float)
    spectrum = np.fft.fftn(C)
    power = np.abs(spectrum) ** 2
    grid_l = int(C.shape[0])
    values = []
    for axis in range(C.ndim):
        plus_index = [0] * C.ndim
        minus_index = [0] * C.ndim
        plus_index[axis] = 1
        minus_index[axis] = grid_l - 1
        values.append(float(power[tuple(plus_index)] / C.size))
        values.append(float(power[tuple(minus_index)] / C.size))
    return float(np.mean(values)) if values else float("nan")


def second_moment_from_s0(s0: float, skmin: float, grid_l: int, dx: float) -> dict[str, Any]:
    denominator = float(2.0 * math.sin(math.pi / grid_l))
    ratio = float(s0 / skmin) if math.isfinite(skmin) and skmin > 0.0 else float("nan")
    radicand = float(ratio - 1.0) if math.isfinite(ratio) else float("nan")
    valid = bool(math.isfinite(radicand) and radicand > 0.0 and denominator > 0.0)
    xi_lattice = float(math.sqrt(radicand) / denominator) if valid else float("nan")
    xi = float(xi_lattice * dx) if valid else float("nan")
    return {
        "S0": s0,
        "S_kmin": skmin,
        "S0_over_S_kmin": ratio,
        "radicand": radicand,
        "lattice_denominator": denominator,
        "xi_proxy": xi,
        "xi_over_L": float(xi / (grid_l * dx)) if math.isfinite(xi) else float("nan"),
        "valid": valid,
        "invalid_reason": None if valid else "S0_not_larger_than_S_kmin",
    }


def run_case_rows() -> list[dict[str, Any]]:
    wave24_helpers = load_module(WAVE24_SCRIPT_PATH, "wave24_structure_factor_estimator")
    wave23_helpers = wave24_helpers.load_wave23_helpers()
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100

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
        status, C, mass_drift, order_parameter = wave23_helpers.simulate_final_field(
            grid_L=grid_l,
            temperature=temperature,
            steps=int(spec["steps"]),
            dt=dt,
            dx=dx,
            kappa=kappa,
            seed=int(spec["seed"]),
        )
        centered = C - float(np.mean(C))
        spatial_variance = float(np.mean(centered**2))
        spatial_susceptibility_proxy = float(C.size * spatial_variance)
        rows.append(
            {
                "label": spec["label"],
                "grid_L": grid_l,
                "domain_length": float(grid_l * dx),
                "seed_set": spec["seed_set"],
                "seed": int(spec["seed"]),
                "steps": int(spec["steps"]),
                "temperature": float(temperature),
                "delta_t": float(1.0 - temperature),
                "dx": float(dx),
                "dt": float(dt),
                "kappa": float(kappa),
                "status": status,
                "mass_drift_abs": float(mass_drift),
                "field_mean": float(np.mean(C)) if np.all(np.isfinite(C)) else float("nan"),
                "spatial_variance": spatial_variance,
                "spatial_susceptibility_proxy": spatial_susceptibility_proxy,
                "lowest_mode_S_kmin_norm": lowest_mode_power_norm(C),
                "order_parameter": float(order_parameter),
                "spinodal_margin": float(wave23_helpers.spinodal_margin(temperature, kappa, grid_l, dx)),
                "max_abs_c": float(np.max(np.abs(C))) if np.all(np.isfinite(C)) else float("nan"),
            }
        )
    return rows


def group_summary(rows: list[dict[str, Any]], *, grid_l: int, label: str) -> dict[str, Any]:
    stable_rows = [row for row in rows if row["status"] == "OK"]
    means = np.asarray([float(row["field_mean"]) for row in stable_rows], dtype=float)
    skmins = np.asarray([float(row["lowest_mode_S_kmin_norm"]) for row in stable_rows], dtype=float)
    spatial_s0s = np.asarray(
        [float(row["spatial_susceptibility_proxy"]) for row in stable_rows],
        dtype=float,
    )
    orders = np.asarray([float(row["order_parameter"]) for row in stable_rows], dtype=float)
    N = float(grid_l**3)
    ensemble_s0 = float(N * np.var(means)) if len(means) else float("nan")
    mean_skmin = float(np.mean(skmins)) if len(skmins) else float("nan")
    spatial_s0 = float(np.mean(spatial_s0s)) if len(spatial_s0s) else float("nan")
    ensemble_estimator = second_moment_from_s0(ensemble_s0, mean_skmin, grid_l, 1.0)
    spatial_proxy_estimator = second_moment_from_s0(spatial_s0, mean_skmin, grid_l, 1.0)
    return {
        "label": label,
        "grid_L": grid_l,
        "case_count": len(rows),
        "stable_case_count": len(stable_rows),
        "ensemble_mean_field_mean": float(np.mean(means)) if len(means) else float("nan"),
        "ensemble_field_mean_variance": float(np.var(means)) if len(means) else float("nan"),
        "ensemble_magnetization_S0": ensemble_s0,
        "mean_S_kmin": mean_skmin,
        "spatial_variance_proxy_S0": spatial_s0,
        "median_order_parameter": float(np.median(orders)) if len(orders) else float("nan"),
        "ensemble_magnetization_estimator": ensemble_estimator,
        "spatial_variance_proxy_estimator": spatial_proxy_estimator,
    }


def safe_l20_over_l16(groups: dict[str, dict[str, Any]], lane: str) -> float:
    l16 = groups["L16_4000"][lane]["xi_proxy"]
    l20 = groups["L20_4000"][lane]["xi_proxy"]
    if not math.isfinite(l16) or not math.isfinite(l20) or l16 <= 0.0:
        return float("nan")
    return float(l20 / l16)


def run_ensemble_susceptibility_lane_gate() -> dict[str, Any]:
    wave32 = load_json(WAVE32_ARTIFACT_PATH) if WAVE32_ARTIFACT_PATH.exists() else {}
    rows = run_case_rows()
    stable_rows = [row for row in rows if row["status"] == "OK"]
    grouped = {
        "L16_all": group_summary(
            [row for row in rows if int(row["grid_L"]) == 16],
            grid_l=16,
            label="L16_all_steps",
        ),
        "L16_4000": group_summary(
            [row for row in rows if int(row["grid_L"]) == 16 and int(row["steps"]) == 4000],
            grid_l=16,
            label="L16_steps4000",
        ),
        "L20_4000": group_summary(
            [row for row in rows if int(row["grid_L"]) == 20],
            grid_l=20,
            label="L20_steps4000",
        ),
    }
    ensemble_valid_groups = [
        name
        for name in ["L16_4000", "L20_4000"]
        if grouped[name]["ensemble_magnetization_estimator"]["valid"]
    ]
    spatial_valid_groups = [
        name
        for name in ["L16_4000", "L20_4000"]
        if grouped[name]["spatial_variance_proxy_estimator"]["valid"]
    ]
    ensemble_l20_over_l16 = safe_l20_over_l16(grouped, "ensemble_magnetization_estimator")
    spatial_l20_over_l16 = safe_l20_over_l16(grouped, "spatial_variance_proxy_estimator")

    thresholds = {
        "minimum_valid_grid_groups": 2,
        "minimum_abs_xi_l20_over_l16": 1.0,
    }
    wave32_chain_gate = {
        "status": (
            "PASS"
            if wave32.get("blocker_label")
            == "lowest_mode_second_moment_candidate_blocked_by_zero_mode_snapshot_observable"
            else "BLOCKED"
        ),
        "required_condition": "Wave 33 must start from the Wave 32 zero-mode snapshot-observable blocker.",
        "wave32_status": wave32.get("status"),
        "wave32_blocker_label": wave32.get("blocker_label"),
    }
    ensemble_susceptibility_definition_gate = {
        "status": "PASS",
        "required_condition": "The candidate must separate source-closer ensemble magnetization susceptibility from the spatial-variance diagnostic proxy.",
        "lanes": {
            "ensemble_magnetization_S0": "N * Var_ensemble(mean(C))",
            "spatial_variance_proxy_S0": "mean_ensemble(N * Var_space(C))",
            "S_kmin": "mean_ensemble(|FFT(C)[k_min]|^2 / N over +/- axes)",
        },
    }
    raw_ensemble_susceptibility_gate = {
        "status": (
            "PASS"
            if len(ensemble_valid_groups) >= thresholds["minimum_valid_grid_groups"]
            else "BLOCKED"
        ),
        "required_condition": "The source-closer ensemble magnetization S(0) lane must produce valid second-moment lengths at both comparable grid sizes.",
        "valid_groups": ensemble_valid_groups,
        "minimum_valid_grid_groups": thresholds["minimum_valid_grid_groups"],
        "l20_over_l16": ensemble_l20_over_l16,
        "claim_boundary": "Mass-conserved dynamics can suppress ensemble mean fluctuations, so this lane may be physically unavailable under fixed-composition conditions.",
    }
    spatial_variance_proxy_gate = {
        "status": "WARN" if len(spatial_valid_groups) >= thresholds["minimum_valid_grid_groups"] else "BLOCKED",
        "required_condition": "The spatial-variance proxy may be recorded as a diagnostic only; it is not accepted as source-equivalent S(0).",
        "valid_groups": spatial_valid_groups,
        "l20_over_l16": spatial_l20_over_l16,
        "claim_boundary": "N * Var_space(C) aggregates nonzero modes and is not the source-family zero-mode susceptibility without a derivation.",
    }
    source_equivalence_gate = {
        "status": "BLOCKED",
        "required_condition": "No S(0) lane may feed exponent gates unless it is source-backed for conserved-order fixed-composition fields.",
        "accepted_S0_lane": None,
        "blocking_reasons": [
            "ensemble_magnetization_S0 is not valid for the current comparable L16/L20 groups"
            if raw_ensemble_susceptibility_gate["status"] == "BLOCKED"
            else "ensemble_magnetization_S0 valid but still lacks finite-size acceptance",
            "spatial_variance_proxy_S0 is diagnostic and not source-equivalent",
        ],
    }
    finite_size_trend_gate = {
        "status": (
            "PASS"
            if raw_ensemble_susceptibility_gate["status"] == "PASS"
            and math.isfinite(ensemble_l20_over_l16)
            and ensemble_l20_over_l16 >= thresholds["minimum_abs_xi_l20_over_l16"]
            else "BLOCKED"
        ),
        "required_condition": "A source-equivalent S(0) lane must show nondeclining absolute length from L16 to L20 before exponent gates.",
        "ensemble_l20_over_l16": ensemble_l20_over_l16,
        "spatial_proxy_l20_over_l16_diagnostic_only": spatial_l20_over_l16,
    }
    replacement_acceptance_gate = {
        "status": "BLOCKED",
        "required_condition": "Replacement requires source equivalence and finite-size trend to pass.",
        "blocking_reasons": [
            name
            for name, gate in {
                "raw_ensemble_susceptibility_gate": raw_ensemble_susceptibility_gate,
                "source_equivalence_gate": source_equivalence_gate,
                "finite_size_trend_gate": finite_size_trend_gate,
            }.items()
            if gate["status"] == "BLOCKED"
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until conserved-order S(0) policy is source-backed or the analysis switches to a source-backed finite-k/canonical estimator.",
        "next_controller": "source_back_conserved_order_susceptibility_or_finite_k_estimator_policy",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Susceptibility-lane diagnostics cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 33 distinguishes diagnostic S0 surrogates from source-equivalent S0 acceptance.",
    }

    if wave32_chain_gate["status"] != "PASS":
        blocker_label = "ensemble_susceptibility_lane_chain_missing"
    elif raw_ensemble_susceptibility_gate["status"] == "BLOCKED":
        blocker_label = "ensemble_susceptibility_lane_blocked_by_conserved_mean_constraint"
    else:
        blocker_label = "ensemble_susceptibility_lane_requires_source_equivalence_policy"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 33 ensemble susceptibility S0 lane gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Ensemble_Susceptibility_Lane_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "susceptibility_lane_diagnostic_only",
        "inputs": [
            artifact_record(WAVE32_ARTIFACT_PATH, "Wave 32 zero-mode snapshot-observable controller"),
            source_record(WAVE24_SCRIPT_PATH, "field generation and RMS helper source"),
            source_record(WAVE32_SCRIPT_PATH, "literal lowest-mode candidate source"),
        ],
        "parameters": thresholds,
        "metrics": {
            "case_count": len(rows),
            "stable_case_count": len(stable_rows),
            "groups": grouped,
            "ensemble_valid_groups": ensemble_valid_groups,
            "spatial_proxy_valid_groups": spatial_valid_groups,
            "ensemble_l20_over_l16": ensemble_l20_over_l16,
            "spatial_proxy_l20_over_l16": spatial_l20_over_l16,
        },
        "gates": {
            "wave32_chain_gate": wave32_chain_gate,
            "ensemble_susceptibility_definition_gate": ensemble_susceptibility_definition_gate,
            "raw_ensemble_susceptibility_gate": raw_ensemble_susceptibility_gate,
            "spatial_variance_proxy_gate": spatial_variance_proxy_gate,
            "source_equivalence_gate": source_equivalence_gate,
            "finite_size_trend_gate": finite_size_trend_gate,
            "replacement_acceptance_gate": replacement_acceptance_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "sample_rows": rows[:6],
        "limitations": [
            "The source-closer ensemble magnetization lane is constrained by conserved mass in the current field generator.",
            "The spatial variance proxy can produce a numeric length but is not accepted as source-equivalent S(0).",
            "No conserved-order fixed-composition susceptibility policy is source-backed by this wave.",
            "No exponent, universality, material, or RG claim may be upgraded from this diagnostic.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 33 blocks source-equivalent S(0) acceptance and keeps spatial-variance susceptibility as diagnostic-only.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_ensemble_susceptibility_lane_gate()
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
