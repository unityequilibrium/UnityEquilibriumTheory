"""Audit the staged data/tooling migration without executing tooling scripts."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "docs" / "core" / "00_governance" / "uet_core_data_tooling_migration_manifest.json"
AUDIT = ROOT / "docs" / "core" / "00_governance" / "uet_core_data_tooling_migration_audit.json"
REDIRECT = re.compile(r"Canonical source: \[[^\]]+\]\(([^)]+)\)")
SHIM = re.compile(r'_CANONICAL_RELATIVE\s*=\s*["\']([^"\']+)["\']')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def redirect_target(path: Path) -> str | None:
    match = REDIRECT.search(path.read_text(encoding="utf-8"))
    if match is None:
        return None
    return (path.parent / match.group(1)).resolve().relative_to(ROOT).as_posix()


def shim_target(path: Path) -> str | None:
    match = SHIM.search(path.read_text(encoding="utf-8"))
    return None if match is None else match.group(1)


def build() -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("records", [])
    failures: list[dict[str, str]] = []
    targets: dict[str, list[str]] = defaultdict(list)
    migrated = 0
    quarantined = 0
    for row in rows:
        current = ROOT / row["legacy_path"]
        target = ROOT / row["canonical_path"]
        state = row.get("migration_state")
        if state == "MIGRATED" and row.get("compatibility_mode") in {
            "archived_runpy_shim",
            "archived_redirect",
        }:
            migrated += 1
            archive_value = row.get("compatibility_archive_path")
            archive = ROOT / archive_value if archive_value else None
            if not target.exists() or archive is None or not archive.exists():
                failures.append({"path": row["legacy_path"], "reason": "archived_shim_or_canonical_target_missing"})
            if archive is not None and archive.exists() and row.get("file_kind") == "documentation":
                observed = redirect_target(archive)
                if observed != row["canonical_path"]:
                    failures.append({"path": row["legacy_path"], "reason": f"archived_redirect_target_mismatch:{observed}"})
            expected_hash = row.get("sha256_after")
            if expected_hash and target.exists() and sha256(target) != expected_hash:
                failures.append({"path": row["legacy_path"], "reason": "canonical_hash_mismatch"})
            continue
        if state == "MIGRATED_WITH_SHIM":
            migrated += 1
            if not current.exists() or not target.exists():
                failures.append({"path": row["legacy_path"], "reason": "shim_or_canonical_target_missing"})
                continue
            if row.get("file_kind") == "python_tool":
                observed = shim_target(current)
                if observed != row["canonical_path"]:
                    failures.append({"path": row["legacy_path"], "reason": f"shim_target_mismatch:{observed}"})
            elif row.get("file_kind") == "documentation":
                observed = redirect_target(current)
                if observed != row["canonical_path"]:
                    failures.append({"path": row["legacy_path"], "reason": f"redirect_target_mismatch:{observed}"})
            expected_hash = row.get("sha256_after")
            if expected_hash and sha256(target) != expected_hash:
                failures.append({"path": row["legacy_path"], "reason": "canonical_hash_mismatch"})
            continue
        if state == "QUARANTINED":
            quarantined += 1
            if not current.exists():
                failures.append({"path": row["legacy_path"], "reason": "quarantined_source_missing"})
            continue
        if state == "MIGRATION_READY":
            failures.append({"path": row["legacy_path"], "reason": "unapplied_ready_source"})
        targets[row["collision_key"]].append(row["legacy_path"])

    duplicate_targets = {key: paths for key, paths in targets.items() if len(paths) > 1}
    if duplicate_targets:
        failures.append({"path": "<manifest>", "reason": "duplicate_canonical_targets"})
    summary = {
        "files_total": len(rows),
        "migrated_with_shim": migrated,
        "quarantined": quarantined,
        "duplicate_targets": duplicate_targets,
        "failures": len(failures),
        "physics_status_changes": payload.get("summary", {}).get("physics_status_changes", 0),
    }
    checks = [
        {"check_id": "manifest_schema", "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL"},
        {"check_id": "migrated_targets_and_shims", "status": "PASS" if not failures else "FAIL"},
        {"check_id": "canonical_target_uniqueness", "status": "PASS" if not duplicate_targets else "FAIL"},
        {"check_id": "organization_does_not_change_physics_status", "status": "PASS" if summary["physics_status_changes"] == 0 else "FAIL"},
    ]
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_data_tooling_migration_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_data_tooling_migration.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "data_tooling_migration_integrity_checks_failed",
        "checks": checks,
        "summary": summary,
        "failures_detail": failures,
    }


def main() -> int:
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "audit": AUDIT.relative_to(ROOT).as_posix(), "failures": result["summary"]["failures"]}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
