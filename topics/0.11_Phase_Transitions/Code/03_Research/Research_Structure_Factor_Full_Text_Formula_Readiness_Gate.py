"""
Wave 37 full-text formula-extraction readiness gate.

Wave 36 extracted abstract-level policy boundaries but left full-text formula
extraction and UET normalization mapping blocked. This verifier records whether
the current source-access state is sufficient to accept formulas. The expected
answer is conservative: rendered/abstract text is useful boundary evidence, but
not enough to accept estimator formulas without local TeX/PDF math extraction.
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_full_text_formula_readiness_gate.json"
WAVE36_ARTIFACT_PATH = (
    ARTIFACT_DIR / "0_11_structure_factor_policy_formula_boundary_gate.json"
)
POLICY_FORMULA_BOUNDARY_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_policy_formula_boundary.json"
)
READINESS_MANIFEST_PATH = (
    TOPIC_DIR
    / "Data"
    / "03_Research"
    / "structure_factor_full_text_formula_extraction_readiness.json"
)

EXPECTED_SOURCE_IDS = {
    "blote_heringa_tsypin_1999_fixed_magnetization_ising",
    "deng_blote_2005_canonical_fss",
    "longo_2021_cahn_hilliard_structure_factor",
}
REQUIRED_RECORD_FIELDS = {
    "source_id",
    "arxiv_url",
    "extraction_status",
    "formula_extraction_gap",
    "usable_boundary_now",
    "accepted_for_formula_use_now",
}


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def record_ready(record: dict[str, Any]) -> bool:
    return all(record.get(field) not in (None, "", []) for field in REQUIRED_RECORD_FIELDS)


def run_full_text_formula_readiness_gate() -> dict[str, Any]:
    wave36 = load_json(WAVE36_ARTIFACT_PATH) if WAVE36_ARTIFACT_PATH.exists() else {}
    formula_boundary = (
        load_json(POLICY_FORMULA_BOUNDARY_PATH)
        if POLICY_FORMULA_BOUNDARY_PATH.exists()
        else {}
    )
    readiness = load_json(READINESS_MANIFEST_PATH) if READINESS_MANIFEST_PATH.exists() else {}
    boundary_extracts = formula_boundary.get("source_boundary_extracts", [])
    readiness_records = readiness.get("source_readiness_records", [])
    boundary_source_ids = {
        str(row.get("source_id")) for row in boundary_extracts if row.get("source_id")
    }
    readiness_source_ids = {
        str(row.get("source_id")) for row in readiness_records if row.get("source_id")
    }
    ready_records = [row for row in readiness_records if record_ready(row)]
    accepted_records = [
        row for row in readiness_records if bool(row.get("accepted_for_formula_use_now"))
    ]
    localized_math_sources = [
        row
        for row in readiness_records
        if "local" in str(row.get("extraction_status", "")).lower()
        and "not_localized" not in str(row.get("extraction_status", "")).lower()
    ]

    wave36_chain_gate = {
        "status": (
            "PASS"
            if wave36.get("blocker_label")
            == "policy_formula_boundaries_partial_full_text_extraction_open"
            else "BLOCKED"
        ),
        "required_condition": "Wave 37 must start from the Wave 36 partial formula-boundary blocker.",
        "wave36_status": wave36.get("status"),
        "wave36_blocker_label": wave36.get("blocker_label"),
    }
    formula_boundary_chain_gate = {
        "status": (
            "PASS"
            if EXPECTED_SOURCE_IDS.issubset(boundary_source_ids)
            and formula_boundary.get("mapping_decision", {}).get("decision")
            == "policy_formula_boundaries_partial_full_text_extraction_open"
            else "BLOCKED"
        ),
        "required_condition": "The Wave 36 formula-boundary manifest must remain present and cover the expected source IDs.",
        "boundary_source_ids": sorted(boundary_source_ids),
        "missing_expected_source_ids": sorted(EXPECTED_SOURCE_IDS - boundary_source_ids),
    }
    readiness_manifest_gate = {
        "status": (
            "PASS"
            if READINESS_MANIFEST_PATH.exists()
            and readiness.get("schema_version")
            and EXPECTED_SOURCE_IDS.issubset(readiness_source_ids)
            and len(ready_records) == len(readiness_records)
            else "BLOCKED"
        ),
        "required_condition": "A formula-extraction readiness manifest must cover every packaged source candidate and record extraction gaps.",
        "readiness_manifest_path": relpath(READINESS_MANIFEST_PATH),
        "readiness_manifest_sha256": hash_file(READINESS_MANIFEST_PATH)
        if READINESS_MANIFEST_PATH.exists()
        else None,
        "record_count": len(readiness_records),
        "ready_record_count": len(ready_records),
        "readiness_source_ids": sorted(readiness_source_ids),
        "missing_expected_source_ids": sorted(EXPECTED_SOURCE_IDS - readiness_source_ids),
    }
    rendered_boundary_gate = {
        "status": "WARN" if ready_records else "BLOCKED",
        "required_condition": "Rendered or abstract source access can support boundary wording only, not formula acceptance.",
        "extraction_statuses": sorted(
            {str(row.get("extraction_status")) for row in ready_records}
        ),
    }
    local_math_source_gate = {
        "status": "PASS" if localized_math_sources else "BLOCKED",
        "required_condition": "Local TeX/PDF math sources must be localized before reliable formula extraction and normalization mapping.",
        "localized_math_source_count": len(localized_math_sources),
    }
    accepted_formula_source_gate = {
        "status": "PASS" if accepted_records else "BLOCKED",
        "required_condition": "At least one source record must explicitly accept formula use before estimator replacement may continue.",
        "accepted_formula_source_count": len(accepted_records),
    }
    normalization_mapping_gate = {
        "status": "BLOCKED",
        "required_condition": "Accepted full-text formulas must be mapped to UET lattice normalization and finite-size admissibility before exponent gates rerun.",
        "missing_mapping": [
            "fixed-composition connected susceptibility policy",
            "finite-k/domain-size to critical-correlation-length policy",
            "lattice normalization and finite-size acceptance rule",
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until local math sources are extracted and accepted, or window/dynamics repair is selected.",
        "next_controller": "localize_tex_or_pdf_math_sources_or_choose_window_dynamics_repair",
        "next_options": [
            "localize TeX or PDF math sources for the packaged candidates",
            "extract exact formulas and map normalization",
            "explicitly reject estimator replacement and return to window/dynamics repair",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Source-access readiness cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 37 records source-access readiness only and accepts no estimator policy.",
    }

    if wave36_chain_gate["status"] != "PASS":
        blocker_label = "full_text_formula_readiness_chain_missing"
    elif accepted_formula_source_gate["status"] == "BLOCKED":
        blocker_label = "full_text_formula_extraction_requires_local_math_source"
    else:
        blocker_label = "full_text_formula_source_ready_for_normalization_mapping"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 37 full-text formula-extraction readiness gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Full_Text_Formula_Readiness_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "formula_extraction_readiness_only",
        "inputs": [
            artifact_record(WAVE36_ARTIFACT_PATH, "Wave 36 formula-boundary controller"),
            source_record(POLICY_FORMULA_BOUNDARY_PATH, "Wave 36 policy formula-boundary manifest"),
            source_record(READINESS_MANIFEST_PATH, "Wave 37 formula-extraction readiness manifest"),
        ],
        "metrics": {
            "readiness_record_count": len(readiness_records),
            "ready_record_count": len(ready_records),
            "localized_math_source_count": len(localized_math_sources),
            "accepted_formula_source_count": len(accepted_records),
            "readiness_source_ids": sorted(readiness_source_ids),
        },
        "gates": {
            "wave36_chain_gate": wave36_chain_gate,
            "formula_boundary_chain_gate": formula_boundary_chain_gate,
            "readiness_manifest_gate": readiness_manifest_gate,
            "rendered_boundary_gate": rendered_boundary_gate,
            "local_math_source_gate": local_math_source_gate,
            "accepted_formula_source_gate": accepted_formula_source_gate,
            "normalization_mapping_gate": normalization_mapping_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Rendered and abstract source access is boundary evidence only.",
            "No local TeX/PDF math extraction is packaged in this artifact.",
            "No conserved-order connected S(0) estimator is accepted.",
            "No finite-k or canonical replacement estimator is accepted.",
            "No exponent, universality, material, or RG claim may be upgraded from this readiness gate.",
        ],
        "claim_boundary": "Wave 37 narrows the full-text formula blocker to local math source localization. It accepts no estimator replacement and does not rerun scaling gates.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_full_text_formula_readiness_gate()
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
