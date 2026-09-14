"""Audit the staged physical migration of docs/core."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
AUDIT = CORE / "00_governance" / "uet_core_physical_migration_audit.json"
REDIRECT_PATTERN = re.compile(r"Canonical source: \[[^\]]+\]\(([^)]+)\)")
SHIM_PATTERN = re.compile(r'_CANONICAL_RELATIVE\s*=\s*"([^"]+)"')
FORWARD_SHIM_PATTERN = re.compile(
    r'forward_public_symbols\(globals\(\),\s*"([^"]+)"\)'
)


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def redirect_target(path: Path) -> str | None:
    match = REDIRECT_PATTERN.search(path.read_text(encoding="utf-8"))
    return None if match is None else repo_path((path.parent / match.group(1)).resolve())


def shim_target(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = SHIM_PATTERN.search(text)
    if match is not None:
        return match.group(1).replace("\\", "/")
    match = FORWARD_SHIM_PATTERN.search(text)
    if match is None:
        return None
    module = match.group(1)
    return module.replace(".", "/") + ".py"


def build() -> dict:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    by_target = defaultdict(list)
    missing_current = []
    redirect_errors = []
    for item in records:
        current = ROOT / item["current_path"]
        if not current.exists():
            missing_current.append(item["current_path"])
            continue
        if item.get("file_kind") == "compatibility_redirect":
            target = redirect_target(current)
            if target is None or not (ROOT / target).exists():
                redirect_errors.append({"path": item["current_path"], "target": target})
            continue
        if item.get("file_kind") == "compatibility_python_shim":
            target = shim_target(current)
            if target is None or not (ROOT / target).exists():
                redirect_errors.append({"path": item["current_path"], "target": target})
            continue
        target = item.get("canonical_path")
        if target and item["current_path"] != target:
            by_target[str(target).lower()].append(item["current_path"])
    duplicate_targets = {key: paths for key, paths in by_target.items() if len(paths) > 1}
    protected = {
        "docs/core/AGENTS.md",
        "docs/core/README.md",
        "docs/core/CORE_FILE_INDEX.md",
        "docs/core/__init__.py",
    }
    root_errors = [path for path in protected if not (ROOT / path).exists()]
    summary = payload.get("summary", {})
    checks = [
        {"check_id": "manifest_schema", "status": "PASS" if payload.get("schema_version") == "1.0" else "FAIL"},
        {"check_id": "canonical_target_uniqueness", "status": "PASS" if not duplicate_targets else "FAIL", "observed": len(duplicate_targets)},
        {"check_id": "current_paths_exist", "status": "PASS" if not missing_current else "FAIL", "observed": len(missing_current)},
        {"check_id": "redirects_point_to_existing_sources", "status": "PASS" if not redirect_errors else "FAIL", "observed": len(redirect_errors)},
        {"check_id": "root_entrypoints_retained", "status": "PASS" if not root_errors else "FAIL", "observed": len(root_errors)},
        {"check_id": "organization_does_not_change_physics_status", "status": "PASS" if summary.get("physics_status_changes") == 0 else "FAIL", "observed": summary.get("physics_status_changes")},
    ]
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_physical_migration_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_physical_migration.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "physical_migration_integrity_checks_failed",
        "checks": checks,
        "duplicate_targets": duplicate_targets,
        "missing_current_paths": missing_current,
        "redirect_errors": redirect_errors,
        "root_entrypoint_errors": root_errors,
        "summary": summary,
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
        "duplicate_targets": len(result["duplicate_targets"]),
        "missing_current_paths": len(result["missing_current_paths"]),
        "redirect_errors": len(result["redirect_errors"]),
    }, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
