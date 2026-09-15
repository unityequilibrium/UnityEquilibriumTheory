"""Regression checks for the Topic 13 causal branch-selection closure."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json"


def test_causal_selection_closes_a_lane_without_erasing_the_baseline_failure() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["baseline_preservation"]["full_candidate_pass"] is False
    assert artifact["baseline_preservation"]["prearrival_leakage_fraction"] > artifact["baseline_preservation"]["locked_threshold"]


def test_selected_branch_meets_the_locked_causal_contract() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    branch = artifact["selected_branch"]
    assert branch["prearrival_leakage_fraction"] <= 1.0e-6
    assert branch["C_arrival_target_abs"] > 0.0
    assert branch["Phi_arrival_target_abs"] > 0.0
    assert branch["max_combined_energy_relative_residual"] <= 1.0e-6
