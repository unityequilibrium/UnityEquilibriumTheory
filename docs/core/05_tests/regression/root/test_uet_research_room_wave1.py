"""Focused contract tests for the UET Wave 1 research-room checkpoint."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path, repo_root

import json
from pathlib import Path


ROOT = (repo_root() / "docs")


def read_json(relative: str) -> dict:
    if relative.startswith("core/artifacts/"):
        return json.loads(
            canonical_artifact_path(relative.split("/")[-1]).read_text(
                encoding="utf-8-sig"
            )
        )
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def test_wave1_contract_has_explicit_mapping_fields_and_rooms() -> None:
    contract = read_json("core/artifacts/uet_research_room_wave1_contract.json")
    required = set(contract["required_mapping_fields"])
    assert contract["claim_promotion"] is False
    assert set(contract["rooms"]) == {"core", "topic_0_13", "topic_0_11", "core_o2", "topic_0_10_comparator"}
    for room in contract["rooms"].values():
        assert required <= set(room)
        assert room["claim_boundary"]
        assert room["next_action"]


def test_thermal_branch_keeps_reference_and_full_candidate_separate() -> None:
    branch = read_json("topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json")
    assert branch["gates"]["locked_threshold_unchanged"] is True
    assert branch["gates"]["selected_causal_reference_prearrival_leakage"] is True
    assert branch["selected_causal_branch"]["prearrival_leakage_fraction"] <= 1.0e-6
    assert branch["gates"]["full_candidate_prearrival_leakage"] is False
    assert branch["full_candidate_branch"]["prearrival_leakage_fraction"] > 1.0e-6
    assert branch["source_contract"]["holdout_consumed"] is False
    assert branch["source_contract"]["numeric_fitting_allowed"] is False
    assert branch["claim_promotion"] is False


def test_provenance_gate_matches_local_source_and_holdout_policy() -> None:
    provenance = read_json("core/artifacts/thermal_source_provenance_gate.json")
    assert provenance["status"] in {"PASS_WITH_PROVISIONAL_DIGITIZATION", "PASS_WITH_FIGURE_DERIVED_NORMALIZED_COMPARISON"}
    assert provenance["metrics"]["provenance_complete"] is True
    assert provenance["metrics"]["local_numeric_count"] >= 1
    assert provenance["metrics"]["holdout_consumed"] is False
    assert provenance["gates"]["hash_match"] is True
    assert provenance["gates"]["uncertainty"] is True
    assert provenance["gates"]["row_identity"] is True


def test_wave1_registry_entries_are_present_without_promotion() -> None:
    registry = read_json("core/artifacts/uet_equation_correspondence_registry.json")
    ids = {entry["equation_id"] for entry in registry["entries"]}
    assert {
        "uet.thermal.ttg_normalized_observable",
        "uet.thermal.causal_reference_branch",
        "uet.phase.structure_factor_estimator_policy",
        "uet.fluid.standard_comparator",
    } <= ids
    assert registry["status"] == "CENTRAL_REGISTRY_WITH_CANDIDATE_ADDENDA_BLOCKED"


def test_housekeeping_does_not_control_thermal_room() -> None:
    gate = read_json("core/artifacts/uet_research_room_wave1_integration_gate.json")
    assert gate["housekeeping"]["topic_0_22_separate_checkpoint"]["status"] == "SEPARATE_PREEXISTING_CHECKPOINT"
    assert gate["rooms"]["topic_0_13"]["claim_boundary"]
    assert gate["claim_promotion"] is False
