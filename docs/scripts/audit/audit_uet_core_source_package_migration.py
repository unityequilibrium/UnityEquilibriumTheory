"""Verify source-package migration hashes and the no-duplicate boundary."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_source_package_migration_manifest.json"
REDIRECT_INDEX = CORE / "00_governance" / "uet_core_source_package_redirects.json"
LEGACY_ROOT = CORE / "data" / "external"
AUDIT = CORE / "00_governance" / "uet_core_source_package_migration_audit.json"
NON_PUBLIC_BINARY_SUFFIXES = frozenset({".sqlite", ".sqlite3", ".db"})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build() -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    redirect = json.loads(REDIRECT_INDEX.read_text(encoding="utf-8"))
    failures: list[dict[str, str]] = []
    retained_legacy = set()
    for row in payload.get("records", []):
        target = ROOT / row["canonical_path"]
        state = row.get("migration_state")
        if state == "QUARANTINED":
            valid = (
                Path(row["legacy_path"]).suffix.lower() in NON_PUBLIC_BINARY_SUFFIXES
                and row["canonical_path"] == row["legacy_path"]
                and target.exists()
                and row.get("next_action") == "retain_non_public_binary_at_legacy_path"
            )
            if not valid:
                failures.append({"path": row["legacy_path"], "reason": "invalid_non_public_binary_retention"})
            else:
                retained_legacy.add(row["legacy_path"])
            continue
        if state != "MIGRATED":
            failures.append({"path": row["legacy_path"], "reason": "record_not_migrated"})
        elif not target.exists():
            failures.append({"path": row["canonical_path"], "reason": "canonical_missing"})
        elif row.get("sha256_after") and sha256(target) != row["sha256_after"]:
            failures.append({"path": row["canonical_path"], "reason": "canonical_hash_mismatch"})
        if row["legacy_path"] in {item.get("legacy_path") for item in redirect.get("records", [])}:
            continue
        failures.append({"path": row["legacy_path"], "reason": "redirect_index_missing_record"})

    raw_legacy = [
        path.relative_to(ROOT).as_posix()
        for path in LEGACY_ROOT.rglob("*")
        if path.is_file() and path.name != "README.md"
        and path.relative_to(ROOT).as_posix() not in retained_legacy
    ] if LEGACY_ROOT.exists() else []
    failures.extend({"path": path, "reason": "raw_file_left_in_legacy_root"} for path in raw_legacy)
    checks = [
        {"check_id": "manifest_schema", "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL"},
        {"check_id": "raw_source_hashes", "status": "PASS" if not failures else "FAIL"},
        {"check_id": "no_duplicate_raw_files", "status": "PASS" if not raw_legacy else "FAIL"},
        {"check_id": "organization_does_not_change_physics_status", "status": "PASS" if payload.get("summary", {}).get("physics_status_changes") == 0 else "FAIL"},
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_source_package_migration_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_source_package_migration.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "source_package_migration_integrity_failed",
        "checks": checks,
        "summary": {
            "records_checked": len(payload.get("records", [])),
            "redirect_records": len(redirect.get("records", [])),
            "raw_legacy_files": len(raw_legacy),
            "failures": len(failures),
        },
        "failures_detail": failures,
    }


def main() -> int:
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "audit": AUDIT.relative_to(ROOT).as_posix(), "failures": result["summary"]["failures"]}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
