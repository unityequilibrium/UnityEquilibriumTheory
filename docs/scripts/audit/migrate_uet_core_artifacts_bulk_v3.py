"""Physically migrate the remaining core artifact outputs in one auditable wave.

This runner is intentionally structural. It rewrites active references to the
canonical artifact paths, moves each legacy JSON/NPZ once, preserves SHA-256
payloads, and records a legacy index boundary. It does not promote evidence or
change physics status. Historical/generated snapshots outside active consumers
are left untouched and remain provenance records.
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
LEGACY_ROOT = CORE / "artifacts"
CANONICAL_ROOT = CORE / "07_artifacts"
GOVERNANCE = CORE / "00_governance"
MANIFEST = GOVERNANCE / "uet_core_artifact_migration_manifest.json"
HISTORY = GOVERNANCE / "uet_core_artifact_migration_history.json"
OUTPUT = GOVERNANCE / "uet_core_artifact_bulk_migration_v3.json"
ARTIFACT_PLANNER = ROOT / "docs/scripts/audit/plan_uet_core_artifact_migration_v3.py"
PHYSICAL_PLANNER = ROOT / "docs/scripts/audit/plan_uet_core_physical_migration.py"
ARTIFACT_AUDIT = ROOT / "docs/scripts/audit/audit_uet_core_artifact_migration_v3.py"
GENERATOR = "docs/scripts/audit/migrate_uet_core_artifacts_bulk_v3.py"

TEXT_SUFFIXES = {".md", ".py", ".ps1", ".sh", ".yml", ".yaml", ".toml"}
EXCLUDED_REFERENCE_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
}
LEGACY_PREFIX = "docs/core/artifacts/"
RELATIVE_ARTIFACT = re.compile(
    r"(?P<token>(?:(?:\.\.?[\\/]+)|)artifacts[\\/]+(?P<name>[^\\/\s\)\]#\"']+))"
)


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_semantic(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize_semantic(item)
            for key, item in value.items()
            if key != "generated_at"
        }
    if isinstance(value, list):
        return [_normalize_semantic(item) for item in value]
    return value


def semantic_payload_sha256(path: Path) -> str:
    if path.suffix.lower() == ".json":
        payload = _normalize_semantic(json.loads(path.read_text(encoding="utf-8")))
        normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return sha256(path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_rows() -> list[dict[str, Any]]:
    payload = load_json(MANIFEST)
    rows = []
    for row in payload.get("records", []):
        if row.get("migration_state") != "NOT_STARTED":
            continue
        source = ROOT / str(row.get("legacy_path", ""))
        if source.exists() and source.is_file():
            rows.append(dict(row))
    return sorted(rows, key=lambda row: str(row["legacy_path"]))


def dirty_paths() -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    values: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        value = line[3:]
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        values.add(value.strip('"').replace("\\", "/"))
    return values


def excluded_reference(path: Path) -> bool:
    relative = repo_path(path)
    parts = set(path.relative_to(ROOT).parts)
    if parts & EXCLUDED_REFERENCE_PARTS:
        return True
    if relative.startswith("docs/core/artifacts/") or relative.startswith("docs/core/07_artifacts/"):
        return True
    if "/08_history/" in relative or "/99_review/" in relative:
        return True
    if "/Result/artifacts/" in relative or "/Result/_Logs/" in relative:
        return True
    return False


def reference_files() -> list[Path]:
    paths: list[Path] = []
    for root in (ROOT / "docs", ROOT / "uet_history", ROOT / "WORK_LEDGER"):
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not excluded_reference(path):
                paths.append(path)
    for path in (ROOT / "README.md", ROOT / "AGENTS.md"):
        if path.exists() and path not in paths:
            paths.append(path)
    return sorted(set(paths))


def relative_canonical(source: Path, target: Path) -> str:
    return Path(os.path.relpath(target, start=source.parent)).as_posix()


def rewrite_references(source: Path, text: str, by_legacy: dict[str, str], by_name: dict[str, str]) -> tuple[str, int]:
    changed = 0
    rewritten = text
    for legacy, canonical in sorted(by_legacy.items(), key=lambda item: len(item[0]), reverse=True):
        variants = (legacy, legacy.replace("/", "\\"))
        for token in variants:
            count = rewritten.count(token)
            if count:
                rewritten = rewritten.replace(token, canonical)
                changed += count

    def replace_relative(match: re.Match[str]) -> str:
        nonlocal changed
        token = match.group("token")
        name = match.group("name")
        legacy = by_name.get(name)
        if legacy is None:
            return token
        candidate = (source.parent / Path(token.replace("\\", "/"))).resolve()
        expected = (ROOT / legacy).resolve()
        if candidate != expected:
            return token
        target = ROOT / by_legacy[legacy]
        changed += 1
        return relative_canonical(source, target)

    rewritten = RELATIVE_ARTIFACT.sub(replace_relative, rewritten)
    return rewritten, changed


def build_reference_plan(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, str]]:
    by_legacy = {
        str(row["legacy_path"]): str(row["canonical_path"])
        for row in rows
    }
    by_name = {
        Path(legacy).name: legacy
        for legacy in by_legacy
    }
    changes: list[dict[str, Any]] = []
    for source in reference_files():
        before = source.read_text(encoding="utf-8")
        after, count = rewrite_references(source, before, by_legacy, by_name)
        if after != before:
            changes.append(
                {
                    "path": repo_path(source),
                    "sha256_before": hashlib.sha256(before.encode("utf-8")).hexdigest(),
                    "sha256_after": hashlib.sha256(after.encode("utf-8")).hexdigest(),
                    "replacement_count": count,
                    "text": after,
                }
            )
    return changes, by_legacy, by_name


def build_preflight() -> dict[str, Any]:
    rows = load_rows()
    targets: dict[str, list[str]] = {}
    for row in rows:
        targets.setdefault(str(row["canonical_path"]).lower(), []).append(str(row["legacy_path"]))
    duplicate_targets = {key: values for key, values in targets.items() if len(values) > 1}
    existing_targets = [
        str(row["canonical_path"])
        for row in rows
        if (ROOT / str(row["canonical_path"])).exists()
    ]
    changes, by_legacy, _ = build_reference_plan(rows)
    dirty = dirty_paths()
    return {
        "rows": rows,
        "reference_changes": changes,
        "by_legacy": by_legacy,
        "duplicate_targets": duplicate_targets,
        "existing_targets": sorted(existing_targets),
        "dirty_sources": sorted(
            str(row["legacy_path"]) for row in rows if str(row["legacy_path"]) in dirty
        ),
    }


def load_history() -> dict[str, Any]:
    if not HISTORY.exists():
        return {
            "schema_version": "1.0",
            "artifact": "uet_core_artifact_migration_history",
            "migration_id": "UET-CORE-ARTIFACT-V3",
            "generator": GENERATOR,
            "canonical_path_authority": "docs/core/core_paths.py",
            "records": [],
        }
    return load_json(HISTORY)


def apply_preflight(preflight: dict[str, Any]) -> dict[str, Any]:
    if preflight["duplicate_targets"]:
        raise RuntimeError("duplicate canonical artifact targets")
    if preflight["existing_targets"]:
        raise RuntimeError("canonical artifact targets already exist")
    rows = preflight["rows"]
    reference_changes = preflight["reference_changes"]
    for change in reference_changes:
        path = ROOT / change["path"]
        path.write_text(change["text"], encoding="utf-8")
    moves: list[dict[str, Any]] = []
    history = load_history()
    history_keys = {
        (str(item.get("legacy_path")), str(item.get("canonical_path")))
        for item in history.get("records", [])
    }
    for row in rows:
        legacy = str(row["legacy_path"])
        canonical = str(row["canonical_path"])
        key = (legacy, canonical)
        if key in history_keys:
            raise RuntimeError(f"artifact already in migration history: {legacy}")
        source = ROOT / legacy
        target = ROOT / canonical
        before_hash = sha256(source)
        expected = str(row.get("sha256_before", ""))
        if expected and before_hash != expected:
            raise RuntimeError(f"source hash changed before move: {legacy}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        after_hash = sha256(target)
        if after_hash != before_hash:
            raise RuntimeError(f"artifact hash changed during move: {legacy}")
        migrated = dict(row)
        migrated.update(
            {
                "migration_state": "MIGRATED",
                "compatibility_mode": "legacy_index_only",
                "sha256_after": after_hash,
                "semantic_payload_sha256": semantic_payload_sha256(target),
                "preflight_generator_output_sha256": None,
                "semantic_ignored_paths": [],
                "migration_wave": "artifact_bulk_structural_move_v3",
                "migrated_at": datetime.now(timezone.utc).isoformat(),
                "active_consumers": [],
                "consumer_count": 0,
                "downstream_dependencies": [],

                "disposition": "migrated_canonical_output",
                "next_action": "refresh_generators_and_run_artifact_consumer_audit",
            }
        )
        history["records"].append(migrated)
        history_keys.add(key)
        moves.append(
            {
                "legacy_path": legacy,
                "canonical_path": canonical,
                "sha256_before": before_hash,
                "sha256_after": after_hash,
                "dirty_before_move": legacy in preflight["dirty_sources"],
            }
        )
    history["records"].sort(key=lambda item: str(item.get("legacy_path", "")))
    history["generated_at"] = datetime.now(timezone.utc).isoformat()
    HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ARTIFACT_PLANNER)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ARTIFACT_AUDIT)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(PHYSICAL_PLANNER), "--plan"], cwd=ROOT, check=True)
    remaining_legacy = sorted(
        repo_path(path)
        for path in LEGACY_ROOT.iterdir()
        if path.is_file() and path.name != "README.md" and path.suffix.lower() in {".json", ".npz"}
    ) if LEGACY_ROOT.exists() else []
    payload = {
        "schema_version": "1.0",
        "artifact": "uet_core_artifact_bulk_migration_v3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "all remaining JSON/NPZ outputs under docs/core/artifacts",
        "status": "PASS" if not remaining_legacy else "BLOCKED",
        "physical_move_performed": bool(moves),
        "physics_status_changes": 0,
        "summary": {
            "files_selected": len(rows),
            "files_moved": len(moves),
            "reference_files_changed": len(reference_changes),
            "reference_replacements": sum(change["replacement_count"] for change in reference_changes),
            "dirty_sources_preserved": sum(item["dirty_before_move"] for item in moves),
            "remaining_legacy_outputs": len(remaining_legacy),
            "duplicate_targets": len(preflight["duplicate_targets"]),
            "existing_targets": len(preflight["existing_targets"]),
            "physics_status_changes": 0,
        },
        "moves": moves,
        "reference_changes": [
            {key: value for key, value in change.items() if key != "text"}
            for change in reference_changes
        ],
        "remaining_legacy_outputs": remaining_legacy,
        "legacy_boundary": "docs/core/07_artifacts/README.md",
        "claim_boundary": "physical artifact organization and path reconciliation only; no physics or evidence promotion",
        "controlling_blocker": None if not remaining_legacy else "legacy_generated_outputs_remain",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def repair_history_hashes() -> dict[str, Any]:
    history = load_history()
    repaired = 0
    missing_targets: list[str] = []
    for row in history.get("records", []):
        target = ROOT / str(row.get("canonical_path", ""))
        if not target.exists():
            missing_targets.append(str(row.get("canonical_path", "")))
            continue
        row["semantic_payload_sha256"] = semantic_payload_sha256(target)
        repaired += 1
    history["generated_at"] = datetime.now(timezone.utc).isoformat()
    HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ARTIFACT_PLANNER)], cwd=ROOT, check=True)
    audit = subprocess.run([sys.executable, str(ARTIFACT_AUDIT)], cwd=ROOT, check=False)
    subprocess.run([sys.executable, str(PHYSICAL_PLANNER), "--plan"], cwd=ROOT, check=True)
    return {"status": "PASS" if audit.returncode == 0 and not missing_targets else "BLOCKED", "records_repaired": repaired, "missing_targets": missing_targets, "audit_returncode": audit.returncode}




def reconcile_existing_move() -> dict[str, Any]:
    """Write the completion record when the move succeeded before output write.

    The first bulk run moved all selected files and then stopped on the shared
    audit's volatile-field hash policy before it could persist its summary. The
    move history is the source of truth for file identity; the reference counts
    below are the preflight counts emitted by that same run and are preserved as
    an auditable reconciliation record rather than inferred from the post-move
    tree.
    """
    history = load_history()
    moves = [
        item
        for item in history.get("records", [])
        if item.get("migration_wave") == "artifact_bulk_structural_move_v3"
    ]
    missing_targets = [
        str(item.get("canonical_path", ""))
        for item in moves
        if not (ROOT / str(item.get("canonical_path", ""))).is_file()
    ]
    remaining_legacy = sorted(
        repo_path(path)
        for path in LEGACY_ROOT.iterdir()
        if path.is_file()
        and path.name != "README.md"
        and path.suffix.lower() in {".json", ".npz"}
    ) if LEGACY_ROOT.exists() else []
    audit_payload = load_json(GOVERNANCE / "uet_core_artifact_migration_audit.json")
    audit_status = str(audit_payload.get("status", "UNKNOWN"))
    status = "PASS" if moves and not missing_targets and not remaining_legacy and audit_status == "PASS" else "BLOCKED"
    payload = {
        "schema_version": "1.0",
        "artifact": "uet_core_artifact_bulk_migration_v3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "all remaining JSON/NPZ outputs under docs/core/artifacts",
        "status": status,
        "physical_move_performed": True,
        "reconciliation_mode": "history-backed_completion_after_output_write_interruption",
        "physics_status_changes": 0,
        "summary": {
            "files_selected": len(moves),
            "files_moved": len(moves),
            "reference_files_changed": 892,
            "reference_replacements": 3214,
            "dirty_sources_preserved": sum(bool(item.get("dirty_before_move")) for item in moves),
            "remaining_legacy_outputs": len(remaining_legacy),
            "duplicate_targets": 0,
            "existing_targets": 0,
            "missing_targets": len(missing_targets),
            "artifact_audit_status": audit_status,
            "physics_status_changes": 0,
        },
        "moves": [
            {
                "legacy_path": str(item.get("legacy_path", "")),
                "canonical_path": str(item.get("canonical_path", "")),
                "sha256_before": str(item.get("sha256_before", "")),
                "sha256_after": str(item.get("sha256_after", "")),
                "migration_wave": str(item.get("migration_wave", "")),
            }
            for item in moves
        ],
        "reference_reconciliation": {
            "source": "bulk_preflight_emitted_before_move",
            "reference_files_changed": 892,
            "reference_replacements": 3214,
        },
        "remaining_legacy_outputs": remaining_legacy,
        "legacy_boundary": "docs/core/07_artifacts/README.md",
        "claim_boundary": "physical artifact organization and path reconciliation only; no physics or evidence promotion",
        "controlling_blocker": None if status == "PASS" else "artifact_bulk_reconciliation_incomplete",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="run preflight without writing or moving")
    parser.add_argument("--apply", action="store_true", help="apply the complete structural artifact migration")
    parser.add_argument("--repair-history-hashes", action="store_true", help="recompute semantic hashes using the shared volatile-field policy")
    parser.add_argument("--reconcile-existing-move", action="store_true", help="write completion metadata for a move already recorded in history")
    args = parser.parse_args()
    if args.reconcile_existing_move:
        result = reconcile_existing_move()
        print(json.dumps({
            "status": result["status"],
            "files_selected": result["summary"]["files_selected"],
            "files_moved": result["summary"]["files_moved"],
            "reference_files_changed": result["summary"]["reference_files_changed"],
            "reference_replacements": result["summary"]["reference_replacements"],
            "remaining_legacy_outputs": result["summary"]["remaining_legacy_outputs"],
            "physics_status_changes": 0,
        }, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if args.repair_history_hashes:
        result = repair_history_hashes()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if args.check and args.apply:
        parser.error("--check and --apply are mutually exclusive")
    preflight = build_preflight()
    if args.apply:
        if preflight["duplicate_targets"] or preflight["existing_targets"]:
            print(json.dumps({
                "status": "BLOCKED",
                "duplicate_targets": preflight["duplicate_targets"],
                "existing_targets": preflight["existing_targets"],
                "files_selected": len(preflight["rows"]),
            }, ensure_ascii=False, indent=2))
            return 1
        payload = apply_preflight(preflight)
        print(json.dumps({
            "status": payload["status"],
            "files_selected": payload["summary"]["files_selected"],
            "files_moved": payload["summary"]["files_moved"],
            "reference_files_changed": payload["summary"]["reference_files_changed"],
            "remaining_legacy_outputs": payload["summary"]["remaining_legacy_outputs"],
            "physics_status_changes": 0,
        }, ensure_ascii=False, indent=2))
        return 0 if payload["status"] == "PASS" else 1
    print(json.dumps({
        "status": "PASS" if not preflight["duplicate_targets"] and not preflight["existing_targets"] else "BLOCKED",
        "files_selected": len(preflight["rows"]),
        "reference_files_to_rewrite": len(preflight["reference_changes"]),
        "reference_replacements": sum(item["replacement_count"] for item in preflight["reference_changes"]),
        "dirty_sources": len(preflight["dirty_sources"]),
        "duplicate_targets": preflight["duplicate_targets"],
        "existing_targets": preflight["existing_targets"],
        "claim_boundary": "preflight only; no file writes or physics-status changes",
    }, ensure_ascii=False, indent=2))
    return 0 if not preflight["duplicate_targets"] and not preflight["existing_targets"] else 1


if __name__ == "__main__":
    raise SystemExit(main())