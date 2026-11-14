"""
Wave 44 source-archive policy gate.

Wave 43 preserved TeX formula fragments but the temporary arXiv source cache was
missing on rerun. This verifier turns that into an explicit provenance policy:
formula fragments may remain repo-local review evidence, while raw source
archives require either a repo archival decision or a reacquisition step with
recorded URL/hash expectations before fresh extraction is reproducible.
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
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
EXTERNAL_DIR = ROOT / "docs" / "data" / "external" / "condensed_matter" / "phase_transitions" / "structure_factor_sources"

ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_source_archive_policy_gate.json"
POLICY_MANIFEST_PATH = DATA_DIR / "structure_factor_source_archive_policy.json"
WAVE43_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_tex_formula_fragment_gate.json"
FORMULA_FRAGMENT_MANIFEST_PATH = DATA_DIR / "structure_factor_tex_formula_fragments.json"
LOCALIZATION_MANIFEST_PATH = DATA_DIR / "structure_factor_source_archive_localization_manifest.json"


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_policy_manifest(localization: dict[str, Any], fragments: dict[str, Any]) -> dict[str, Any]:
    source_archives = []
    for row in localization.get("source_archives", []):
        source_id = row["source_id"]
        repo_archive_candidate_path = EXTERNAL_DIR / source_id / Path(str(row.get("local_cache_path"))).name
        repo_archive_exists = repo_archive_candidate_path.exists()
        source_archives.append(
            {
                "source_id": source_id,
                "source_url": row.get("source_url"),
                "archive_kind": row.get("archive_kind"),
                "expected_sha256": row.get("expected_sha256"),
                "expected_bytes": row.get("expected_bytes"),
                "expected_tex_members": row.get("expected_tex_members", []),
                "temporary_cache_path": row.get("local_cache_path"),
                "repo_archive_candidate_path": relpath(repo_archive_candidate_path),
                "repo_archival_status": "repo_archive_present" if repo_archive_exists else "not_committed",
                "reacquisition_required": not repo_archive_exists,
                "policy_role": "formula_refresh_source_only",
            }
        )

    restored_count = sum(1 for row in source_archives if not row["reacquisition_required"])
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "0_11_structure_factor_source_archive_policy",
        "topic": "0.11_Phase_Transitions",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "policy_decision": {
            "decision": (
                "repo_archives_restored_estimator_policy_open"
                if restored_count == len(source_archives)
                else "formula_fragments_preserved_raw_archives_not_repo_archived"
            ),
            "repo_archive_root_candidate": relpath(EXTERNAL_DIR),
            "raw_archive_policy": (
                "repo_archives_available_for_fresh_formula_extraction_estimator_policy_still_blocked"
                if restored_count == len(source_archives)
                else "do_not_claim_reproducible_fresh_formula_extraction_until_raw_archives_are_restored_or_repo_archived"
            ),
            "formula_fragment_manifest": relpath(FORMULA_FRAGMENT_MANIFEST_PATH),
            "formula_fragment_manifest_sha256": hash_file(FORMULA_FRAGMENT_MANIFEST_PATH)
            if FORMULA_FRAGMENT_MANIFEST_PATH.exists()
            else None,
            "formula_fragment_count": sum(
                int(row.get("extracted_fragment_count", 0))
                for row in fragments.get("source_formula_fragments", [])
            ),
        },
        "source_archives": source_archives,
        "claim_boundary": (
            "This manifest records source-archive policy only. It preserves acquisition URLs, "
            "expected hashes, candidate repo paths, and formula-fragment linkage. It does not "
            "accept an estimator policy, UET normalization mapping, exponent result, RG closure, "
            "material validation, or universality claim."
        ),
    }
    POLICY_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


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


def run_source_archive_policy_gate() -> dict[str, Any]:
    wave43 = load_json(WAVE43_ARTIFACT_PATH) if WAVE43_ARTIFACT_PATH.exists() else {}
    localization = load_json(LOCALIZATION_MANIFEST_PATH)
    fragments = load_json(FORMULA_FRAGMENT_MANIFEST_PATH)
    policy_manifest = write_policy_manifest(localization, fragments)

    source_archives = policy_manifest.get("source_archives", [])
    repo_archive_paths = [ROOT / row["repo_archive_candidate_path"] for row in source_archives]
    repo_archived = [path for path in repo_archive_paths if path.exists()]
    temp_paths = [Path(str(row["temporary_cache_path"])) for row in source_archives]
    temp_present = [path for path in temp_paths if path.exists()]
    fragment_count = policy_manifest["policy_decision"]["formula_fragment_count"]

    wave43_chain_gate = {
        "status": (
            "PASS"
            if wave43.get("blocker_label")
            in {
                "tex_formula_fragments_extracted_source_cache_missing",
                "tex_formula_fragments_extracted_estimator_policy_open",
            }
            else "BLOCKED"
        ),
        "required_condition": "Wave 44 must start from the Wave 43 formula-fragment/source-cache blocker.",
        "wave43_status": wave43.get("status"),
        "wave43_blocker_label": wave43.get("blocker_label"),
    }
    formula_fragment_preservation_gate = {
        "status": "PASS" if FORMULA_FRAGMENT_MANIFEST_PATH.exists() and fragment_count >= 3 else "BLOCKED",
        "required_condition": "Formula fragments must remain repo-local review evidence even if raw source archives are not currently present.",
        "formula_fragment_count": fragment_count,
        "manifest_path": relpath(FORMULA_FRAGMENT_MANIFEST_PATH),
        "manifest_sha256": hash_file(FORMULA_FRAGMENT_MANIFEST_PATH)
        if FORMULA_FRAGMENT_MANIFEST_PATH.exists()
        else None,
    }
    source_archive_policy_manifest_gate = {
        "status": "PASS" if POLICY_MANIFEST_PATH.exists() and len(source_archives) == 3 else "BLOCKED",
        "required_condition": "A source archive policy manifest must record URLs, expected hashes, candidate repo paths, and claim boundary.",
        "manifest_path": relpath(POLICY_MANIFEST_PATH),
        "manifest_sha256": hash_file(POLICY_MANIFEST_PATH) if POLICY_MANIFEST_PATH.exists() else None,
        "source_archive_count": len(source_archives),
    }
    repo_archive_availability_gate = {
        "status": "PASS" if len(repo_archived) == len(source_archives) else "BLOCKED",
        "required_condition": "Raw source archives must be present in the declared repo archive paths before fresh formula extraction is repo-reproducible.",
        "repo_archived_count": len(repo_archived),
        "expected_count": len(source_archives),
        "missing_repo_archive_paths": [
            row["repo_archive_candidate_path"]
            for row, path in zip(source_archives, repo_archive_paths)
            if not path.exists()
        ],
    }
    temporary_cache_availability_gate = {
        "status": "PASS" if len(temp_present) == len(source_archives) else "BLOCKED",
        "required_condition": "Temporary cache availability is not a stable repo claim, but fresh extraction can use it when present.",
        "temporary_cache_present_count": len(temp_present),
        "expected_count": len(source_archives),
        "missing_temporary_cache_paths": [
            str(path).replace("\\", "/") for path in temp_paths if not path.exists()
        ],
    }
    estimator_policy_gate = {
        "status": "BLOCKED",
        "required_condition": "Source archival policy does not accept an estimator policy or UET normalization mapping.",
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until source archive availability is restored and estimator policy mapping passes.",
        "next_controller": "restore_or_archive_sources_then_map_estimator_policy",
        "next_options": [
            "reacquire the three arXiv e-print archives and verify expected hashes",
            "store allowed source records or raw archives under the declared repo archive root if policy permits",
            "map preserved TeX fragments into an accepted finite-k or conserved-susceptibility estimator policy",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Source archival policy cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 44 records source archival policy only; fresh source availability and estimator policy remain blocked.",
    }

    blocker_label = (
        "source_archive_policy_recorded_repo_archives_missing"
        if repo_archive_availability_gate["status"] == "BLOCKED"
        else "source_archive_policy_recorded_ready_for_fresh_extraction"
    )

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 44 source-archive policy gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Source_Archive_Policy_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_archive_policy_only",
        "inputs": [
            artifact_record(WAVE43_ARTIFACT_PATH, "Wave 43 formula-fragment/source-cache controller"),
            source_record(FORMULA_FRAGMENT_MANIFEST_PATH, "Wave 43 formula-fragment manifest"),
            source_record(LOCALIZATION_MANIFEST_PATH, "Wave 38 source localization manifest"),
            source_record(POLICY_MANIFEST_PATH, "Wave 44 source archive policy manifest"),
        ],
        "metrics": {
            "source_archive_count": len(source_archives),
            "formula_fragment_count": fragment_count,
            "repo_archived_count": len(repo_archived),
            "temporary_cache_present_count": len(temp_present),
        },
        "gates": {
            "wave43_chain_gate": wave43_chain_gate,
            "formula_fragment_preservation_gate": formula_fragment_preservation_gate,
            "source_archive_policy_manifest_gate": source_archive_policy_manifest_gate,
            "repo_archive_availability_gate": repo_archive_availability_gate,
            "temporary_cache_availability_gate": temporary_cache_availability_gate,
            "estimator_policy_gate": estimator_policy_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Formula fragments are preserved but raw source archives are not currently repo-archived.",
            "The current temporary cache is not a stable reproducibility source.",
            "No estimator policy, UET normalization mapping, exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "claim_boundary": "Wave 44 records source-archive policy and keeps source availability plus estimator policy blocked.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_source_archive_policy_gate()
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
