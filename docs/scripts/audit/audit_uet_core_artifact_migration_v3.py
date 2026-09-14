"""Audit the generated-artifact migration plan and completed bounded moves."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_artifact_migration_manifest.json"
HISTORY = CORE / "00_governance" / "uet_core_artifact_migration_history.json"
AUDIT = CORE / "00_governance" / "uet_core_artifact_migration_audit.json"


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    payload = load_json(MANIFEST)
    rows = payload.get("records", [])
    missing_sources: list[str] = []
    source_hash_mismatches: list[dict[str, str | None]] = []
    missing_targets: list[str] = []
    target_hash_mismatches: list[dict[str, str | None]] = []
    migrated_source_present: list[str] = []
    migrated_active_consumer_rows: list[str] = []
    existing_targets: list[str] = []
    by_target: dict[str, list[str]] = defaultdict(list)
    migrated_keys: set[tuple[str, str]] = set()

    for row in rows:
        state = str(row.get("migration_state", "NOT_STARTED"))
        legacy_path = str(row["legacy_path"])
        canonical_path = str(row["canonical_path"])
        source = ROOT / legacy_path
        target = ROOT / canonical_path
        by_target[str(row["collision_key"])].append(legacy_path)
        key = (legacy_path, canonical_path)
        if state == "MIGRATED":
            migrated_keys.add(key)
            if (
                row.get("downstream_dependencies")
                or row.get("active_consumers")
                or row.get("consumer_count") not in (None, 0)
            ):
                migrated_active_consumer_rows.append(legacy_path)
            if not target.exists():
                missing_targets.append(canonical_path)
            else:
                expected = row.get("sha256_after") or row.get("sha256_before")
                observed = sha256(target)
                if expected and observed != expected:
                    target_hash_mismatches.append({
                        "path": canonical_path,
                        "expected": expected,
                        "observed": observed,
                    })
            if source.exists():
                migrated_source_present.append(legacy_path)
        else:
            if not source.exists():
                missing_sources.append(legacy_path)
            else:
                observed = sha256(source)
                if observed != row.get("sha256_before"):
                    source_hash_mismatches.append({
                        "path": legacy_path,
                        "expected": row.get("sha256_before"),
                        "observed": observed,
                    })
            if target.exists():
                existing_targets.append(canonical_path)

    duplicate_targets = {
        key: values for key, values in by_target.items() if len(values) > 1
    }

    history_errors: list[str] = []
    history_keys: set[tuple[str, str]] = set()
    if migrated_keys and not HISTORY.exists():
        history_errors.append("history_file_missing")
    elif HISTORY.exists():
        try:
            history = load_json(HISTORY)
            history_rows = history.get("records", [])
            if history.get("schema_version") != "1.0":
                history_errors.append("history_schema_invalid")
            if not isinstance(history_rows, list):
                history_errors.append("history_records_not_list")
                history_rows = []
            for item in history_rows:
                key = (str(item.get("legacy_path", "")), str(item.get("canonical_path", "")))
                if key in history_keys:
                    history_errors.append(f"history_duplicate:{key[0]}")
                history_keys.add(key)
                if item.get("migration_state") != "MIGRATED":
                    history_errors.append(f"history_non_migrated:{key[0]}")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            history_errors.append(f"history_unreadable:{type(exc).__name__}")
    if history_keys != migrated_keys:
        history_errors.append("history_manifest_key_mismatch")

    boundary = CORE / "artifacts" / "README.md"
    checks = [
        {
            "check_id": "manifest_schema",
            "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL",
        },
        {
            "check_id": "active_legacy_sources_exist",
            "status": "PASS" if not missing_sources else "FAIL",
            "observed": len(missing_sources),
        },
        {
            "check_id": "active_source_hashes_stable",
            "status": "PASS" if not source_hash_mismatches else "FAIL",
            "observed": len(source_hash_mismatches),
        },
        {
            "check_id": "migrated_canonical_targets_exist",
            "status": "PASS" if not missing_targets else "FAIL",
            "observed": len(missing_targets),
        },
        {
            "check_id": "migrated_target_hashes_stable",
            "status": "PASS" if not target_hash_mismatches else "FAIL",
            "observed": len(target_hash_mismatches),
        },
        {
            "check_id": "migrated_legacy_sources_absent",
            "status": "PASS" if not migrated_source_present else "FAIL",
            "observed": len(migrated_source_present),
        },
        {
            "check_id": "migrated_active_consumers_empty",
            "status": "PASS" if not migrated_active_consumer_rows else "FAIL",
            "observed": len(migrated_active_consumer_rows),
        },
        {
            "check_id": "migration_history_matches_manifest",
            "status": "PASS" if not history_errors else "FAIL",
            "observed": history_errors,
        },
        {
            "check_id": "canonical_targets_unique",
            "status": "PASS" if not duplicate_targets else "FAIL",
            "observed": len(duplicate_targets),
        },
        {
            "check_id": "active_canonical_targets_not_written_before_consumer_switch",
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
        "controlling_blocker": None if status == "PASS" else "artifact_migration_integrity_failed",
        "checks": checks,
        "missing_sources": missing_sources,
        "source_hash_mismatches": source_hash_mismatches,
        "missing_targets": missing_targets,
        "target_hash_mismatches": target_hash_mismatches,
        "migrated_source_present": migrated_source_present,
        "migrated_active_consumer_rows": migrated_active_consumer_rows,
        "duplicate_targets": duplicate_targets,
        "existing_targets": existing_targets,
        "summary": payload.get("summary", {}),
        "claim_boundary": "artifact organization and compatibility control only; no physics-status promotion",
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
        "missing_targets": len(result["missing_targets"]),
        "target_hash_mismatches": len(result["target_hash_mismatches"]),
        "duplicate_targets": len(result["duplicate_targets"]),
        "existing_targets": len(result["existing_targets"]),
        "migrated_active_consumers": len(result["migrated_active_consumer_rows"]),
    }, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())