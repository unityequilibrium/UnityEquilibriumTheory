"""Audit the physical migration of the UET core test surface."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_test_migration_manifest.json"
AUDIT = CORE / "00_governance" / "uet_core_test_migration_audit.json"


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
    migrated_missing = []
    migrated_hash_mismatches = []
    quarantined_missing = []
    duplicate_targets: dict[str, list[str]] = defaultdict(list)
    stale_old_python = []
    for row in rows:
        legacy = ROOT / row["legacy_path"]
        canonical = ROOT / row["canonical_path"]
        state = row.get("migration_state")
        if state == "MIGRATED":
            if not canonical.exists():
                migrated_missing.append(row["canonical_path"])
            else:
                observed = sha256(canonical)
                expected = row.get("sha256_before")
                if expected and observed != expected:
                    migrated_hash_mismatches.append({
                        "canonical_path": row["canonical_path"],
                        "expected_sha256": expected,
                        "observed_sha256": observed,
                    })
            if legacy.exists() and legacy.suffix.lower() == ".py":
                stale_old_python.append(row["legacy_path"])
        elif state == "QUARANTINED" and not legacy.exists():
            quarantined_missing.append(row["legacy_path"])
        if state != "MIGRATED":
            duplicate_targets[row["collision_key"]].append(row["legacy_path"])
    duplicate_targets = {
        key: values for key, values in duplicate_targets.items() if len(values) > 1
    }
    old_boundary = CORE / "test" / "README.md"
    checks = [
        {
            "check_id": "manifest_schema",
            "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL",
        },
        {
            "check_id": "migrated_canonical_files_exist",
            "status": "PASS" if not migrated_missing else "FAIL",
            "observed": len(migrated_missing),
        },
        {
            "check_id": "migrated_hashes_preserved",
            "status": "PASS" if not migrated_hash_mismatches else "FAIL",
            "observed": len(migrated_hash_mismatches),
        },
        {
            "check_id": "quarantined_sources_retained",
            "status": "PASS" if not quarantined_missing else "FAIL",
            "observed": len(quarantined_missing),
        },
        {
            "check_id": "no_duplicate_test_targets",
            "status": "PASS" if not duplicate_targets else "FAIL",
            "observed": len(duplicate_targets),
        },
        {
            "check_id": "no_old_python_wrappers_for_moved_tests",
            "status": "PASS" if not stale_old_python else "FAIL",
            "observed": len(stale_old_python),
        },
        {
            "check_id": "legacy_test_boundary_present",
            "status": "PASS" if old_boundary.exists() else "FAIL",
        },
        {
            "check_id": "organization_does_not_change_physics_status",
            "status": "PASS" if payload.get("summary", {}).get("physics_status_changes") == 0 else "FAIL",
            "observed": payload.get("summary", {}).get("physics_status_changes"),
        },
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_test_migration_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_test_migration.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "test_migration_integrity_checks_failed",
        "checks": checks,
        "migrated_missing": migrated_missing,
        "migrated_hash_mismatches": migrated_hash_mismatches,
        "quarantined_missing": quarantined_missing,
        "duplicate_targets": duplicate_targets,
        "stale_old_python_wrappers": stale_old_python,
        "summary": payload.get("summary", {}),
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
        "migrated_missing": len(result["migrated_missing"]),
        "hash_mismatches": len(result["migrated_hash_mismatches"]),
        "quarantined_missing": len(result["quarantined_missing"]),
        "duplicate_targets": len(result["duplicate_targets"]),
        "stale_old_python_wrappers": len(result["stale_old_python_wrappers"]),
    }, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
