"""Migrate the remaining non-Python assets from the legacy core test boundary.

This is an explicit, provenance-aware wave.  It intentionally uses an allowlist
instead of guessing from filenames, because CSV/JSON test inputs must keep
their relative subtree and must not be duplicated at a second canonical path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_path_for

OUTPUT = ROOT / "docs" / "core" / "00_governance" / "uet_core_test_asset_migration_manifest.json"
GENERATOR = "docs/scripts/audit/migrate_uet_core_test_assets_v3.py"

ASSETS = (
    {
        "legacy_path": "docs/core/test/03_Research/UET_V3_Parameter_Matrix.csv",
        "canonical_path": "docs/core/05_tests/regression/03_Research/UET_V3_Parameter_Matrix.csv",
        "file_kind": "test_input_csv",
        "compatibility_mode": "path_resolver",
    },
    {
        "legacy_path": "docs/core/test/examples/matrix_config_demo.json",
        "canonical_path": "docs/core/05_tests/regression/examples/matrix_config_demo.json",
        "file_kind": "test_input_json",
        "compatibility_mode": "path_resolver",
    },
    {
        "legacy_path": "docs/core/05_tests/regression/root/README.md",
        "canonical_path": "docs/core/05_tests/regression/root/README.md",
        "file_kind": "legacy_boundary_readme",
        "compatibility_mode": "markdown_redirect",
    },
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
    return "UET-TEST-ASSET-" + hashlib.sha256(legacy_path.encode("utf-8")).hexdigest()[:12].upper()


def redirect_text(canonical_path: str) -> str:
    relative = Path(canonical_path).relative_to("docs/core")
    return (
        "# Compatibility redirect\n\n"
        "> This path is retained as a legacy discovery boundary.\n\n"
        f"Canonical source: [docs/core/{relative.as_posix()}]"
        f"({relative.as_posix()})\n\n"
        "Do not store test data or source prose at this legacy path.\n"
    )


def build_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in ASSETS:
        resolved = canonical_path_for(item["legacy_path"])
        if resolved != item["canonical_path"]:
            raise RuntimeError(
                f"allowlisted target disagrees with canonical path authority: "
                f"{item['legacy_path']} -> {resolved} (expected {item['canonical_path']})"
            )
        legacy = ROOT / item["legacy_path"]
        canonical = ROOT / item["canonical_path"]
        legacy_exists = legacy.exists()
        canonical_exists = canonical.exists()
        if legacy_exists and canonical_exists:
            if item["file_kind"] == "legacy_boundary_readme" and legacy.read_text(encoding="utf-8").startswith(
                "# Compatibility redirect"
            ):
                state = "MIGRATED_WITH_REDIRECT"
            else:
                state = "CONFLICT"
        elif legacy_exists:
            state = "MIGRATION_READY"
        elif canonical_exists:
            state = "MIGRATED"
        else:
            state = "MISSING"
        records.append(
            {
                "asset_id": asset_id(item["legacy_path"]),
                "legacy_path": item["legacy_path"],
                "canonical_path": item["canonical_path"],
                "file_kind": item["file_kind"],
                "logical_area": "05_tests/regression",
                "compatibility_mode": item["compatibility_mode"],
                "legacy_exists": legacy_exists,
                "canonical_exists": canonical_exists,
                "sha256_legacy": sha256(legacy),
                "sha256_canonical": sha256(canonical),
                "migration_state": state,
                "owner_id": "EVIDENCE",
                "room_id": "ROOM_CORE_FOUNDATION",
                "source_or_generated": "source",
                "organization_status": "ASSIGNED",
                "evidence_status": "INTERNAL",
                "claim_boundary": "test input/boundary organization only; no physics-status promotion",
                "next_action": "none" if state in {"MIGRATED", "MIGRATED_WITH_REDIRECT"} else "resolve_asset_state",
            }
        )
    return records


def build_payload(records: list[dict[str, Any]], physical_move_performed: bool) -> dict[str, Any]:
    states = {state: sum(record["migration_state"] == state for record in records) for state in (
        "MIGRATION_READY",
        "MIGRATED",
        "MIGRATED_WITH_REDIRECT",
        "CONFLICT",
        "MISSING",
    )}
    status = "PASS" if states["CONFLICT"] == 0 and states["MISSING"] == 0 and states["MIGRATION_READY"] == 0 else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_test_asset_migration_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "explicit non-Python assets in docs/core/test",
        "physical_move_performed": physical_move_performed,
        "status": status,
        "controlling_blocker": None if status == "PASS" else "test_asset_provenance_and_legacy_data_boundary",
        "summary": {
            "files_total": len(records),
            "migration_ready": states["MIGRATION_READY"],
            "migrated": states["MIGRATED"],
            "migrated_with_redirect": states["MIGRATED_WITH_REDIRECT"],
            "conflicts": states["CONFLICT"],
            "missing": states["MISSING"],
            "physics_status_changes": 0,
        },
        "records": records,
        "claim_boundary": "organization and path compatibility only; no equation, evidence, or physics claim promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="audit the allowlist without moving files")
    parser.add_argument("--apply", action="store_true", help="move the allowlisted assets")
    args = parser.parse_args()
    if args.check and args.apply:
        parser.error("--check and --apply are mutually exclusive")

    prior_before_hashes: dict[str, str | None] = {}
    if OUTPUT.exists():
        try:
            prior_payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
            prior_before_hashes = {
                record["legacy_path"]: record.get("sha256_before")
                for record in prior_payload.get("records", [])
                if record.get("legacy_path")
            }
        except (OSError, json.JSONDecodeError):
            prior_before_hashes = {}

    before = build_records()
    for record in before:
        record["sha256_before"] = (
            record["sha256_legacy"] or prior_before_hashes.get(record["legacy_path"]) or record["sha256_canonical"]
        )
    conflicts = [record for record in before if record["migration_state"] == "CONFLICT"]
    missing = [record for record in before if record["migration_state"] == "MISSING"]
    ready = [record for record in before if record["migration_state"] == "MIGRATION_READY"]
    if (conflicts or missing) and args.apply:
        raise SystemExit("asset migration blocked by conflict or missing source")

    moved = False
    if args.apply:
        for record in ready:
            source = ROOT / record["legacy_path"]
            target = ROOT / record["canonical_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise SystemExit(f"refusing to overwrite existing target: {record['canonical_path']}")
            shutil.move(str(source), str(target))
            moved = True
            if record["compatibility_mode"] == "markdown_redirect":
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text(redirect_text(record["canonical_path"]), encoding="utf-8")

    records = build_records()
    for record in records:
        record["sha256_before"] = (
            prior_before_hashes.get(record["legacy_path"])
            or next(
                before_record["sha256_before"]
                for before_record in before
                if before_record["legacy_path"] == record["legacy_path"]
            )
        )
        record["sha256_after"] = record["sha256_canonical"] or record["sha256_legacy"]
    payload = build_payload(records, moved)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "physical_move_performed": moved,
                "summary": payload["summary"],
                "output": OUTPUT.relative_to(ROOT).as_posix(),
            },
            ensure_ascii=False,
        )
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
