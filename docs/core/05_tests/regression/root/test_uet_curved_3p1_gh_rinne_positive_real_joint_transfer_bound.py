from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_positive_real_joint_transfer_bound.json"


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_transfer_bound_closes_only_the_registered_lane() -> None:
    artifact = _artifact()
    major = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_POSITIVE_REAL_UNIFORM_TRANSFER_BOUND"
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["core_parent_status"] == "PARTIAL"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "not a useful stability constant" in artifact["CLAIM_BOUNDARY"]


def test_chartwise_bounds_and_registered_case_reproduction_pass() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    assert all(verification["checks"].values())
    assert verification["case_count"] == 92
    assert verification["chart_counts"] == {
        "unit_generic_eigenmodes": 64,
        "normalized_confluent_divided_difference": 24,
        "source_ode_consistent_jordan": 4,
    }
    assert verification["max_determinant_log_error"] < 1.0e-8
    assert verification["max_transfer_factorization_error"] < 1.0e-8
    assert verification["max_generic_confluent_overlap_error"] < 1.0e-10
    bounds = verification["chartwise_bounds"]
    assert bounds["unit_generic_eigenmodes"]["log10_transfer_norm_upper_bound"] < 67.0
    assert bounds["normalized_confluent_divided_difference"]["log10_transfer_norm_upper_bound"] < 60.0
    assert bounds["source_ode_consistent_jordan"]["log10_transfer_norm_upper_bound"] < 62.0


def test_recorded_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
