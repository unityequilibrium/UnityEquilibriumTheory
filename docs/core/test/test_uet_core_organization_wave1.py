"""Regression checks for the non-destructive Wave 1 organization pass."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"


def load_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_wave1_covers_previous_review_queue_without_physical_move() -> None:
    registry = load_json("uet_research_organization_registry.json")
    migration = load_json("uet_core_file_migration_map.json")
    audit = load_json("uet_core_organization_audit.json")

    assert registry["organization_wave"] == "WAVE_1_ASSIGN_AND_QUARANTINE"
    review_count = registry["pre_disposition_review_count"]
    assert registry["dispositioned_review_count"] == review_count

    assert registry["undispositioned_review_count"] == 0
    assert registry["review_queue_count"] == registry["quarantine_count"]
    assert registry["assigned_review_count"] == review_count

    assert audit["undispositioned_paths"] == []
    assert audit["unassigned_paths"] == []
    assert registry["quarantine_count"] == len(audit["quarantined_paths"])
    assert migration["physical_move_performed"] is False


def test_wave1_assignments_do_not_promote_scientific_evidence() -> None:
    registry = load_json("uet_research_organization_registry.json")
    assigned = [
        item
        for item in registry["files"]
        if item.get("organization_disposition") is not None
    ]

    assert len(assigned) == registry["pre_disposition_review_count"]
    assert all(item["evidence_status"] == "BLOCKED" for item in assigned)
    assert all(item["status_source"].endswith("uet_research_organization_policy.json") for item in assigned)
    assert registry["scientific_foundation_status"]["status"] == "BLOCKED"
    assert registry["controlling_blocker"] in {"assigned_records_need_scientific_link_review", "manual_scope_review_for_quarantined_records"}


def test_wave1_disposition_rules_are_explicit_and_used() -> None:
    policy = load_json("../00_governance/uet_research_organization_policy.json")
    registry = load_json("uet_research_organization_registry.json")
    rule_ids = {rule["disposition_id"] for rule in policy["review_disposition_rules"]}
    used_ids = set(registry["disposition_counts"])

    assert len(rule_ids) == 14
    assert used_ids <= rule_ids
    assert used_ids >= {
        "W1-T13-HOLDOUT",
        "W1-EQUATION-O2-EXTENDED",
        "W1-LANE-THERMAL-SUPPORT",
    }
