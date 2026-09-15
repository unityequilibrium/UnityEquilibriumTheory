"""Move one root-level UET Python family to its canonical package safely.

This migration utility is intentionally structural.  It preserves a legacy
root import as a thin compatibility shim and records hashes for every moved
implementation.  It refuses to guess how to rewrite relative imports, move a
dirty source, or overwrite an existing canonical destination.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
GOVERNANCE = CORE / "00_governance"
PHYSICAL_MANIFEST = GOVERNANCE / "uet_core_physical_migration_manifest.json"
HISTORY_PATH = GOVERNANCE / "uet_core_python_family_migration_history.json"
PLANNER = ROOT / "docs" / "scripts" / "audit" / "plan_uet_core_physical_migration.py"
GENERATOR = "docs/scripts/audit/migrate_uet_core_python_family_v3.py"
COMPATIBILITY_KINDS = {"compatibility_python_shim", "compatibility_redirect"}
SAFE_FAMILY = re.compile(r"^[a-z0-9_]+$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def dirty_paths() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        value = line[3:]
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        output.add(value.strip('"').replace("\\", "/"))
    return output


def load_manifest() -> dict[str, Any]:
    if not PHYSICAL_MANIFEST.exists():
        raise FileNotFoundError(
            "physical migration manifest is missing; run the physical planner first"
        )
    return json.loads(PHYSICAL_MANIFEST.read_text(encoding="utf-8"))


def canonical_module_name(path: str) -> str:
    if not path.endswith(".py"):
        raise ValueError(f"not a Python module: {path}")
    return path[:-3].replace("/", ".")


def shim_text(canonical_path: str) -> str:
    module_name = canonical_module_name(canonical_path)
    return f'''"""Compatibility shim for `{canonical_path}`."""

from __future__ import annotations

if __package__:
    from .core_compat import forward_public_symbols as _forward_public_symbols
else:
    import sys as _sys
    from pathlib import Path as _Path

    _current = _Path(__file__).resolve()
    for _parent in (_current, *_current.parents):
        if (_parent / "docs" / "core").is_dir():
            _sys.path.insert(0, str(_parent))
            break
    from docs.core.core_compat import forward_public_symbols as _forward_public_symbols
    del _sys, _Path, _current, _parent

_forward_public_symbols(globals(), "{module_name}")
del _forward_public_symbols
'''


def relative_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            values.append("." * node.level + (node.module or ""))
    return values


def build_plan(target_prefix: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dirty = dirty_paths()
    manifest = load_manifest()
    prefix = target_prefix.rstrip("/") + "/"
    records: list[dict[str, Any]] = []
    for row in manifest.get("records", []):
        current = str(row.get("current_path", ""))
        canonical = str(row.get("canonical_path", ""))
        if not canonical.startswith(prefix):
            continue
        if current == canonical or row.get("file_kind") in COMPATIBILITY_KINDS:
            continue
        if not current.startswith("docs/core/") or current.count("/") != 2:
            continue
        if not current.endswith(".py") or not canonical.endswith(".py"):
            continue
        source = ROOT / current
        target = ROOT / canonical
        imports = relative_imports(source) if source.exists() else ["source_missing"]
        records.append(
            {
                "legacy_path": current,
                "canonical_path": canonical,
                "sha256_before": sha256(source) if source.exists() else None,
                "dirty_source": current in dirty,
                "relative_imports": imports,
                "target_exists": target.exists(),
                "rollback_path": current,
            }
        )
    records.sort(key=lambda item: item["legacy_path"])
    by_target: dict[str, list[str]] = {}
    for record in records:
        by_target.setdefault(record["canonical_path"].lower(), []).append(record["legacy_path"])
    collisions = {key: paths for key, paths in by_target.items() if len(paths) > 1}
    summary = {
        "files_selected": len(records),
        "dirty_sources": sum(bool(item["dirty_source"]) for item in records),
        "relative_import_blocks": {
            item["legacy_path"]: item["relative_imports"]
            for item in records
            if item["relative_imports"]
        },
        "existing_target_conflicts": [
            item["canonical_path"] for item in records if item["target_exists"]
        ],
        "duplicate_targets": collisions,
    }
    summary["ready"] = not any(
        (
            summary["dirty_sources"],
            summary["relative_import_blocks"],
            summary["existing_target_conflicts"],
            summary["duplicate_targets"],
        )
    )
    return records, summary


def load_history() -> dict[str, Any]:
    if not HISTORY_PATH.exists():
        return {"schema_version": "1.0", "artifact": "uet_core_python_family_migration_history", "events": []}
    return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))


def refresh_physical_manifest() -> None:
    subprocess.run([sys.executable, str(PLANNER), "--plan"], cwd=ROOT, check=True)


def apply(target_prefix: str, family: str) -> dict[str, Any]:
    records, summary = build_plan(target_prefix)
    if not summary["ready"]:
        raise RuntimeError(json.dumps({"status": "BLOCKED", "summary": summary}, ensure_ascii=False))
    moved: list[dict[str, str]] = []
    try:
        for record in records:
            source = ROOT / record["legacy_path"]
            target = ROOT / record["canonical_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            source.write_text(shim_text(record["canonical_path"]), encoding="utf-8")
            after = sha256(target)
            if after != record["sha256_before"]:
                raise RuntimeError(f"hash mismatch after move: {record['legacy_path']}")
            moved.append(
                {
                    "legacy_path": record["legacy_path"],
                    "canonical_path": record["canonical_path"],
                    "sha256_before": record["sha256_before"],
                    "sha256_after": after,
                }
            )
    except Exception:
        # Every moved implementation remains recoverable from the just-created
        # shim.  Stop immediately rather than attempting an unverified bulk
        # rollback that could overwrite a user's intervening edit.
        raise

    refresh_physical_manifest()
    history = load_history()
    history.setdefault("events", []).append(
        {
            "family": family,
            "target_prefix": target_prefix,
            "generator": GENERATOR,
            "applied_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "MIGRATED_WITH_SHIM",
            "files_moved": len(moved),
            "moves": moved,
            "claim_boundary": "Organization migration only; no physics status or claim changed.",
        }
    )
    HISTORY_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"status": "PASS", "family": family, "files_moved": len(moved), "moves": moved}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True, help="stable family label for migration history")
    parser.add_argument("--target-prefix", required=True, help="canonical package directory under docs/core")
    parser.add_argument("--check", action="store_true", help="validate one family without moving it")
    parser.add_argument("--apply", action="store_true", help="perform the checked migration")
    args = parser.parse_args()
    if not SAFE_FAMILY.fullmatch(args.family):
        parser.error("family must contain only lowercase letters, digits, and underscores")
    prefix = args.target_prefix.replace("\\", "/").rstrip("/")
    if not prefix.startswith(("docs/core/02_equations/", "docs/core/03_lanes/")):
        parser.error("target-prefix must be an equation or lane package under docs/core")
    if args.apply:
        print(json.dumps(apply(prefix, args.family), ensure_ascii=False, indent=2))
        return 0
    records, summary = build_plan(prefix)
    print(json.dumps({"status": "PASS" if summary["ready"] else "BLOCKED", "family": args.family, "target_prefix": prefix, "summary": summary, "records": records}, ensure_ascii=False, indent=2))
    return 0 if summary["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
