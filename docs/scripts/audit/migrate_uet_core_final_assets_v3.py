"""Migrate the two remaining non-artifact core assets with explicit records."""

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
GOVERNANCE = ROOT / "docs" / "core" / "00_governance"
OUTPUT = GOVERNANCE / "uet_core_final_assets_migration_v3.json"
PLANNER = ROOT / "docs/scripts/audit/plan_uet_core_physical_migration.py"
GENERATOR = "docs/scripts/audit/migrate_uet_core_final_assets_v3.py"
MAPPINGS = (
    ("docs/core/04_proofs/Proof_00_Master_Balance.py", "docs/core/04_proofs/Proof_00_Master_Balance.py", "python_shim"),
    ("docs/core/99_review/unresolved_assets/T13_HOLDOUT_EXPOSURE_2026_09_10.json", "docs/core/99_review/unresolved_assets/T13_HOLDOUT_EXPOSURE_2026_09_10.json", "none"),
)
TEXT_SUFFIXES = {".md", ".py", ".ps1", ".sh", ".yml", ".yaml", ".toml"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def excluded(path: Path) -> bool:
    rel = repo_path(path)
    return (
        "/07_artifacts/" in rel
        or "/08_history/" in rel
        or "/99_review/" in rel
        or "/Result/artifacts/" in rel
    )


def reference_files() -> list[Path]:
    paths: list[Path] = []
    for root in (ROOT / "docs", ROOT / "WORK_LEDGER", ROOT / "uet_history"):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not excluded(path):
                paths.append(path)
    for path in (ROOT / "README.md", ROOT / "AGENTS.md"):
        if path.exists():
            paths.append(path)
    return sorted(set(paths))


def build_preflight() -> dict[str, Any]:
    refs: list[dict[str, Any]] = []
    for source in reference_files():
        before = source.read_text(encoding="utf-8")
        after = before
        count = 0
        for legacy, canonical, _ in MAPPINGS:
            for token in (legacy, legacy.replace("/", "\\")):
                count += after.count(token)
                after = after.replace(token, canonical)
        if after != before:
            refs.append({"path": repo_path(source), "sha256_before": hashlib.sha256(before.encode()).hexdigest(), "sha256_after": hashlib.sha256(after.encode()).hexdigest(), "replacement_count": count, "text": after})
    moves = []
    conflicts = []
    missing = []
    for legacy, canonical, mode in MAPPINGS:
        source = ROOT / legacy
        target = ROOT / canonical
        if not source.exists():
            missing.append(legacy)
        if target.exists():
            conflicts.append(canonical)
        moves.append({"legacy_path": legacy, "canonical_path": canonical, "compatibility_mode": mode, "sha256_before": sha256(source) if source.exists() else None})
    return {"moves": moves, "references": refs, "missing": missing, "conflicts": conflicts}


def shim_text(canonical: str) -> str:
    return f'''"""Compatibility shim for the migrated proof path."""

from __future__ import annotations

import runpy
from pathlib import Path

_CANONICAL_RELATIVE = "{canonical}"


def _run() -> None:
    current = Path(__file__).resolve()
    for ancestor in (current.parent, *current.parents):
        candidate = ancestor / _CANONICAL_RELATIVE
        if candidate.exists():
            runpy.run_path(str(candidate), run_name="__main__")
            return
    raise FileNotFoundError(_CANONICAL_RELATIVE)


if __name__ == "__main__":
    _run()
'''


def apply(preflight: dict[str, Any]) -> dict[str, Any]:
    if preflight["missing"] or preflight["conflicts"]:
        raise RuntimeError(json.dumps({"missing": preflight["missing"], "conflicts": preflight["conflicts"]}))
    for item in preflight["references"]:
        (ROOT / item["path"]).write_text(item["text"], encoding="utf-8")
    applied: list[dict[str, Any]] = []
    for item in preflight["moves"]:
        source = ROOT / item["legacy_path"]
        target = ROOT / item["canonical_path"]
        before = sha256(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        after = sha256(target)
        if after != before:
            raise RuntimeError(f"hash changed during move: {item['legacy_path']}")
        if item["compatibility_mode"] == "python_shim":
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(shim_text(item["canonical_path"]), encoding="utf-8")
        applied.append({**item, "sha256_before": before, "sha256_after": after})
    subprocess.run([sys.executable, str(PLANNER), "--plan"], cwd=ROOT, check=True)
    payload = {
        "schema_version": "1.0",
        "artifact": "uet_core_final_assets_migration_v3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "status": "PASS",
        "physical_move_performed": bool(applied),
        "physics_status_changes": 0,
        "summary": {"files_selected": len(MAPPINGS), "files_moved": len(applied), "reference_files_changed": len(preflight["references"]), "reference_replacements": sum(item["replacement_count"] for item in preflight["references"]), "python_shims_created": sum(item["compatibility_mode"] == "python_shim" for item in applied), "physics_status_changes": 0},
        "moves": applied,
        "reference_changes": [{key: value for key, value in item.items() if key != "text"} for item in preflight["references"]],
        "claim_boundary": "physical organization and compatibility only; no physics/evidence promotion",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.check and args.apply:
        parser.error("--check and --apply are mutually exclusive")
    preflight = build_preflight()
    if args.apply:
        payload = apply(preflight)
        print(json.dumps({"status": payload["status"], **payload["summary"]}, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"status": "PASS" if not preflight["missing"] and not preflight["conflicts"] else "BLOCKED", "files_selected": len(preflight["moves"]), "reference_files_to_rewrite": len(preflight["references"]), "reference_replacements": sum(item["replacement_count"] for item in preflight["references"]), "missing": preflight["missing"], "conflicts": preflight["conflicts"]}, ensure_ascii=False, indent=2))
    return 0 if not preflight["missing"] and not preflight["conflicts"] else 1


if __name__ == "__main__":
    raise SystemExit(main())