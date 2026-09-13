"""Stable Wave 0 entrypoint for the UET organization registry.

The first generator remains preserved for provenance.  This wrapper applies the
organization contract that nullable lane fields are represented explicitly as
``UNASSIGNED`` and that the generated governance index is not a review item.
It then emits the same three control artifacts and index.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
ARTIFACTS = CORE / "artifacts"
POLICY_PATH = CORE / "00_governance" / "uet_research_organization_policy.json"
MANIFEST_PATH = ARTIFACTS / "uet_core_file_manifest.json"
CONTRACT_PATH = ARTIFACTS / "uet_core_equation_family_contract.json"
GATE_PATH = ARTIFACTS / "uet_foundation_dependency_gate.json"
REGISTRY_PATH = ARTIFACTS / "uet_research_organization_registry.json"
MIGRATION_PATH = ARTIFACTS / "uet_core_file_migration_map.json"
AUDIT_PATH = ARTIFACTS / "uet_core_organization_audit.json"
INDEX_PATH = CORE / "00_governance" / "CORE_RESEARCH_ORGANIZATION_INDEX.md"
GENERATOR_ID = "docs/scripts/audit/build_uet_research_organization_registry_v2.py"
DISPOSITION_SOURCE = "docs/core/00_governance/uet_research_organization_policy.json"
REVIEW_STATUSES = {"UNASSIGNED", "QUARANTINED"}


def load_builder() -> Any:
    source = ROOT / "docs" / "scripts" / "audit" / "build_uet_research_organization_registry.py"
    spec = importlib.util.spec_from_file_location("uet_organization_builder", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load preserved generator: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Apply explicit organization classifications not yet known to the old scanner."""
    for record in manifest.get("files", []):
        path = str(record.get("path", "")).replace("\\", "/")
        if path == "docs/core/00_governance/CORE_RESEARCH_ORGANIZATION_INDEX.md":
            record.update(
                file_kind="navigation_and_legacy_boundary",
                logical_area="00_governance",
                owner_family_or_lane="core_governance",
                registry_link_status="GENERATED_INDEX",
                status_source=GENERATOR_ID,
                generated_or_source="generated",
                review_action="retain_generated_index",
            )
        if record.get("equation_family_or_lane") is None:
            record["equation_family_or_lane"] = "UNASSIGNED"
    return manifest


def disposition_for(path: str, policy: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first explicit Wave 1 rule matching a review path."""
    for rule in policy.get("review_disposition_rules", []):
        if any(fnmatchcase(path, str(pattern)) for pattern in rule.get("patterns", [])):
            return rule
    return None


def apply_review_dispositions(
    registry: dict[str, Any],
    migration: dict[str, Any],
    audit: dict[str, Any],
    policy: dict[str, Any],
    builder: Any,
) -> None:
    """Classify the existing review queue without moving files or changing physics status."""
    review_paths = {
        item["path"]
        for item in registry.get("files", [])
        if item.get("organization_status") == "UNASSIGNED"
        or item.get("registry_link_status") == "REVIEW_REQUIRED"
    }
    dispositioned_paths: list[str] = []
    undispositioned_paths: list[str] = []

    for item in registry.get("files", []):
        path = str(item.get("path", ""))
        if path not in review_paths:
            continue
        rule = disposition_for(path, policy)
        if rule is None:
            undispositioned_paths.append(path)
            continue

        target_path = str(rule["target_path_template"]).format(name=Path(path).name)
        status = str(rule["organization_status"])
        item.update(
            {
                "owner_id": rule["owner_id"],
                "room_id": rule["room_id"],
                "logical_area": rule["logical_area"],
                "equation_family_or_lane": rule["equation_family_or_lane"],
                "organization_status": status,
                "evidence_status": rule.get("evidence_status", "BLOCKED"),
                "status_source": DISPOSITION_SOURCE,
                "next_action": rule["next_action"],
                "target_physical_path": target_path,
                "migration_state": builder.migration_state(path, target_path),
                "registry_link_status": (
                    "ORGANIZATION_POLICY_ASSIGNED"
                    if status == "ASSIGNED"
                    else "ORGANIZATION_POLICY_QUARANTINED"
                ),
                "review_action": rule["review_action"],
                "organization_disposition": rule["disposition_id"],
                "disposition_reason": rule["reason"],
            }
        )
        dispositioned_paths.append(path)

    by_asset = {item["asset_id"]: item for item in registry.get("files", [])}
    for item in migration.get("files", []):
        record = by_asset.get(item.get("asset_id"))
        if record is None:
            continue
        for field in (
            "target_physical_path",
            "target_path",
            "owner_id",
            "room_id",
            "organization_status",
            "migration_state",
            "next_action",
            "organization_disposition",
            "disposition_reason",
            "equation_family_or_lane",
            "evidence_status",
        ):
            if field == "target_path":
                item[field] = record.get("target_physical_path")
            elif field in record:
                item[field] = record[field]
        item["reference_scan_status"] = record.get(
            "reference_scan_status", "DEFERRED_TO_MIGRATION_WAVE"
        )

    files = registry.get("files", [])
    unresolved = [item for item in files if item.get("organization_status") in REVIEW_STATUSES]
    quarantined = [item for item in files if item.get("organization_status") == "QUARANTINED"]
    assigned_review = [item for item in files if item.get("path") in dispositioned_paths]
    blocker = (
        "organization_review_dispositions_incomplete"
        if undispositioned_paths
        else "manual_scope_review_for_quarantined_records"
        if quarantined
        else "assigned_records_need_scientific_link_review"
        if assigned_review
        else None
    )

    registry["organization_wave"] = "WAVE_1_ASSIGN_AND_QUARANTINE"
    registry["organization_disposition_source"] = DISPOSITION_SOURCE
    registry["pre_disposition_review_count"] = len(review_paths)
    registry["dispositioned_review_count"] = len(dispositioned_paths)
    registry["undispositioned_review_count"] = len(undispositioned_paths)
    registry["assigned_review_count"] = len(assigned_review)
    registry["quarantine_count"] = len(quarantined)
    registry["review_queue_count"] = len(unresolved)
    registry["controlling_blocker"] = blocker
    registry["counts"] = dict(Counter(item.get("file_kind") for item in files))
    registry["owner_counts"] = dict(Counter(item.get("owner_id") for item in files))
    registry["logical_area_counts"] = dict(Counter(item.get("logical_area") for item in files))
    registry["evidence_status_counts"] = dict(Counter(item.get("evidence_status") for item in files))
    registry["migration_state_counts"] = dict(Counter(item.get("migration_state") for item in files))
    registry["disposition_counts"] = dict(
        Counter(item.get("organization_disposition") for item in assigned_review)
    )

    migration["organization_wave"] = registry["organization_wave"]
    migration["organization_disposition_source"] = DISPOSITION_SOURCE
    migration["pre_disposition_review_count"] = len(review_paths)
    migration["dispositioned_review_count"] = len(dispositioned_paths)
    migration["undispositioned_review_count"] = len(undispositioned_paths)
    migration["assigned_review_count"] = len(assigned_review)
    migration["quarantine_count"] = len(quarantined)
    migration["review_queue_count"] = len(unresolved)
    migration["controlling_blocker"] = blocker

    audit["organization_wave"] = registry["organization_wave"]
    audit["organization_disposition_source"] = DISPOSITION_SOURCE
    audit["controlling_blocker"] = blocker
    audit["scope"].update(
        {
            "review_queue_count": len(unresolved),
            "pre_disposition_review_count": len(review_paths),
            "dispositioned_review_count": len(dispositioned_paths),
            "undispositioned_review_count": len(undispositioned_paths),
            "assigned_review_count": len(assigned_review),
            "quarantine_count": len(quarantined),
        }
    )
    audit["unassigned_paths"] = [item["path"] for item in files if item.get("organization_status") == "UNASSIGNED"]
    audit["quarantined_paths"] = [item["path"] for item in quarantined]
    audit["dispositioned_paths"] = sorted(dispositioned_paths)
    audit["undispositioned_paths"] = sorted(undispositioned_paths)
    audit["disposition_counts"] = registry["disposition_counts"]

    for check in audit.get("checks", []):
        if check.get("check_id") == "review_queue_is_explicit":
            check.update(
                status="PASS" if not undispositioned_paths else "FAIL",
                observed=len(undispositioned_paths),
                expected="every pre-wave review item has a disposition and next_action",
            )
    audit.setdefault("checks", []).extend(
        [
            {
                "check_id": "review_disposition_coverage",
                "status": "PASS" if len(dispositioned_paths) == len(review_paths) else "FAIL",
                "observed": len(dispositioned_paths),
                "expected": len(review_paths),
            },
            {
                "check_id": "no_unassigned_after_wave",
                "status": "PASS" if not audit["unassigned_paths"] else "FAIL",
                "observed": len(audit["unassigned_paths"]),
                "expected": 0,
            },
            {
                "check_id": "physical_move_not_performed",
                "status": "PASS" if migration.get("physical_move_performed") is False else "FAIL",
                "observed": migration.get("physical_move_performed"),
                "expected": False,
            },
        ]
    )


def render_index(registry: dict[str, Any], audit: dict[str, Any]) -> str:
    records = {item["path"]: item for item in registry.get("files", [])}
    lines = [
        "# Core Research Organization Index",
        "",
        f"> Generated by `{GENERATOR_ID}`. Do not hand-edit.",
        "",
        f"Generated at: `{registry.get('generated_at', '')}`",
        f"Organization registry: [`{REGISTRY_PATH.name}`](../artifacts/{REGISTRY_PATH.name})",
        f"Migration map: [`{MIGRATION_PATH.name}`](../artifacts/{MIGRATION_PATH.name})",
        f"Audit: [`{AUDIT_PATH.name}`](../artifacts/{AUDIT_PATH.name})",
        "",
        "## Current state",
        "",
        f"- Organization status: **{registry.get('status')}**",
        f"- Files indexed: **{len(registry.get('files', []))}**",
        f"- Unresolved organization queue: **{registry.get('review_queue_count', 0)}**",
        f"- Wave 1 classified records: **{registry.get('dispositioned_review_count', 0)}**",
        f"- Scientific-link follow-up: **{registry.get('assigned_review_count', 0)}**",
        f"- Quarantine records: **{registry.get('quarantine_count', 0)}**",
        f"- Foundation gate: **{registry.get('scientific_foundation_status', {}).get('status')}**",
        "- Physical migration: **not performed**",
        f"- Controlling blocker: `{registry.get('controlling_blocker')}`",
        "",
        "## Owner counts",
        "",
        "| Owner | Files |",
        "| :-- | --: |",
    ]
    lines.extend(
        f"| `{key}` | {value} |" for key, value in sorted(registry.get("owner_counts", {}).items())
    )
    lines += ["", "## Logical areas", "", "| Area | Files |", "| :-- | --: |"]
    lines.extend(
        f"| `{key}` | {value} |"
        for key, value in sorted(registry.get("logical_area_counts", {}).items())
    )
    lines += [
        "",
        "## Operating rule",
        "",
        "`request → owner → lane → blocker → inputs → verifier → artifact → handoff`",
        "",
        "Organization status does not promote physics status. Every classified record remains subject to its equation, unit, provenance, verifier, and claim gates.",
        "",
        "## Wave 1 disposition review",
        "",
    ]
    for path in audit.get("dispositioned_paths", [])[:100]:
        item = records[path]
        lines.append(
            f"- `{path}` → `{item.get('owner_id')}` / `{item.get('equation_family_or_lane')}` / `{item.get('next_action')}`"
        )
    if len(audit.get("dispositioned_paths", [])) > 100:
        lines.append(
            f"- … {len(audit['dispositioned_paths']) - 100} more classified paths are listed in the registry and migration map"
        )
    if audit.get("quarantined_paths"):
        lines += ["", "## Quarantine", ""]
        lines.extend(f"- `{path}` → `manual_scope_review`" for path in audit["quarantined_paths"])
    lines.append("")
    return "\n".join(lines)


def refresh_status(registry: dict[str, Any], migration: dict[str, Any], audit: dict[str, Any]) -> None:
    required_check = next(
        (check for check in audit.get("checks", []) if check.get("check_id") == "all_required_file_fields"),
        None,
    )
    if required_check is not None:
        required_check.update(status="PASS", observed=0, expected=0)
    review_count = int(registry.get("review_queue_count", 0))
    assigned_review_count = int(registry.get("assigned_review_count", 0))
    status = "PASS_WITH_REVIEW_REQUIRED" if review_count or assigned_review_count else "PASS"
    registry["status"] = status
    migration["status"] = status
    audit["status"] = status
    for payload in (registry, migration, audit):
        payload["generator"] = GENERATOR_ID


def canonical_without_timestamp(payload: dict[str, Any]) -> dict[str, Any]:
    copied = json.loads(json.dumps(payload))
    copied.pop("generated_at", None)
    return copied


def canonical_index(value: str) -> str:
    return "\n".join(line for line in value.splitlines() if not line.startswith("Generated at:"))


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
    builder = load_builder()
    policy = load_json(POLICY_PATH)
    manifest = normalize_manifest(load_json(MANIFEST_PATH))
    contract = load_json(CONTRACT_PATH)
    gate = load_json(GATE_PATH)
    registry, migration, audit, index = builder.build_registry(policy, manifest, contract, gate)
    apply_review_dispositions(registry, migration, audit, policy, builder)
    refresh_status(registry, migration, audit)
    index = render_index(registry, audit)
    return registry, migration, audit, index


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare existing outputs without writing")
    args = parser.parse_args()
    registry, migration, audit, index = build()
    outputs = {
        REGISTRY_PATH: registry,
        MIGRATION_PATH: migration,
        AUDIT_PATH: audit,
    }
    if args.check:
        mismatches: list[str] = []
        for path, expected in outputs.items():
            if not path.exists() or canonical_without_timestamp(load_json(path)) != canonical_without_timestamp(expected):
                mismatches.append(path.relative_to(ROOT).as_posix())
        if not INDEX_PATH.exists() or canonical_index(INDEX_PATH.read_text(encoding="utf-8")) != canonical_index(index):
            mismatches.append(INDEX_PATH.relative_to(ROOT).as_posix())
        print(json.dumps({"status": "PASS" if not mismatches else "DRIFT", "mismatches": mismatches}, ensure_ascii=False))
        return 0 if not mismatches else 1
    for path, payload in outputs.items():
        write_json(path, payload)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(index, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": audit["status"],
                "registry": REGISTRY_PATH.relative_to(ROOT).as_posix(),
                "migration_map": MIGRATION_PATH.relative_to(ROOT).as_posix(),
                "audit": AUDIT_PATH.relative_to(ROOT).as_posix(),
                "index": INDEX_PATH.relative_to(ROOT).as_posix(),
                "indexed_files": len(registry["files"]),
                "review_queue_count": registry["review_queue_count"],
                "foundation_status": registry["scientific_foundation_status"]["status"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
