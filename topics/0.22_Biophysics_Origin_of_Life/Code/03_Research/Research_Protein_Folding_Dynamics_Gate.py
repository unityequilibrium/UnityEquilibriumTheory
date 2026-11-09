"""Wave-0 preflight gate for the protein-folding dynamics lane.

This script checks the source and runtime contract only. It does not download
external data, run molecular dynamics, create trajectories, or generate a
protein-folding result. A BLOCKED gate is a valid preflight outcome and keeps
the umbrella topic at Draft/Tier B/WARN.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOPIC_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = TOPIC_ROOT.parents[2]
ARTIFACT_PATH = TOPIC_ROOT / "Result" / "artifacts" / "0_22_protein_folding_dynamics_gate.json"
SPEC_PATH = TOPIC_ROOT / "DYNAMICS_RESEARCH_SPEC.md"
DATA_MANIFEST_PATH = TOPIC_ROOT / "DYNAMICS_DATA_MANIFEST.json"
RUNTIME_MANIFEST_PATH = TOPIC_ROOT / "DYNAMICS_RUNTIME_MANIFEST.json"


def relative_repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def package_probe(import_name: str) -> dict[str, Any]:
    try:
        found = importlib.util.find_spec(import_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        found = False
    return {"import_name": import_name, "available": found}


def build_gate() -> dict[str, Any]:
    data_manifest = load_json(DATA_MANIFEST_PATH)
    runtime_manifest = load_json(RUNTIME_MANIFEST_PATH)

    required_files = [SPEC_PATH, DATA_MANIFEST_PATH, RUNTIME_MANIFEST_PATH]
    file_checks = {
        relative_repo_path(path): {
            "exists": path.exists(),
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        for path in required_files
    }

    source_records = data_manifest.get("source_records", [])
    source_lock_count = sum(
        1
        for record in source_records
        if record.get("local_path") and record.get("raw_sha256")
    )
    cohort = data_manifest.get("cohort_contract", {})
    cohort_entries = cohort.get("entries", [])
    cohort_ready = (
        cohort.get("selection_status") == "source_locked"
        and len(cohort_entries) >= cohort.get("target_total", 12)
    )

    package_checks = []
    for package in runtime_manifest.get("required_packages", []):
        probe = package_probe(package["import_name"])
        package_checks.append(
            {
                "distribution": package["distribution"],
                "import_name": package["import_name"],
                "minimum_version": package.get("minimum_version"),
                **probe,
            }
        )
    runtime_packages_ready = all(item["available"] for item in package_checks)
    force_field = runtime_manifest.get("force_field_contract", {})
    force_field_ready = (
        force_field.get("asset_status") == "present_and_hashed"
        and bool(force_field.get("asset_local_paths"))
    )
    smoke_ready = all(
        item.get("status") == "pass"
        for item in runtime_manifest.get("smoke_tests", [])
        if item.get("required")
    )

    checks = {
        "contract_files_present": all(item["exists"] for item in file_checks.values()),
        "source_records_declared": len(source_records) >= 5,
        "source_locked_records_present": source_lock_count >= 1,
        "source_locked_cohort_ready": cohort_ready,
        "required_runtime_packages_available": runtime_packages_ready,
        "force_field_assets_ready": force_field_ready,
        "runtime_smoke_tests_pass": smoke_ready,
        "external_download_performed": False,
        "atomistic_result_generated": False,
    }
    gate_status = "PASS" if all(
        checks[key]
        for key in (
            "contract_files_present",
            "source_locked_cohort_ready",
            "required_runtime_packages_available",
            "force_field_assets_ready",
            "runtime_smoke_tests_pass",
        )
    ) else "BLOCKED"

    resolved_input_paths = [
        relative_repo_path(SPEC_PATH),
        relative_repo_path(DATA_MANIFEST_PATH),
        relative_repo_path(RUNTIME_MANIFEST_PATH),
    ]
    input_hashes = {
        path: file_checks[path]["sha256"]
        for path in resolved_input_paths
        if file_checks[path]["sha256"]
    }

    return {
        "schema_version": "0.22.dynamics.gate.v1",
        "artifact": "0_22_protein_folding_dynamics_gate",
        "topic": "0.22_Biophysics_Origin_of_Life",
        "lane": "protein_folding_dynamics",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate_status": gate_status,
        "claim_class": "B",
        "data_class": "source_referenced_only",
        "topic_status_impact": "NONE",
        "canonical_topic_status": "Draft",
        "canonical_topic_tier": "B",
        "primary_verifier_status": "WARN",
        "controlling_blocker": "source_locked_cohort_and_atomistic_runtime_missing",
        "resolved_input_paths": resolved_input_paths,
        "resolution_base": "repository_root",
        "resolution_status": "resolved",
        "input_hashes": input_hashes,
        "file_checks": file_checks,
        "source_summary": {
            "declared_source_records": len(source_records),
            "source_locked_records": source_lock_count,
            "cohort_target_total": cohort.get("target_total"),
            "cohort_entries_present": len(cohort_entries),
            "selection_status": cohort.get("selection_status"),
        },
        "runtime_summary": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "packages": package_checks,
            "force_field_name": force_field.get("name"),
            "force_field_status": force_field.get("asset_status"),
            "smoke_tests": runtime_manifest.get("smoke_tests", []),
        },
        "checks": checks,
        "next_required_evidence": [
            "Freeze a source-backed 12-protein cohort with 8 development and 4 protein-level holdout entries.",
            "Install and pin OpenMM, MDTraj, and openmmtools or record a documented alternative.",
            "Hash AMBER ff14SB, TIP3P, ion, topology, and preparation assets.",
            "Pass the CPU one-step and trajectory round-trip smoke tests.",
        ],
        "claim_boundary": "This is a Wave-0 source/runtime preflight only. It does not establish atomistic protein folding, a cellular mechanism, PDB/CASP validation, AlphaFold replication, or external replication.",
    }


def main() -> int:
    artifact = build_gate()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(artifact, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"artifact": relative_repo_path(ARTIFACT_PATH), "gate_status": artifact["gate_status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
