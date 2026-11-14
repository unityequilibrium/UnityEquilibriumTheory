"""
Wave 30 structure-factor estimator source-manifest gate.

Wave 29 found no local source support for accepting the structure-factor
calibration. This verifier checks a new source manifest that packages primary
source candidates for second-moment / finite-size correlation-length review.

Passing this gate means the source candidates are organized for review. It does
not mean the estimator formula, calibration factor, exponent gate, or
universality claim is accepted.
"""

from __future__ import annotations

import json
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_source_manifest_gate.json"
SOURCE_MANIFEST_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_source_manifest.json"
)
WAVE29_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_calibration_source_support_gate.json"

REQUIRED_FORMULA_ROLES = {
    "finite_size_scaling_and_3d_ising_correlation_length_benchmark_candidate",
    "reduced_second_moment_correlation_length_candidate",
    "finite_size_correlation_length_regime_caution_candidate",
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


def manifest_source_ready(source: dict[str, Any]) -> bool:
    required_fields = [
        "source_id",
        "title",
        "url",
        "doi",
        "formula_role",
        "claim_boundary",
        "primary_source",
        "local_status",
    ]
    return all(source.get(field) not in (None, "") for field in required_fields) and bool(
        source.get("primary_source")
    )


def run_source_manifest_gate() -> dict[str, Any]:
    wave29 = load_json(WAVE29_ARTIFACT_PATH) if WAVE29_ARTIFACT_PATH.exists() else {}
    manifest = load_json(SOURCE_MANIFEST_PATH) if SOURCE_MANIFEST_PATH.exists() else {}
    sources = manifest.get("source_candidates", [])
    ready_sources = [source for source in sources if manifest_source_ready(source)]
    formula_roles = {str(source.get("formula_role")) for source in ready_sources}
    missing_roles = sorted(REQUIRED_FORMULA_ROLES - formula_roles)
    metadata_only_sources = [
        source for source in ready_sources if source.get("local_status") == "metadata_only_not_formula_extracted"
    ]
    local_full_text_sources = [
        source for source in ready_sources if source.get("local_full_text_path")
    ]

    wave29_chain_gate = {
        "status": (
            "PASS"
            if wave29.get("blocker_label")
            == "structure_factor_calibration_source_support_missing_locally"
            else "BLOCKED"
        ),
        "required_condition": "Wave 30 must start from the Wave 29 local source-support gap.",
        "wave29_status": wave29.get("status"),
        "wave29_blocker_label": wave29.get("blocker_label"),
    }
    manifest_schema_gate = {
        "status": "PASS" if SOURCE_MANIFEST_PATH.exists() and manifest.get("schema_version") else "BLOCKED",
        "required_condition": "A source manifest must exist with schema_version and candidate source rows.",
        "manifest_path": relpath(SOURCE_MANIFEST_PATH),
        "manifest_sha256": hash_file(SOURCE_MANIFEST_PATH) if SOURCE_MANIFEST_PATH.exists() else None,
        "source_count": len(sources),
    }
    primary_source_metadata_gate = {
        "status": "PASS" if len(ready_sources) >= 3 and not missing_roles else "BLOCKED",
        "required_condition": "The manifest must include primary source candidates with URL/DOI, roles, and claim boundaries for required estimator-support classes.",
        "ready_source_count": len(ready_sources),
        "required_formula_roles": sorted(REQUIRED_FORMULA_ROLES),
        "observed_formula_roles": sorted(formula_roles),
        "missing_formula_roles": missing_roles,
    }
    local_formula_extraction_gate = {
        "status": "BLOCKED",
        "required_condition": "At least one source must have extracted formula text or a local full-text path before calibration can be accepted.",
        "metadata_only_source_count": len(metadata_only_sources),
        "local_full_text_source_count": len(local_full_text_sources),
        "claim_boundary": "Metadata packaging is enough for source-review queueing, not formula acceptance.",
    }
    calibration_acceptance_gate = {
        "status": "BLOCKED",
        "required_condition": "The observed calibration factor must be derived from, or benchmarked against, packaged source formulas before use.",
        "candidate_calibration_factor": manifest.get("estimator_under_review", {}).get(
            "candidate_calibration_factor_from_wave28"
        ),
        "accepted_calibration_factor": None,
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until source formulas are extracted and the current estimator is mapped or rejected.",
        "next_controller": "extract_source_formula_boundary_for_second_moment_estimator",
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Source manifest packaging cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 30 organizes primary-source candidates for formula review only.",
    }

    if wave29_chain_gate["status"] != "PASS":
        blocker_label = "structure_factor_source_manifest_chain_missing"
    elif primary_source_metadata_gate["status"] == "PASS":
        blocker_label = "structure_factor_source_manifest_packaged_formula_extraction_open"
    else:
        blocker_label = "structure_factor_source_manifest_metadata_incomplete"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 30 structure-factor estimator source-manifest gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Source_Manifest_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_manifest_packaging_only",
        "inputs": [
            artifact_record(WAVE29_ARTIFACT_PATH, "Wave 29 source-support gap controller"),
            {
                "path": relpath(SOURCE_MANIFEST_PATH),
                "role": "Wave 30 primary source candidate manifest",
                "exists": SOURCE_MANIFEST_PATH.exists(),
                "sha256": hash_file(SOURCE_MANIFEST_PATH) if SOURCE_MANIFEST_PATH.exists() else None,
            },
        ],
        "metrics": {
            "source_count": len(sources),
            "ready_source_count": len(ready_sources),
            "metadata_only_source_count": len(metadata_only_sources),
            "local_full_text_source_count": len(local_full_text_sources),
            "formula_roles": sorted(formula_roles),
            "missing_formula_roles": missing_roles,
        },
        "gates": {
            "wave29_chain_gate": wave29_chain_gate,
            "manifest_schema_gate": manifest_schema_gate,
            "primary_source_metadata_gate": primary_source_metadata_gate,
            "local_formula_extraction_gate": local_formula_extraction_gate,
            "calibration_acceptance_gate": calibration_acceptance_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "The manifest records candidate primary sources but does not extract formulas from them.",
            "The current RMS inverse-k estimator remains unmapped to a source-backed second-moment estimator.",
            "The observed calibration factor remains unaccepted.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 30 only packages source candidates and leaves formula extraction open.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_source_manifest_gate()
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
