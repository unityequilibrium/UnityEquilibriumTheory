"""Regression checks for the bounded matter-space flux scientific-link package."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = repo_root()
def load_json(path: Path) -> dict:
    path = Path(path)
    return json.loads(
        canonical_artifact_path(path.name).read_text(encoding="utf-8")
    )


def test_flux_family_contract_has_explicit_scientific_chain() -> None:
    contract = load_json("uet_core_equation_family_contract.json")
    family = next(item for item in contract["families"] if item["family_id"] == "core.matter_space_flux")

    assert family["module_paths"] == [
        "docs/core/02_equations/matter_space/uet_matter_space_flux_telegraph.py",
        "docs/core/02_equations/matter_space/uet_matter_space_flux_phi.py",
    ]
    assert family["unit_lane"] == "normalized_v1"
    assert family["formula_ids"] == [
        "uet.matter_space_flux.conservation",
        "uet.matter_space_flux.relaxation",
        "uet.matter_space_flux.phi_response",
        "uet.matter_space_flux.shared_energy_ledger",
    ]
    assert all((ROOT / path).exists() for path in family["verifier_paths"])
    assert all((ROOT / path).exists() for path in family["evidence_paths"])
    assert family["organization_review_required"] is True
    assert "not SI" in family["claim_ceiling"]


def test_flux_records_materialize_links_without_promoting_evidence() -> None:
    registry = load_json("uet_research_organization_registry.json")
    records = [
        item
        for item in registry["files"]
        if item.get("equation_family_or_lane") == "core.matter_space_flux"
        and item.get("current_path") == item.get("canonical_path")
    ]

    assert {item["path"] for item in records} == {
        "docs/core/02_equations/matter_space/uet_matter_space_flux_phi.py",
        "docs/core/02_equations/matter_space/uet_matter_space_flux_telegraph.py",
    }
    assert all(item["formula_ids"] for item in records)
    assert all(item["unit_lane"] == "normalized_v1" for item in records)
    assert all(item["verifier_paths"] for item in records)
    assert all(item["artifact_paths"] for item in records)
    assert all(item["claim_ceiling"] for item in records)
    assert all(item["evidence_status"] == "BLOCKED" for item in records)
    assert all(item["organization_status"] == "MIGRATED" for item in records)
    assert all(item["registry_link_status"] == "CANONICAL_PATH" for item in records)


def test_flux_formula_ids_are_present_in_central_correspondence_registry() -> None:
    family = next(
        item
        for item in load_json("uet_core_equation_family_contract.json")["families"]
        if item["family_id"] == "core.matter_space_flux"
    )
    central = load_json("uet_equation_correspondence_registry.json")
    entries = {
        entry["equation_id"]: entry
        for entry in central["entries"]
    }

    assert set(family["formula_ids"]) <= set(entries)
    for equation_id in family["formula_ids"]:
        entry = entries[equation_id]
        assert entry["unit_lane"] == "normalized_v1"
        assert entry["implementation_paths"]
        assert entry["verifier_paths"]
        assert entry["claim_boundary"]
