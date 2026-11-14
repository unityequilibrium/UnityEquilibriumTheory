"""Regression checks for the bounded Noether mapping scientific-link package."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = repo_root()
def load_json(name: str) -> dict:
    return json.loads(
        canonical_artifact_path(name).read_text(encoding="utf-8-sig")
    )


FORMULA_IDS = [
    "uet.noether_mapping.frame_projected_charge_density",
    "uet.noether_mapping.affine_phase_coordinate",
    "uet.noether_mapping.normalized_current_coordinate",
    "uet.noether_mapping.continuity_residual_scaling",
    "uet.noether_mapping.o2_polar_current",
    "uet.noether_mapping.symmetric_double_well_conjugacy",
    "uet.noether_mapping.normalized_constitutive_scales",
]


def test_noether_mapping_family_has_explicit_scientific_chain() -> None:
    contract = load_json("uet_core_equation_family_contract.json")
    family = next(
        item
        for item in contract["families"]
        if item["family_id"] == "core.noether_mapping"
    )

    assert family["module_paths"] == [
        "docs/core/02_equations/lorentz_noether/uet_noether.py",
        "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py",
    ]
    assert family["unit_lane"] == "natural_parent_plus_normalized_map"
    assert family["formula_ids"] == FORMULA_IDS
    assert all((ROOT / path).exists() for path in family["verifier_paths"])
    assert all((ROOT / path).exists() for path in family["evidence_paths"])
    assert family["organization_review_required"] is True
    assert "no universal C ontology" in family["claim_ceiling"]


def test_noether_mapping_records_materialize_links_without_promotion() -> None:
    registry = load_json("uet_research_organization_registry.json")
    records = [
        item
        for item in registry["files"]
        if item.get("equation_family_or_lane") == "core.noether_mapping"
        and item.get("current_path") == item.get("canonical_path")
    ]

    assert {item["path"] for item in records} == {
        "docs/core/02_equations/lorentz_noether/uet_noether.py",
        "docs/core/02_equations/lorentz_noether/uet_noether_phase_field_map.py",
    }
    for record in records:
        assert record["formula_ids"] == FORMULA_IDS
        assert record["unit_lane"] == "natural_parent_plus_normalized_map"
        assert record["verifier_paths"]
        assert record["artifact_paths"]
        assert record["claim_ceiling"] == "mapping/diagnostic only; no universal C ontology"
        assert record["evidence_status"] == "BLOCKED"
        assert record["organization_status"] == "MIGRATED"
        assert record["registry_link_status"] == "CANONICAL_PATH"


def test_noether_mapping_family_points_to_central_records() -> None:
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
        assert all(
            "::" not in path for path in entry["implementation_paths"]
        )
        assert entry["verifier_paths"]
        assert entry["claim_boundary"]
        assert entry["evidence_class"].startswith("INTERNAL_")
    assert any(
        "universal C" in entry["claim_boundary"] for entry in entries.values()
    )
    assert any(
        "microscopic" in entry["failure_mode"] for entry in entries.values()
    )


def test_noether_mapping_addendum_preserves_warn_and_blocked_scope() -> None:
    addendum = load_json(
        "uet_equation_correspondence_registry_noether_mapping_addendum.json"
    )
    formula_audit = load_json("noether_phase_field_map_formula_audit.json")
    verification = load_json("noether_phase_field_state_map_verification.json")
    dependency = load_json("noether_phase_field_dependency_gate.json")

    assert addendum["status"] == "CANDIDATE_ENTRY_MERGED_INTO_CENTRAL_REGISTRY"
    assert [item["equation_id"] for item in addendum["equation_entries"]] == FORMULA_IDS
    assert addendum["merge_metadata"]["claim_promotion"] is False
    assert formula_audit["status"] == "WARN"
    assert verification["audit_status"] == "PASS"
    assert verification["evidence_status"] == "PARTIAL_HYDRODYNAMIC_STATE_COORDINATE_MAP"
    assert dependency["status"] == "BLOCKED"
    assert dependency["controlling_blocker"] == (
        "noether_charge_equation_of_state_and_covariant_transport_matching_missing"
    )
    assert "equation_of_state_from_covariant_O2_action" in addendum["open_gates"]
    assert "system_specific_SI_map" in addendum["open_gates"]
