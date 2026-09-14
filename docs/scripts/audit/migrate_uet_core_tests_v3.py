"""Migrate the safe subset of the legacy core test surface.

Tests are moved without compatibility copies: leaving Python wrappers in the old
test tree would make pytest collect the same test twice.  The legacy location is
therefore retained only as a boundary README after a successful move.  Tests
that derive paths from their location, refer to the legacy tree, are dirty, or
are explicitly sandbox/package support remain in place and are recorded for a
later review wave.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
SOURCE_ROOT = CORE / "test"
GOVERNANCE = CORE / "00_governance"
MANIFEST = GOVERNANCE / "uet_core_test_migration_manifest.json"
REPORT = GOVERNANCE / "UET_CORE_TEST_MIGRATION_REPORT.md"
GENERATOR = "docs/scripts/audit/migrate_uet_core_tests_v3.py"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_path_for  # noqa: E402


PATH_SENSITIVE = re.compile(
    r"(__file__|parents\s*\[|docs/core/test|Path\s*\(|os\.path\.|sys\.path|PROJECT_ROOT|REPO_ROOT)"
)
EXCLUDED_PARTS = {"__pycache__", ".git"}


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def dirty_paths() -> set[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return set()
    values: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        value = line[3:]
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        values.add(value.strip('"').replace("\\", "/"))
    return values


def role_for(path: Path) -> str:
    name = path.name.lower()
    relative = repo_path(path).lower()
    if any(token in name for token in ("formula", "derivative", "stationarity", "eos", "action", "noether")):
        return "equation"
    if any(token in name for token in ("causal", "convergence", "stability", "numerical", "conservation", "energy")):
        return "numerical"
    if any(token in name for token in ("artifact", "schema", "manifest", "registry", "organization")):
        return "artifact"
    if "validation" in relative or "parameter_engine" in relative:
        return "regression"
    return "regression"


def previous_records() -> dict[str, dict[str, Any]]:
    if not MANIFEST.exists():
        return {}
    try:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        str(row.get("legacy_path")): row
        for row in payload.get("records", [])
        if row.get("legacy_path")
    }


def classify(path: Path, dirty: set[str]) -> tuple[str, str, bool]:
    """Return (state, reason, eligible_for_first_wave)."""

    relative = repo_path(path)
    if path.name == "__init__.py":
        return "QUARANTINED", "package_boundary_requires_explicit_review", False
    if path.name == "sandbox_emergent.py":
        return "QUARANTINED", "sandbox_surface_not_promoted_to_production_tests", False
    if "parameter_engine" in repo_path(path).lower():
        return "QUARANTINED", "package_import_depends_on_legacy_test_path", False
    try:
        text = read_text(path)
    except (OSError, UnicodeDecodeError):
        return "QUARANTINED", "unreadable_test_source", False
    if relative in dirty:
        return "QUARANTINED", "dirty_source_held_back", False
    if PATH_SENSITIVE.search(text):
        return "QUARANTINED", "path_bootstrap_or_legacy_reference_requires_review", False
    return "MIGRATION_READY", "path_safe_first_wave_candidate", True


def make_record(path: Path, dirty: set[str], prior: dict[str, Any] | None = None) -> dict[str, Any]:
    relative = repo_path(path)
    canonical = canonical_path_for(relative)
    state, reason, eligible = classify(path, dirty)
    prior = prior or {}
    before = str(prior.get("sha256_before") or sha256(path))
    return {
        "asset_id": "UET-TEST-" + hashlib.sha1(relative.encode()).hexdigest()[:12].upper(),
        "legacy_path": relative,
        "canonical_path": canonical,
        "file_kind": "test_python",
        "logical_area": "05_tests",
        "owner_id": "EVIDENCE",
        "room_id": "ROOM_CORE_FOUNDATION",
        "equation_family_or_lane": "core_test_surface",
        "organization_status": "ASSIGNED",
        "evidence_status": "INTERNAL",
        "status_source": "test_migration_manifest",
        "source_or_generated": "source",
        "generator_path": None,
        "formula_ids": [],
        "verifier_paths": ["docs/scripts/audit/audit_uet_core_test_migration.py", "docs/scripts/audit/audit_uet_core_test_collection.py"],
        "artifact_paths": ["docs/core/00_governance/uet_core_test_migration_audit.json", "docs/core/00_governance/uet_core_test_collection_audit.json"],
        "upstream_dependencies": ["docs/core/AGENTS.md", "docs/core/core_paths.py"],
        "downstream_dependencies": [],
        "sha256_before": before,
        "sha256_after": prior.get("sha256_after"),
        "migration_wave": "test_surface_safe_subset",
        "migration_state": state,
        "compatibility_mode": "test_path_moved_no_wrapper" if eligible else "legacy_path_retained",
        "dirty_source": relative in dirty,
        "path_sensitive": not eligible,
        "disposition": reason,
        "collision_key": canonical.lower(),
        "rollback_path": relative,
        "next_action": "apply_safe_test_move" if eligible else reason,
    }


def records() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dirty = dirty_paths()
    prior = previous_records()
    rows: list[dict[str, Any]] = []
    current_legacy: set[str] = set()
    if SOURCE_ROOT.exists():
        for path in sorted(SOURCE_ROOT.rglob("*.py")):
            if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            relative = repo_path(path)
            current_legacy.add(relative)
            rows.append(make_record(path, dirty, prior.get(relative)))

    # Keep records for files already moved in an earlier invocation.  Their
    # legacy path is intentionally absent from the filesystem after migration.
    for relative, old in prior.items():
        if relative in current_legacy:
            continue
        if old.get("migration_state") not in {"MIGRATED", "MIGRATED_WITH_SHIM"}:
            continue
        canonical = str(old.get("canonical_path"))
        target = ROOT / canonical
        if not target.exists():
            continue
        row = dict(old)
        row["verifier_paths"] = ["docs/scripts/audit/audit_uet_core_test_migration.py", "docs/scripts/audit/audit_uet_core_test_collection.py"]
        row["artifact_paths"] = ["docs/core/00_governance/uet_core_test_migration_audit.json", "docs/core/00_governance/uet_core_test_collection_audit.json"]
        row["sha256_after"] = sha256(target)
        row["migration_state"] = "MIGRATED"
        row["compatibility_mode"] = "test_path_moved_no_wrapper"
        row["next_action"] = "verify_moved_test_surface"
        rows.append(row)

    by_target: dict[str, list[str]] = {}
    for row in rows:
        if row["migration_state"] == "MIGRATED":
            continue
        by_target.setdefault(row["collision_key"], []).append(row["legacy_path"])
    duplicate_targets = {key: values for key, values in by_target.items() if len(values) > 1}
    existing_conflicts = sorted(
        {
            row["canonical_path"]
            for row in rows
            if row["migration_state"] == "MIGRATION_READY"
            and (ROOT / row["canonical_path"]).exists()
        }
    )
    summary = {
        "files_total": len(rows),
        "migration_ready": sum(row["migration_state"] == "MIGRATION_READY" for row in rows),
        "migrated": sum(row["migration_state"] == "MIGRATED" for row in rows),
        "quarantined": sum(row["migration_state"] == "QUARANTINED" for row in rows),
        "dirty_sources": sum(bool(row["dirty_source"]) for row in rows),
        "duplicate_targets": duplicate_targets,
        "existing_target_conflicts": existing_conflicts,
        "physics_status_changes": 0,
        "physical_move_performed": False,
    }
    return rows, summary


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# UET Core Test Migration Report",
        "",
        "> Organization migration report. It does not promote a physics claim.",
        "",
        f"Generated at: {payload['generated_at']}",
        f"Generator: {payload['generator']}",
        "",
        "## Current state",
        "",
        f"- Test files indexed: **{summary['files_total']}**",
        f"- Safe first-wave candidates: **{summary['migration_ready']}**",
        f"- Physically migrated: **{summary['migrated']}**",
        f"- Quarantined for path/package/sandbox review: **{summary['quarantined']}**",
        f"- Dirty sources held back: **{summary['dirty_sources']}**",
        f"- Duplicate targets: **{len(summary['duplicate_targets'])}**",
        f"- Existing target conflicts: **{len(summary['existing_target_conflicts'])}**",
        f"- Physics status changes: **{summary['physics_status_changes']}**",
        "",
        "## Test-specific compatibility rule",
        "",
        "- Moved Python tests do not receive old-path wrappers, because wrappers would create duplicate pytest collection.",
        "- The old tree is retained only for tests not yet safe to move and for its boundary README after the move wave.",
        "- The migration manifest is the path map for moved tests; it is not evidence that the tests prove the underlying physics.",
        "- Path-sensitive, dirty, package-boundary, and sandbox surfaces remain outside the first wave.",
    ]
    if summary["duplicate_targets"]:
        lines += ["", "## Collision keys", ""]
        lines.extend(f"- `{key}`: {', '.join(values)}" for key, values in sorted(summary["duplicate_targets"].items()))
    return "\n".join(lines) + "\n"


def write_payload(rows: list[dict[str, Any]], summary: dict[str, Any], performed: bool = False) -> dict[str, Any]:
    summary = dict(summary)
    summary["physical_move_performed"] = performed or bool(summary.get("migrated"))
    payload = {
        "schema_version": "1.0",
        "migration_id": "UET-CORE-TEST-V3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "docs/core/test",
        "canonical_path_authority": "docs/core/core_paths.py",
        "legacy_test_wrappers": False,
        "summary": summary,
        "records": sorted(rows, key=lambda row: row["legacy_path"]),
    }
    GOVERNANCE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(payload), encoding="utf-8")
    return payload


def apply_moves(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload["summary"]
    if summary["duplicate_targets"] or summary["existing_target_conflicts"]:
        raise RuntimeError("test migration has duplicate or existing target conflicts")
    moved = 0
    for row in payload["records"]:
        if row["migration_state"] != "MIGRATION_READY":
            continue
        source = ROOT / row["legacy_path"]
        target = ROOT / row["canonical_path"]
        if not source.exists():
            raise FileNotFoundError(f"test source disappeared before move: {row['legacy_path']}")
        if target.exists():
            raise FileExistsError(f"test target already exists: {row['canonical_path']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        row["migration_state"] = "MIGRATED"
        row["sha256_after"] = sha256(target)
        row["next_action"] = "verify_moved_test_surface"
        moved += 1
    payload["summary"]["migration_ready"] = 0
    payload["summary"]["migrated"] = sum(row["migration_state"] == "MIGRATED" for row in payload["records"])
    payload["summary"]["quarantined"] = sum(row["migration_state"] == "QUARANTINED" for row in payload["records"])
    payload["summary"]["physical_move_performed"] = moved > 0
    payload["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(payload), encoding="utf-8")
    return {"moved": moved, "payload": payload}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="perform the safe physical move")
    parser.add_argument("--check", action="store_true", help="write the plan without moving files")
    args = parser.parse_args()
    rows, summary = records()
    payload = write_payload(rows, summary)
    if args.apply:
        result = apply_moves(payload)
        print(json.dumps({
            "status": "APPLIED",
            "moved": result["moved"],
            "quarantined": result["payload"]["summary"]["quarantined"],
            "manifest": repo_path(MANIFEST),
        }, ensure_ascii=False))
        return 0
    print(json.dumps({
        "status": "PLAN_ONLY",
        "ready": summary["migration_ready"],
        "migrated": summary["migrated"],
        "quarantined": summary["quarantined"],
        "duplicate_targets": len(summary["duplicate_targets"]),
        "existing_target_conflicts": len(summary["existing_target_conflicts"]),
        "manifest": repo_path(MANIFEST),
    }, ensure_ascii=False))
    return 0 if not summary["duplicate_targets"] and not summary["existing_target_conflicts"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
