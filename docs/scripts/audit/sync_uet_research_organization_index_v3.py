"""Generate the organization index after the first physical migration wave."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MIGRATION = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
REGISTRY = CORE / "artifacts" / "uet_research_organization_registry.json"
INDEX = CORE / "00_governance" / "CORE_RESEARCH_ORGANIZATION_INDEX.md"


def main() -> int:
    migration = json.loads(MIGRATION.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    summary = migration["summary"]
    lines = [
        "# Core Research Organization Index",
        "",
        "> Generated organization view. Organization migration does not promote physics evidence.",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Control plane",
        "",
        "- Root navigation: [CORE_FILE_INDEX.md](../CORE_FILE_INDEX.md)",
        "- Physical migration manifest: [uet_core_physical_migration_manifest.json](uet_core_physical_migration_manifest.json)",
        "- Physical migration audit: [uet_core_physical_migration_audit.json](uet_core_physical_migration_audit.json)",
        "- Scientific registry: [uet_research_organization_registry.json](../artifacts/uet_research_organization_registry.json)",
        "- Scientific foundation gate: [uet_foundation_dependency_gate.json](../artifacts/uet_foundation_dependency_gate.json)",
        "",
        "## Current state",
        "",
        f"- Physical files indexed: **{summary['files_total']}**",
        f"- Canonical move targets remaining: **{summary['files_to_move']}**",
        f"- Contracts/history files migrated in the latest completed wave: **{summary.get('files_migrated_in_wave', 0)}**",
        f"- Dirty sources held back: **{summary['dirty_sources']}**",
        f"- Duplicate canonical targets: **{len(summary['duplicate_targets'])}**",
        f"- Physics status changes from this migration: **{summary['physics_status_changes']}**",
        f"- Scientific registry status: **{registry.get('status')}**",
        f"- Foundation status: **{registry.get('scientific_foundation_status', {}).get('status')}**",
        f"- Organization controller: **{registry.get('controlling_blocker')}**",
        "",
        "## Owner counts from scientific registry",
        "",
        "| Owner | Records |",
        "| :-- | --: |",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in sorted(registry.get("owner_counts", {}).items()))
    lines += [
        "",
        "## Migration boundary",
        "",
        "Canonical contract and history documents are now physically grouped under 01_contracts, 03_lanes/topic13_support, 08_history and 00_governance. Their former root paths are compatibility redirects.",
        "",
        "Tests, data, generated artifacts and Python implementations remain pending until their consumer, import and generator checkpoints are complete.",
        "",
        "Organization status is separate from evidence status. The current foundation gate remains BLOCKED where its scientific evidence is incomplete.",
        "",
    ]
    INDEX.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "index": str(INDEX.relative_to(ROOT)).replace("\\", "/"),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
