"""
Wave 28 structure-factor / axis-estimator reconciliation gate.

Wave 27 defined a conservative acceptance preflight and blocked exponent use
because the structure-factor estimator was not reconciled with the axis
correlation estimator. This verifier narrows that blocker: it checks whether
the disagreement is unstable/noisy, or whether it behaves like a stable
calibration-factor gap that still lacks derivation/source support.

This is an artifact-only diagnostic. It does not rerun dynamics, accept a
calibration factor, or promote exponent/universality claims.
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_estimator_reconciliation_gate.json"

WAVE24_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_conserved_order_spectral_l16_structure_factor_estimator.json"
WAVE26_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_conserved_order_spectral_structure_factor_l20_probe.json"
WAVE27_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_acceptance_rule_gate.json"


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


def safe_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator) or denominator <= 0:
        return float("nan")
    return float(numerator / denominator)


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


def estimator_summary(artifact: dict[str, Any], grid_label: str, grid_l: int) -> dict[str, float]:
    overall = artifact.get("metrics", {}).get("overall", {})
    axis_lower = overall.get("axis_lower_0_30", {})
    axis_default = overall.get("axis_default", {})
    sf = overall.get("structure_factor_rms", {})

    axis_lower_xi_over_l = finite_float(axis_lower.get("median_xi_over_L"))
    axis_default_xi_over_l = finite_float(axis_default.get("median_xi_over_L"))
    sf_xi_over_l = finite_float(sf.get("median_xi_over_L"))
    axis_lower_xi = finite_float(axis_lower.get("median_xi_proxy"))
    axis_default_xi = finite_float(axis_default.get("median_xi_proxy"))
    sf_xi = finite_float(sf.get("median_xi_proxy"))

    if not math.isfinite(axis_lower_xi):
        axis_lower_xi = axis_lower_xi_over_l * grid_l
    if not math.isfinite(axis_default_xi):
        axis_default_xi = axis_default_xi_over_l * grid_l
    if not math.isfinite(sf_xi):
        sf_xi = sf_xi_over_l * grid_l

    return {
        "grid_L": float(grid_l),
        "axis_default_median_xi_over_L": axis_default_xi_over_l,
        "axis_default_median_xi": axis_default_xi,
        "axis_lower_median_xi_over_L": axis_lower_xi_over_l,
        "axis_lower_median_xi": axis_lower_xi,
        "structure_factor_median_xi_over_L": sf_xi_over_l,
        "structure_factor_median_xi": sf_xi,
        "structure_factor_to_axis_lower_ratio": safe_ratio(sf_xi, axis_lower_xi),
        "structure_factor_to_axis_default_ratio": safe_ratio(sf_xi, axis_default_xi),
        "axis_lower_pass_fraction": finite_float(axis_lower.get("pass_fraction")),
        "structure_factor_pass_fraction": finite_float(sf.get("pass_fraction")),
    }


def run_reconciliation_gate() -> dict[str, Any]:
    wave24 = load_json(WAVE24_ARTIFACT_PATH) if WAVE24_ARTIFACT_PATH.exists() else {}
    wave26 = load_json(WAVE26_ARTIFACT_PATH) if WAVE26_ARTIFACT_PATH.exists() else {}
    wave27 = load_json(WAVE27_ARTIFACT_PATH) if WAVE27_ARTIFACT_PATH.exists() else {}

    l16 = estimator_summary(wave24, "L16", 16)
    l20 = estimator_summary(wave26, "L20", 20)
    ratio_l16 = l16["structure_factor_to_axis_lower_ratio"]
    ratio_l20 = l20["structure_factor_to_axis_lower_ratio"]
    ratio_drift = abs(ratio_l20 - ratio_l16) / ratio_l16 if ratio_l16 > 0 else float("nan")

    sf_l20_over_l16 = safe_ratio(
        l20["structure_factor_median_xi"],
        l16["structure_factor_median_xi"],
    )
    axis_lower_l20_over_l16 = safe_ratio(
        l20["axis_lower_median_xi"],
        l16["axis_lower_median_xi"],
    )
    axis_default_l20_over_l16 = safe_ratio(
        l20["axis_default_median_xi"],
        l16["axis_default_median_xi"],
    )

    thresholds = {
        "maximum_ratio_drift_fraction": 0.10,
        "maximum_unreconciled_estimator_ratio": 2.0,
        "minimum_abs_xi_l20_over_l16": 1.0,
    }

    wave27_chain_gate = {
        "status": (
            "PASS"
            if wave27.get("blocker_label")
            == "structure_factor_acceptance_rule_defined_current_evidence_fails_consistency"
            else "BLOCKED"
        ),
        "required_condition": "Wave 28 must start from the Wave 27 failed acceptance-rule application.",
        "wave27_status": wave27.get("status"),
        "wave27_blocker_label": wave27.get("blocker_label"),
    }
    ratio_stability_gate = {
        "status": (
            "PASS"
            if math.isfinite(ratio_drift)
            and ratio_drift <= thresholds["maximum_ratio_drift_fraction"]
            else "BLOCKED"
        ),
        "required_condition": "The structure-factor/axis-lower ratio should be stable enough across L16 and L20 to treat disagreement as a calibration-gap candidate.",
        "ratio_l16": ratio_l16,
        "ratio_l20": ratio_l20,
        "relative_ratio_drift": ratio_drift,
        "maximum_ratio_drift_fraction": thresholds["maximum_ratio_drift_fraction"],
    }
    magnitude_reconciliation_gate = {
        "status": (
            "BLOCKED"
            if max(ratio_l16, ratio_l20) > thresholds["maximum_unreconciled_estimator_ratio"]
            else "PASS"
        ),
        "required_condition": "The raw estimator ratio must stay below the unreconciled-ratio ceiling, or an explicit calibration derivation/source must exist.",
        "maximum_unreconciled_estimator_ratio": thresholds["maximum_unreconciled_estimator_ratio"],
        "max_observed_ratio": max(ratio_l16, ratio_l20),
        "calibration_derivation_or_source": None,
    }
    shared_absolute_length_trend_gate = {
        "status": (
            "PASS"
            if sf_l20_over_l16 >= thresholds["minimum_abs_xi_l20_over_l16"]
            and axis_lower_l20_over_l16 >= thresholds["minimum_abs_xi_l20_over_l16"]
            else "BLOCKED"
        ),
        "required_condition": "Both estimators should show nondecreasing absolute length from L16 to L20 before the issue is treated as estimator-only.",
        "minimum_abs_xi_l20_over_l16": thresholds["minimum_abs_xi_l20_over_l16"],
        "structure_factor_l20_over_l16": sf_l20_over_l16,
        "axis_lower_l20_over_l16": axis_lower_l20_over_l16,
        "axis_default_l20_over_l16": axis_default_l20_over_l16,
    }
    calibration_factor_gate = {
        "status": "BLOCKED",
        "required_condition": "A stable ratio can only become an accepted calibration factor after a source-backed benchmark or derivation is recorded.",
        "candidate_calibration_factor": (ratio_l16 + ratio_l20) / 2.0,
        "calibration_factor_status": "observed_stable_ratio_only",
        "claim_boundary": "Do not divide the structure-factor estimator by this factor for exponent fits until it is source-backed or derived.",
    }
    reconciliation_application_gate = {
        "status": "BLOCKED",
        "required_condition": "Estimator reconciliation may only unblock exponent preflight if ratio magnitude, calibration provenance, and shared absolute-length trend all pass.",
        "blocking_reasons": [
            name
            for name, gate in {
                "magnitude_reconciliation_gate": magnitude_reconciliation_gate,
                "shared_absolute_length_trend_gate": shared_absolute_length_trend_gate,
                "calibration_factor_gate": calibration_factor_gate,
            }.items()
            if gate["status"] == "BLOCKED"
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until a source-backed calibration factor exists or the dynamics/window repair produces nondecreasing absolute lengths.",
        "next_controller": "source_backed_estimator_calibration_or_window_repair_for_absolute_length_growth",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "This reconciliation diagnostic cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 28 shows the estimator ratio is stable enough to study, but still unaccepted and blocked for exponent use.",
    }

    if wave27_chain_gate["status"] != "PASS":
        blocker_label = "structure_factor_reconciliation_chain_missing"
    elif ratio_stability_gate["status"] == "PASS":
        blocker_label = "structure_factor_estimator_ratio_stable_but_uncalibrated_and_lengths_decline"
    else:
        blocker_label = "structure_factor_estimator_ratio_unstable_reconciliation_blocked"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 28 structure-factor / axis-estimator reconciliation gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Estimator_Reconciliation_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "diagnostic_estimator_reconciliation_only",
        "inputs": [
            artifact_record(WAVE24_ARTIFACT_PATH, "Wave 24 L16 estimator comparison"),
            artifact_record(WAVE26_ARTIFACT_PATH, "Wave 26 L20 estimator comparison"),
            artifact_record(WAVE27_ARTIFACT_PATH, "Wave 27 acceptance-rule preflight"),
        ],
        "parameters": thresholds,
        "metrics": {
            "L16": l16,
            "L20": l20,
            "ratio_l16": ratio_l16,
            "ratio_l20": ratio_l20,
            "relative_ratio_drift": ratio_drift,
            "candidate_calibration_factor": (ratio_l16 + ratio_l20) / 2.0,
            "structure_factor_l20_over_l16": sf_l20_over_l16,
            "axis_lower_l20_over_l16": axis_lower_l20_over_l16,
            "axis_default_l20_over_l16": axis_default_l20_over_l16,
        },
        "gates": {
            "wave27_chain_gate": wave27_chain_gate,
            "ratio_stability_gate": ratio_stability_gate,
            "magnitude_reconciliation_gate": magnitude_reconciliation_gate,
            "shared_absolute_length_trend_gate": shared_absolute_length_trend_gate,
            "calibration_factor_gate": calibration_factor_gate,
            "reconciliation_application_gate": reconciliation_application_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "A stable estimator ratio is not a derivation or source-backed calibration.",
            "Both axis-lower and structure-factor absolute lengths decline from L16 to L20, so the current blocker is not estimator-only.",
            "No exponent, universality, material, or RG claim may be upgraded from this diagnostic.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 28 narrows the blocker to source-backed estimator calibration or a window/dynamics repair that restores absolute-length growth.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_reconciliation_gate()
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
