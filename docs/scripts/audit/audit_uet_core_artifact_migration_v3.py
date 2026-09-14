"""Audit the consumer-aware generated-artifact migration plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_artifact_migration_manifest.json"
AUDIT = CORE / "00_governance" / "uet_core_artifact_migration_audit.json"


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build() -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("records", [])
    missing_sources = []
    source_hash_mismatches = []
    existing_targets = []
    by_target: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        source = ROOT / row["legacy_path"]
        target = ROOT / row["canonical_path"]
        if not source.exists():
            missing_sources.append(row["legacy_path"])
        else:
            observed = sha256(source)
            if observed != row.get("sha256_before"):
                source_hash_mismatches.append({
                    "path": row["legacy_path"],
                    "expected": row.get("sha256_before"),
                    "observed": observed,
                })
        if target.exists():
            existing_targets.append(row["canonical_path"])
        by_target[row["collision_key"]].append(row["legacy_path"])
    duplicate_targets = {
        key: values for key, values in by_target.items() if len(values) > 1
    }
    boundary = CORE / "artifacts" / "README.md"
    checks = [
        {
            "check_id": "manifest_schema",
            "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL",
        },
        {
            "check_id": "legacy_sources_exist",
            "status": "PASS" if not missing_sources else "FAIL",
            "observed": len(missing_sources),
        },
        {
            "check_id": "source_hashes_stable",
            "status": "PASS" if not source_hash_mismatches else "FAIL",
            "observed": len(source_hash_mismatches),
        },
        {
            "check_id": "canonical_targets_unique",
            "status": "PASS" if not duplicate_targets else "FAIL",
            "observed": len(duplicate_targets),
        },
        {
            "check_id": "canonical_targets_not_written_before_consumer_switch",
            "status": "PASS" if not existing_targets else "FAIL",
            "observed": len(existing_targets),
        },
        {
            "check_id": "legacy_artifact_boundary_present",
            "status": "PASS" if boundary.exists() else "FAIL",
        },
        {
            "check_id": "physics_status_unchanged",
            "status": "PASS" if payload.get("summary", {}).get("physics_status_changes") == 0 else "FAIL",
            "observed": payload.get("summary", {}).get("physics_status_changes"),
        },
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_artifact_migration_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_artifact_migration_v3.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "artifact_migration_plan_integrity_failed",
        "checks": checks,
        "missing_sources": missing_sources,
        "source_hash_mismatches": source_hash_mismatches,
        "duplicate_targets": duplicate_targets,
        "existing_targets": existing_targets,
        "summary": payload.get("summary", {}),
        "claim_boundary": "artifact organization plan only; no physics-status promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "audit": repo_path(AUDIT),
        "missing_sources": len(result["missing_sources"]),
        "hash_mismatches": len(result["source_hash_mismatches"]),
        "duplicate_targets": len(result["duplicate_targets"]),
        "existing_targets": len(result["existing_targets"]),
    }, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
