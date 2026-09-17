"""Consolidate migrated compatibility files out of the visible core root.

The first migration waves moved the implementations but intentionally left
one wrapper per old path. This runner performs the next, explicit boundary:
root Python wrappers are archived and served by one lazy import registry;
Markdown redirects and legacy directory boundaries are moved to governance;
old active references are rewritten to canonical paths. No source equation,
physics status, or evidence class is changed.
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
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
GOVERNANCE = CORE / "00_governance"
ALIAS_REGISTRY = GOVERNANCE / "uet_core_legacy_module_aliases.json"
DATA_MANIFEST = GOVERNANCE / "uet_core_data_tooling_migration_manifest.json"
OUTPUT = GOVERNANCE / "uet_core_compatibility_consolidation_v4.json"
GENERATOR = "docs/scripts/audit/consolidate_uet_core_compatibility_v4.py"
PLANNER = ROOT / "docs/scripts/audit/plan_uet_core_physical_migration.py"

PROTECTED_ROOT = {"AGENTS.md", "README.md", "CORE_FILE_INDEX.md", "__init__.py", "core_paths.py", "core_compat.py"}
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".sh", ".yml", ".yaml", ".toml"}
OLD_BOUNDARY_ROOTS = (
    CORE / "data",
    CORE / "test",
    CORE / "02_Proof",
    CORE / "artifacts",
)
MODULE_PATTERN = re.compile(r'"(docs\.(?:core|scripts)\.[^"]+)"')
RUNPY_TARGET_PATTERN = re.compile(r'_CANONICAL_RELATIVE\s*=\s*["\']([^"\']+)["\']')
REDIRECT_PATTERN = re.compile(r"Canonical source:\s*\[[^\]]+\]\(([^)]+)\)")
LINK_PATTERN = re.compile(r"(?P<prefix>!?\[[^\]]*\]\()(?P<target>[^)\s]+)(?P<suffix>[^)]*\))")


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_utf8(path: Path, content: str) -> None:
    """Retry transient Windows file-sharing failures during a bulk rewrite."""

    for attempt in range(5):
        try:
            path.write_text(content, encoding="utf-8")
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.5)


def is_root_python_shim(path: Path) -> bool:
    return path.is_file() and path.parent == CORE and path.suffix == ".py" and path.name not in PROTECTED_ROOT


def module_target(path: Path) -> str | None:
    matches = MODULE_PATTERN.findall(path.read_text(encoding="utf-8"))
    return matches[-1] if matches else None


def runpy_target(path: Path) -> str | None:
    match = RUNPY_TARGET_PATTERN.search(path.read_text(encoding="utf-8"))
    return None if match is None else match.group(1).replace("\\", "/")


def canonical_from_redirect(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = REDIRECT_PATTERN.search(text)
    if match is None:
        return None
    link = match.group(1).strip()
    if link.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    if link.startswith("docs/"):
        candidate = ROOT / link
    else:
        candidate = (path.parent / link).resolve()
    try:
        return repo_path(candidate)
    except ValueError:
        return None


def relative_link(source: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start=source.parent)).as_posix()


def action_kind(path: Path) -> str:
    if is_root_python_shim(path):
        return "root_python_shim"
    if path.parent == CORE and path.suffix.lower() == ".md":
        return "root_markdown_redirect"
    if path.is_relative_to(CORE / "data" / "scripts") and path.suffix.lower() == ".py":
        return "legacy_tool_shim"
    if path.is_relative_to(CORE / "02_Proof") and path.suffix.lower() == ".py":
        return "legacy_proof_shim"
    return "legacy_boundary_redirect"


def archive_path(path: Path, kind: str) -> Path:
    if kind == "root_python_shim":
        return CORE / "08_history" / "legacy" / "compatibility_shims" / "python" / path.name
    if kind == "legacy_tool_shim":
        tail = path.relative_to(CORE / "data" / "scripts")
        return CORE / "08_history" / "legacy" / "compatibility_shims" / "data_scripts" / tail
    if kind == "legacy_proof_shim":
        tail = path.relative_to(CORE / "02_Proof")
        return CORE / "08_history" / "legacy" / "compatibility_shims" / "proofs" / tail
    if kind == "root_markdown_redirect":
        return GOVERNANCE / "redirects" / "root" / path.name
    tail = path.relative_to(CORE)
    return GOVERNANCE / "redirects" / "legacy" / tail


def target_for(path: Path, kind: str) -> str | None:
    if kind == "root_python_shim":
        target = module_target(path)
        return None if target is None else target.replace(".", "/") + ".py"
    if kind in {"legacy_tool_shim", "legacy_proof_shim"}:
        return runpy_target(path)
    if path.as_posix().endswith("docs/core/07_artifacts/README.md"):
        return "docs/core/07_artifacts/README.md"
    return canonical_from_redirect(path)


def collect_actions() -> tuple[list[dict[str, Any]], list[str]]:
    actions: list[dict[str, Any]] = []
    failures: list[str] = []
    candidates: list[Path] = []
    candidates.extend(sorted(CORE.glob("*.py")))
    candidates.extend(sorted(CORE.glob("*.md")))
    for base in OLD_BOUNDARY_ROOTS:
        if base.exists():
            candidates.extend(sorted(path for path in base.rglob("*") if path.is_file() and path.suffix.lower() != ".pyc"))

    seen: set[Path] = set()
    for path in candidates:
        path = path.resolve()
        if path in seen or not path.exists():
            continue
        seen.add(path)
        if path.parent == CORE and path.name in PROTECTED_ROOT:
            continue
        kind = action_kind(path)
        if kind == "legacy_boundary_redirect" and path.name != "README.md" and path.suffix.lower() != ".md":
            failures.append(repo_path(path))
            continue
        target = target_for(path, kind)
        if target is None or not (ROOT / target).exists():
            failures.append(f"{repo_path(path)} -> {target or '<unresolved>'}")
            continue
        destination = archive_path(path, kind)
        actions.append(
            {
                "legacy_path": repo_path(path),
                "canonical_path": target,
                "archive_path": repo_path(destination),
                "kind": kind,
                "sha256_before": sha256(path),
                "canonical_sha256": sha256(ROOT / target),
            }
        )

    destinations = Counter(item["archive_path"].lower() for item in actions)
    for destination, count in destinations.items():
        if count > 1:
            failures.append(f"duplicate archive target: {destination}")
    for item in actions:
        destination = ROOT / item["archive_path"]
        if destination.exists() and destination.resolve() != (ROOT / item["legacy_path"]).resolve():
            failures.append(f"archive target exists: {item['archive_path']}")
    return sorted(actions, key=lambda item: item["legacy_path"]), sorted(set(failures))


def redirect_content(destination: Path, legacy: str, target: Path, original: str) -> str:
    link = relative_link(destination, target)
    updated = REDIRECT_PATTERN.sub(
        lambda match: match.group(0)[: match.group(0).rfind("(") + 1] + link + ")",
        original,
        count=1,
    )
    if updated == original and "Canonical source:" not in original:
        updated = (
            "# Compatibility redirect\n\n"
            "> This legacy boundary is retained as an archive pointer.\n\n"
            f"Canonical source: [{repo_path(target)}]({link})\n\n"
            "Do not edit this file; update the canonical source instead.\n"
        )
    if not updated.startswith("# Compatibility redirect"):
        updated = "# Compatibility redirect\n\n" + updated
    if f"Legacy path: {legacy}" not in updated:
        updated = updated.rstrip() + f"\n\nLegacy path: {legacy}\n"
    return updated


def active_reference_files(actions: list[dict[str, Any]]) -> list[Path]:
    action_paths = {item["legacy_path"] for item in actions}
    paths: list[Path] = []
    candidates: list[Path] = []
    docs_root = ROOT / "docs"
    if docs_root.exists():
        candidates.extend(docs_root.rglob("*"))
    candidates.extend(
        path for path in (ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "CONTRIBUTING.md")
        if path.exists()
    )
    for path in candidates:
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = repo_path(path)
        if relative in action_paths:
            continue
        if any(part in {".git", "__pycache__", "07_artifacts", "08_history", "uet_history", "WORK_LEDGER"} for part in path.parts):
            continue
        paths.append(path)
    return sorted(paths)


def rewrite_active_references(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    old_to_target = {item["legacy_path"]: item["canonical_path"] for item in actions}
    old_abs_to_target = {
        (ROOT / old).resolve(): (ROOT / target).resolve()
        for old, target in old_to_target.items()
    }
    alias_map: dict[str, str] = {}
    if ALIAS_REGISTRY.exists():
        payload = json.loads(ALIAS_REGISTRY.read_text(encoding="utf-8"))
        for item in payload.get("aliases", []):
            legacy = item.get("legacy_module")
            canonical = item.get("canonical_module")
            if isinstance(legacy, str) and isinstance(canonical, str):
                alias_map[legacy] = canonical

    changes: list[dict[str, Any]] = []
    for path in active_reference_files(actions):
        before = path.read_text(encoding="utf-8")
        after = before

        def replace_link(match: re.Match[str]) -> str:
            target_text = match.group("target")
            if target_text.startswith(("http://", "https://", "mailto:", "data:", "#")):
                return match.group(0)
            candidate = (path.parent / target_text).resolve()
            mapped = old_abs_to_target.get(candidate)
            if mapped is None:
                return match.group(0)
            return match.group("prefix") + relative_link(path, mapped) + match.group("suffix")

        if path.suffix.lower() == ".md":
            after = LINK_PATTERN.sub(replace_link, after)
        for old, target in sorted(old_to_target.items(), key=lambda pair: len(pair[0]), reverse=True):
            after = after.replace(old, target).replace(old.replace("/", "\\"), target)
        for old_module, new_module in sorted(alias_map.items(), key=lambda pair: len(pair[0]), reverse=True):
            # Numeric folders are valid filesystem paths but not valid Python
            # syntax in from/import statements. Keep the legacy alias in
            # source code; importlib-based callers may use the canonical name.
            if new_module.startswith("docs.core.0"):
                continue
            after = re.sub(
                rf"(?<![A-Za-z0-9_.]){re.escape(old_module)}(?![A-Za-z0-9_])",
                new_module,
                after,
            )
        if after != before:
            write_utf8(path, after)
            changes.append(
                {
                    "path": repo_path(path),
                    "sha256_before": hashlib.sha256(before.encode("utf-8")).hexdigest(),
                    "sha256_after": hashlib.sha256(after.encode("utf-8")).hexdigest(),
                }
            )
    return changes


def update_data_manifest(actions: list[dict[str, Any]]) -> None:
    if not DATA_MANIFEST.exists():
        return
    payload = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
    by_legacy = {item["legacy_path"]: item for item in actions}
    for row in payload.get("records", []):
        action = by_legacy.get(row.get("legacy_path"))
        if action is None or not action["legacy_path"].startswith("docs/core/data/"):
            continue
        row["migration_state"] = "MIGRATED"
        row["compatibility_mode"] = (
            "archived_runpy_shim" if action["kind"] == "legacy_tool_shim" else "archived_redirect"
        )
        row["compatibility_archive_path"] = action["archive_path"]
        row["archive_sha256"] = sha256(ROOT / action["archive_path"])
        row["next_action"] = "use_canonical_tool_or_documentation_path"
        row["physical_compatibility_removed"] = True
    payload["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["generator"] = GENERATOR
    payload["legacy_compatibility_consolidated"] = True
    write_utf8(DATA_MANIFEST, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def prune_empty_legacy_directories() -> None:
    for base in OLD_BOUNDARY_ROOTS:
        if not base.exists():
            continue
        for cache in sorted(base.rglob("*.pyc")):
            try:
                cache.unlink()
            except OSError:
                pass
        directories = sorted((path for path in base.rglob("*") if path.is_dir()), key=lambda path: len(path.parts), reverse=True)
        # Remove children first, then the legacy root itself.
        for directory in [*directories, base]:
            try:
                if directory.exists() and not any(directory.iterdir()):
                    directory.rmdir()
            except OSError:
                pass


def apply(actions: list[dict[str, Any]], failures: list[str]) -> dict[str, Any]:
    if failures:
        raise RuntimeError(json.dumps({"status": "BLOCKED", "preflight_failures": failures}, ensure_ascii=False))
    reference_changes = rewrite_active_references(actions)
    applied: list[dict[str, Any]] = []
    for item in actions:
        source = ROOT / item["legacy_path"]
        destination = ROOT / item["archive_path"]
        target = ROOT / item["canonical_path"]
        original = source.read_text(encoding="utf-8") if source.suffix.lower() == ".md" else None
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        if original is not None:
            write_utf8(destination, redirect_content(destination, item["legacy_path"], target, original))
        applied.append(
            {
                **item,
                "sha256_after": sha256(destination),
                "status": "ARCHIVED_COMPATIBILITY",
            }
        )
    update_data_manifest(applied)
    prune_empty_legacy_directories()
    subprocess.run([sys.executable, str(PLANNER), "--plan"], cwd=ROOT, check=True)
    payload = {
        "schema_version": "1.0",
        "artifact": "uet_core_compatibility_consolidation",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "status": "PASS",
        "physical_move_performed": bool(applied),
        "physics_status_changes": 0,
        "summary": {
            "files_archived": len(applied),
            "root_python_shims_archived": sum(item["kind"] == "root_python_shim" for item in applied),
            "root_markdown_redirects_archived": sum(item["kind"] == "root_markdown_redirect" for item in applied),
            "legacy_tool_shims_archived": sum(item["kind"] == "legacy_tool_shim" for item in applied),
            "legacy_boundary_files_archived": sum(item["kind"] in {"legacy_boundary_redirect", "legacy_proof_shim"} for item in applied),
            "active_reference_files_rewritten": len(reference_changes),
            "physics_status_changes": 0,
        },
        "actions": applied,
        "reference_changes": reference_changes,
        "claim_boundary": "physical organization and compatibility consolidation only; no physics/evidence promotion",
    }
    write_utf8(OUTPUT, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run preflight without moving files")
    parser.add_argument("--apply", action="store_true", help="archive compatibility files and rewrite active references")
    args = parser.parse_args()
    if args.check and args.apply:
        parser.error("--check and --apply are mutually exclusive")
    actions, failures = collect_actions()
    if args.apply:
        payload = apply(actions, failures)
        print(json.dumps({"status": payload["status"], **payload["summary"]}, ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {
                "status": "PASS" if not failures else "BLOCKED",
                "files_selected": len(actions),
                "root_python_shims": sum(item["kind"] == "root_python_shim" for item in actions),
                "root_markdown_redirects": sum(item["kind"] == "root_markdown_redirect" for item in actions),
                "legacy_tool_shims": sum(item["kind"] == "legacy_tool_shim" for item in actions),
                "legacy_boundaries": sum(item["kind"] in {"legacy_boundary_redirect", "legacy_proof_shim"} for item in actions),
                "failures": failures,
            },
            ensure_ascii=False,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
