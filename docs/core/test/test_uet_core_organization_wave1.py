"""Regression checks for the organization control plane and review boundary."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"


def load_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_organization_registry_covers_review_queue_without_promoting_physics() -> None:
    registry = load_json("uet_research_organization_registry.json")
    migration = load_json("uet_core_file_migration_map.json")
    audit = load_json("uet_core_organization_audit.json")

    assert registry["status"] in {"PASS_WITH_REVIEW_REQUIRED", "PASS"}
    assert len(registry["files"]) == sum(registry["counts"].values())
    assert registry["review_queue_count"] == len(audit["unassigned_paths"]) + len(audit["quarantined_paths"])
    assert migration["physical_move_performed"] is False
    assert {item["asset_id"] for item in migration["files"]} == {
        item["asset_id"] for item in registry["files"]
    }
    assert registry["scientific_foundation_status"]["status"] == "BLOCKED"
    assert audit["claim_boundary"]


def test_review_items_have_explicit_next_actions_and_blocked_evidence() -> None:
    registry = load_json("uet_research_organization_registry.json")
    review_items = [
        item for item in registry["files"] if item["organization_status"] in {"UNASSIGNED", "QUARANTINED"}
    ]

    assert review_items
    assert all(item["next_action"] for item in review_items)
    assert all(item["evidence_status"] == "BLOCKED" for item in review_items)
    assert all(item["status_source"] for item in review_items)


def test_organization_policy_and_canonical_migration_remain_distinct() -> None:
    policy = load_json("../00_governance/uet_research_organization_policy.json")
    registry = load_json("uet_research_organization_registry.json")
    migration = load_json("uet_core_file_migration_map.json")

    rule_ids = {rule["disposition_id"] for rule in policy["review_disposition_rules"]}
    assert len(rule_ids) == len(policy["review_disposition_rules"])
    assert registry["rules"]["organization_status_does_not_promote_physics"] is True
    assert all(item["compatibility_plan"] for item in migration["files"])
    assert migration["controlling_blocker"]