"""Safely migrate one generated core artifact to its canonical path.

The runner is intentionally bounded: it requires one resolved generator, rejects
unresolved active consumers, compares the generator output with the legacy
payload, and records an auditable migration history before the next family is
allowed to move.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
GOVERNANCE = CORE / "00_governance"
MANIFEST = GOVERNANCE / "uet_core_artifact_migration_manifest.json"
HISTORY = GOVERNANCE / "uet_core_artifact_migration_history.json"
PLANNER = ROOT / "docs/scripts/audit/plan_uet_core_artifact_migration_v3.py"
AUDITOR = ROOT / "docs/scripts/audit/audit_uet_core_artifact_migration_v3.py"
RUNNER = "docs/scripts/audit/migrate_uet_core_artifact_family_v3.py"

REFERENCE_ONLY_PREFIXES = (
    "docs/core/00_governance/",
    "docs/core/08_history/",
    "WORK_LEDGER/",
    "uet_history/",
)


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_history() -> dict[str, Any]:
    if not HISTORY.exists():
        return {
            "schema_version": "1.0",
            "artifact": "uet_core_artifact_migration_history",
            "migration_id": "UET-CORE-ARTIFACT-V3",
            "generator": RUNNER,
            "canonical_path_authority": "docs/core/core_paths.py",
            "records": [],
        }
    payload = load_json(HISTORY)
    if not isinstance(payload.get("records"), list):
        raise RuntimeError("artifact migration history records must be a list")
    return payload


def find_row(payload: dict[str, Any], selector: str) -> dict[str, Any]:
    normalized = selector.replace("\\", "/")
    rows = payload.get("records", [])
    matches = [
        row
        for row in rows
        if row.get("legacy_path") == normalized
        or Path(str(row.get("legacy_path", ""))).name == Path(normalized).name
        or row.get("canonical_path") == normalized
    ]
    if len(matches) != 1:
        raise RuntimeError(f"artifact selector must resolve to exactly one active record: {selector}")
    return matches[0]


VOLATILE_JSON_KEYS = frozenset({"generated_at"})


def normalize_json_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalize_json_payload(item)
            for key, item in value.items()
            if key not in VOLATILE_JSON_KEYS
        }
    if isinstance(value, list):
        return [normalize_json_payload(item) for item in value]
    return value


def is_volatile_json_path(path: str) -> bool:
    return path == "generated_at" or path.endswith(".generated_at")


def semantic_metadata_difference_paths(source: Path, target: Path) -> list[str]:
    if source.suffix.lower() != ".json" or target.suffix.lower() != ".json":
        return []
    differences = differing_json_paths(load_json(source), load_json(target))
    return [path for path in differences if is_volatile_json_path(path)]


def semantic_equal(source: Path, target: Path) -> bool:
    if source.suffix.lower() == ".json" and target.suffix.lower() == ".json":
        return normalize_json_payload(load_json(source)) == normalize_json_payload(load_json(target))
    return source.read_bytes() == target.read_bytes()


def semantic_payload_sha256(path: Path) -> str:
    """Hash artifact content after removing declared volatile JSON metadata."""
    if path.suffix.lower() == ".json":
        payload = normalize_json_payload(load_json(path))
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    else:
        encoded = path.read_bytes()
    return hashlib.sha256(encoded).hexdigest()


def differing_json_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    """Return stable paths for a small, reviewable JSON payload difference."""
    if isinstance(left, dict) and isinstance(right, dict):
        paths: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{prefix}.{key}" if prefix else str(key)
            if key not in left or key not in right:
                paths.append(child)
            else:
                paths.extend(differing_json_paths(left[key], right[key], child))
        return paths
    if isinstance(left, list) and isinstance(right, list):
        paths: list[str] = []
        for index in range(max(len(left), len(right))):
            child = f"{prefix}[{index}]"
            if index >= len(left) or index >= len(right):
                paths.append(child)
            else:
                paths.extend(differing_json_paths(left[index], right[index], child))
        return paths
    return [] if left == right else [prefix]


def provenance_only_refresh(source: Path, target: Path) -> bool:
    """Allow only source SHA refreshes before a move; never hide physics drift."""
    if source.suffix.lower() != ".json" or target.suffix.lower() != ".json":
        return False
    differences = differing_json_paths(load_json(source), load_json(target))
    return bool(differences) and all(
        path.startswith("sources[") and path.endswith("].sha256")
        for path in differences
    )


def validate_preconditions(row: dict[str, Any]) -> tuple[Path, Path, Path]:
    source = ROOT / str(row["legacy_path"])
    target = ROOT / str(row["canonical_path"])
    generator_value = row.get("generator_path")
    if row.get("migration_state") != "NOT_STARTED":
        raise RuntimeError(f"artifact is not an active NOT_STARTED record: {row['legacy_path']}")
    if row.get("generator_count") != 1 or not generator_value:
        raise RuntimeError("artifact generator identity is not uniquely resolved")
    active_consumers = {
        path
        for path in row.get("downstream_dependencies", [])
        if not any(str(path).replace("\\", "/").startswith(prefix) for prefix in REFERENCE_ONLY_PREFIXES)
    }
    if active_consumers:
        raise RuntimeError(f"active artifact consumers must be rewritten first: {sorted(active_consumers)}")
    if not source.exists():
        raise FileNotFoundError(source)
    if target.exists():
        raise FileExistsError(f"canonical target already exists: {target}")
    observed = sha256(source)
    if observed != row.get("sha256_before"):
        raise RuntimeError(
            f"legacy artifact hash changed before migration: expected {row.get('sha256_before')}, observed {observed}"
        )
    generator = ROOT / str(generator_value)
    if not generator.exists():
        raise FileNotFoundError(generator)
    generator_text = generator.read_text(encoding="utf-8")
    if "canonical_artifact_path" not in generator_text:
        raise RuntimeError("generator is not switched to core_paths.canonical_artifact_path")
    if str(row["legacy_path"]) in generator_text:
        raise RuntimeError("generator still contains the legacy artifact output path")
    return source, target, generator


def run_generator(generator: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(generator)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"artifact generator failed ({result.returncode}): {result.stdout[-1000:]} {result.stderr[-1000:]}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"stdout": result.stdout[-2000:]}


def update_history(
    row: dict[str, Any],
    preflight_hash: str,
    after_hash: str,
    semantic_ignored_paths: list[str],
    semantic_hash: str,
) -> dict[str, Any]:
    history = load_history()
    existing = [
        item
        for item in history["records"]
        if item.get("legacy_path") == row.get("legacy_path")
        or item.get("canonical_path") == row.get("canonical_path")
    ]
    if existing:
        raise RuntimeError("artifact already has a migration-history record")
    migrated = dict(row)
    migrated.update(
        {
            "migration_state": "MIGRATED",
            "compatibility_mode": "legacy_index_only",
            "sha256_after": after_hash,
            "preflight_generator_output_sha256": preflight_hash,
            "semantic_payload_sha256": semantic_hash,
            "semantic_ignored_paths": semantic_ignored_paths,
            "migration_wave": "artifact_family_bounded_move",
            "migrated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "active_consumers": [],
            "consumer_count": 0,
            "downstream_dependencies": [],
            "rollback_path": row["legacy_path"],
            "disposition": "migrated_canonical_output",
            "next_action": "refresh_generated_indexes_and_verify_canonical_consumer_paths",
        }
    )
    history["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    history["records"].append(migrated)
    history["records"].sort(key=lambda item: str(item.get("legacy_path", "")))
    write_json(HISTORY, history)
    return migrated


def apply(row: dict[str, Any]) -> dict[str, Any]:
    source, target, generator = validate_preconditions(row)
    run_result = run_generator(generator)
    if not target.exists():
        raise RuntimeError("generator did not create the canonical target")
    preflight_hash = sha256(target)
    semantic_ignored_paths = semantic_metadata_difference_paths(source, target)
    if not semantic_equal(source, target):
        drift_kind = (
            "source-provenance metadata"
            if provenance_only_refresh(source, target)
            else "semantic content"
        )
        target.unlink()
        raise RuntimeError(
            f"canonical generator payload differs in {drift_kind}; legacy output was not overwritten"
        )

    backup_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="uet-artifact-", suffix=source.suffix, delete=False) as handle:
            backup_path = Path(handle.name)
        shutil.copy2(source, backup_path)
        target.unlink()
        shutil.move(str(source), str(target))
        after_hash = sha256(target)
        if after_hash != row.get("sha256_before") or not semantic_equal(backup_path, target):
            raise RuntimeError("post-move artifact hash or semantic payload changed")
        migrated = update_history(
            row,
            preflight_hash,
            after_hash,
            semantic_ignored_paths,
            semantic_payload_sha256(target),
        )
    except Exception:
        if target.exists() and not source.exists():
            target.unlink()
        if backup_path and backup_path.exists():
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, source)
        raise
    finally:
        if backup_path and backup_path.exists():
            backup_path.unlink()

    subprocess.run([sys.executable, str(PLANNER)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(AUDITOR)], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(PLANNER), "--check"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(AUDITOR), "--check"], cwd=ROOT, check=True)
    return {
        "status": "APPLIED",
        "legacy_path": migrated["legacy_path"],
        "canonical_path": migrated["canonical_path"],
        "sha256": migrated["sha256_after"],
        "generator": migrated["generator_path"],
        "generator_result": run_result,
        "history": repo_path(HISTORY),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True, help="legacy or canonical artifact path/name")
    parser.add_argument("--apply", action="store_true", help="perform the bounded physical move")

    args = parser.parse_args()
    payload = load_json(MANIFEST)
    row = find_row(payload, args.artifact)
    if not args.apply:
        source, target, generator = validate_preconditions(row)
        print(json.dumps(
            {
                "status": "READY",
                "legacy_path": repo_path(source),
                "canonical_path": repo_path(target),
                "generator": repo_path(generator),
                "sha256_before": row.get("sha256_before"),
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0
    try:
        print(json.dumps(apply(row), ensure_ascii=False, indent=2))
        return 0
    except (FileExistsError, FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())