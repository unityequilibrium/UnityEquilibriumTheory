"""Regression checks for the bounded covariant-parent scientific-link package."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = repo_root()
def load_json(name: str) -> dict:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def test_covariant_parent_family_has_explicit_scientific_chain() -> None:
    contract = load_json("uet_core_equation_family_contract.json")
    family = next(
        item
        for item in contract["families"]
        if item["family_id"] == "core.covariant_parent"
    )

    assert family["module_paths"] == [
        "docs/core/02_equations/covariant/uet_covariant_parent.py"
    ]
    assert family["unit_lane"] == "natural_only_v1"
    assert family["formula_ids"] == ["uet.main_theory.covariant_parent"]
    assert all((ROOT / path).exists() for path in family["verifier_paths"])
    assert all((ROOT / path).exists() for path in family["evidence_paths"])
    assert family["organization_review_required"] is True
    assert "not a metric PDE solver" in family["claim_ceiling"]


def test_covariant_parent_record_materializes_links_without_promotion() -> None:
    registry = load_json("uet_research_organization_registry.json")
    records = [
        item
        for item in registry["files"]
        if item.get("equation_family_or_lane") == "core.covariant_parent"
        and item.get("current_path") == item.get("canonical_path")
    ]

    assert {item["path"] for item in records} == {
        "docs/core/02_equations/covariant/uet_covariant_parent.py"
    }
    record = records[0]
    assert record["formula_ids"] == ["uet.main_theory.covariant_parent"]
    assert record["unit_lane"] == "natural_only_v1"
    assert record["verifier_paths"]
    assert record["artifact_paths"]
    assert record["claim_ceiling"]
    assert record["evidence_status"] == "BLOCKED"
    assert record["organization_status"] == "MIGRATED"
    assert record["registry_link_status"] == "CANONICAL_PATH"


def test_covariant_parent_family_points_to_the_central_record() -> None:
    family = next(
        item
        for item in load_json("uet_core_equation_family_contract.json")["families"]
        if item["family_id"] == "core.covariant_parent"
    )
    central = load_json("uet_equation_correspondence_registry.json")
    entry = next(
        item
        for item in central["entries"]
        if item["equation_id"] == family["formula_ids"][0]
    )

    assert entry["unit_lane"] == "natural_only_v1"
    assert entry["implementation_paths"]
    assert entry["verifier_paths"]
    assert entry["claim_boundary"]
