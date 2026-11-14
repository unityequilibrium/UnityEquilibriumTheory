"""
Wave 27 structure-factor acceptance-rule preflight.

Wave 26 showed that the L20 structure-factor proxy relieves one domain-scale
symptom, but it did not define which grids or estimator disagreements are
admissible for exponent fitting. This verifier turns that vague blocker into a
machine-readable rule application.

The rule below is a topic-derived preflight, not accepted physics. It decides
whether the current Wave 24-26 artifact chain is ready to feed exponent or
universality gates. It does not rerun the dynamics and it does not promote the
structure-factor proxy to a critical correlation length.
"""

from __future__ import annotations

import json
import math
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_acceptance_rule_gate.json"

WAVE24_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_conserved_order_spectral_l16_structure_factor_estimator.json"
WAVE25_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_conserved_order_spectral_structure_factor_multigrid_calibration.json"
WAVE26_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_conserved_order_spectral_structure_factor_l20_probe.json"


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


def status_from_blockers(blockers: list[bool]) -> str:
    return "BLOCKED" if any(blockers) else "PASS"


def run_acceptance_rule_gate() -> dict[str, Any]:
    wave24 = load_json(WAVE24_ARTIFACT_PATH) if WAVE24_ARTIFACT_PATH.exists() else {}
    wave25 = load_json(WAVE25_ARTIFACT_PATH) if WAVE25_ARTIFACT_PATH.exists() else {}
    wave26 = load_json(WAVE26_ARTIFACT_PATH) if WAVE26_ARTIFACT_PATH.exists() else {}

    thresholds = {
        "domain_scale_exclusion_xi_over_L": 0.75,
        "largest_grid_strong_relief_xi_over_L": 0.45,
        "minimum_admissible_grid_count": 3,
        "minimum_abs_xi_adjacent_ratio": 1.0,
        "maximum_unreconciled_estimator_ratio": 2.0,
    }

    wave26_scaling = wave26.get("metrics", {}).get("extended_structure_factor_scaling", {})
    xi_over_l_by_grid = {
        int(key): finite_float(value)
        for key, value in wave26_scaling.get("median_xi_over_L_by_grid", {}).items()
    }
    xi_proxy_by_grid = {
        int(key): finite_float(value)
        for key, value in wave26_scaling.get("median_xi_proxy_by_grid", {}).items()
    }
    grid_sizes = sorted(xi_over_l_by_grid)
    admissible_grids = [
        grid
        for grid in grid_sizes
        if xi_over_l_by_grid[grid] < thresholds["domain_scale_exclusion_xi_over_L"]
    ]
    excluded_domain_scale_grids = [
        grid
        for grid in grid_sizes
        if xi_over_l_by_grid[grid] >= thresholds["domain_scale_exclusion_xi_over_L"]
    ]

    adjacent_abs_xi_ratios: dict[str, float] = {}
    for left, right in zip(grid_sizes, grid_sizes[1:]):
        left_xi = xi_proxy_by_grid.get(left, float("nan"))
        right_xi = xi_proxy_by_grid.get(right, float("nan"))
        ratio = right_xi / left_xi if math.isfinite(left_xi) and left_xi > 0 else float("nan")
        adjacent_abs_xi_ratios[f"L{right}/L{left}"] = float(ratio)

    largest_grid = max(grid_sizes) if grid_sizes else None
    largest_grid_xi_over_l = (
        xi_over_l_by_grid[largest_grid] if largest_grid is not None else float("nan")
    )
    l20_ratio = finite_float(wave26_scaling.get("l20_over_l16_xi_proxy_ratio"))
    estimator_ratio = finite_float(wave26_scaling.get("l20_structure_factor_to_axis_lower_ratio"))
    log_xi_vs_log_l = wave26_scaling.get("log_xi_vs_log_L", {})

    expected_blockers = {
        "wave24": "spectral_core_l16_structure_factor_domain_scale_needs_multigrid_calibration",
        "wave25": "spectral_core_structure_factor_multigrid_domain_scale_saturated",
        "wave26": "spectral_core_structure_factor_larger_grid_probe_needs_acceptance_rule",
    }
    artifact_chain_gate = {
        "status": (
            "PASS"
            if wave24.get("blocker_label") == expected_blockers["wave24"]
            and wave25.get("blocker_label") == expected_blockers["wave25"]
            and wave26.get("blocker_label") == expected_blockers["wave26"]
            else "BLOCKED"
        ),
        "required_condition": "Wave 27 must start from the Wave 24-26 estimator-calibration blocker chain.",
        "expected_blockers": expected_blockers,
        "observed_blockers": {
            "wave24": wave24.get("blocker_label"),
            "wave25": wave25.get("blocker_label"),
            "wave26": wave26.get("blocker_label"),
        },
    }

    candidate_rule_definition_gate = {
        "status": "PASS",
        "required_condition": "The verifier must expose an explicit preflight rule before any exponent rerun uses the structure-factor proxy.",
        "rule_id": "sf_rms_acceptance_preflight_v1",
        "rule_origin": "topic_derived_preflight_rule",
        "rule_scope": "Controls whether current artifacts may feed finite-size/exponent gates; it is not physics acceptance.",
        "requirements": [
            "Exclude grids whose median structure-factor xi/L is domain-scale saturated.",
            "Keep the largest included grid below the strong-relief xi/L threshold.",
            "Retain at least three admissible grid sizes before any exponent preflight.",
            "Require absolute structure-factor length to be nondecreasing across adjacent grids.",
            "Require a documented reconciliation rule when structure-factor and axis estimators disagree strongly.",
        ],
        "thresholds": thresholds,
    }

    domain_scale_exclusion_gate = {
        "status": "BLOCKED" if excluded_domain_scale_grids else "PASS",
        "required_condition": "No grid with median structure-factor xi/L >= 0.75 may be silently included in exponent fitting.",
        "median_xi_over_L_by_grid": xi_over_l_by_grid,
        "excluded_domain_scale_grids": excluded_domain_scale_grids,
        "candidate_admissible_grids": admissible_grids,
    }

    admissible_subset_gate = {
        "status": (
            "PASS"
            if len(admissible_grids) >= thresholds["minimum_admissible_grid_count"]
            and math.isfinite(largest_grid_xi_over_l)
            and largest_grid_xi_over_l <= thresholds["largest_grid_strong_relief_xi_over_L"]
            else "BLOCKED"
        ),
        "required_condition": "A declared subset must retain at least three grids and the largest grid must satisfy strong domain-scale relief.",
        "candidate_admissible_grids": admissible_grids,
        "largest_grid": largest_grid,
        "largest_grid_xi_over_L": largest_grid_xi_over_l,
    }

    monotonicity_failures = [
        key
        for key, ratio in adjacent_abs_xi_ratios.items()
        if not math.isfinite(ratio) or ratio < thresholds["minimum_abs_xi_adjacent_ratio"]
    ]
    absolute_length_consistency_gate = {
        "status": "BLOCKED" if monotonicity_failures else "PASS",
        "required_condition": "Absolute structure-factor length should be nondecreasing with grid size before it is used as a scaling length.",
        "median_xi_proxy_by_grid": xi_proxy_by_grid,
        "adjacent_abs_xi_ratios": adjacent_abs_xi_ratios,
        "failing_adjacent_ratios": monotonicity_failures,
        "l20_over_l16_xi_proxy_ratio": l20_ratio,
        "log_xi_vs_log_L": log_xi_vs_log_l,
    }

    estimator_reconciliation_gate = {
        "status": (
            "BLOCKED"
            if not math.isfinite(estimator_ratio)
            or estimator_ratio > thresholds["maximum_unreconciled_estimator_ratio"]
            else "WARN"
        ),
        "required_condition": "Structure-factor and axis-threshold estimators need a documented reconciliation rule before exponent fitting.",
        "structure_factor_to_axis_lower_ratio_at_l20": estimator_ratio,
        "maximum_unreconciled_estimator_ratio": thresholds["maximum_unreconciled_estimator_ratio"],
        "reconciliation_artifact": None,
    }

    source_or_derivation_support_gate = {
        "status": "WARN",
        "required_condition": "The rule must be source-backed or explicitly derived before it can promote claims.",
        "current_support": "topic_derived_preflight_only",
        "claim_boundary": "This verifier defines a conservative preflight rule but does not source-lock the estimator to an external benchmark.",
    }

    application_blockers = [
        artifact_chain_gate["status"] != "PASS",
        domain_scale_exclusion_gate["status"] == "BLOCKED",
        admissible_subset_gate["status"] != "PASS",
        absolute_length_consistency_gate["status"] == "BLOCKED",
        estimator_reconciliation_gate["status"] == "BLOCKED",
    ]
    acceptance_rule_application_gate = {
        "status": status_from_blockers(application_blockers),
        "required_condition": "The current artifact chain must satisfy the preflight rule before exponent or universality gates may use the structure-factor proxy.",
        "accepted_for_exponent_gate": False,
        "blocking_reasons": [
            name
            for name, gate in {
                "artifact_chain_gate": artifact_chain_gate,
                "domain_scale_exclusion_gate": domain_scale_exclusion_gate,
                "admissible_subset_gate": admissible_subset_gate,
                "absolute_length_consistency_gate": absolute_length_consistency_gate,
                "estimator_reconciliation_gate": estimator_reconciliation_gate,
            }.items()
            if gate["status"] == "BLOCKED"
        ],
    }

    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent or universality gates until the preflight blockers are cleared or an external/source-backed estimator benchmark overrides them.",
        "next_controller": "structure_factor_absolute_length_consistency_and_estimator_reconciliation",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "The acceptance-rule artifact must not promote the estimator, operator, exponent, material, RG, or universality claim.",
        "claim_boundary": "Wave 27 defines and applies a preflight rule; the current evidence fails it.",
    }

    if artifact_chain_gate["status"] != "PASS":
        blocker_label = "structure_factor_acceptance_rule_chain_missing"
    elif acceptance_rule_application_gate["status"] == "PASS":
        blocker_label = "structure_factor_acceptance_rule_preflight_passed_exponent_gate_next"
    else:
        blocker_label = "structure_factor_acceptance_rule_defined_current_evidence_fails_consistency"

    inputs = [
        artifact_record(WAVE24_ARTIFACT_PATH, "Wave 24 single-grid structure-factor estimator controller"),
        artifact_record(WAVE25_ARTIFACT_PATH, "Wave 25 multi-grid domain-scale calibration controller"),
        artifact_record(WAVE26_ARTIFACT_PATH, "Wave 26 L20 larger-grid acceptance-rule controller"),
    ]

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 27 structure-factor acceptance-rule preflight",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Acceptance_Rule_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_acceptance_preflight_only",
        "inputs": inputs,
        "acceptance_rule": {
            "rule_id": "sf_rms_acceptance_preflight_v1",
            "origin": "topic_derived_preflight_rule",
            "proof_status": "heuristic_preflight_not_physics_acceptance",
            "thresholds": thresholds,
            "allowed_use_if_passed": "May justify rerunning a separate exponent/universality verifier; does not itself validate exponent claims.",
            "forbidden_use": "Must not be cited as an accepted critical correlation length, material validation, RG closure, or universality-class shift.",
        },
        "metrics": {
            "grid_sizes": grid_sizes,
            "median_xi_over_L_by_grid": xi_over_l_by_grid,
            "median_xi_proxy_by_grid": xi_proxy_by_grid,
            "candidate_admissible_grids": admissible_grids,
            "excluded_domain_scale_grids": excluded_domain_scale_grids,
            "adjacent_abs_xi_ratios": adjacent_abs_xi_ratios,
            "l20_over_l16_xi_proxy_ratio": l20_ratio,
            "structure_factor_to_axis_lower_ratio_at_l20": estimator_ratio,
            "log_xi_vs_log_L": log_xi_vs_log_l,
        },
        "gates": {
            "artifact_chain_gate": artifact_chain_gate,
            "candidate_rule_definition_gate": candidate_rule_definition_gate,
            "domain_scale_exclusion_gate": domain_scale_exclusion_gate,
            "admissible_subset_gate": admissible_subset_gate,
            "absolute_length_consistency_gate": absolute_length_consistency_gate,
            "estimator_reconciliation_gate": estimator_reconciliation_gate,
            "source_or_derivation_support_gate": source_or_derivation_support_gate,
            "acceptance_rule_application_gate": acceptance_rule_application_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "The preflight rule is topic-derived and conservative; it is not an externally validated estimator theory.",
            "The current artifact chain still contains a domain-scale L8 point that must be excluded or justified before exponent fitting.",
            "The current absolute structure-factor length is not monotone from L16 to L20.",
            "The structure-factor and axis-threshold estimators remain unreconciled.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 27 only narrows the blocker to absolute-length consistency plus estimator reconciliation.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_acceptance_rule_gate()
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
