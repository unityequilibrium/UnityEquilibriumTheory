"""Audit canonical-path and ownership invariants for the physical core migration.

This audit is deliberately organizational.  It validates that the migration
manifest is internally consistent, that canonical targets are unique, and that
protected entry points remain available.  It never upgrades a physics or
evidence status.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
AUDIT = CORE / "00_governance" / "uet_core_paths_audit.json"

PROTECTED = {
    "docs/core/AGENTS.md",
    "docs/core/README.md",
    "docs/core/CORE_FILE_INDEX.md",
    "docs/core/__init__.py",
}


def build() -> dict[str, object]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = payload.get("records", [])
    missing_current: list[str] = []
    missing_canonical: list[str] = []
    duplicate_targets: dict[str, list[str]] = defaultdict(list)
    unassigned: list[str] = []
    invalid_states: list[str] = []

    allowed_states = {
        "NOT_STARTED",
        "MIGRATION_READY",
        "MIGRATED_WITH_SHIM",
        "MIGRATED",
        "QUARANTINED",
    }
    for row in rows:
        current = str(row.get("current_path", ""))
        canonical = str(row.get("canonical_path", ""))
        state = str(row.get("migration_state", ""))
        if current and not (ROOT / current).exists():
            missing_current.append(current)
        if canonical and state in {"MIGRATED", "MIGRATED_WITH_SHIM"} and not (ROOT / canonical).exists():
            missing_canonical.append(canonical)
        if canonical and state not in {"MIGRATED", "MIGRATED_WITH_SHIM"}:
            duplicate_targets[canonical.lower()].append(current)
        if not row.get("owner_id") or not row.get("organization_status"):
            unassigned.append(current)
        if state not in allowed_states:
            invalid_states.append(current)

    duplicate_targets = {
        key: values for key, values in duplicate_targets.items() if len(values) > 1
    }
    missing_protected = sorted(path for path in PROTECTED if not (ROOT / path).exists())
    summary = payload.get("summary", {})
    checks = [
        {
            "check_id": "manifest_schema",
            "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL",
        },
        {
            "check_id": "current_paths_exist",
            "status": "PASS" if not missing_current else "FAIL",
            "observed": len(missing_current),
        },
        {
            "check_id": "migrated_canonical_paths_exist",
            "status": "PASS" if not missing_canonical else "FAIL",
            "observed": len(missing_canonical),
        },
        {
            "check_id": "canonical_targets_unique",
            "status": "PASS" if not duplicate_targets else "FAIL",
            "observed": len(duplicate_targets),
        },
        {
            "check_id": "all_records_have_owner_and_disposition",
            "status": "PASS" if not unassigned else "FAIL",
            "observed": len(unassigned),
        },
        {
            "check_id": "migration_states_declared",
            "status": "PASS" if not invalid_states else "FAIL",
            "observed": len(invalid_states),
        },
        {
            "check_id": "root_entrypoints_retained",
            "status": "PASS" if not missing_protected else "FAIL",
            "observed": len(missing_protected),
        },
        {
            "check_id": "organization_does_not_change_physics_status",
            "status": "PASS" if summary.get("physics_status_changes") == 0 else "FAIL",
            "observed": summary.get("physics_status_changes"),
        },
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_paths_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_paths.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "canonical_path_or_ownership_integrity_failed",
        "checks": checks,
        "missing_current_paths": missing_current,
        "missing_canonical_paths": missing_canonical,
        "duplicate_targets": duplicate_targets,
        "unassigned_records": unassigned,
        "invalid_migration_states": invalid_states,
        "missing_protected_entrypoints": missing_protected,
        "claim_boundary": "organization/path audit only; no physics-status promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "audit": str(AUDIT.relative_to(ROOT))}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
