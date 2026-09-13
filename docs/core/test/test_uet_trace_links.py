"""Regression checks for the bounded derived-trace family link."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "docs" / "core" / "artifacts"


def load_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8-sig"))


FORMULA_IDS = ["uet.trace.derived_observable"]


def test_trace_family_has_explicit_scientific_chain() -> None:
    contract = load_json("uet_core_equation_family_contract.json")
    family = next(
        item
        for item in contract["families"]
        if item["family_id"] == "core.trace"
    )

    assert family["module_paths"] == ["docs/core/uet_trace.py"]
    assert family["unit_lane"] == "normalized_v1"
    assert family["formula_ids"] == FORMULA_IDS
    assert all((ROOT / path).exists() for path in family["verifier_paths"])
    assert all((ROOT / path).exists() for path in family["evidence_paths"])
    assert family["organization_review_required"] is True
    assert "derived observable" in family["claim_ceiling"]


def test_trace_record_materializes_links_without_promotion() -> None:
    registry = load_json("uet_research_organization_registry.json")
    records = [
        item
        for item in registry["files"]
        if item.get("equation_family_or_lane") == "core.trace"
        and item.get("path") == "docs/core/uet_trace.py"
    ]

    assert len(records) == 1
    record = records[0]
    assert record["formula_ids"] == FORMULA_IDS
    assert record["unit_lane"] == "normalized_v1"
    assert record["verifier_paths"]
    assert record["artifact_paths"]
    assert record["claim_ceiling"] == "diagnostic derived observable; no substance/energy-reservoir claim"
    assert record["evidence_status"] == "BLOCKED"
    assert record["organization_disposition"] == "W2-EQUATION-TRACE"
    assert record["registry_link_status"] == "ORGANIZATION_POLICY_ASSIGNED"


def test_trace_family_points_to_existing_central_record() -> None:
    central = load_json("uet_equation_correspondence_registry.json")
    entries = [
        item
        for item in central["entries"]
        if item.get("equation_id") in FORMULA_IDS
    ]

    assert len(entries) == 1
    entry = entries[0]
    assert entry["unit_lane"] == "normalized"
    assert entry["implementation_paths"]
    assert all("::" not in path for path in entry["implementation_paths"])
    assert entry["verifier_paths"]
    assert entry["observable_mapping"]["status"] == "BLOCKED"
    assert "no backreaction" in entry["claim_boundary"]
    assert entry["evidence_class"] == "INTERNAL"


def test_trace_artifacts_keep_derived_only_boundary() -> None:
    verification = load_json("spacetime_trace_verification.json")
    formula_audit = load_json("trace_kernel_formula_audit.json")

    assert verification["status"] == "WARN"
    assert verification["internal_gate_status"] == "PASS"
    assert verification["units_contract"] == "normalized lane checked; SI lane open"
    assert verification["claim_boundary"] == "candidate mechanism; simulation-only benchmark"
    assert formula_audit["status"] == "WARN"
    assert "trace must be treated as new mass or energy" in " ".join(
        formula_audit["falsification_conditions"]
    )
