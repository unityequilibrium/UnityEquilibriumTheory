"""
Wave 31 structure-factor estimator formula-boundary gate.

Wave 30 packaged source candidates for estimator review. This verifier checks
the extracted formula-boundary manifest and decides whether the current
all-nonzero-mode RMS inverse-k proxy can be treated as the source-backed
second-moment correlation-length estimator.

The expected result is conservative: source formula boundaries can pass while
the current proxy remains rejected for exponent or calibration use.
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_formula_boundary_gate.json"
SOURCE_MANIFEST_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_source_manifest.json"
)
FORMULA_BOUNDARY_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_formula_boundary.json"
)
WAVE30_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_source_manifest_gate.json"
WAVE24_SCRIPT_PATH = (
    TOPIC_DIR
    / "Code"
    / "03_Research"
    / "Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py"
)

REQUIRED_BOUNDARY_IDS = {
    "source_second_moment_lowest_mode_lattice",
    "finite_size_admissibility_boundary",
    "current_rms_inverse_k_proxy",
}

REQUIRED_SOURCE_SECOND_MOMENT_OBSERVABLES = {
    "S(0)",
    "S(k_min)",
    "k_min",
    "lattice denominator 2*sin(k_min/2)",
}


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def source_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
    }


def finite_float(value: Any, default: float = float("nan")) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def formula_by_id(boundaries: list[dict[str, Any]], boundary_id: str) -> dict[str, Any]:
    for row in boundaries:
        if row.get("boundary_id") == boundary_id:
            return row
    return {}


def run_formula_boundary_gate() -> dict[str, Any]:
    wave30 = load_json(WAVE30_ARTIFACT_PATH) if WAVE30_ARTIFACT_PATH.exists() else {}
    source_manifest = load_json(SOURCE_MANIFEST_PATH) if SOURCE_MANIFEST_PATH.exists() else {}
    formula_boundary = load_json(FORMULA_BOUNDARY_PATH) if FORMULA_BOUNDARY_PATH.exists() else {}
    boundaries = formula_boundary.get("extracted_formula_boundaries", [])
    boundary_ids = {str(row.get("boundary_id")) for row in boundaries}
    missing_boundary_ids = sorted(REQUIRED_BOUNDARY_IDS - boundary_ids)

    source_second_moment = formula_by_id(boundaries, "source_second_moment_lowest_mode_lattice")
    current_proxy = formula_by_id(boundaries, "current_rms_inverse_k_proxy")
    mapping_decision = formula_boundary.get("mapping_decision", {})
    source_observables = set(source_second_moment.get("required_observables", []))
    missing_second_moment_observables = sorted(
        REQUIRED_SOURCE_SECOND_MOMENT_OBSERVABLES - source_observables
    )
    source_ids = {str(source.get("source_id")) for source in source_manifest.get("source_candidates", [])}
    referenced_source_ids = {
        str(source_id)
        for row in boundaries
        for source_id in row.get("source_ids", [])
        if source_id
    }
    missing_referenced_sources = sorted(referenced_source_ids - source_ids)
    candidate_calibration_factor = finite_float(
        mapping_decision.get("candidate_calibration_factor_from_wave28")
    )

    wave30_chain_gate = {
        "status": (
            "PASS"
            if wave30.get("blocker_label")
            == "structure_factor_source_manifest_packaged_formula_extraction_open"
            else "BLOCKED"
        ),
        "required_condition": "Wave 31 must start from the Wave 30 source-manifest formula-extraction blocker.",
        "wave30_status": wave30.get("status"),
        "wave30_blocker_label": wave30.get("blocker_label"),
    }
    formula_boundary_schema_gate = {
        "status": (
            "PASS"
            if FORMULA_BOUNDARY_PATH.exists()
            and formula_boundary.get("schema_version")
            and not missing_boundary_ids
            else "BLOCKED"
        ),
        "required_condition": "A formula-boundary manifest must define source formula, finite-size boundary, and current-proxy rows.",
        "formula_boundary_path": relpath(FORMULA_BOUNDARY_PATH),
        "formula_boundary_sha256": hash_file(FORMULA_BOUNDARY_PATH)
        if FORMULA_BOUNDARY_PATH.exists()
        else None,
        "observed_boundary_ids": sorted(boundary_ids),
        "missing_boundary_ids": missing_boundary_ids,
    }
    source_formula_extraction_gate = {
        "status": (
            "PASS"
            if source_second_moment
            and source_second_moment.get("status") == "source_formula_boundary_extracted"
            and not missing_second_moment_observables
            and not missing_referenced_sources
            else "BLOCKED"
        ),
        "required_condition": "The source second-moment formula boundary must expose the required observables and reference packaged sources.",
        "source_formula_boundary_id": source_second_moment.get("boundary_id"),
        "required_observables": sorted(REQUIRED_SOURCE_SECOND_MOMENT_OBSERVABLES),
        "observed_observables": sorted(source_observables),
        "missing_observables": missing_second_moment_observables,
        "referenced_source_ids": sorted(referenced_source_ids),
        "missing_referenced_sources": missing_referenced_sources,
    }
    current_proxy_source_match_gate = {
        "status": (
            "PASS"
            if mapping_decision.get("current_proxy_matches_source_second_moment") is True
            else "BLOCKED"
        ),
        "required_condition": "The current RMS inverse-k proxy must match the source-family second-moment estimator before exponent or calibration use.",
        "current_formula": current_proxy.get("relation"),
        "source_formula": source_second_moment.get("relation"),
        "mapping_decision": mapping_decision.get("decision"),
        "current_proxy_matches_source_second_moment": mapping_decision.get(
            "current_proxy_matches_source_second_moment"
        ),
        "mismatch_reasons": source_second_moment.get("mismatch_to_current_proxy", []),
    }
    calibration_acceptance_gate = {
        "status": "BLOCKED",
        "required_condition": "The Wave 28 calibration factor cannot be accepted unless the estimator formula matches a source-backed relation or a separate derivation is recorded.",
        "candidate_calibration_factor": candidate_calibration_factor,
        "accepted_calibration_factor": None,
        "calibration_factor_status": "rejected_for_current_proxy_claim_use",
    }
    replacement_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until a lowest-mode second-moment estimator candidate is implemented and compared, or the window/dynamics path repairs absolute-length growth.",
        "next_controller": mapping_decision.get(
            "next_controller",
            "implement_lowest_mode_second_moment_estimator_candidate_or_repair_window_dynamics",
        ),
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Formula-boundary extraction cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": formula_boundary.get("claim_boundary"),
    }

    if wave30_chain_gate["status"] != "PASS":
        blocker_label = "structure_factor_formula_boundary_chain_missing"
    elif source_formula_extraction_gate["status"] == "PASS":
        blocker_label = "structure_factor_source_formula_extracted_current_rms_proxy_mismatch"
    else:
        blocker_label = "structure_factor_source_formula_boundary_incomplete"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 31 structure-factor estimator formula-boundary gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Formula_Boundary_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_formula_boundary_only",
        "inputs": [
            artifact_record(WAVE30_ARTIFACT_PATH, "Wave 30 source-manifest controller"),
            source_record(SOURCE_MANIFEST_PATH, "primary estimator-source manifest"),
            source_record(FORMULA_BOUNDARY_PATH, "Wave 31 extracted formula-boundary manifest"),
            source_record(WAVE24_SCRIPT_PATH, "current RMS inverse-k structure-factor proxy implementation"),
        ],
        "metrics": {
            "boundary_count": len(boundaries),
            "source_backed_boundary_count": sum(1 for row in boundaries if row.get("source_ids")),
            "missing_boundary_ids": missing_boundary_ids,
            "missing_second_moment_observables": missing_second_moment_observables,
            "current_proxy_matches_source_second_moment": mapping_decision.get(
                "current_proxy_matches_source_second_moment"
            ),
            "candidate_calibration_factor": candidate_calibration_factor,
        },
        "gates": {
            "wave30_chain_gate": wave30_chain_gate,
            "formula_boundary_schema_gate": formula_boundary_schema_gate,
            "source_formula_extraction_gate": source_formula_extraction_gate,
            "current_proxy_source_match_gate": current_proxy_source_match_gate,
            "calibration_acceptance_gate": calibration_acceptance_gate,
            "replacement_path_gate": replacement_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "The source formula boundary is extracted as a review boundary, not as a completed derivation of UET behavior.",
            "The current RMS inverse-k proxy is rejected for source-backed second-moment estimator claims.",
            "No lowest-mode second-moment estimator candidate has been implemented in the core/topic verifier path yet.",
            "The observed Wave 28 calibration factor remains unaccepted.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 31 extracts the source formula family and blocks the current RMS inverse-k proxy for source-backed exponent use.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_formula_boundary_gate()
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
