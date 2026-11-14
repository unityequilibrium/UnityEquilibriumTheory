"""
Wave 36 estimator-policy formula-boundary gate.

Wave 35 packaged source candidates for conserved-order/fixed-composition and
finite-k/canonical estimator policy review. This verifier checks the next
controlled step: abstract-level policy/formula boundaries are extracted, while
full-text formula extraction, UET normalization mapping, and policy acceptance
remain blocked.
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_policy_formula_boundary_gate.json"
WAVE35_ARTIFACT_PATH = (
    ARTIFACT_DIR / "0_11_structure_factor_policy_source_candidate_gate.json"
)
POLICY_SOURCE_CANDIDATES_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_policy_source_candidates.json"
)
POLICY_FORMULA_BOUNDARY_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_policy_formula_boundary.json"
)

EXPECTED_SOURCE_IDS = {
    "blote_heringa_tsypin_1999_fixed_magnetization_ising",
    "deng_blote_2005_canonical_fss",
    "longo_2021_cahn_hilliard_structure_factor",
}
EXPECTED_POLICY_IDS = {
    "conserved_order_fixed_composition_susceptibility_policy",
    "finite_k_or_canonical_estimator_policy",
}
REQUIRED_BOUNDARY_FIELDS = {
    "boundary_id",
    "source_id",
    "source_url",
    "policy_ids",
    "extracted_boundary",
    "policy_implication",
    "boundary_extract_status",
    "accepted_for_estimator_policy_now",
    "claim_boundary",
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


def boundary_ready(boundary: dict[str, Any]) -> bool:
    return all(boundary.get(field) not in (None, "", []) for field in REQUIRED_BOUNDARY_FIELDS)


def run_policy_formula_boundary_gate() -> dict[str, Any]:
    wave35 = load_json(WAVE35_ARTIFACT_PATH) if WAVE35_ARTIFACT_PATH.exists() else {}
    source_candidates = (
        load_json(POLICY_SOURCE_CANDIDATES_PATH)
        if POLICY_SOURCE_CANDIDATES_PATH.exists()
        else {}
    )
    formula_boundary = (
        load_json(POLICY_FORMULA_BOUNDARY_PATH)
        if POLICY_FORMULA_BOUNDARY_PATH.exists()
        else {}
    )
    candidates = source_candidates.get("source_candidates", [])
    boundaries = formula_boundary.get("source_boundary_extracts", [])
    candidate_source_ids = {str(row.get("source_id")) for row in candidates if row.get("source_id")}
    boundary_source_ids = {str(row.get("source_id")) for row in boundaries if row.get("source_id")}
    ready_boundaries = [row for row in boundaries if boundary_ready(row)]
    accepted_boundaries = [
        row for row in boundaries if bool(row.get("accepted_for_estimator_policy_now"))
    ]
    boundary_policy_ids = {
        str(policy_id)
        for row in boundaries
        for policy_id in row.get("policy_ids", [])
    }

    wave35_chain_gate = {
        "status": (
            "PASS"
            if wave35.get("blocker_label")
            == "estimator_policy_source_candidates_packaged_formula_extraction_open"
            else "BLOCKED"
        ),
        "required_condition": "Wave 36 must start from the Wave 35 source-candidate formula-extraction blocker.",
        "wave35_status": wave35.get("status"),
        "wave35_blocker_label": wave35.get("blocker_label"),
    }
    source_candidate_chain_gate = {
        "status": (
            "PASS"
            if EXPECTED_SOURCE_IDS.issubset(candidate_source_ids)
            and source_candidates.get("policy_source_decision", {}).get("decision")
            == "source_candidates_packaged_formula_extraction_open"
            else "BLOCKED"
        ),
        "required_condition": "The Wave 35 source-candidate manifest must remain present and cover the expected source IDs.",
        "candidate_source_ids": sorted(candidate_source_ids),
        "missing_expected_source_ids": sorted(EXPECTED_SOURCE_IDS - candidate_source_ids),
    }
    formula_boundary_manifest_gate = {
        "status": (
            "PASS"
            if POLICY_FORMULA_BOUNDARY_PATH.exists()
            and formula_boundary.get("schema_version")
            and EXPECTED_SOURCE_IDS.issubset(boundary_source_ids)
            and EXPECTED_POLICY_IDS.issubset(boundary_policy_ids)
            and len(ready_boundaries) == len(boundaries)
            else "BLOCKED"
        ),
        "required_condition": "A policy formula-boundary manifest must record boundary extracts for all packaged source candidates and relevant policy IDs.",
        "formula_boundary_path": relpath(POLICY_FORMULA_BOUNDARY_PATH),
        "formula_boundary_sha256": hash_file(POLICY_FORMULA_BOUNDARY_PATH)
        if POLICY_FORMULA_BOUNDARY_PATH.exists()
        else None,
        "boundary_count": len(boundaries),
        "ready_boundary_count": len(ready_boundaries),
        "boundary_source_ids": sorted(boundary_source_ids),
        "missing_expected_source_ids": sorted(EXPECTED_SOURCE_IDS - boundary_source_ids),
        "boundary_policy_ids": sorted(boundary_policy_ids),
        "missing_expected_policy_ids": sorted(EXPECTED_POLICY_IDS - boundary_policy_ids),
    }
    abstract_boundary_gate = {
        "status": "PASS" if ready_boundaries else "BLOCKED",
        "required_condition": "Abstract-level source boundaries must be explicit enough to prevent silent estimator promotion.",
        "boundary_extract_statuses": sorted(
            {str(row.get("boundary_extract_status")) for row in ready_boundaries}
        ),
        "claim_boundary": "This gate accepts boundary extraction only, not estimator formulas.",
    }
    accepted_estimator_formula_gate = {
        "status": "PASS" if accepted_boundaries else "BLOCKED",
        "required_condition": "At least one boundary must explicitly accept an estimator policy before replacement or exponent gates rerun.",
        "accepted_boundary_count": len(accepted_boundaries),
    }
    normalization_mapping_gate = {
        "status": "BLOCKED",
        "required_condition": "Accepted formula boundaries must be mapped to the current UET lattice normalization before use.",
        "missing_mapping": [
            "conserved-order connected S(0) policy",
            "finite-k or canonical estimator relation",
            "UET lattice normalization and finite-size admissibility",
        ],
    }
    spatial_variance_boundary_gate = {
        "status": "PASS",
        "required_condition": "Spatial variance remains diagnostic-only because no source boundary accepts equivalence to source-family S(0).",
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until full-text policy formulas are extracted and accepted, or window/dynamics repair is selected.",
        "next_controller": "extract_full_text_policy_formulas_or_choose_window_dynamics_repair",
        "next_options": [
            "obtain/extract full-text formula details for fixed-magnetization/canonical susceptibility",
            "obtain/extract full-text finite-k Cahn-Hilliard structure-factor relations and admissibility limits",
            "explicitly reject estimator replacement and return to window/dynamics repair",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Partial source-boundary extraction cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 36 narrows the formula gap but accepts no estimator policy.",
    }

    if wave35_chain_gate["status"] != "PASS":
        blocker_label = "policy_formula_boundary_gate_chain_missing"
    elif accepted_estimator_formula_gate["status"] == "BLOCKED":
        blocker_label = "policy_formula_boundaries_partial_full_text_extraction_open"
    else:
        blocker_label = "policy_formula_boundary_acceptance_ready_for_normalization_mapping"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 36 estimator policy formula-boundary gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Policy_Formula_Boundary_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "estimator_policy_formula_boundary_partial_only",
        "inputs": [
            artifact_record(WAVE35_ARTIFACT_PATH, "Wave 35 source-candidate controller"),
            source_record(POLICY_SOURCE_CANDIDATES_PATH, "Wave 35 estimator policy source-candidate manifest"),
            source_record(POLICY_FORMULA_BOUNDARY_PATH, "Wave 36 estimator policy formula-boundary manifest"),
        ],
        "metrics": {
            "candidate_source_count": len(candidate_source_ids),
            "boundary_count": len(boundaries),
            "ready_boundary_count": len(ready_boundaries),
            "accepted_boundary_count": len(accepted_boundaries),
            "boundary_source_ids": sorted(boundary_source_ids),
            "boundary_policy_ids": sorted(boundary_policy_ids),
        },
        "gates": {
            "wave35_chain_gate": wave35_chain_gate,
            "source_candidate_chain_gate": source_candidate_chain_gate,
            "formula_boundary_manifest_gate": formula_boundary_manifest_gate,
            "abstract_boundary_gate": abstract_boundary_gate,
            "accepted_estimator_formula_gate": accepted_estimator_formula_gate,
            "normalization_mapping_gate": normalization_mapping_gate,
            "spatial_variance_boundary_gate": spatial_variance_boundary_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Boundary extraction uses source pages and metadata-level review; local full-text extraction remains open.",
            "No conserved-order connected S(0) estimator is accepted.",
            "No finite-k or canonical replacement estimator is accepted.",
            "No UET lattice normalization mapping is accepted.",
            "No exponent, universality, material, or RG claim may be upgraded from this boundary gate.",
        ],
        "claim_boundary": "Wave 36 extracts conservative source boundaries only. It accepts no estimator replacement and does not rerun scaling gates.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_policy_formula_boundary_gate()
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
