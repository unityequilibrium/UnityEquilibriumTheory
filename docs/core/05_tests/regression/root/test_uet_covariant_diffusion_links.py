"""Regression checks for the bounded covariant-diffusion scientific-link package."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = repo_root()
def load_json(name: str) -> dict:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


FORMULA_IDS = [
    "uet.covariant_diffusion.frame_decomposition",
    "uet.covariant_diffusion.finite_relaxation_current",
    "uet.covariant_diffusion.energy_identity",
    "uet.covariant_diffusion.adiabatic_model_b_limit",
]


def test_covariant_diffusion_family_has_explicit_scientific_chain() -> None:
    contract = load_json("uet_core_equation_family_contract.json")
    family = next(
        item
        for item in contract["families"]
        if item["family_id"] == "core.covariant_diffusion"
    )

    assert family["module_paths"] == [
        "docs/core/02_equations/covariant/uet_covariant_diffusion.py"
    ]
    assert family["unit_lane"] == "natural_or_normalized_control"
    assert family["formula_ids"] == FORMULA_IDS
    assert all((ROOT / path).exists() for path in family["verifier_paths"])
    assert all((ROOT / path).exists() for path in family["evidence_paths"])
    assert family["organization_review_required"] is True
    assert "coefficient provenance" in family["claim_ceiling"]


def test_covariant_diffusion_record_materializes_links_without_promotion() -> None:
    registry = load_json("uet_research_organization_registry.json")
    records = [
        item
        for item in registry["files"]
        if item.get("equation_family_or_lane") == "core.covariant_diffusion"
        and item.get("current_path") == item.get("canonical_path")
    ]

    assert {item["path"] for item in records} == {
        "docs/core/02_equations/covariant/uet_covariant_diffusion.py"
    }
    record = records[0]
    assert record["formula_ids"] == FORMULA_IDS
    assert record["unit_lane"] == "natural_or_normalized_control"
    assert record["verifier_paths"]
    assert record["artifact_paths"]
    assert record["claim_ceiling"]
    assert record["evidence_status"] == "BLOCKED"
    assert record["organization_status"] == "MIGRATED"
    assert record["registry_link_status"] == "CANONICAL_PATH"


def test_covariant_diffusion_family_points_to_central_records() -> None:
    central = load_json("uet_equation_correspondence_registry.json")
    entries = {
        item["equation_id"]: item
        for item in central["entries"]
        if item.get("equation_id") in FORMULA_IDS
    }

    assert set(entries) == set(FORMULA_IDS)
    for entry in entries.values():
        assert entry["unit_lane"] == "natural_to_normalized"
        assert entry["implementation_paths"]
        assert entry["verifier_paths"]
        assert entry["claim_boundary"]
        assert entry["evidence_class"] == "INTERNAL_CONSTITUTIVE_NUMERICAL"


def test_covariant_diffusion_addendum_preserves_partial_scope() -> None:
    addendum = load_json(
        "uet_equation_correspondence_registry_covariant_diffusion_addendum.json"
    )

    assert addendum["status"] == "CANDIDATE_ENTRY_MERGED_INTO_CENTRAL_REGISTRY"
    assert [item["equation_id"] for item in addendum["equation_entries"]] == FORMULA_IDS
    assert addendum["merge_metadata"]["claim_promotion"] is False
    assert "first_order_hyperbolic_gradient_phase_field" in addendum["open_gates"]
    assert "system_specific_SI_map" in addendum["open_gates"]
