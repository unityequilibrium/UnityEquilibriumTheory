"""Migrate raw external files under docs/core/data without duplicating them."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
SOURCE_ROOT = CORE / "data" / "external"
TARGET_ROOT = CORE / "06_data" / "source_packages"
GOVERNANCE = CORE / "00_governance"
MANIFEST = GOVERNANCE / "uet_core_source_package_migration_manifest.json"
REDIRECT_INDEX = GOVERNANCE / "uet_core_source_package_redirects.json"
TARGET_README = TARGET_ROOT / "README.md"
LEGACY_README = SOURCE_ROOT / "README.md"
GENERATOR = "docs/scripts/audit/migrate_uet_core_source_packages_v3.py"
EXCLUDED_PARTS = {"__pycache__", ".git"}
NON_PUBLIC_BINARY_SUFFIXES = frozenset({".sqlite", ".sqlite3", ".db"})


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        if len(line) >= 4:
            value = line[3:]
            if " -> " in value:
                value = value.split(" -> ", 1)[1]
            values.add(value.strip('"').replace("\\", "/"))
    return values


def canonical_for(relative: str) -> str:
    if Path(relative).suffix.lower() in NON_PUBLIC_BINARY_SUFFIXES:
        return relative
    tail = relative.removeprefix("docs/core/data/external/")
    return f"docs/core/06_data/source_packages/{tail}"


def build_plan() -> dict[str, Any]:
    dirty = dirty_paths()
    rows: list[dict[str, Any]] = []
    for path in sorted(SOURCE_ROOT.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        relative = repo_path(path)
        if relative == repo_path(LEGACY_README):
            continue
        canonical = canonical_for(relative)
        rows.append(
            {
                "asset_id": "UET-SOURCE-" + hashlib.sha1(relative.encode()).hexdigest()[:12].upper(),
                "legacy_path": relative,
                "canonical_path": canonical,
                "file_kind": "source_package_file",
                "source_or_generated": "source",
                "sha256_before": sha256(path),
                "sha256_after": None,
                "migration_state": "QUARANTINED" if canonical == relative else "MIGRATION_READY",
                "dirty_source": relative in dirty,
                "collision_key": canonical.lower(),
                "rollback_path": relative,
                "next_action": (
                    "retain_non_public_binary_at_legacy_path"
                    if canonical == relative
                    else "apply_source_package_move"
                ),
            }
        )
    by_target: dict[str, list[str]] = {}
    for row in rows:
        by_target.setdefault(row["collision_key"], []).append(row["legacy_path"])
    collisions = {key: values for key, values in by_target.items() if len(values) > 1}
    existing = sorted({
        row["canonical_path"]
        for row in rows
        if row["canonical_path"] != row["legacy_path"]
        and (ROOT / row["canonical_path"]).exists()
    })
    summary = {
        "files_total": len(rows),
        "migration_ready": sum(row["migration_state"] == "MIGRATION_READY" for row in rows),
        "quarantined": sum(row["migration_state"] == "QUARANTINED" for row in rows),
        "dirty_sources": sum(row["dirty_source"] for row in rows),
        "duplicate_targets": collisions,
        "existing_target_conflicts": existing,
        "raw_hash_changes": 0,
        "physics_status_changes": 0,
        "physical_move_performed": False,
    }
    return {
        "schema_version": "1.0",
        "migration_id": "UET-CORE-SOURCE-PACKAGES-V3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "docs/core/data/external",
        "canonical_path_authority": "docs/core/core_paths.py",
        "summary": summary,
        "records": rows,
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    return "\n".join(
        [
            "# UET Core Source Package Migration Report",
            "",
            "> Raw source migration report. It does not promote physics evidence or claims.",
            "",
            f"Generated at: {payload['generated_at']}",
            f"Generator: {payload['generator']}",
            "",
            "## State",
            "",
            f"- Source package files indexed: **{summary['files_total']}**",
            f"- Ready to move: **{summary['migration_ready']}**",
            f"- Dirty sources held back: **{summary['dirty_sources']}**",
            f"- Duplicate targets: **{len(summary['duplicate_targets'])}**",
            f"- Existing destination conflicts: **{len(summary['existing_target_conflicts'])}**",
            f"- Raw hash changes: **{summary['raw_hash_changes']}**",
            f"- Physics status changes: **{summary['physics_status_changes']}**",
            "",
            "## Compatibility boundary",
            "",
            "Raw files have one canonical copy under 06_data/source_packages. The former external directory retains only a README redirect. The governance redirect index records legacy path, canonical path, and source hash without duplicating raw data.",
            "",
            "Source-package metadata is not automatically benchmark-ready; provenance, units, preprocessing, and evidence status remain controlled by the relevant scientific manifests.",
            "",
        ]
    )


def source_readme() -> str:
    return """# Core source packages

This directory is the canonical physical location for raw external files that were formerly stored under `docs/core/data/external/`.

The files remain source packages, not automatic empirical evidence. Consult the package manifest, source hash, units, preprocessing record, and topic gate before using a file in a benchmark.

The migration index is [`../00_governance/uet_core_source_package_redirects.json`](../../00_governance/uet_core_source_package_redirects.json).
"""


def legacy_readme() -> str:
    return """# Compatibility redirect

> This path is retained temporarily for compatibility. Raw source files are not duplicated.

Canonical source: [docs/core/06_data/source_packages/README.md](../../06_data/source_packages/README.md)

The legacy-to-canonical file map and hashes are recorded in [`docs/core/00_governance/uet_core_source_package_redirects.json`](../../00_governance/uet_core_source_package_redirects.json).

Do not add new source files here; use `docs/core/06_data/source_packages/`.
"""


def apply(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload["summary"]
    if summary["duplicate_targets"] or summary["existing_target_conflicts"]:
        raise RuntimeError("source package migration has duplicate or existing targets")
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for row in payload["records"]:
        if row.get("migration_state") == "QUARANTINED":
            skipped.append({"path": row["legacy_path"], "reason": row["next_action"]})
            continue
        source = ROOT / row["legacy_path"]
        target = ROOT / row["canonical_path"]
        if row["dirty_source"]:
            skipped.append({"path": row["legacy_path"], "reason": "dirty_source_held_back"})
            continue
        if not source.exists():
            skipped.append({"path": row["legacy_path"], "reason": "source_missing"})
            continue
        if target.exists():
            skipped.append({"path": row["legacy_path"], "reason": "target_exists"})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        before = sha256(source)
        shutil.move(str(source), str(target))
        after = sha256(target)
        applied.append({
            "legacy_path": row["legacy_path"],
            "canonical_path": row["canonical_path"],
            "sha256_before": before,
            "sha256_after": after,
            "hash_equal": before == after,
        })
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    TARGET_README.write_text(source_readme(), encoding="utf-8")
    LEGACY_README.parent.mkdir(parents=True, exist_ok=True)
    LEGACY_README.write_text(legacy_readme(), encoding="utf-8")
    REDIRECT_INDEX.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "artifact": "uet_core_source_package_redirects",
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "generator": GENERATOR,
                "canonical_root": "docs/core/06_data/source_packages",
                "raw_files_duplicated": False,
                "records": applied,
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    payload["summary"]["physical_move_performed"] = bool(applied)
    payload["summary"]["raw_hash_changes"] = sum(not item["hash_equal"] for item in applied)
    payload["summary"]["files_migrated_in_wave"] = len(applied)
    payload["summary"]["files_skipped_in_wave"] = len(skipped)
    for row in payload["records"]:
        matched = next((item for item in applied if item["legacy_path"] == row["legacy_path"]), None)
        skipped_item = next((item for item in skipped if item["path"] == row["legacy_path"]), None)
        if matched:
            row["migration_state"] = "MIGRATED"
            row["sha256_after"] = matched["sha256_after"]
            row["next_action"] = "verify_source_package_consumers"
        elif skipped_item:
            row["migration_state"] = "QUARANTINED"
            row["next_action"] = skipped_item["reason"]
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (GOVERNANCE / "UET_CORE_SOURCE_PACKAGE_MIGRATION_REPORT.md").write_text(render_report(payload), encoding="utf-8")
    return {"status": "PASS" if not skipped and payload["summary"]["raw_hash_changes"] == 0 else "PARTIAL", "applied": applied, "skipped": skipped}


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    for row in payload.get("records", []):
        target = ROOT / row["canonical_path"]
        if row.get("migration_state") == "MIGRATED":
            if not target.exists():
                failures.append(f"missing:{row['canonical_path']}")
            elif row.get("sha256_after") and sha256(target) != row["sha256_after"]:
                failures.append(f"hash:{row['canonical_path']}")
    return {"status": "PASS" if not failures else "BLOCKED", "files_checked": len(payload.get("records", [])), "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    remaining = [path for path in SOURCE_ROOT.rglob("*") if path.is_file() and path != LEGACY_README]
    if args.check and MANIFEST.exists() and not remaining:
        result = validate(json.loads(MANIFEST.read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    payload = build_plan()
    GOVERNANCE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (GOVERNANCE / "UET_CORE_SOURCE_PACKAGE_MIGRATION_REPORT.md").write_text(render_report(payload), encoding="utf-8")
    blocked = bool(payload["summary"]["duplicate_targets"] or payload["summary"]["existing_target_conflicts"])
    if args.apply:
        if blocked:
            print(json.dumps({"status": "BLOCKED", "summary": payload["summary"]}, ensure_ascii=False, indent=2))
            return 1
        result = apply(payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    print(json.dumps({"status": "BLOCKED" if blocked else "PASS", "manifest": repo_path(MANIFEST), "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
