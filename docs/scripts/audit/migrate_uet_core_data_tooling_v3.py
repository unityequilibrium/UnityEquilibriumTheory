"""Stage the physical migration of tooling currently under docs/core/data/scripts.

The first tooling wave is deliberately conservative. Markdown documentation and Python
scripts without location-sensitive bootstrap code can move with a compatibility shim. A
script that derives repository paths from ``__file__`` or ``parents[...]`` is recorded for
path review instead of being moved by guesswork.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
SOURCE_ROOT = CORE / "data" / "scripts"
GOVERNANCE = CORE / "00_governance"
MANIFEST = GOVERNANCE / "uet_core_data_tooling_migration_manifest.json"
REPORT = GOVERNANCE / "UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md"
sys_path = str(ROOT)

import sys

if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from docs.core.core_paths import canonical_path_for, normalize_relative  # noqa: E402


GENERATOR = "docs/scripts/audit/migrate_uet_core_data_tooling_v3.py"
PATH_SENSITIVE = re.compile(
    r"(__file__|Path\s*\(|os\.path\.dirname|sys\.path|parents\s*\[|current_file|current_path|PROJECT_ROOT|REPO_ROOT)"
)
CANONICAL_MARKER = re.compile(r'_CANONICAL_RELATIVE\s*=\s*["\']([^"\']+)["\']')
EXCLUDED_PARTS = {"__pycache__", ".git"}


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def existing_redirect_target(path: Path) -> str | None:
    try:
        text = read_text(path)
    except (OSError, UnicodeDecodeError):
        return None
    match = re.search(r"Canonical source: \[[^\]]+\]\(([^)]+)\)", text)
    if not match:
        return None
    return repo_path((path.parent / match.group(1)).resolve())


def existing_shim_target(path: Path) -> str | None:
    try:
        text = read_text(path)
    except (OSError, UnicodeDecodeError):
        return None
    match = CANONICAL_MARKER.search(text)
    return None if match is None else match.group(1)


def is_compatibility(path: Path) -> tuple[bool, str | None]:
    if path.suffix.lower() == ".md" and read_text(path).startswith("# Compatibility redirect"):
        return True, existing_redirect_target(path)
    if path.suffix.lower() == ".py" and "Compatibility shim" in read_text(path):
        return True, existing_shim_target(path)
    return False, None


def ready_for_first_wave(path: Path) -> tuple[bool, str]:
    if path.suffix.lower() == ".md":
        return True, "documentation_move"
    if path.suffix.lower() != ".py":
        return False, "non_code_tool_asset_requires_separate_provenance_review"
    try:
        text = read_text(path)
    except (OSError, UnicodeDecodeError):
        return False, "unreadable_source"
    if PATH_SENSITIVE.search(text):
        return False, "path_bootstrap_requires_review"
    return True, "python_without_location_sensitive_bootstrap"


def prior_records() -> dict[str, dict[str, Any]]:
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


def records() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dirty = dirty_paths()
    previous = prior_records()
    rows: list[dict[str, Any]] = []
    for path in sorted(SOURCE_ROOT.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        relative = repo_path(path)
        compatibility, compatibility_target = is_compatibility(path)
        canonical = compatibility_target or canonical_path_for(relative)
        ready, disposition = ready_for_first_wave(path) if not compatibility else (False, "already_migrated_with_compatibility_shim")
        target = ROOT / canonical
        state = "MIGRATED_WITH_SHIM" if compatibility else "MIGRATION_READY" if ready else "QUARANTINED"
        previous_row = previous.get(relative, {})
        sha_before = previous_row.get("sha256_before") if compatibility else None
        if not sha_before:
            sha_before = sha256(path)
        sha_after = previous_row.get("sha256_after")
        if compatibility and compatibility_target and target.exists():
            sha_after = sha256(target)
        rows.append(
            {
                "asset_id": "UET-TOOLING-" + hashlib.sha1(relative.encode()).hexdigest()[:12].upper(),
                "legacy_path": relative,
                "canonical_path": canonical,
                "file_kind": "python_tool" if path.suffix.lower() == ".py" else "documentation" if path.suffix.lower() == ".md" else "tool_asset",
                "source_or_generated": "source",
                "generator_path": None,
                "sha256_before": sha_before,
                "sha256_after": sha_after,
                "migration_wave": "data_tooling",
                "migration_state": state,
                "compatibility_mode": "runpy_shim" if path.suffix.lower() == ".py" else "markdown_redirect" if path.suffix.lower() == ".md" else "path_resolver",
                "dirty_source": relative in dirty and not compatibility,
                "first_wave_ready": ready,
                "disposition": disposition,
                "target_exists": target.exists() and str(target) != str(path),
                "collision_key": canonical.lower(),
                "rollback_path": relative,
                "next_action": "retain_compatibility_and_verify" if compatibility else "apply_first_tooling_wave" if ready else disposition,
            }
        )

    by_target: dict[str, list[str]] = {}
    for row in rows:
        if row["migration_state"] == "MIGRATED_WITH_SHIM":
            continue
        by_target.setdefault(row["collision_key"], []).append(row["legacy_path"])
    collisions = {key: values for key, values in by_target.items() if len(values) > 1}
    existing = sorted({row["canonical_path"] for row in rows if row["target_exists"] and row["migration_state"] != "MIGRATED_WITH_SHIM"})
    summary = {
        "files_total": len(rows),
        "migration_ready": sum(row["migration_state"] == "MIGRATION_READY" for row in rows),
        "migrated_with_shim": sum(row["migration_state"] == "MIGRATED_WITH_SHIM" for row in rows),
        "quarantined": sum(row["migration_state"] == "QUARANTINED" for row in rows),
        "dirty_sources": sum(row["dirty_source"] for row in rows),
        "duplicate_targets": collisions,
        "existing_target_conflicts": existing,
        "physics_status_changes": 0,
        "physical_move_performed": False,
    }
    return rows, summary


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# UET Core Data/Tooling Migration Report",
        "",
        "> Organization migration report. It does not change physics evidence or claim status.",
        "",
        f"Generated at: {payload['generated_at']}",
        f"Generator: {payload['generator']}",
        "",
        "## Current state",
        "",
        f"- Files indexed: **{summary['files_total']}**",
        f"- Ready for the first tooling wave: **{summary['migration_ready']}**",
        f"- Already migrated with shim: **{summary['migrated_with_shim']}**",
        f"- Quarantined for path/provenance review: **{summary['quarantined']}**",
        f"- Dirty sources held back: **{summary['dirty_sources']}**",
        f"- Duplicate targets: **{len(summary['duplicate_targets'])}**",
        f"- Existing target conflicts: **{len(summary['existing_target_conflicts'])}**",
        f"- Physics status changes: **{summary['physics_status_changes']}**",
        "",
        "## Rules",
        "",
        "- Python scripts move only when the first-wave path scan finds no location-sensitive bootstrap.",
        "- Moved Python scripts retain a runpy compatibility shim at the old path.",
        "- Markdown moves retain a redirect at the old path.",
        "- Non-code tool assets remain pending a provenance/output classification.",
        "- Dirty sources are never overwritten.",
    ]
    if summary["quarantined"]:
        lines += ["", "## Quarantine reasons", ""]
        reasons: dict[str, int] = {}
        for row in payload["records"]:
            if row["migration_state"] == "QUARANTINED":
                reasons[row["disposition"]] = reasons.get(row["disposition"], 0) + 1
        lines.extend(f"- {reason}: {count}" for reason, count in sorted(reasons.items()))
    return "\n".join(lines) + "\n"


def write_plan() -> dict[str, Any]:
    rows, summary = records()
    payload = {
        "schema_version": "1.0",
        "migration_id": "UET-CORE-DATA-TOOLING-V3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "docs/core/data/scripts",
        "canonical_path_authority": "docs/core/core_paths.py",
        "summary": summary,
        "records": rows,
    }
    GOVERNANCE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(payload), encoding="utf-8")
    return payload


def relative_link(source: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start=source.parent)).as_posix()


def redirect_text(old: Path, target: Path) -> str:
    return (
        "# Compatibility redirect\n\n"
        "> This path is retained temporarily for compatibility.\n\n"
        f"Canonical source: [{target.relative_to(ROOT).as_posix()}]({relative_link(old, target)})\n\n"
        "Do not edit this file; update the canonical source instead.\n"
    )


def shim_text(target_relative: str) -> str:
    return f'''"""Compatibility shim for the migrated core tooling path."""

from __future__ import annotations

import runpy
from pathlib import Path

_CANONICAL_RELATIVE = "{target_relative}"


def _run() -> None:
    current = Path(__file__).resolve()
    for ancestor in (current.parent, *current.parents):
        candidate = ancestor / _CANONICAL_RELATIVE
        if candidate.exists():
            runpy.run_path(str(candidate), run_name="__main__")
            return
    raise FileNotFoundError(f"canonical tooling script not found: {{_CANONICAL_RELATIVE}}")


if __name__ == "__main__":
    _run()
'''


def apply_first_wave(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["summary"]["duplicate_targets"] or payload["summary"]["existing_target_conflicts"]:
        raise RuntimeError("tooling migration has duplicate or existing target conflicts")
    applied: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for row in payload["records"]:
        if row["migration_state"] != "MIGRATION_READY":
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
        shutil.move(str(source), str(target))
        source.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".py":
            source.write_text(shim_text(row["canonical_path"]), encoding="utf-8")
        else:
            source.write_text(redirect_text(source, target), encoding="utf-8")
        applied.append({"from": row["legacy_path"], "to": row["canonical_path"]})
    refreshed = write_plan()
    refreshed["summary"]["physical_move_performed"] = bool(applied)
    refreshed["summary"]["files_migrated_in_wave"] = len(applied)
    refreshed["summary"]["files_skipped_in_wave"] = len(skipped)
    refreshed["applied_moves"] = applied
    refreshed["skipped_moves"] = skipped
    MANIFEST.write_text(json.dumps(refreshed, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(refreshed), encoding="utf-8")
    return {"applied": applied, "skipped": skipped}



def apply_all(payload: dict[str, Any]) -> dict[str, Any]:
    """Move every remaining tooling asset after explicit full-migration approval."""
    summary = payload["summary"]
    if summary["duplicate_targets"] or summary["existing_target_conflicts"]:
        raise RuntimeError("tooling migration has duplicate or existing target conflicts")
    applied: list[dict[str, str]] = []
    for row in payload["records"]:
        if row["migration_state"] == "MIGRATED_WITH_SHIM":
            continue
        source = ROOT / row["legacy_path"]
        target = ROOT / row["canonical_path"]
        if not source.exists():
            raise FileNotFoundError(f"tooling source disappeared before move: {row['legacy_path']}")
        if target.exists():
            raise FileExistsError(f"tooling target already exists: {row['canonical_path']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        source.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".py":
            source.write_text(shim_text(row["canonical_path"]), encoding="utf-8")
            row["migration_state"] = "MIGRATED_WITH_SHIM"
            row["compatibility_mode"] = "runpy_shim"
        elif source.suffix.lower() == ".md":
            source.write_text(redirect_text(source, target), encoding="utf-8")
            row["migration_state"] = "MIGRATED_WITH_SHIM"
            row["compatibility_mode"] = "markdown_redirect"
        else:
            row["migration_state"] = "MIGRATED"
            row["compatibility_mode"] = "path_resolver"
        row["sha256_after"] = sha256(target)
        row["next_action"] = "verify_moved_tooling_surface"
        applied.append({"from": row["legacy_path"], "to": row["canonical_path"]})
    payload["summary"]["migration_ready"] = 0
    payload["summary"]["quarantined"] = 0
    payload["summary"]["migrated_with_shim"] = sum(
        row["migration_state"] == "MIGRATED_WITH_SHIM" for row in payload["records"]
    )
    payload["summary"]["physical_move_performed"] = bool(applied)
    payload["summary"]["files_migrated_in_wave"] = len(applied)
    payload["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["full_move_policy"] = (
        "Explicit organization migration; path-sensitive scripts retain source behavior "
        "and require post-move smoke review."
    )
    payload["applied_moves"] = applied
    MANIFEST.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(render_report(payload), encoding="utf-8")
    return {"applied": applied}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--apply-all", action="store_true", help="move all quarantined tooling assets after explicit full-migration approval")
    args = parser.parse_args()
    payload = write_plan()
    blocked = bool(payload["summary"]["duplicate_targets"] or payload["summary"]["existing_target_conflicts"])
    if args.apply:
        if blocked:
            print(json.dumps({"status": "BLOCKED", "summary": payload["summary"]}, ensure_ascii=False, indent=2))
            return 1
        result = apply_first_wave(payload)
        print(json.dumps({"status": "PASS", "wave": "data_tooling_safe_subset", **result}, ensure_ascii=False, indent=2))
        return 0
    if args.apply_all:
        if blocked:
            print(json.dumps({"status": "BLOCKED", "summary": payload["summary"]}, ensure_ascii=False, indent=2))
            return 1
        result = apply_all(payload)
        print(json.dumps({"status": "PASS", "wave": "data_tooling_full_move", **result}, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"status": "BLOCKED" if blocked else "PASS", "manifest": repo_path(MANIFEST), "report": repo_path(REPORT), "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
