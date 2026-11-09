"""
Wave 38 arXiv source-archive localization gate.

Wave 37 established that rendered/abstract source access is insufficient for
accepted formula extraction. This verifier checks whether arXiv source archives
have been localized in a temporary cache and whether the main TeX files are
identifiable. It still blocks estimator/formula acceptance until TeX formulas
are extracted and mapped to UET normalization.
"""

from __future__ import annotations

import json
import platform
import sys
import tarfile
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_source_archive_localization_gate.json"
WAVE37_ARTIFACT_PATH = (
    ARTIFACT_DIR / "0_11_structure_factor_full_text_formula_readiness_gate.json"
)
READINESS_MANIFEST_PATH = (
    TOPIC_DIR
    / "Data"
    / "03_Research"
    / "structure_factor_full_text_formula_extraction_readiness.json"
)
LOCALIZATION_MANIFEST_PATH = (
    TOPIC_DIR
    / "Data"
    / "03_Research"
    / "structure_factor_source_archive_localization_manifest.json"
)

EXPECTED_SOURCE_IDS = {
    "blote_heringa_tsypin_1999_fixed_magnetization_ising",
    "deng_blote_2005_canonical_fss",
    "longo_2021_cahn_hilliard_structure_factor",
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


def archive_observation(record: dict[str, Any]) -> dict[str, Any]:
    path = Path(str(record.get("local_cache_path", "")))
    exists = path.exists()
    observed_sha = hash_file(path) if exists else None
    observed_bytes = path.stat().st_size if exists else None
    is_tar = tarfile.is_tarfile(path) if exists else False
    tex_members: list[dict[str, Any]] = []
    if is_tar:
        with tarfile.open(path) as archive:
            for member in archive.getmembers():
                if member.name.lower().endswith((".tex", ".ltx")):
                    tex_members.append({"name": member.name, "size": int(member.size)})
    expected_tex = {
        (row.get("name"), int(row.get("size", -1)))
        for row in record.get("expected_tex_members", [])
    }
    observed_tex = {(row["name"], int(row["size"])) for row in tex_members}
    return {
        "source_id": record.get("source_id"),
        "local_cache_path": str(path).replace("\\", "/"),
        "exists": exists,
        "expected_bytes": record.get("expected_bytes"),
        "observed_bytes": observed_bytes,
        "expected_sha256": record.get("expected_sha256"),
        "observed_sha256": observed_sha,
        "sha256_match": observed_sha == record.get("expected_sha256"),
        "bytes_match": observed_bytes == record.get("expected_bytes"),
        "archive_kind": record.get("archive_kind"),
        "is_tar": is_tar,
        "tex_members": tex_members,
        "expected_tex_members_present": expected_tex.issubset(observed_tex),
        "claim_boundary": "Archive localization and TeX member discovery do not accept formulas.",
    }


def run_source_archive_localization_gate() -> dict[str, Any]:
    wave37 = load_json(WAVE37_ARTIFACT_PATH) if WAVE37_ARTIFACT_PATH.exists() else {}
    readiness = load_json(READINESS_MANIFEST_PATH) if READINESS_MANIFEST_PATH.exists() else {}
    localization = (
        load_json(LOCALIZATION_MANIFEST_PATH)
        if LOCALIZATION_MANIFEST_PATH.exists()
        else {}
    )
    source_archives = localization.get("source_archives", [])
    observations = [archive_observation(record) for record in source_archives]
    source_ids = {str(row.get("source_id")) for row in source_archives if row.get("source_id")}
    observed_source_ids = {
        str(row.get("source_id")) for row in observations if row.get("source_id")
    }
    localized_count = sum(1 for row in observations if row["exists"] and row["sha256_match"])
    tex_ready_count = sum(
        1 for row in observations if row["is_tar"] and row["expected_tex_members_present"]
    )

    wave37_chain_gate = {
        "status": (
            "PASS"
            if wave37.get("blocker_label")
            == "full_text_formula_extraction_requires_local_math_source"
            else "BLOCKED"
        ),
        "required_condition": "Wave 38 must start from the Wave 37 local math source blocker.",
        "wave37_status": wave37.get("status"),
        "wave37_blocker_label": wave37.get("blocker_label"),
    }
    readiness_chain_gate = {
        "status": (
            "PASS"
            if readiness.get("readiness_decision", {}).get("decision")
            == "full_text_formula_extraction_requires_local_math_source"
            else "BLOCKED"
        ),
        "required_condition": "The Wave 37 readiness manifest must remain present and point to local math source localization.",
    }
    localization_manifest_gate = {
        "status": (
            "PASS"
            if LOCALIZATION_MANIFEST_PATH.exists()
            and localization.get("schema_version")
            and EXPECTED_SOURCE_IDS.issubset(source_ids)
            else "BLOCKED"
        ),
        "required_condition": "A source-archive localization manifest must cover all expected source IDs and record cache policy.",
        "localization_manifest_path": relpath(LOCALIZATION_MANIFEST_PATH),
        "localization_manifest_sha256": hash_file(LOCALIZATION_MANIFEST_PATH)
        if LOCALIZATION_MANIFEST_PATH.exists()
        else None,
        "source_ids": sorted(source_ids),
        "missing_expected_source_ids": sorted(EXPECTED_SOURCE_IDS - source_ids),
        "cache_policy": localization.get("local_cache_policy", {}),
    }
    temporary_local_archive_gate = {
        "status": "PASS" if localized_count == len(EXPECTED_SOURCE_IDS) else "BLOCKED",
        "required_condition": "All expected source archives must exist in the declared temporary cache and match recorded hashes.",
        "localized_count": localized_count,
        "expected_count": len(EXPECTED_SOURCE_IDS),
    }
    tex_member_identification_gate = {
        "status": "PASS" if tex_ready_count == len(EXPECTED_SOURCE_IDS) else "BLOCKED",
        "required_condition": "Each localized archive must expose at least the expected main TeX member.",
        "tex_ready_count": tex_ready_count,
        "expected_count": len(EXPECTED_SOURCE_IDS),
    }
    repo_archival_policy_gate = {
        "status": "WARN",
        "required_condition": "Raw arXiv sources are intentionally not committed in this wave; future formula extraction must either use the temporary cache or define a repo archival policy.",
        "cache_scope": localization.get("local_cache_policy", {}).get("cache_scope"),
        "repo_archival_status": localization.get("local_cache_policy", {}).get(
            "repo_archival_status"
        ),
    }
    formula_extraction_gate = {
        "status": "BLOCKED",
        "required_condition": "TeX formulas must be extracted, reviewed, and mapped before estimator policy acceptance.",
        "next_required_artifacts": [
            "formula fragment extraction manifest",
            "UET normalization mapping manifest",
            "finite-size admissibility rule",
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until formulas are extracted from localized source archives and accepted, or window/dynamics repair is selected.",
        "next_controller": "extract_tex_formula_fragments_or_choose_window_dynamics_repair",
        "next_options": [
            "extract exact TeX formula fragments from the identified members",
            "define a repository archival policy for raw source archives before formula extraction",
            "explicitly reject estimator replacement and return to window/dynamics repair",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Source archive localization cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 38 localizes archives and TeX members only; no formulas or estimator policies are accepted.",
    }

    if wave37_chain_gate["status"] != "PASS":
        blocker_label = "source_archive_localization_chain_missing"
    elif formula_extraction_gate["status"] == "BLOCKED":
        blocker_label = "localized_source_archives_present_tex_formula_extraction_open"
    else:
        blocker_label = "localized_source_archives_ready_for_formula_acceptance"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 38 arXiv source-archive localization gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Source_Archive_Localization_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "source_archive_localization_only",
        "inputs": [
            artifact_record(WAVE37_ARTIFACT_PATH, "Wave 37 formula-readiness controller"),
            source_record(READINESS_MANIFEST_PATH, "Wave 37 formula-readiness manifest"),
            source_record(LOCALIZATION_MANIFEST_PATH, "Wave 38 source-archive localization manifest"),
        ],
        "metrics": {
            "localized_archive_count": localized_count,
            "tex_ready_count": tex_ready_count,
            "observed_source_ids": sorted(observed_source_ids),
            "observations": observations,
        },
        "gates": {
            "wave37_chain_gate": wave37_chain_gate,
            "readiness_chain_gate": readiness_chain_gate,
            "localization_manifest_gate": localization_manifest_gate,
            "temporary_local_archive_gate": temporary_local_archive_gate,
            "tex_member_identification_gate": tex_member_identification_gate,
            "repo_archival_policy_gate": repo_archival_policy_gate,
            "formula_extraction_gate": formula_extraction_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Temporary source-cache paths are environment-local and not repository archives.",
            "Raw arXiv sources are not committed by this wave.",
            "Main TeX member discovery does not extract or accept formulas.",
            "No conserved-order S(0), finite-k estimator, calibration, exponent, universality, material, or RG claim may be upgraded.",
        ],
        "claim_boundary": "Wave 38 narrows the blocker to TeX formula-fragment extraction or repo archival policy. It accepts no estimator replacement and does not rerun scaling gates.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_source_archive_localization_gate()
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
