"""Artifact, provenance, and claim-boundary checks for the Topic 0.11 pilot."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
TOPIC = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
DATA = TOPIC / "Data" / "03_Research"
ARTIFACT = TOPIC / "Result" / "artifacts" / "0_11_matter_space_coupled_diagnostic.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_preregistration_locks_synthetic_scope_and_initial_conditions() -> None:
    prereg = _read(DATA / "matter_space_coupled_preregistration.json")
    assert prereg["status"] == "LOCKED_BEFORE_EXECUTION"
    assert prereg["unit_lane"] == "normalized"
    assert prereg["external_numeric_inputs"] == []
    assert prereg["parameter_fitting"] is False
    assert prereg["random_seeds"] == [1101, 1102, 1103]
    assert prereg["claim_policy"]["topic_readiness_change_allowed"] is False
    assert prereg["claim_policy"]["structure_factor_gate_change_allowed"] is False
    assert prereg["claim_policy"]["trace_backreaction_allowed"] is False


def test_numerical_amendment_preserves_locked_failure_and_physics() -> None:
    prereg_path = DATA / "matter_space_coupled_preregistration.json"
    amendment = _read(DATA / "matter_space_coupled_numerical_amendment_001.json")
    assert amendment["status"] == "POST_DIAGNOSTIC_NUMERICAL_AMENDMENT"
    assert amendment["blind_preregistration"] is False
    assert amendment["trigger"]["locked_preregistration_sha256"] == _sha256(prereg_path)
    assert amendment["amendment"]["ledger_refinement_dt_fraction_of_preflight"] < amendment["trigger"]["locked_dt_fraction_of_preflight"]
    for key in (
        "physical_parameters_changed",
        "initial_conditions_changed",
        "seeds_changed",
        "thresholds_changed",
        "external_data_added",
        "parameter_fitting",
    ):
        assert amendment["amendment"][key] is False


def test_internal_gates_pass_but_dependencies_and_topic_status_stay_blocked() -> None:
    artifact = _read(ARTIFACT)
    assert artifact["status"] == "INTERNAL_DIAGNOSTIC"
    assert artifact["internal_gate_status"] == "PASS"
    assert artifact["dependency_status"] == "BLOCKED"
    assert artifact["controlling_blocker"] == "inherited_core_prearrival_leakage"
    assert artifact["topic_status_impact"] == "NONE"
    assert artifact["topic_readiness_before_after"] == ["Draft", "Draft"]
    assert artifact["topic_tier_before_after"] == ["B", "B"]
    assert artifact["topic_controlling_blocker_unchanged"] == "ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open"
    assert artifact["failed_gates"] == []
    assert all(artifact["gates"].values())


def test_trace_is_invariant_but_physical_state_is_not_erased() -> None:
    artifact = _read(ARTIFACT)
    metrics = artifact["metrics"]
    threshold = artifact["thresholds"]["trace_physical_difference_max"]
    assert metrics["trace_switch_physical_difference"] <= threshold
    assert metrics["full_run_trace_switch_physical_difference"] <= threshold
    assert metrics["different_trace_history_physical_difference"] <= threshold
    assert metrics["different_trace_history_observable_difference"] > 1e-12
    assert metrics["same_C_different_state_response"] > threshold
    assert artifact["run_integrity"]["trace_backreaction"] is False


def test_locked_and_refined_ledger_results_are_both_reported() -> None:
    artifact = _read(ARTIFACT)
    metrics = artifact["metrics"]
    threshold = artifact["thresholds"]["ledger_closure_relative_max"]
    assert metrics["locked_max_ledger_closure_relative"] > threshold
    assert metrics["refined_max_ledger_closure_relative"] <= threshold
    assert artifact["gates"]["ledger_closure_refined"] is True
    assert artifact["numerical_amendment"]["blind_preregistration"] is False
    assert "not blind confirmation" in artifact["ledger_refinement"]["role"]


def test_effect_resolution_and_adiabatic_controls_are_nontrivial() -> None:
    artifact = _read(ARTIFACT)
    metrics = artifact["metrics"]
    assert metrics["primary_coupling_effect_rms"] > artifact["thresholds"]["coupling_effect_absolute_min"]
    assert metrics["effect_to_temporal_error_ratio"] >= artifact["thresholds"]["effect_to_temporal_error_min"]
    assert metrics["resolution_effect_ratio"] >= artifact["thresholds"]["resolution_effect_ratio_min"]
    errors = [row["relative_error"] for row in artifact["adiabatic_control"]]
    assert all(right <= left for left, right in zip(errors, errors[1:]))
    assert errors[-1] <= artifact["thresholds"]["adiabatic_finest_relative_error_max"]


def test_hashes_and_diagnostic_claim_boundary_match_local_files() -> None:
    artifact = _read(ARTIFACT)
    for block in ("preregistration", "numerical_amendment"):
        path = ROOT / artifact[block]["path"]
        assert artifact[block]["sha256"] == _sha256(path)
    for dependency in artifact["dependencies"].values():
        path = ROOT / dependency["path"]
        assert dependency["sha256"] == _sha256(path)
    csv_record = artifact["outputs"]["profiles_csv"]
    assert csv_record["sha256"] == _sha256(ROOT / csv_record["path"])
    for figure in artifact["outputs"]["figures"]:
        assert figure["sha256"] == _sha256(ROOT / figure["path"])
    assert artifact["run_integrity"]["morphology_metrics_claim_bearing"] is False
    boundary = " ".join(artifact["claim_boundary"])
    assert "not accepted estimators" in boundary
    assert "No universality" in boundary
