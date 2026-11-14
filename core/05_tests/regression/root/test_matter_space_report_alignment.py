"""Artifact-boundary tests for the post-Wave-9 report addendum."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path

from docs.scripts.audit.audit_matter_space_report_alignment import (
    ADDENDUM_PATH,
    BASE_MATTER_CONTROLLER,
    BASE_REPORT_PATH,
    GR_CONTROLLER,
    OUTPUT_PATH,
    build_alignment_gate,
)


ROOT = repo_root()


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_generated_alignment_gate_matches_current_inputs() -> None:
    artifact = _read(OUTPUT_PATH)
    assert artifact == build_alignment_gate(generated_at=artifact["generated_at"])
    assert artifact["source_snapshot_at"] <= artifact["generated_at"]


def test_historical_report_is_retained_with_addendum_warning() -> None:
    artifact = _read(OUTPUT_PATH)
    assert artifact["status"] == "WARN"
    assert artifact["alignment_status"] == "PASS_WITH_HISTORICAL_BASE_REPORT_WARN"
    assert artifact["report_status_impact"] == "NONE"
    assert artifact["gates"]["base_report_scope_gate"]["status"] == "PASS"
    assert artifact["gates"]["post_wave10_addendum_gate"]["status"] == "PASS"
    assert BASE_REPORT_PATH.is_file()
    assert ADDENDUM_PATH.is_file()


def test_matter_space_and_extended_gr_controllers_are_separate() -> None:
    artifact = _read(OUTPUT_PATH)
    assert artifact["base_matter_space_controller"] == BASE_MATTER_CONTROLLER
    assert artifact["controlling_blocker"] == GR_CONTROLLER
    gate = artifact["gates"]["controller_separation_gate"]
    assert gate["status"] == "PASS"
    assert gate["matter_space_controller"] != gate["extended_gr_controller"]


def test_exact_gr_null_does_not_decide_global_universe_closure() -> None:
    artifact = _read(OUTPUT_PATH)
    gate = artifact["gates"]["gr_null_vs_global_closure_gate"]
    assert gate["status"] == "PASS"
    assert gate["gr_null_model"] == {
        "parameter": "epsilon_nc",
        "value": 0,
        "verification_status": "PASS",
    }
    assert gate["global_universe_closure"] == "UNRESOLVED"
    assert artifact["global_universe_closure"] == "UNRESOLVED"


def test_topic_0_11_historical_status_drift_is_explicit() -> None:
    artifact = _read(OUTPUT_PATH)
    gate = artifact["gates"]["topic_0_11_historical_status_gate"]
    assert gate["status"] == "WARN"
    assert gate["drift_detected"] is True
    assert gate["historical_report_status"] == "Draft"
    assert gate["canonical_status"] == "Structured"
    assert gate["canonical_tier"] == "B"
    assert artifact["canonical_topics"]["0.11"]["status"] == "Structured"


def test_downstream_dependency_packets_do_not_promote_topics() -> None:
    artifact = _read(OUTPUT_PATH)
    gate = artifact["gates"]["downstream_dependency_gate"]
    assert gate["status"] == "PASS"
    for topic in ("topic_0_11", "topic_0_19", "topic_0_13"):
        assert gate[topic]["status"] == "BLOCKED"
        assert gate[topic]["topic_status_impact"] == "NONE"
    assert artifact["canonical_topics"]["0.19"] == {
        "name": "0.19_Gravity_GR",
        "status": "Draft",
        "tier": "B",
    }
    assert artifact["canonical_topics"]["0.13"] == {
        "name": "0.13_Thermodynamic_Bridge",
        "status": "Draft",
        "tier": "B",
    }


def test_ontology_and_claim_boundaries_remain_restricted() -> None:
    artifact = _read(OUTPUT_PATH)
    ontology = artifact["gates"]["ontology_separation_gate"]
    assert ontology["status"] == "PASS"
    assert ontology["trace_backreaction"] is False
    assert ontology["phi_metric_identity"] is False
    assert ontology["equation_of_state_derived"] is False
    claims = artifact["gates"]["claim_boundary_gate"]
    assert claims["status"] == "PASS"
    assert "the complete universe is proved open or closed" in claims["blocked"]
    assert "downstream topic promotion or external validation" in claims["blocked"]


def test_all_recorded_input_hashes_match_current_files() -> None:
    artifact = _read(OUTPUT_PATH)
    records = list(artifact["input_artifacts"].values()) + list(
        artifact["input_documents"].values()
    )
    assert len(records) == 9
    for record in records:
        path = ROOT / record["path"]
        assert path.is_file()
        assert _sha256(path) == record["sha256"]


def test_addendum_contains_all_required_markers_and_links() -> None:
    artifact = _read(OUTPUT_PATH)
    gate = artifact["gates"]["post_wave10_addendum_gate"]
    assert all(gate["required_markers"].values())
    assert all(gate["required_links"].values())
    assert len(artifact["drift_table"]) == 3
    assert [item["repair_order"] for item in artifact["drift_table"]] == [1, 2, 3]


def test_next_evidence_keeps_both_scope_specific_blockers_visible() -> None:
    artifact = _read(OUTPUT_PATH)
    requirements = artifact["required_next_evidence"]
    assert any("equation of state" in item for item in requirements)
    assert any("pre-arrival leakage" in item for item in requirements)
    assert artifact["next_controller"] == GR_CONTROLLER
