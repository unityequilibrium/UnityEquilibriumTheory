"""
Wave 26 conserved-order spectral structure-factor L20 larger-grid probe.

Wave 25 showed that the threshold-free structure-factor RMS estimator
replicates across L=8, 12, and 16, but remains close enough to the domain scale
that it cannot support exponent or universality gates. This verifier adds an
L=20 probe and combines the new L20 medians with the Wave 25 L=8/12/16 medians.

This is a calibration diagnostic only. It does not promote the estimator, the
spectral conserved-order operator, or any UET phase-transition claim.
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
    / "0_11_conserved_order_spectral_structure_factor_l20_probe.json"
)
CSV_PATH = TOPIC_DIR / "Result" / "gl_conserved_order_spectral_structure_factor_l20_probe_stats.csv"
CORE_ENGINE_PATH = ROOT / "docs" / "core" / "uet_master_equation.py"
WAVE25_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_Structure_Factor_Multigrid_Calibration.py"
)
WAVE25_ARTIFACT_PATH = (
    TOPIC_DIR
    / "Result"
    / "artifacts"
    / "0_11_conserved_order_spectral_structure_factor_multigrid_calibration.json"
)
INBOX_ALIGNMENT_ARTIFACT_PATH = ROOT / "docs" / "core" / "artifacts" / "inbox_research_alignment_gate.json"


def load_wave25_helpers():
    spec = importlib.util.spec_from_file_location("wave25_multigrid_calibration", WAVE25_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Wave 25 helper script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def run_l20_probe() -> dict[str, Any]:
    wave25_helpers = load_wave25_helpers()
    wave24_helpers = wave25_helpers.load_wave24_helpers()
    wave23_helpers = wave24_helpers.load_wave23_helpers()
    wave25 = load_json(WAVE25_ARTIFACT_PATH) if WAVE25_ARTIFACT_PATH.exists() else {}
    inbox_alignment = (
        load_json(INBOX_ALIGNMENT_ARTIFACT_PATH) if INBOX_ALIGNMENT_ARTIFACT_PATH.exists() else {}
    )

    grid_L = 20
    seed_sets = {
        "wave25_fresh_seed_set": [21001, 21002, 21003],
        "l20_probe_seed_set": [22001, 22002, 22003],
    }
    dx = 1.0
    dt = 0.05
    temperature = 0.900
    kappa = 0.100
    steps = 4000
    xi_gate_threshold = 0.20
    order_floor = 0.005
    domain_scale_warning_threshold = 0.50
    l20_relief_threshold = 0.50
    l20_strong_relief_threshold = 0.45
    lower_axis_threshold = 0.30

    rows: list[dict[str, Any]] = []
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
            sf_xi = finite_float(sf.get("xi_proxy"))
            sf_xi_over_l = float(sf_xi / domain_length) if math.isfinite(sf_xi) else float("nan")
            axis_default_xi_over_l = float(axis_default_xi / domain_length)
            axis_lower_xi_over_l = float(axis_lower_xi / domain_length)
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
                    "spinodal_margin": float(wave23_helpers.spinodal_margin(temperature, kappa, grid_L, dx)),
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
                    "structure_factor_total_power": finite_float(sf.get("total_power")),
                    "structure_factor_mean_k2": finite_float(sf.get("mean_k2")),
                    "structure_factor_rms_k": finite_float(sf.get("rms_k")),
                    "structure_factor_valid": bool(sf.get("valid")),
                    "structure_factor_pass": bool(
                        status == "OK"
                        and bool(sf.get("valid"))
                        and sf_xi_over_l >= xi_gate_threshold
                        and order_parameter >= order_floor
                    ),
                }
            )

    stable_rows = [row for row in rows if row["status"] == "OK"]
    positive_margin_rows = [row for row in stable_rows if float(row["spinodal_margin"]) > 0.0]
    sf_valid_rows = [row for row in stable_rows if bool(row["structure_factor_valid"])]

    overall = {
        "axis_default": wave25_helpers.summarize_metric(
            stable_rows,
            xi_key="axis_default_xi_over_L",
            pass_key="axis_default_pass",
        ),
        "axis_lower_0_30": wave25_helpers.summarize_metric(
            stable_rows,
            xi_key="axis_lower_xi_over_L",
            pass_key="axis_lower_pass",
        ),
        "structure_factor_rms": wave25_helpers.summarize_metric(
            stable_rows,
            xi_key="structure_factor_xi_over_L",
            pass_key="structure_factor_pass",
        ),
    }
    by_seed_set = {
        seed_set_label: {
            "axis_default": wave25_helpers.summarize_metric(
                [row for row in stable_rows if row["seed_set"] == seed_set_label],
                xi_key="axis_default_xi_over_L",
                pass_key="axis_default_pass",
            ),
            "axis_lower_0_30": wave25_helpers.summarize_metric(
                [row for row in stable_rows if row["seed_set"] == seed_set_label],
                xi_key="axis_lower_xi_over_L",
                pass_key="axis_lower_pass",
            ),
            "structure_factor_rms": wave25_helpers.summarize_metric(
                [row for row in stable_rows if row["seed_set"] == seed_set_label],
                xi_key="structure_factor_xi_over_L",
                pass_key="structure_factor_pass",
            ),
        }
        for seed_set_label in seed_sets
    }

    wave25_scaling = wave25.get("metrics", {}).get("structure_factor_scaling", {})
    prior_xi_over_l = {
        str(key): finite_float(value)
        for key, value in wave25_scaling.get("median_xi_over_L_by_grid", {}).items()
    }
    prior_xi_proxy = {
        str(key): finite_float(value)
        for key, value in wave25_scaling.get("median_xi_proxy_by_grid", {}).items()
    }
    l20_median_xi_over_l = overall["structure_factor_rms"]["median_xi_over_L"]
    l20_median_xi_proxy = overall["structure_factor_rms"]["median_xi_proxy"]
    extended_xi_over_l = dict(prior_xi_over_l)
    extended_xi_proxy = dict(prior_xi_proxy)
    extended_xi_over_l[str(grid_L)] = l20_median_xi_over_l
    extended_xi_proxy[str(grid_L)] = l20_median_xi_proxy

    sorted_grid_sizes = sorted(int(key) for key in extended_xi_proxy)
    extended_scaling = wave25_helpers.log_slope(
        [float(size) for size in sorted_grid_sizes],
        [float(extended_xi_proxy[str(size)]) for size in sorted_grid_sizes],
    )
    median_xi_over_l_values = [float(extended_xi_over_l[str(size)]) for size in sorted_grid_sizes]
    prior_l16_xi_over_l = prior_xi_over_l.get("16", float("nan"))
    prior_l16_xi_proxy = prior_xi_proxy.get("16", float("nan"))
    l20_minus_l16_xi_over_l = float(l20_median_xi_over_l - prior_l16_xi_over_l)
    l20_over_l16_xi_proxy_ratio = (
        float(l20_median_xi_proxy / prior_l16_xi_proxy)
        if math.isfinite(prior_l16_xi_proxy) and prior_l16_xi_proxy > 0
        else float("nan")
    )
    l20_axis_lower_median = overall["axis_lower_0_30"]["median_xi_over_L"]
    l20_estimator_ratio_to_axis_lower = (
        float(l20_median_xi_over_l / l20_axis_lower_median)
        if math.isfinite(l20_axis_lower_median) and l20_axis_lower_median > 0
        else float("nan")
    )

    wave25_chain_gate = {
        "status": (
            "PASS"
            if wave25.get("blocker_label")
            == "spectral_core_structure_factor_multigrid_domain_scale_saturated"
            else "BLOCKED"
        ),
        "required_condition": "Wave 26 must start from the Wave 25 domain-scale saturation blocker.",
        "wave25_status": wave25.get("status"),
        "wave25_blocker_label": wave25.get("blocker_label"),
    }
    inbox_chain_gate = {
        "status": (
            "PASS"
            if inbox_alignment.get("blocker_label")
            == "inbox_claims_mapped_current_controller_domain_scale_saturation"
            else "BLOCKED"
        ),
        "required_condition": "The inbox alignment gate must point to the current domain-scale calibration controller.",
        "inbox_status": inbox_alignment.get("status"),
        "inbox_blocker_label": inbox_alignment.get("blocker_label"),
    }
    engine_path_gate = {
        "status": "PASS",
        "required_condition": "The probe must generate fields through docs.core.uet_master_equation via Wave 23/24/25 helpers.",
        "operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "core_engine_path": relpath(CORE_ENGINE_PATH),
    }
    larger_grid_probe_gate = {
        "status": (
            "PASS"
            if len(stable_rows) == len(rows)
            and len(positive_margin_rows) == len(rows)
            and len(sf_valid_rows) == len(rows)
            else "BLOCKED"
        ),
        "required_condition": "All L20 cases must be stable, positive-margin, and structure-factor measurable.",
        "grid_L": grid_L,
        "case_count": len(rows),
        "stable_case_count": len(stable_rows),
        "positive_margin_case_count": len(positive_margin_rows),
        "structure_factor_valid_case_count": len(sf_valid_rows),
        "minimum_spinodal_margin": float(min(float(row["spinodal_margin"]) for row in rows)),
    }
    l20_margin_gate = {
        "status": (
            "PASS"
            if overall["structure_factor_rms"]["pass_fraction"] >= 0.75
            and overall["structure_factor_rms"]["min_xi_over_L"] >= xi_gate_threshold
            and overall["structure_factor_rms"]["min_order_parameter"] >= order_floor
            else "BLOCKED"
        ),
        "required_condition": "The L20 structure-factor margin must replicate before interpreting larger-grid behavior.",
        "xi_gate_threshold": xi_gate_threshold,
        "order_floor": order_floor,
        "overall": overall["structure_factor_rms"],
        "by_seed_set": {
            label: summary["structure_factor_rms"] for label, summary in by_seed_set.items()
        },
    }
    l20_domain_scale_relief_gate = {
        "status": (
            "PASS"
            if l20_median_xi_over_l <= l20_strong_relief_threshold
            else "WARN"
            if l20_median_xi_over_l <= l20_relief_threshold
            else "BLOCKED"
        ),
        "required_condition": "The L20 median xi/L should fall below the domain-scale warning threshold, with strong relief below 0.45.",
        "domain_scale_warning_threshold": domain_scale_warning_threshold,
        "l20_relief_threshold": l20_relief_threshold,
        "l20_strong_relief_threshold": l20_strong_relief_threshold,
        "l20_median_xi_over_L": l20_median_xi_over_l,
        "wave25_l16_median_xi_over_L": prior_l16_xi_over_l,
        "l20_minus_l16_xi_over_L": l20_minus_l16_xi_over_l,
    }
    extended_scaling_gate = {
        "status": "WARN",
        "required_condition": "Four-grid scaling is evidence for estimator triage only; it is not accepted finite-size scaling.",
        "grid_sizes": sorted_grid_sizes,
        "median_xi_over_L_by_grid": extended_xi_over_l,
        "median_xi_proxy_by_grid": extended_xi_proxy,
        "median_xi_over_L_spread": float(max(median_xi_over_l_values) - min(median_xi_over_l_values)),
        "log_xi_vs_log_L": extended_scaling,
        "l20_over_l16_xi_proxy_ratio": l20_over_l16_xi_proxy_ratio,
    }
    derived_acceptance_rule_gate = {
        "status": "BLOCKED",
        "required_condition": "Before exponent gates can use this estimator, a source-backed or derived acceptance rule must justify which grids, thresholds, and estimator disagreements are admissible.",
        "candidate_rule_requirements": [
            "No grid used for exponent fitting should have median structure-factor xi/L at or above 0.75.",
            "The largest-grid median structure-factor xi/L should stay below 0.45 or be justified by an external/source-backed benchmark.",
            "Structure-factor and axis-threshold estimators must have a documented reconciliation rule before exponent fitting.",
            "At least one independent benchmark or derived finite-size rule must be recorded before universality claims.",
        ],
        "current_failures": {
            "prior_l8_domain_scale": prior_xi_over_l.get("8", float("nan")) >= 0.75,
            "largest_grid_above_strong_relief": l20_median_xi_over_l > l20_strong_relief_threshold,
            "structure_factor_to_axis_lower_ratio": l20_estimator_ratio_to_axis_lower,
        },
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent or universality gates until the acceptance rule or a source-backed estimator benchmark is available.",
        "claim_boundary": "Wave 26 can only decide the next estimator-calibration path; it cannot validate scaling claims.",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This diagnostic cannot validate exponent, material, RG, or universality claims.",
        "claim_boundary": "L20 larger-grid behavior is estimator triage only.",
    }

    if larger_grid_probe_gate["status"] != "PASS":
        blocker_label = "spectral_core_structure_factor_l20_probe_not_stable"
    elif l20_margin_gate["status"] != "PASS":
        blocker_label = "spectral_core_structure_factor_l20_margin_not_replicated"
    elif l20_domain_scale_relief_gate["status"] == "BLOCKED":
        blocker_label = "spectral_core_structure_factor_domain_scale_persists_at_l20"
    else:
        blocker_label = "spectral_core_structure_factor_larger_grid_probe_needs_acceptance_rule"

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
            "path": relpath(WAVE25_SCRIPT_PATH),
            "sha256": hash_file(WAVE25_SCRIPT_PATH),
            "role": "Wave 25 multigrid helper and prior calibration artifact builder",
        },
    ]
    if WAVE25_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(WAVE25_ARTIFACT_PATH),
                "sha256": hash_file(WAVE25_ARTIFACT_PATH),
                "role": "Wave 25 domain-scale saturation controller",
            }
        )
    if INBOX_ALIGNMENT_ARTIFACT_PATH.exists():
        inputs.append(
            {
                "path": relpath(INBOX_ALIGNMENT_ARTIFACT_PATH),
                "sha256": hash_file(INBOX_ALIGNMENT_ARTIFACT_PATH),
                "role": "inbox alignment controller",
            }
        )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 26 conserved_order_spectral_v1 structure-factor L20 larger-grid probe",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Structure_Factor_L20_Probe.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_larger_grid_estimator_probe_only",
        "candidate_operator_mode": CONSERVED_ORDER_SPECTRAL_OPERATOR_MODE,
        "inputs": inputs,
        "parameters": {
            "grid_L": grid_L,
            "seed_sets": seed_sets,
            "dx": dx,
            "dt": dt,
            "temperature": temperature,
            "kappa": kappa,
            "steps": steps,
            "xi_gate_threshold": xi_gate_threshold,
            "order_floor": order_floor,
            "domain_scale_warning_threshold": domain_scale_warning_threshold,
            "l20_relief_threshold": l20_relief_threshold,
            "l20_strong_relief_threshold": l20_strong_relief_threshold,
            "axis_default_threshold": math.exp(-1.0),
            "axis_lower_threshold": lower_axis_threshold,
            "structure_factor_formula": "xi_sf = 2*pi / sqrt(sum(S(k)*k^2)/sum(S(k))) over nonzero FFT modes",
            "case_count": len(rows),
        },
        "metrics": {
            "overall": overall,
            "by_seed_set": by_seed_set,
            "wave25_reference": {
                "median_xi_over_L_by_grid": prior_xi_over_l,
                "median_xi_proxy_by_grid": prior_xi_proxy,
            },
            "extended_structure_factor_scaling": {
                "median_xi_over_L_by_grid": extended_xi_over_l,
                "median_xi_proxy_by_grid": extended_xi_proxy,
                "log_xi_vs_log_L": extended_scaling,
                "l20_minus_l16_xi_over_L": l20_minus_l16_xi_over_l,
                "l20_over_l16_xi_proxy_ratio": l20_over_l16_xi_proxy_ratio,
                "l20_structure_factor_to_axis_lower_ratio": l20_estimator_ratio_to_axis_lower,
            },
            "stats_csv": str(CSV_PATH.relative_to(TOPIC_DIR)).replace("\\", "/"),
        },
        "gates": {
            "wave25_chain_gate": wave25_chain_gate,
            "inbox_chain_gate": inbox_chain_gate,
            "engine_path_gate": engine_path_gate,
            "larger_grid_probe_gate": larger_grid_probe_gate,
            "l20_margin_gate": l20_margin_gate,
            "l20_domain_scale_relief_gate": l20_domain_scale_relief_gate,
            "extended_scaling_gate": extended_scaling_gate,
            "derived_acceptance_rule_gate": derived_acceptance_rule_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "This is a larger-grid estimator probe, not a finite-size scaling proof.",
            "A lower L20 xi/L can reduce one symptom of domain-scale saturation but does not define an accepted estimator rule.",
            "The result must not be used as material validation, RG closure, or a universality-class claim.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims until a source-backed or derived structure-factor acceptance rule exists and exponent gates are rerun.",
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
    result = run_l20_probe()
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"Wrote {ARTIFACT_PATH}")
