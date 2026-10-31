from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_negative_shift_kreiss_symbol.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_negative_shift_source_matched_grid_passes_without_unlocking_core() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    assert artifact["STATUS"] == (
        "PASS_SOURCE_MATCHED_NEGATIVE_SHIFT_SAMPLE_WITH_EXACT_DEGENERACY_CORRECTION"
    )
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert verification["generic_grid_passed"] is True
    assert verification["generic_case_count"] == 626
    assert all(verification["generic_checks"].values())
    assert sum(row["generic_case_count"] for row in verification["per_beta"]) == 626
    assert all(row["generic_minimum_boundary_rank"] == 30 for row in verification["per_beta"])
    assert all(
        0.0 < row["source_eq_124_to_corrected_jordan_determinant_ratio"] < 1.0
        for row in verification["per_beta"]
    )
    assert verification["subresult_closure"]["preregistered_non_degenerate_grid"] == "CLOSED_FOR_LANE"
    assert verification["subresult_closure"]["exact_degenerate_source_mode"] == (
        "CLOSED_FOR_LANE_WITH_ODE_CONSISTENT_JORDAN_CORRECTION"
    )
    assert verification["source_exact_degeneracy_issue_confirmed"] is True
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "uniform Kreiss" in " ".join(artifact["WHAT_REMAINS_OPEN"])


def test_determinant_phase_difference_is_one_global_orientation_sign() -> None:
    verification = _artifact()["VERIFICATION"]
    assert verification["generic_eq_123_global_orientation_sign"] in {"-1", "+1"}
    assert verification["maximum_generic_eq_123_log_offset"] < 1.0e-8
    assert verification["maximum_generic_eq_123_phase_deviation_from_global_sign"] < 1.0e-8
    assert all(
        row["generic_maximum_eq_123_phase_offset_radians"] > 3.0
        for row in verification["per_beta"]
    )


def test_degenerate_jordan_chain_and_confluent_limit_are_explicit() -> None:
    verification = _artifact()["VERIFICATION"]
    findings = verification["degenerate_findings"]
    assert findings["printed_eq_74_basis_reproduces_printed_eq_124_determinant"] is True
    assert findings["printed_eq_74_basis_satisfies_principal_ode"] is False
    assert findings["ode_consistent_source_norm_jordan_repair_passes_principal_ode"] is True
    assert findings[
        "ode_consistent_source_norm_jordan_repair_has_rank_30_and_finite_determinant"
    ] is True
    assert findings["corrected_jordan_determinant_matches_analytic_confluent_limit"] is True
    assert findings["off_grid_corrected_jordan_cases_have_rank_30_and_pass_ode"] is True
    assert verification["maximum_corrected_jordan_determinant_log_offset"] < 1.0e-8
    assert findings["generic_confluent_limit_basis_passes_principal_ode"] is True
    assert findings["near_degenerate_confluence_remains_full_rank"] is True
    assert findings[
        "near_degenerate_determinant_converges_to_exact_generic_limit_basis"
    ] is True
    for row in verification["per_beta"]:
        assert row["degenerate_literal_euclidean_norm_basis"][
            "maximum_principal_mode_residual"
        ] > 1.0e-8
        corrected = row["degenerate_ode_consistent_source_norm_basis"]
        assert corrected[
            "maximum_principal_mode_residual"
        ] < 1.0e-8
        assert corrected["boundary_matrix_rank"] == 30
        assert math.isfinite(corrected["basis_determinant_log_abs"])
        assert abs(corrected["corrected_jordan_determinant_log_offset"]) < 1.0e-8
        assert row["degenerate_confluent_limit_basis"][
            "maximum_principal_mode_residual"
        ] < 1.0e-8
        sequence = row["near_degenerate_confluence_sequence"]
        assert len(sequence) == 4
        assert all(sample["confluent_rank"] == 30 for sample in sequence)
        assert abs(
            sequence[-1]["confluent_determinant_log_abs"]
            - row["degenerate_confluent_limit_basis"]["basis_determinant_log_abs"]
        ) < 2.0e-6
    off_grid = verification["off_grid_corrected_jordan_cases"]
    assert [row["beta"] for row in off_grid] == [-0.01, -0.25, -0.75, -0.99]
    assert all(row["rank"] == 30 for row in off_grid)
    assert all(row["principal_ode_residual"] < 1.0e-8 for row in off_grid)
    assert all(abs(row["determinant_log_offset"]) < 1.0e-8 for row in off_grid)


def test_all_registered_source_hashes_match() -> None:
    artifact = _artifact()
    for relative_path, expected in artifact["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
