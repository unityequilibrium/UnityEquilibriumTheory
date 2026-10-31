from __future__ import annotations

import importlib
import json
from pathlib import Path

import numpy as np


AUDIT = importlib.import_module(
    "docs.scripts.audit.audit_curved_3p1_gh_rinne_sat_penalty_screen"
)
ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_sat_penalty_screen.json"
)
BASELINE = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_full_u1_max_diss_sat_control.json"
)


def test_independent_matrix_assembly_matches_frozen_rinne_operator() -> None:
    operators = AUDIT.TT_SBP.legendre_lobatto_operators(4)
    components = AUDIT._operator_components(operators)
    assert components["strong_match_residual"] == 0.0


def test_screen_closes_only_the_declared_finite_gain_grid() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["status"] == "PASS_BASELINE_REPRODUCTION_AND_SCREEN"
    assert all(artifact["checks"].values())
    assert artifact["claim_promotion"] is False
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["major_result"]["dependency_unlocked"].startswith("none;")
    for row in artifact["order_results"]:
        assert row["weak_pi_residual_gain_scan"]["passing_sigma_hat_values"] == []
        assert row["weak_incoming_characteristic_gain_scan"]["passing_sigma_hat_values"] == []
    direct_passes = [
        row["direct_strong_rinne_amplitude_scan"]["passing_sigma_hat_values"]
        for row in artifact["order_results"]
    ]
    assert direct_passes[0]
    assert direct_passes[1:] == [[], []]
    assert artifact["checks"]["direct_strength_scan_has_no_common_gain_across_all_orders"]


def test_pi_only_result_separates_constraint_preservation_from_stability() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for row in artifact["order_results"]:
        result = row["pi_only_exact_correction"]
        assert result["reduction_constraint_linf"] < 1.0e-12
        assert result["pulse_absorption_pass"] is False
        assert result["maximum_eigenvalue_real_part"] > 1.0e-6
        assert result["positive_modes_above_1e-6"] > 0


def test_source_hashes_and_claim_boundary_are_locked() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    baseline_hash = AUDIT._sha256(BASELINE)
    audit_hash = AUDIT._sha256(AUDIT.AUDIT_SOURCE)
    assert artifact["source_hashes"][BASELINE.relative_to(ROOT).as_posix()] == baseline_hash
    assert artifact["source_hashes"][AUDIT.AUDIT_SOURCE.relative_to(ROOT).as_posix()] == audit_hash
    assert artifact["scope"]["holdout_access"] is False
    assert artifact["scope"]["clipping"] is False
    assert "finite zero-shift LGL scalar-gain screen" in artifact["major_result"]["claim_boundary"]
