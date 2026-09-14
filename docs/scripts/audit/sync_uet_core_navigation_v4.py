"""Generate the root core navigation index with all active migration controllers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
PHYSICAL = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
TOOLING = CORE / "00_governance" / "uet_core_data_tooling_migration_manifest.json"
SOURCE_MANIFEST = CORE / "00_governance" / "uet_core_source_package_migration_manifest.json"
SOURCE_AUDIT = CORE / "00_governance" / "uet_core_source_package_migration_audit.json"
TEST_MANIFEST = CORE / "00_governance" / "uet_core_test_migration_manifest.json"
TEST_AUDIT = CORE / "00_governance" / "uet_core_test_migration_audit.json"
COLLECTION_AUDIT = CORE / "00_governance" / "uet_core_test_collection_audit.json"
INDEX = CORE / "CORE_FILE_INDEX.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def area_counts(records: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in records:
        path = item.get("current_path", "")
        if not path.startswith("docs/core/"):
            continue
        tail = path[len("docs/core/") :]
        area = tail.split("/", 1)[0] if "/" in tail else "root_entrypoints"
        counts[area] = counts.get(area, 0) + 1
    return counts


def wave_counts(records: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in records:
        wave = str(item.get("migration_wave", "unclassified"))
        counts[wave] = counts.get(wave, 0) + 1
    return counts


def render(physical: dict, tooling: dict, tests: dict, test_audit: dict, collection_audit: dict) -> str:
    summary = physical.get("summary", {})
    tooling_summary = tooling.get("summary", {})
    test_summary = tests.get("summary", {})
    collection_summary = collection_audit.get("collections", {})
    lines = [
        "# Core File Index",
        "",
        "> Generated navigation entrypoint. Organization state is not physics evidence.",
        "",
        "## Canonical control plane",
        "",
        "- Organization index: [00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md](00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md)",
        "- Physical migration manifest: [00_governance/uet_core_physical_migration_manifest.json](00_governance/uet_core_physical_migration_manifest.json)",
        "- Physical migration report: [00_governance/UET_CORE_PHYSICAL_MIGRATION_REPORT.md](00_governance/UET_CORE_PHYSICAL_MIGRATION_REPORT.md)",
        "- Data/tooling manifest: [00_governance/uet_core_data_tooling_migration_manifest.json](00_governance/uet_core_data_tooling_migration_manifest.json)",
        "- Data/tooling report: [00_governance/UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md](00_governance/UET_CORE_DATA_TOOLING_MIGRATION_REPORT.md)",
        "- Source-package manifest: [00_governance/uet_core_source_package_migration_manifest.json](00_governance/uet_core_source_package_migration_manifest.json)",
        "- Source-package audit: [00_governance/uet_core_source_package_migration_audit.json](00_governance/uet_core_source_package_migration_audit.json)",
        "- Test migration manifest: [00_governance/uet_core_test_migration_manifest.json](00_governance/uet_core_test_migration_manifest.json)",
        "- Test migration audit: [00_governance/uet_core_test_migration_audit.json](00_governance/uet_core_test_migration_audit.json)",
        "- Test collection audit: [00_governance/uet_core_test_collection_audit.json](00_governance/uet_core_test_collection_audit.json)",
        "- Path authority: [core_paths.py](core_paths.py)",
        "- Compatibility loader: [core_compat.py](core_compat.py)",
        "",
        "## Root policy",
        "",
        "AGENTS.md, README.md, CORE_FILE_INDEX.md and __init__.py remain permanent root entrypoints. Implementations, tests, data and generated results belong in their canonical areas.",
        "",
        "## Physical state",
        "",
        f"- Files indexed: **{summary.get('files_total', 0)}**",
        f"- Move targets: **{summary.get('files_to_move', 0)}**",
        f"- Already canonical or protected: **{summary.get('already_canonical', 0)}**",
        f"- Dirty sources held back: **{summary.get('dirty_sources', 0)}**",
        f"- Duplicate targets: **{len(summary.get('duplicate_targets', {}))}**",
        f"- Existing destination conflicts: **{len(summary.get('existing_target_conflicts', []))}**",
        f"- Physics status changes from organization migration: **{summary.get('physics_status_changes', 0)}**",
        "",
        "## Data/tooling wave",
        "",
        f"- Tooling files indexed: **{tooling_summary.get('files_total', 0)}**",
        f"- Migrated with shim/redirect: **{tooling_summary.get('migrated_with_shim', 0)}**",
        f"- Quarantined for path/provenance review: **{tooling_summary.get('quarantined', 0)}**",
        f"- Tooling duplicate targets: **{len(tooling_summary.get('duplicate_targets', {}))}**",
        f"- Tooling physics status changes: **{tooling_summary.get('physics_status_changes', 0)}**",
        "",
        "",
        "## Test surface wave",
        "",
        f"- Tests indexed in migration manifest: **{test_summary.get('files_total', 0)}**",
        f"- Tests physically migrated: **{test_summary.get('migrated', 0)}**",
        f"- Tests quarantined for path/package review: **{test_summary.get('quarantined', 0)}**",
        f"- Test migration audit: **{test_audit.get('status', 'UNKNOWN')}**",
        f"- Full pytest collection: **{collection_summary.get('full', {}).get('status', 'UNKNOWN')}** ({collection_summary.get('full', {}).get('collected', 0)} collected)",
        f"- Canonical-only collection: **{collection_summary.get('canonical_only', {}).get('status', 'UNKNOWN')}** ({collection_summary.get('canonical_only', {}).get('collected', 0)} collected)",
        f"- Test physics status changes: **{test_summary.get('physics_status_changes', 0)}**",
        "## Canonical areas",
        "",
        "| Area | Indexed paths |",
        "| :-- | --: |",
    ]
    lines.extend(f"| {area} | {count} |" for area, count in sorted(area_counts(physical.get("records", [] )).items()))
    lines += ["", "## Migration waves", "", "| Wave | Paths |", "| :-- | --: |"]
    lines.extend(f"| {wave} | {count} |" for wave, count in sorted(wave_counts(physical.get("records", [])).items()))
    lines += [
        "",
        "## Working rule",
        "",
        "request → owner → canonical path → compatibility check → verifier → artifact → handoff",
        "",
        "A migrated path is easier to find; it is not thereby derived, validated or promoted. The current foundation gate remains authoritative.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    physical = load(PHYSICAL)
    tooling = load(TOOLING)
    tests = load(TEST_MANIFEST)
    test_audit = load(TEST_AUDIT)
    collection_audit = load(COLLECTION_AUDIT)
    INDEX.write_text(render(physical, tooling, tests, test_audit, collection_audit), encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "index": INDEX.relative_to(ROOT).as_posix(),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
