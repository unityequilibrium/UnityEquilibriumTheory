"""Build and apply the staged physical migration map for docs/core.

This tool owns organization metadata only. It never promotes a scientific
claim, edits a generated physics result, or changes a foundation gate.
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
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
GOVERNANCE = CORE / "00_governance"
MANIFEST_PATH = GOVERNANCE / "uet_core_physical_migration_manifest.json"
REPORT_PATH = GOVERNANCE / "UET_CORE_PHYSICAL_MIGRATION_REPORT.md"
sys.path.insert(0, str(ROOT))
from docs.core.core_paths import (  # noqa: E402
    PROTECTED_CORE_ROOT_FILES,
    canonical_module_name,
    canonical_path_for,
    is_markdown_redirect,
    is_python_shim,
    normalize_relative,
)


GENERATOR = "docs/scripts/audit/plan_uet_core_physical_migration.py"
EXCLUDED_PARTS = {"__pycache__", ".git"}


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def git_dirty_paths() -> set[str]:
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
    output: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        value = line[3:]
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        output.add(value.strip('"').replace("\\", "/"))
    return output


def existing_metadata() -> dict[str, dict[str, Any]]:
    manifest = load_json(
        ROOT / canonical_path_for("docs/core/07_artifacts/provenance/uet_core_file_manifest.json")
    )
    registry = load_json(
        ROOT / canonical_path_for("docs/core/07_artifacts/gates/uet_research_organization_registry.json")
    )
    merged: dict[str, dict[str, Any]] = {}
    for item in manifest.get("files", []):
        path = normalize_relative(item.get("path", ""))
        if path:
            merged[path] = dict(item)
    for item in registry.get("files", []):
        path = normalize_relative(item.get("path", item.get("current_path", "")))
        if path:
            merged.setdefault(path, {}).update(item)
    # Moved implementations retain the authoritative classification of their
    # legacy source while the canonical record becomes the active source of
    # truth.  This prevents every physical move from creating an unassigned
    # canonical record.
    for legacy, item in list(merged.items()):
        canonical = canonical_path_for(legacy)
        if canonical == legacy:
            continue
        target = merged.setdefault(canonical, {})
        for key, value in item.items():
            if key not in target or target[key] in (None, "", [], {}):
                target[key] = value
    return merged




def _organization_defaults(relative: str) -> dict[str, Any]:
    """Provide a conservative owner for newly created canonical support files."""

    tail = relative.removeprefix("docs/core/")
    parts = Path(tail).parts
    area = parts[0] if parts else "99_review"
    owner_by_area = {
        "00_governance": "ORG",
        "01_contracts": "FOUNDATION",
        "02_equations": "EQUATION",
        "03_lanes": "LANE",
        "04_proofs": "EVIDENCE",
        "05_tests": "EVIDENCE",
        "06_data": "DATA",
        "07_artifacts": "EVIDENCE",
        "08_history": "ORG",
        "99_review": "ORG",
    }
    owner = owner_by_area.get(area, "ORG")
    room_by_owner = {
        "ORG": "ROOM_CORE_ORGANIZATION",
        "FOUNDATION": "ROOM_CORE_FOUNDATION",
        "EQUATION": "ROOM_CORE_FOUNDATION",
        "LANE": "ROOM_CORE_FOUNDATION",
        "EVIDENCE": "ROOM_CORE_FOUNDATION",
        "DATA": "ROOM_CORE_FOUNDATION",
    }
    if area == "03_lanes" and len(parts) > 1 and parts[1] == "topic13_support":
        room_by_owner["LANE"] = "ROOM_TOPIC_013"
    if area == "05_tests":
        family = "core_test_surface"
    elif area == "02_equations" and len(parts) > 1:
        family = f"core.{parts[1]}"
    elif area == "03_lanes" and len(parts) > 1:
        family = f"lane.{parts[1]}"
    else:
        family = f"core_{area}"
    return {
        "logical_area": area,
        "owner_id": owner,
        "room_id": room_by_owner[owner],
        "equation_family_or_lane": family,
        "evidence_status": "INTERNAL",
        "status_source": "docs/core/00_governance/uet_research_organization_policy.json",
    }

def inferred_kind(relative: str, old: dict[str, Any]) -> str:
    if old.get("file_kind") and old.get("file_kind") not in {"compatibility_redirect", "compatibility_python_shim"}:
        return str(old["file_kind"])
    lower = relative.lower()
    if "/artifacts/" in lower:
        return "generated_artifact"
    if "/test/" in lower:
        return "verifier_or_regression_test"
    if "/data/" in lower:
        return "data_or_tooling"
    if lower.endswith(".py"):
        return "python_surface"
    if lower.endswith(".md"):
        return "documentation"
    return "unresolved_asset"


def wave_for(relative: str, canonical: str) -> str:
    if relative == canonical:
        return "already_canonical"
    lower = relative.lower()
    if lower.startswith("docs/core/data/scripts/") or lower.startswith("docs/core/data/"):
        return "data_tooling"
    if lower.startswith("docs/core/test/"):
        return "tests"
    if lower.startswith("docs/core/artifacts/"):
        return "artifacts"
    if lower.startswith("docs/core/02_proof/"):
        return "proofs"
    if relative.endswith(".py"):
        return "equation_or_lane"
    if relative.endswith(".md"):
        return "contracts_history"
    return "review"


def compatibility_for(relative: str, canonical: str) -> str:
    if relative == canonical:
        return "none"
    tail = relative.removeprefix("docs/core/")
    if relative.endswith(".py") and "/" not in tail:
        return "root_python_shim"
    if relative.endswith(".md"):
        return "markdown_redirect"
    if relative.startswith("docs/core/artifacts/"):
        return "legacy_artifact_index"
    return "path_resolver"


def build_records() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata = existing_metadata()
    dirty = git_dirty_paths()
    records: list[dict[str, Any]] = []
    for path in sorted(CORE.rglob("*")):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        relative = repo_path(path)
        redirect = is_markdown_redirect(path)
        shim = is_python_shim(path)
        compatibility = redirect or shim
        # A compatibility file is still indexed against the implementation it
        # forwards to.  Treating the shim itself as canonical creates a false
        # target collision as soon as a real source is moved beside it.
        canonical = canonical_path_for(relative)
        old = dict(metadata.get(relative, {}))
        defaults = _organization_defaults(relative)
        for key, value in defaults.items():
            if old.get(key) in (None, "", [], {}):
                old[key] = value
        records.append(
            {
                "asset_id": old.get(
                    "asset_id",
                    "UET-MIGRATION-" + hashlib.sha1(relative.encode()).hexdigest()[:12].upper(),
                ),
                "legacy_path": relative if relative != canonical else None,
                "current_path": relative,
                "canonical_path": canonical,
                "file_kind": (
                    "compatibility_redirect"
                    if redirect
                    else "compatibility_python_shim"
                    if shim
                    else inferred_kind(relative, old)
                ),
                "logical_area": old.get("logical_area"),
                "owner_id": old.get("owner_id"),
                "room_id": old.get("room_id"),
                "equation_family_or_lane": old.get("equation_family_or_lane"),
                "organization_status": "MIGRATED" if relative == canonical or compatibility else old.get("organization_status", "MIGRATION_READY"),
                "evidence_status": old.get("evidence_status"),
                "status_source": old.get("status_source"),
                "generated_or_source": old.get(
                    "generated_or_source",
                    "generated" if "/artifacts/" in relative else "source",
                ),
                "generator_path": old.get("generator"),
                "formula_ids": old.get("formula_ids", []),
                "verifier_paths": old.get("verifier_paths", []),
                "artifact_paths": old.get("artifact_paths", []),
                "upstream_dependencies": old.get("upstream_dependencies", []),
                "downstream_dependencies": old.get("downstream_dependencies", []),
                "sha256_before": sha256(path),
                "sha256_after": None,
                "collision_key": canonical.lower(),
                "rollback_path": relative,
                "migration_wave": "already_canonical" if compatibility else wave_for(relative, canonical),
                "migration_state": (
                    "MIGRATED_WITH_SHIM"
                    if compatibility and relative != canonical
                    else "MIGRATED"
                    if relative == canonical
                    else "NOT_STARTED"
                ),
                "compatibility_mode": "redirect_or_shim" if compatibility else compatibility_for(relative, canonical),
                "dirty_source": relative in dirty and not compatibility,
                "next_action": (
                    "retain_canonical_path"
                    if relative == canonical
                    else "retain_compatibility_shim"
                    if compatibility
                    else "resolve_preconditions_then_apply_staged_move"
                ),
            }
        )

    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        # A source and its declared compatibility shim intentionally share a
        # canonical target.  Only active source records participate in target
        # collision detection.
        if record["file_kind"] in {"compatibility_redirect", "compatibility_python_shim"}:
            continue
        by_target[record["collision_key"]].append(record)
    collisions = {
        key: [item["current_path"] for item in values]
        for key, values in by_target.items()
        if len(values) > 1
    }
    existing_conflicts = []
    for record in records:
        if record["file_kind"] in {"compatibility_redirect", "compatibility_python_shim"}:
            continue
        source = ROOT / record["current_path"]
        target = ROOT / record["canonical_path"]
        if source != target and target.exists():
            existing_conflicts.append(record["canonical_path"])
    compatibility_kinds = {"compatibility_redirect", "compatibility_python_shim"}
    active_records = [item for item in records if item["file_kind"] not in compatibility_kinds]
    compatibility_records = [item for item in records if item["file_kind"] in compatibility_kinds]
    summary = {
        "files_total": len(records),
        "files_to_move": sum(item["current_path"] != item["canonical_path"] for item in active_records),
        "already_canonical": sum(item["current_path"] == item["canonical_path"] for item in active_records) + len(compatibility_records),
        "dirty_sources": sum(item["dirty_source"] for item in records),
        "duplicate_targets": collisions,
        "existing_target_conflicts": sorted(set(existing_conflicts)),
        "migration_wave_counts": dict(Counter(item["migration_wave"] for item in records)),
        "compatibility_counts": dict(Counter(item["compatibility_mode"] for item in records)),
        "physics_status_changes": 0,
        "physical_move_performed": False,
        "physical_migration_complete": sum(item["current_path"] != item["canonical_path"] for item in active_records) == 0,
    }
    return records, summary


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# UET Core Physical Migration Report",
        "",
        "> Organization control-plane report. Physical migration does not promote physics evidence.",
        "",
        f"Generated at: {payload['generated_at']}",
        f"Generator: {payload['generator']}",
        "",
        "## Current control state",
        "",
        f"- Files indexed: **{summary['files_total']}**",
        f"- Files with a move target: **{summary['files_to_move']}**",
        f"- Already canonical/protected: **{summary['already_canonical']}**",
        f"- Dirty sources held back: **{summary['dirty_sources']}**",
        f"- Duplicate targets: **{len(summary['duplicate_targets'])}**",
        f"- Existing target conflicts: **{len(summary['existing_target_conflicts'])}**",
        f"- Physical migration complete: **{summary['physical_migration_complete']}**",
        f"- Physical move performed in this run: **{summary['physical_move_performed']}**",
        f"- Physics status changes: **{summary['physics_status_changes']}**",
        "",
        "## Migration waves",
        "",
        "| Wave | Files |",
        "| :-- | --: |",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in sorted(summary["migration_wave_counts"].items()))
    lines += [
        "",
        "## Safety rules",
        "",
        "- Duplicate canonical targets and existing destinations block apply.",
        "- Dirty user files are held back and never overwritten.",
        "- Root entrypoints and the public facade stay in place.",
        "- Python implementations live at numeric canonical paths; old imports use one lazy alias registry, and old Markdown paths use redirects.",
        "- Generated artifacts are canonicalized by a provenance-aware migration; generator/consumer validation remains a separate evidence gate.",
        "- Organization migration is not a scientific pass.",
        "",
    ]
    if summary["duplicate_targets"]:
        lines.extend(["## Blocking collisions", ""])
        for target, sources in sorted(summary["duplicate_targets"].items()):
            lines.append(f"- {target}: " + ", ".join(sources))
        lines.append("")
    return "\n".join(lines)


def write_plan() -> dict[str, Any]:
    prior = load_json(MANIFEST_PATH)
    records, summary = build_records()
    prior_summary = prior.get("summary", {})
    summary["files_migrated_in_wave"] = prior_summary.get("files_migrated_in_wave", 0)
    summary["files_skipped_in_wave"] = prior_summary.get("files_skipped_in_wave", 0)
    summary["compatibility_assets_present"] = sum(item["file_kind"] in {"compatibility_redirect", "compatibility_python_shim"} for item in records)
    payload = {
        "schema_version": "1.0",
        "migration_id": "UET-CORE-PHYSICAL-MIGRATION-V3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "all non-cache files currently under docs/core",
        "canonical_path_authority": "docs/core/core_paths.py",
        "physical_move_performed": False,
        "summary": summary,
        "records": records,
    }
    GOVERNANCE.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    return payload


def relative_link(source: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start=source.parent)).as_posix()


def redirect_text(old: Path, new: Path) -> str:
    target = relative_link(old, new)
    return (
        "# Compatibility redirect\n\n"
        "> This path is retained temporarily for compatibility.\n\n"
        f"Canonical source: [{new.relative_to(ROOT).as_posix()}]({target})\n\n"
        "Do not edit this file; update the canonical source instead.\n"
    )


def rewrite_moved_markdown(path: Path, old_relative: str, moved: dict[str, str]) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    old_parent = (ROOT / old_relative).parent
    pattern = re.compile(r"(?P<prefix>!?\[[^\]]*\]\()(?P<target>[^)#]+)(?P<suffix>\)?(?:#[^)]*)?)")

    def replace(match: re.Match[str]) -> str:
        target = match.group("target").strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "data:", "#")):
            return match.group(0)
        candidate = (old_parent / target).resolve()
        try:
            old_target = repo_path(candidate)
        except ValueError:
            return match.group(0)
        if old_target not in moved:
            return match.group(0)
        return match.group("prefix") + relative_link(path, ROOT / moved[old_target]) + match.group("suffix")

    updated = pattern.sub(replace, content)
    if updated != content:
        path.write_text(updated, encoding="utf-8")


def apply_contracts_history(payload: dict[str, Any]) -> dict[str, Any]:
    selected = [item for item in payload["records"] if item["migration_wave"] == "contracts_history"]
    keys = [item["collision_key"] for item in selected]
    if len(keys) != len(set(keys)):
        raise RuntimeError("contracts_history has duplicate canonical targets")
    moved: dict[str, str] = {}
    applied: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for item in selected:
        old = item["current_path"]
        new = item["canonical_path"]
        source = ROOT / old
        target = ROOT / new
        if item["dirty_source"]:
            skipped.append({"from": old, "reason": "dirty_source_held_back"})
            continue
        if not source.exists():
            skipped.append({"from": old, "reason": "source_missing"})
            continue
        if target.exists():
            skipped.append({"from": old, "reason": "target_exists"})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        moved[old] = new
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(redirect_text(source, target), encoding="utf-8")
        applied.append({"from": old, "to": new})
    for old, new in moved.items():
        rewrite_moved_markdown(ROOT / new, old, moved)
    refreshed = write_plan()
    refreshed["physical_move_performed"] = bool(applied)
    refreshed["summary"]["physical_move_performed"] = bool(applied)
    refreshed["summary"]["files_migrated_in_wave"] = len(applied)
    refreshed["summary"]["files_skipped_in_wave"] = len(skipped)
    refreshed["applied_wave"] = "contracts_history"
    refreshed["applied_moves"] = applied
    refreshed["skipped_moves"] = skipped
    MANIFEST_PATH.write_text(json.dumps(refreshed, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(refreshed), encoding="utf-8")
    return {"wave": "contracts_history", "applied": applied, "skipped": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="write the current migration manifest")
    parser.add_argument("--check", action="store_true", help="check target uniqueness and conflicts")
    parser.add_argument("--apply", action="store_true", help="apply the low-risk contracts/history wave")
    parser.add_argument("--wave", default="contracts_history")
    args = parser.parse_args()
    if args.apply:
        if args.wave.replace("-", "_") != "contracts_history":
            print(json.dumps({
                "status": "BLOCKED",
                "reason": "only contracts_history is enabled before consumer checkpoints",
                "requested_wave": args.wave,
            }, ensure_ascii=False))
            return 1
        payload = write_plan()
        summary = payload["summary"]
        if summary["duplicate_targets"] or summary["existing_target_conflicts"]:
            print(json.dumps({"status": "BLOCKED", "summary": summary}, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps(apply_contracts_history(payload), ensure_ascii=False, indent=2))
        return 0
    payload = write_plan()
    if args.check:
        ok = not payload["summary"]["duplicate_targets"] and not payload["summary"]["existing_target_conflicts"]
        print(json.dumps({"status": "PASS" if ok else "BLOCKED", "summary": payload["summary"]}, ensure_ascii=False, indent=2))
        return 0 if ok else 1
    print(json.dumps({
        "status": "PLAN_WRITTEN",
        "manifest": repo_path(MANIFEST_PATH),
        "report": repo_path(REPORT_PATH),
        "summary": payload["summary"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
