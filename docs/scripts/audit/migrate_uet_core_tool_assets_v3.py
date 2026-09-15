"""Migrate explicitly classified non-Python assets from the core tooling tree.

The allowlist preserves each source subtree and records hashes because these
files may be legacy inputs or reports rather than executable code.  No file is
overwritten and no old-path duplicate is retained.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "docs" / "core" / "00_governance" / "uet_core_tool_asset_migration_manifest.json"
GENERATOR = "docs/scripts/audit/migrate_uet_core_tool_assets_v3.py"

ASSETS = (
    {
        "legacy_path": "docs/core/data/scripts/generate_core_standards.ps1",
        "canonical_path": "docs/scripts/core/generate_core_standards.ps1",
        "file_kind": "tool_asset",
        "classification": "support_script",
    },
    {
        "legacy_path": "docs/core/data/scripts/maintenance/log/logging_compliance_report.json",
        "canonical_path": "docs/scripts/core/maintenance/log/logging_compliance_report.json",
        "file_kind": "tool_asset",
        "classification": "legacy_report",
    },
    *(
        {
            "legacy_path": f"docs/core/data/scripts/Legacy/txt/{name}",
            "canonical_path": f"docs/scripts/core/legacy/txt/{name}",
            "file_kind": "tool_asset",
            "classification": "legacy_text_report",
        }
        for name in (
            "all_structure.txt",
            "all_test_files.txt",
            "audit_output.txt",
            "audit_report.txt",
            "audit_results.txt",
            "topic_files.txt",
            "verification_results.txt",
            "verification_results_v2.txt",
            "verification_results_v3.txt",
            "verification_results_v4.txt",
        )
    ),
)


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def asset_id(legacy_path: str) -> str:
    return "UET-TOOL-ASSET-" + hashlib.sha256(legacy_path.encode("utf-8")).hexdigest()[:12].upper()


def prior_hashes() -> dict[str, str | None]:
    if not OUTPUT.exists():
        return {}
    try:
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {
        record["legacy_path"]: record.get("sha256_before")
        for record in payload.get("records", [])
        if record.get("legacy_path")
    }


def build_records(previous: dict[str, str | None]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in ASSETS:
        source = ROOT / item["legacy_path"]
        target = ROOT / item["canonical_path"]
        source_exists = source.exists()
        target_exists = target.exists()
        state = "MIGRATION_READY" if source_exists and not target_exists else "MIGRATED" if target_exists and not source_exists else "CONFLICT" if source_exists and target_exists else "MISSING"
        records.append(
            {
                "asset_id": asset_id(item["legacy_path"]),
                **item,
                "owner_id": "ORG",
                "room_id": "ROOM_CORE_ORGANIZATION",
                "source_or_generated": "legacy_support_asset",
                "legacy_exists": source_exists,
                "canonical_exists": target_exists,
                "sha256_before": previous.get(item["legacy_path"]) or sha256(source) or sha256(target),
                "sha256_after": sha256(target),
                "migration_state": state,
                "compatibility_mode": "path_resolver",
                "claim_boundary": "organization/tooling traceability only; no physics-status promotion",
                "next_action": "none" if state == "MIGRATED" else "resolve_asset_state",
            }
        )
    return records


def payload(records: list[dict[str, Any]], physical_move_performed: bool) -> dict[str, Any]:
    counts = {
        state: sum(record["migration_state"] == state for record in records)
        for state in ("MIGRATION_READY", "MIGRATED", "CONFLICT", "MISSING")
    }
    status = "PASS" if counts["MIGRATION_READY"] == 0 and counts["CONFLICT"] == 0 and counts["MISSING"] == 0 else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_tool_asset_migration_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "explicit non-Python assets in docs/core/data/scripts",
        "physical_move_performed": physical_move_performed,
        "status": status,
        "controlling_blocker": None if status == "PASS" else "tool_asset_provenance_and_target_conflict",
        "summary": {
            "files_total": len(records),
            "migration_ready": counts["MIGRATION_READY"],
            "migrated": counts["MIGRATED"],
            "conflicts": counts["CONFLICT"],
            "missing": counts["MISSING"],
            "physics_status_changes": 0,
        },
        "records": records,
        "claim_boundary": "organization and path provenance only; no equation, evidence, or physics claim promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.check and args.apply:
        parser.error("--check and --apply are mutually exclusive")

    previous = prior_hashes()
    before = build_records(previous)
    ready = [record for record in before if record["migration_state"] == "MIGRATION_READY"]
    if any(record["migration_state"] in {"CONFLICT", "MISSING"} for record in before):
        raise SystemExit("tool asset migration blocked by conflict or missing source")

    moved = False
    if args.apply:
        for record in ready:
            source = ROOT / record["legacy_path"]
            target = ROOT / record["canonical_path"]
            if target.exists():
                raise SystemExit(f"refusing to overwrite existing target: {record['canonical_path']}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            moved = True

    records = build_records(previous)
    for record in records:
        record["sha256_before"] = next(
            before_record["sha256_before"]
            for before_record in before
            if before_record["legacy_path"] == record["legacy_path"]
        )
        record["sha256_after"] = record["sha256_canonical"] if "sha256_canonical" in record else sha256(ROOT / record["canonical_path"])
    result = payload(records, moved)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"], "output": OUTPUT.relative_to(ROOT).as_posix()}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
