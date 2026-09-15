"""Regression checks for the Wave 2 scientific-link audit."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"


def load_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_scientific_link_audit_keeps_open_links_blocked() -> None:
    audit = load_json("uet_core_scientific_link_audit.json")

    assert audit["audit_status"] == "BLOCKED_OPEN_SCIENTIFIC_LINKS"
    assert audit["summary"]["assigned_records"] == 137
    assert audit["summary"]["audited_records"] == 137
    assert audit["summary"]["canonical_family_contract_matches"] == 5
    assert audit["summary"]["families_without_canonical_contract"] == 8
    assert audit["summary"]["records_without_canonical_contract"] == 130
    assert audit["summary"]["missing_link_field_counts"] == {
        "artifact_paths": 130,
        "claim_ceiling": 130,
        "formula_ids": 130,
        "unit_lane": 130,
        "verifier_paths": 130,
    }
    assert audit["summary"]["records_with_formula_ids"] == 7
    assert audit["summary"]["records_with_unit_lane"] == 7
    assert audit["summary"]["records_with_verifier_paths"] == 7
    assert audit["summary"]["records_with_artifact_paths"] == 7
    assert audit["summary"]["records_with_claim_ceiling"] == 7
    flux_family = next(
        family for family in audit["families"]
        if family["family_or_lane"] == "core.matter_space_flux"
    )
    assert flux_family["link_status"] == "LINKED_PENDING_VERIFICATION"
    parent_family = next(
        family for family in audit["families"]
        if family["family_or_lane"] == "core.covariant_parent"
    )
    assert parent_family["link_status"] == "LINKED_PENDING_VERIFICATION"
    diffusion_family = next(
        family for family in audit["families"]
        if family["family_or_lane"] == "core.covariant_diffusion"
    )
    assert diffusion_family["link_status"] == "LINKED_PENDING_VERIFICATION"
    noether_family = next(
        family for family in audit["families"]
        if family["family_or_lane"] == "core.noether_mapping"
    )
    assert noether_family["link_status"] == "LINKED_PENDING_VERIFICATION"
    trace_family = next(
        family for family in audit["families"]
        if family["family_or_lane"] == "core.trace"
    )
    assert trace_family["link_status"] == "LINKED_PENDING_VERIFICATION"
    assert all(
        family["link_status"].startswith("BLOCKED")
        for family in audit["families"]
        if family["family_or_lane"] not in {
            "core.matter_space_flux",
            "core.covariant_parent",
            "core.covariant_diffusion",
            "core.noether_mapping",
            "core.trace",
        }
    )


def test_scientific_link_audit_preserves_organization_boundary() -> None:
    audit = load_json("uet_core_scientific_link_audit.json")
    checks = {check["check_id"]: check for check in audit["checks"]}

    assert checks["assigned_records_are_all_audited"]["status"] == "PASS"
    assert checks["assigned_source_paths_exist"]["status"] == "PASS"
    assert checks["organization_does_not_promote_evidence"]["status"] == "PASS"
    assert checks["foundation_gate_remains_blocked"]["status"] == "PASS"
    assert checks["physical_move_not_performed"]["status"] == "PASS"
    assert audit["claim_boundary"].startswith("organization/scientific-link audit only")


def test_correspondence_case_lint_is_visible_without_declaring_json_invalid() -> None:
    audit = load_json("uet_core_scientific_link_audit.json")

    assert ["G_munu", "g_munu"] in audit["case_insensitive_key_collisions"]
    collision_check = next(
        check for check in audit["checks"]
        if check["check_id"] == "case_insensitive_metadata_key_lint"
    )
    assert collision_check["status"] == "REVIEW_REQUIRED"
    assert audit["checks"][-1]["check_id"] == "case_insensitive_metadata_key_lint"
