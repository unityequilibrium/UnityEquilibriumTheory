"""Regression tests for the core organization control plane."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"


def load(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_registry_has_one_owner_and_role_per_file() -> None:
    registry = load("uet_research_organization_registry.json")
    declared_owners = {item["owner_id"] for item in registry["owners"]}
    declared_rooms = {item["room_id"] for item in registry["rooms"]}
    required = {
        "asset_id",
        "path",
        "file_kind",
        "logical_area",
        "owner_id",
        "room_id",
        "organization_status",
        "evidence_status",
        "status_source",
        "generated_or_source",
        "formula_ids",
        "verifier_paths",
        "artifact_paths",
        "upstream_dependencies",
        "downstream_dependencies",
        "sha256",
        "migration_state",
        "next_action",
    }
    files = registry["files"]
    assert files
    assert len({item["asset_id"] for item in files}) == len(files)
    for item in files:
        assert required <= set(item)
        assert item["owner_id"] in declared_owners
        assert item["room_id"] in declared_rooms
        assert item["next_action"]


def test_migration_map_preserves_current_paths_and_does_not_move_files() -> None:
    registry = load("uet_research_organization_registry.json")
    migration = load("uet_core_file_migration_map.json")
    assert migration["physical_move_performed"] is False
    assert {item["asset_id"] for item in migration["files"]} == {
        item["asset_id"] for item in registry["files"]
    }
    for item in migration["files"]:
        assert item["current_path"].startswith("docs/core/")
        assert item["target_path"].startswith("docs/core/")
        assert item["compatibility_plan"]


def test_organization_audit_does_not_promote_foundation_gate() -> None:
    audit = load("uet_core_organization_audit.json")
    registry = load("uet_research_organization_registry.json")
    assert audit["claim_boundary"]
    assert registry["scientific_foundation_status"]["status"] == "BLOCKED"
    assert registry["status"] in {"PASS_WITH_REVIEW_REQUIRED", "PASS"}
    assert all(check["status"] in {"PASS", "REVIEW_REQUIRED"} for check in audit["checks"])
