"""Cross-topic status, provenance, and claim-boundary tests for Wave 6."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

from docs.scripts.audit.audit_matter_space_research_program import (
    OUTPUT_PATH,
    build_program_gate,
)


ROOT = repo_root()


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_generated_program_gate_matches_current_inputs() -> None:
    artifact = _read(OUTPUT_PATH)
    assert artifact == build_program_gate(generated_at=artifact["generated_at"])
    assert artifact["source_snapshot_at"] <= artifact["generated_at"]


def test_core_closure_is_separate_from_failed_causal_cone() -> None:
    gate = _read(OUTPUT_PATH)
    assert gate["status"] == "BLOCKED"
    assert gate["controlling_blocker"] == "core_prearrival_leakage"
    assert gate["summary"]["core_gates_passed"] == 16
    assert gate["summary"]["core_gates_total"] == 17
    assert gate["gates"]["internal_variational_and_ledger_closure"]["status"] == "PASS"
    causal = gate["gates"]["causal_compact_support"]
    assert causal["status"] == "FAIL"
    assert causal["value"] > causal["threshold"]
    assert causal["arrival_speed_relative_error"] <= causal["arrival_speed_threshold"]


def test_trace_remains_derived_and_has_no_backreaction() -> None:
    gate = _read(OUTPUT_PATH)
    assert gate["gates"]["ontology_separation"]["status"] == "PASS"
    assert gate["gates"]["trace_no_backreaction"]["status"] == "PASS"
    assert gate["gates"]["trace_no_backreaction"]["core_trace_history_physical_difference"] == 0.0
    assert gate["gates"]["trace_no_backreaction"]["phase_trace_history_physical_difference"] == 0.0
    assert "R established as matter, energy, or an independent information field" in gate[
        "claim_boundary"
    ]["blocked"]


def test_pilot_statuses_and_topic_controller_are_not_promoted() -> None:
    gate = _read(OUTPUT_PATH)
    assert gate["summary"]["thermal_status"] == "SIMULATION_ONLY"
    assert gate["summary"]["thermal_dependency_status"] == "BLOCKED"
    assert gate["summary"]["phase_status"] == "INTERNAL_DIAGNOSTIC"
    assert gate["summary"]["phase_internal_gate_status"] == "PASS"
    assert gate["summary"]["phase_dependency_status"] == "BLOCKED"
    assert gate["summary"]["phase_topic_status_impact"] == "NONE"
    assert gate["summary"]["phase_topic_readiness"] == "Draft"
    assert gate["summary"]["phase_topic_tier"] == "B"
    assert gate["summary"]["phase_topic_controller"] == (
        "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open"
    )


def test_ledger_amendments_are_disclosed_not_blind_confirmations() -> None:
    ledger = _read(OUTPUT_PATH)["gates"]["pilot_energy_ledgers"]
    assert ledger["status"] == "WARN"
    assert ledger["locked_runs_passed"] is False
    assert ledger["refined_runs_passed"] is True
    assert ledger["blind_preregistration"] is False
    assert ledger["physical_parameters_changed"] is False
    assert ledger["thresholds_changed"] is False


def test_dependency_and_foundation_claims_remain_blocked() -> None:
    gate = _read(OUTPUT_PATH)
    assert all(
        item["status"] == "BLOCKED"
        for item in gate["downstream_dependency_gates"].values()
    )
    assert gate["deferred_foundation"]["claim_state"] == "NOT_ESTABLISHED_DEFERRED"
    assert "Lorentz-covariant action" in gate["deferred_foundation"]["entry_requirements"]
    blocked = gate["claim_boundary"]["blocked"]
    assert "Dirac, positron, neutrino, or CPT derivation" in blocked
    assert "galaxy dynamics or dark-matter replacement" in blocked


def test_artifact_hashes_pass_while_legacy_figure_layout_is_warned() -> None:
    gate = _read(OUTPUT_PATH)
    integrity = gate["gates"]["artifact_integrity"]
    assert integrity["status"] == "PASS"
    assert integrity["checked_output_count"] == 10
    assert integrity["checked_dependency_count"] == 3
    assert all(check["match"] for check in integrity["checks"])
    layout = gate["gates"]["artifact_layout"]
    assert layout["status"] == "WARN"
    assert layout["legacy_figure_count"] == 8
    assert layout["required_canonical_location"] == "Result/02_Figures"
    assert all((ROOT / path).is_file() for path in layout["legacy_figure_paths"])
