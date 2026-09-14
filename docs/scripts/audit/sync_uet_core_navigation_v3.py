"""Generate the root navigation index for the physical core layout."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
MANIFEST = CORE / "00_governance" / "uet_core_physical_migration_manifest.json"
INDEX = CORE / "CORE_FILE_INDEX.md"


def load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def render(payload: dict) -> str:
    summary = payload["summary"]
    records = payload["records"]
    areas = {}
    waves = {}
    for item in records:
        path = item["current_path"]
        if path.startswith("docs/core/"):
            tail = path[len("docs/core/") :]
            area = tail.split("/", 1)[0] if "/" in tail else "root_entrypoints"
            areas[area] = areas.get(area, 0) + 1
        wave = item["migration_wave"]
        waves[wave] = waves.get(wave, 0) + 1
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
        "- Path authority: [core_paths.py](core_paths.py)",
        "- Compatibility loader: [core_compat.py](core_compat.py)",
        "",
        "## Root policy",
        "",
        "AGENTS.md, README.md, CORE_FILE_INDEX.md and __init__.py remain permanent root entrypoints. Implementations, tests, data and generated results belong in their canonical areas.",
        "",
        "## Physical state",
        "",
        f"- Files indexed: **{summary['files_total']}**",
        f"- Move targets: **{summary['files_to_move']}**",
        f"- Already canonical or protected: **{summary['already_canonical']}**",
        f"- Dirty sources held back: **{summary['dirty_sources']}**",
        f"- Duplicate targets: **{len(summary['duplicate_targets'])}**",
        f"- Existing destination conflicts: **{len(summary['existing_target_conflicts'])}**",
        f"- Physics status changes from organization migration: **{summary['physics_status_changes']}**",
        "",
        "## Canonical areas",
        "",
        "| Area | Indexed paths |",
        "| :-- | --: |",
    ]
    lines.extend(f"| {area} | {count} |" for area, count in sorted(areas.items()))
    lines += ["", "## Migration waves", "", "| Wave | Paths |", "| :-- | --: |"]
    lines.extend(f"| {wave} | {count} |" for wave, count in sorted(waves.items()))
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
    payload = load()
    INDEX.write_text(render(payload), encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "index": str(INDEX.relative_to(ROOT)).replace("\\", "/"),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
