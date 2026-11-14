"""
Wave 35 estimator-policy source-candidate gate.

Wave 34 made the required estimator policies explicit but kept both accepted
paths blocked because policy-specific source support was missing. This verifier
checks the next source-packaging step: candidate sources are now listed for
fixed-composition/canonical and finite-k structure-factor review, but none is
accepted until a formula-boundary extraction maps it to the current UET
normalization and claim boundary.
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_policy_source_candidate_gate.json"
WAVE34_ARTIFACT_PATH = (
    ARTIFACT_DIR / "0_11_structure_factor_estimator_policy_source_gate.json"
)
POLICY_REQUIREMENTS_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_policy_requirements.json"
)
POLICY_SOURCE_CANDIDATES_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_policy_source_candidates.json"
)

EXPECTED_POLICY_IDS = {
    "conserved_order_fixed_composition_susceptibility_policy",
    "finite_k_or_canonical_estimator_policy",
    "spatial_variance_proxy_policy",
}
REQUIRED_CANDIDATE_FIELDS = {
    "source_id",
    "title",
    "url",
    "doi",
    "formula_role",
    "policy_ids",
    "local_status",
    "accepted_for_policy_now",
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


def candidate_ready(candidate: dict[str, Any]) -> bool:
    return all(candidate.get(field) not in (None, "", []) for field in REQUIRED_CANDIDATE_FIELDS)


def policy_source_counts(candidates: list[dict[str, Any]]) -> dict[str, int]:
    counts = {policy_id: 0 for policy_id in EXPECTED_POLICY_IDS}
    for candidate in candidates:
        for policy_id in candidate.get("policy_ids", []):
            if policy_id in counts:
                counts[policy_id] += 1
    return counts


def run_policy_source_candidate_gate() -> dict[str, Any]:
    wave34 = load_json(WAVE34_ARTIFACT_PATH) if WAVE34_ARTIFACT_PATH.exists() else {}
    policy_requirements = (
        load_json(POLICY_REQUIREMENTS_PATH) if POLICY_REQUIREMENTS_PATH.exists() else {}
    )
    source_candidates = (
        load_json(POLICY_SOURCE_CANDIDATES_PATH)
        if POLICY_SOURCE_CANDIDATES_PATH.exists()
        else {}
    )
    candidates = source_candidates.get("source_candidates", [])
    mappings = source_candidates.get("policy_mapping", [])
    mapping_by_policy = {str(row.get("policy_id")): row for row in mappings}
    candidate_ids = {str(row.get("source_id")) for row in candidates if row.get("source_id")}
    ready_candidates = [row for row in candidates if candidate_ready(row)]
    missing_policy_mappings = sorted(EXPECTED_POLICY_IDS - set(mapping_by_policy))
    counts = policy_source_counts(candidates)

    accepted_candidates = [
        row for row in candidates if bool(row.get("accepted_for_policy_now"))
    ]
    accepted_mappings = [row for row in mappings if bool(row.get("accepted_now"))]

    wave34_chain_gate = {
        "status": (
            "PASS"
            if wave34.get("blocker_label")
            == "estimator_policy_source_support_missing_for_conserved_susceptibility_or_finite_k_path"
            else "BLOCKED"
        ),
        "required_condition": "Wave 35 must start from the Wave 34 estimator-policy source-support blocker.",
        "wave34_status": wave34.get("status"),
        "wave34_blocker_label": wave34.get("blocker_label"),
    }
    policy_requirements_chain_gate = {
        "status": (
            "PASS"
            if policy_requirements.get("policy_candidates")
            and len(policy_requirements.get("policy_candidates", [])) >= len(EXPECTED_POLICY_IDS)
            else "BLOCKED"
        ),
        "required_condition": "The Wave 34 policy requirements manifest must remain present as the policy contract.",
        "policy_requirement_manifest_path": relpath(POLICY_REQUIREMENTS_PATH),
        "policy_requirement_manifest_exists": POLICY_REQUIREMENTS_PATH.exists(),
    }
    source_candidate_manifest_gate = {
        "status": (
            "PASS"
            if POLICY_SOURCE_CANDIDATES_PATH.exists()
            and source_candidates.get("schema_version")
            and len(candidates) >= 3
            and len(ready_candidates) == len(candidates)
            and not missing_policy_mappings
            else "BLOCKED"
        ),
        "required_condition": "A source-candidate manifest must define candidate rows and policy mappings for all Wave 34 policy IDs.",
        "source_candidate_manifest_path": relpath(POLICY_SOURCE_CANDIDATES_PATH),
        "source_candidate_manifest_sha256": hash_file(POLICY_SOURCE_CANDIDATES_PATH)
        if POLICY_SOURCE_CANDIDATES_PATH.exists()
        else None,
        "candidate_count": len(candidates),
        "ready_candidate_count": len(ready_candidates),
        "candidate_source_ids": sorted(candidate_ids),
        "missing_policy_mappings": missing_policy_mappings,
    }
    conserved_policy_candidate_gate = {
        "status": (
            "WARN"
            if counts["conserved_order_fixed_composition_susceptibility_policy"] > 0
            else "BLOCKED"
        ),
        "required_condition": "At least one fixed-composition/canonical source candidate must be packaged before formula extraction can start.",
        "candidate_count": counts["conserved_order_fixed_composition_susceptibility_policy"],
        "policy_mapping": mapping_by_policy.get(
            "conserved_order_fixed_composition_susceptibility_policy", {}
        ),
        "claim_boundary": "Candidate source presence is not acceptance of conserved-order S(0).",
    }
    finite_k_policy_candidate_gate = {
        "status": (
            "WARN" if counts["finite_k_or_canonical_estimator_policy"] > 0 else "BLOCKED"
        ),
        "required_condition": "At least one finite-k/canonical source candidate must be packaged before formula extraction can start.",
        "candidate_count": counts["finite_k_or_canonical_estimator_policy"],
        "policy_mapping": mapping_by_policy.get("finite_k_or_canonical_estimator_policy", {}),
        "claim_boundary": "Candidate source presence is not acceptance of a finite-k replacement estimator.",
    }
    spatial_variance_boundary_gate = {
        "status": (
            "PASS"
            if not mapping_by_policy.get("spatial_variance_proxy_policy", {}).get(
                "accepted_now"
            )
            else "BLOCKED"
        ),
        "required_condition": "Spatial variance must remain diagnostic-only unless source-equivalence is explicitly accepted.",
        "policy_mapping": mapping_by_policy.get("spatial_variance_proxy_policy", {}),
    }
    formula_extraction_gate = {
        "status": "BLOCKED",
        "required_condition": "Candidate sources must be formula-extracted and mapped to current UET normalization before any policy can be accepted.",
        "not_extracted_policy_ids": sorted(
            row.get("policy_id")
            for row in mappings
            if str(row.get("formula_boundary_status")) == "not_extracted"
        ),
    }
    accepted_policy_gate = {
        "status": "PASS" if accepted_mappings or accepted_candidates else "BLOCKED",
        "required_condition": "At least one source-backed policy path must be explicitly accepted before estimator replacement or exponent gates rerun.",
        "accepted_candidate_count": len(accepted_candidates),
        "accepted_mapping_count": len(accepted_mappings),
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until policy formula boundaries are extracted and accepted, or window/dynamics repair is selected.",
        "next_controller": "extract_policy_formula_boundaries_or_choose_window_dynamics_repair",
        "next_options": [
            "extract fixed-composition/canonical susceptibility policy formulas",
            "extract finite-k/domain-scale estimator formulas and admissibility limits",
            "explicitly reject policy candidates and return to window/dynamics repair",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Source-candidate packaging cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 35 packages candidate sources only; it accepts no estimator policy.",
    }

    if wave34_chain_gate["status"] != "PASS":
        blocker_label = "policy_source_candidate_gate_chain_missing"
    elif accepted_policy_gate["status"] == "BLOCKED":
        blocker_label = "estimator_policy_source_candidates_packaged_formula_extraction_open"
    else:
        blocker_label = "estimator_policy_source_candidate_acceptance_ready_for_rerun"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 35 estimator policy source-candidate gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Policy_Source_Candidate_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "estimator_policy_source_candidate_packaging_only",
        "inputs": [
            artifact_record(WAVE34_ARTIFACT_PATH, "Wave 34 estimator-policy source controller"),
            source_record(POLICY_REQUIREMENTS_PATH, "Wave 34 estimator policy requirements manifest"),
            source_record(POLICY_SOURCE_CANDIDATES_PATH, "Wave 35 estimator policy source-candidate manifest"),
        ],
        "metrics": {
            "candidate_count": len(candidates),
            "ready_candidate_count": len(ready_candidates),
            "policy_source_counts": counts,
            "accepted_candidate_count": len(accepted_candidates),
            "accepted_policy_mapping_count": len(accepted_mappings),
            "candidate_source_ids": sorted(candidate_ids),
        },
        "gates": {
            "wave34_chain_gate": wave34_chain_gate,
            "policy_requirements_chain_gate": policy_requirements_chain_gate,
            "source_candidate_manifest_gate": source_candidate_manifest_gate,
            "conserved_policy_candidate_gate": conserved_policy_candidate_gate,
            "finite_k_policy_candidate_gate": finite_k_policy_candidate_gate,
            "spatial_variance_boundary_gate": spatial_variance_boundary_gate,
            "formula_extraction_gate": formula_extraction_gate,
            "accepted_policy_gate": accepted_policy_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Source candidates are metadata-level packaged; local full text and formula extraction remain open.",
            "Canonical/fixed-magnetization sources do not automatically define a UET conserved-order S(0) policy.",
            "Cahn-Hilliard structure-factor sources do not automatically accept the current second-moment or finite-k estimator.",
            "Spatial variance remains diagnostic-only.",
            "No exponent, universality, material, or RG claim may be upgraded from this source-candidate gate.",
        ],
        "claim_boundary": "Wave 35 narrows the policy-source gap to formula extraction and acceptance. It accepts no estimator replacement and does not rerun scaling gates.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_policy_source_candidate_gate()
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
