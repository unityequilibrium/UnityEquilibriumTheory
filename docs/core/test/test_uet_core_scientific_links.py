"""Regression checks for the Wave 2 scientific-link audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"


def load_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_scientific_link_audit_keeps_open_links_blocked() -> None:
    audit = load_json("uet_core_scientific_link_audit.json")

    assert audit["audit_status"] == "BLOCKED_OPEN_SCIENTIFIC_LINKS"
    assert audit["summary"]["assigned_records"] == 133
    assert audit["summary"]["audited_records"] == 133
    assert audit["summary"]["canonical_family_contract_matches"] == 1
    assert audit["summary"]["families_without_canonical_contract"] == 8
    assert audit["summary"]["records_without_canonical_contract"] == 131
    assert audit["summary"]["missing_link_field_counts"] == {
        "artifact_paths": 131,
        "claim_ceiling": 131,
        "formula_ids": 131,
        "unit_lane": 131,
        "verifier_paths": 131,
    }
    assert audit["summary"]["records_with_formula_ids"] == 2
    assert audit["summary"]["records_with_unit_lane"] == 2
    assert audit["summary"]["records_with_verifier_paths"] == 2
    assert audit["summary"]["records_with_artifact_paths"] == 2
    assert audit["summary"]["records_with_claim_ceiling"] == 2
    flux_family = next(
        family for family in audit["families"]
        if family["family_or_lane"] == "core.matter_space_flux"
    )
    assert flux_family["link_status"] == "LINKED_PENDING_VERIFICATION"
    assert all(
        family["link_status"].startswith("BLOCKED")
        for family in audit["families"]
        if family is not flux_family
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
