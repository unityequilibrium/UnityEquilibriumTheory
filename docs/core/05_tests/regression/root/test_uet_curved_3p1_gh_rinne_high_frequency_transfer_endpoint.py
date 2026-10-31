from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_high_frequency_transfer_endpoint.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_exact_high_frequency_endpoint_is_lane_closed_not_core_closed() -> None:
    artifact = _artifact()
    assert artifact["STATUS"] == "PASS_EXACT_HIGH_FREQUENCY_TRANSFER_MATRIX_ENDPOINT"
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")


def test_endpoint_matrix_determinant_and_convergence_checks() -> None:
    verification = _artifact()["VERIFICATION"]
    assert all(verification["checks"].values())
    assert len(verification["endpoint_cases"]) == 12
    assert len(verification["finite_frequency_matrix_convergence_cases"]) == 36
    assert sum(
        row["case_count"]
        for row in verification["finite_frequency_matrix_convergence_cases"]
    ) == 180
    assert verification["maximum_eq123_asymptotic_log_error"] < 1.0e-10
    assert verification["maximum_norm_candidate_abs_error"] < 1.0e-12
    assert verification["maximum_last_radius_relative_matrix_error"] < 5.0e-7
    assert verification["exploratory_grid_design"]["status"] == "EXPLORATORY_NOT_PREREGISTERED"
    assert "only numerically checked" in _artifact()["CLAIM_BOUNDARY"]


def test_endpoint_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
