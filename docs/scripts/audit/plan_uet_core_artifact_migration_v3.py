"""Build a consumer-aware plan for moving generated core artifacts.

This wave is deliberately plan-only.  Generated artifacts are not moved until
their generator and every active consumer have been switched to the canonical
path authority.  The plan records the exact legacy references so a later
bounded artifact family can be migrated without leaving stale readers behind.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
SOURCE_ROOT = CORE / "artifacts"
GOVERNANCE = CORE / "00_governance"
MANIFEST = GOVERNANCE / "uet_core_artifact_migration_manifest.json"
REPORT = GOVERNANCE / "UET_CORE_ARTIFACT_MIGRATION_REPORT.md"
GENERATOR = "docs/scripts/audit/plan_uet_core_artifact_migration_v3.py"
EXCLUDED_PARTS = {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache", ".mypy_cache"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".ps1", ".sh"}
LEGACY_PREFIX = "docs/core/artifacts/"
SCAN_ROOTS = [ROOT / "docs", ROOT / "uet_history", ROOT / "WORK_LEDGER", ROOT / "README.md", ROOT / "AGENTS.md"]


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_for(name: str) -> str:
    # Keep the single target decision in core_paths.py instead of duplicating
    # artifact-domain rules in this planner.
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from docs.core.core_paths import canonical_path_for

    return canonical_path_for(f"{LEGACY_PREFIX}{name}")


def text_files() -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for base in SCAN_ROOTS:
        candidates = base.rglob("*") if base.is_dir() else [base]
        for path in candidates:
            if path in seen or not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            if path.is_relative_to(SOURCE_ROOT):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            seen.add(path)
            result.append(path)
    return result


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def reference_index(names: list[str]) -> dict[str, list[str]]:
    """Stream artifact references with ripgrep without caching the repository."""
    index: dict[str, list[str]] = {name: [] for name in names}
    if not names:
        return index
    roots = [
        "docs/core",
        "docs/scripts",
        "docs/topics",
        "uet_history",
        "WORK_LEDGER",
        "README.md",
        "AGENTS.md",
    ]
    for start in range(0, len(names), 40):
        chunk = names[start : start + 40]
        command = [
            "rg",
            "--json",
            "--fixed-strings",
            "--no-messages",
            "--glob",
            "!docs/core/artifacts/**",
            "--glob",
            "!docs/core/07_artifacts/**",
        ]
        for name in chunk:
            command.extend(["-e", name])
        command.extend(roots)
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            continue
        for raw in result.stdout.splitlines():
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "match":
                continue
            data = event.get("data", {})
            path_text = str(data.get("path", {}).get("text", ""))
            if not path_text:
                continue
            relative = path_text.replace("\\", "/")
            for submatch in data.get("submatches", []):
                matched = str(submatch.get("match", {}).get("text", ""))
                if matched in index and relative not in index[matched]:
                    index[matched].append(relative)
    return index


def classify_generator(path: str, name: str) -> bool:
    lower = path.lower()
    # A likely writer is an audit/build/generator script mentioning both the
    # artifact and an output/write operation. This is a candidate identity,
    # not proof that the script is the sole generator.
    if not lower.endswith((".py", ".ps1", ".sh")):
        return False
    text = load_text(ROOT / path)
    if name not in text:
        return False
    return bool(re.search(rf"(?im)^\s*(?:OUTPUT|OUTPUT_PATH|ARTIFACT_PATH|output)\s*=\s*[^\n]*{re.escape(name)}", text))


def build_records() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    artifacts = [
        path
        for path in sorted(SOURCE_ROOT.iterdir())
        if path.is_file() and path.name != "README.md" and path.suffix.lower() in {".json", ".npz"}
    ]
    reference_map = reference_index([path.name for path in artifacts])
    rows: list[dict[str, Any]] = []
    for path in artifacts:
        name = path.name
        legacy = repo_path(path)
        target = canonical_for(name)
        hits = reference_map.get(name, [])
        generator_candidates = [item for item in hits if classify_generator(item, name)]
        consumer_paths = [item for item in hits if item not in generator_candidates]
        if not generator_candidates:
            disposition = "generator_identity_not_resolved"
        elif consumer_paths:
            disposition = "generator_and_consumer_rewrite_required"
        else:
            disposition = "generator_switch_required_before_move"
        rows.append(
            {
                "asset_id": "UET-ARTIFACT-" + hashlib.sha1(legacy.encode()).hexdigest()[:12].upper(),
                "legacy_path": legacy,
                "canonical_path": target,
                "file_kind": "generated_artifact",
                "logical_area": "07_artifacts",
                "owner_id": "EVIDENCE",
                "room_id": "ROOM_CORE_FOUNDATION",
                "equation_family_or_lane": "generated_core_artifact",
                "organization_status": "ASSIGNED",
                "evidence_status": "INTERNAL",
                "status_source": "artifact_migration_manifest",
                "source_or_generated": "generated",
                "generator_candidates": generator_candidates,
                "generator_path": generator_candidates[0] if len(generator_candidates) == 1 else None,
                "formula_ids": [],
                "verifier_paths": [],
                "artifact_paths": [],
                "upstream_dependencies": [],
                "downstream_dependencies": consumer_paths,
                "sha256_before": sha256(path),
                "sha256_after": None,
                "migration_wave": "artifact_consumer_control",
                "migration_state": "NOT_STARTED",
                "compatibility_mode": "legacy_artifact_index_until_consumer_switch",
                "collision_key": target.lower(),
                "rollback_path": legacy,
                "legacy_reference_paths": hits,
                "generator_count": len(generator_candidates),
                "consumer_count": len(consumer_paths),
                "disposition": disposition,
                "next_action": "map_and_switch_generator_and_consumers",
            }
        )
    by_target: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        by_target[row["collision_key"]].append(row["legacy_path"])
    duplicate_targets = {key: values for key, values in by_target.items() if len(values) > 1}
    existing_targets = sorted(
        {
            row["canonical_path"]
            for row in rows
            if (ROOT / row["canonical_path"]).exists()
        }
    )
    summary = {
        "files_total": len(rows),
        "json_files": sum(row["legacy_path"].lower().endswith(".json") for row in rows),
        "npz_files": sum(row["legacy_path"].lower().endswith(".npz") for row in rows),
        "generator_identity_resolved": sum(row["generator_count"] == 1 for row in rows),
        "generator_identity_ambiguous": sum(row["generator_count"] > 1 for row in rows),
        "generator_identity_missing": sum(row["generator_count"] == 0 for row in rows),
        "consumer_rewrite_required": sum(row["consumer_count"] > 0 for row in rows),
        "duplicate_targets": duplicate_targets,
        "existing_target_conflicts": existing_targets,
        "physical_move_performed": False,
        "physics_status_changes": 0,
        "claim_promotion": False,
        "disposition_counts": dict(Counter(row["disposition"] for row in rows)),
    }
    return rows, summary


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# UET Core Artifact Migration Report",
        "",
        "> Plan-only control artifact. No generated output is moved by this wave.",
        "",
        f"Generated at: {payload['generated_at']}",
        f"Generator: {payload['generator']}",
        "",
        "## Inventory",
        "",
        f"- Generated artifacts indexed: **{summary['files_total']}** ({summary['json_files']} JSON, {summary['npz_files']} NPZ)",
        f"- One generator identity resolved: **{summary['generator_identity_resolved']}**",
        f"- Ambiguous generator identity: **{summary['generator_identity_ambiguous']}**",
        f"- Missing generator identity: **{summary['generator_identity_missing']}**",
        f"- Consumer rewrite required: **{summary['consumer_rewrite_required']}**",
        f"- Duplicate canonical targets: **{len(summary['duplicate_targets'])}**",
        f"- Existing canonical targets: **{len(summary['existing_target_conflicts'])}**",
        f"- Physical move performed: **{summary['physical_move_performed']}**",
        f"- Physics status changes: **{summary['physics_status_changes']}**",
        "",
        "## Gate",
        "",
        "Every artifact remains at its legacy path until its generator writes the canonical path and every active consumer is switched. The legacy directory remains a compatibility boundary; it is not a second generated-output store after a family is migrated.",
        "",
        "## Required next action",
        "",
        "Select one bounded artifact family, patch its generator and consumers to use core_paths.canonical_artifact_path, regenerate in check mode, compare semantic payload and hashes, then perform a scoped move with a no-duplicate audit.",
    ]
    return "\n".join(lines) + "\n"


def build_payload() -> dict[str, Any]:
    rows, summary = build_records()
    return {
        "schema_version": "1.0",
        "migration_id": "UET-CORE-ARTIFACT-V3",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "docs/core/artifacts generated JSON and NPZ outputs",
        "canonical_path_authority": "docs/core/core_paths.py",
        "legacy_boundary": "docs/core/artifacts/README.md",
        "summary": summary,
        "records": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    payload = build_payload()
    GOVERNANCE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(payload), encoding="utf-8")
    summary = payload["summary"]
    status = "PASS" if not summary["duplicate_targets"] and not summary["existing_target_conflicts"] else "BLOCKED"
    print(json.dumps({
        "status": status,
        "files_total": summary["files_total"],
        "generator_identity_resolved": summary["generator_identity_resolved"],
        "generator_identity_ambiguous": summary["generator_identity_ambiguous"],
        "generator_identity_missing": summary["generator_identity_missing"],
        "consumer_rewrite_required": summary["consumer_rewrite_required"],
        "duplicate_targets": len(summary["duplicate_targets"]),
        "existing_target_conflicts": len(summary["existing_target_conflicts"]),
        "manifest": repo_path(MANIFEST),
    }, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
