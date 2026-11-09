from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / "docs/core/07_artifacts/verification/curved_3p1_gh_rinne_rescaled_determinant_floor.json"


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_determinant_floor_closes_only_the_declared_lane() -> None:
    artifact = _artifact()
    major = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_CHARTWISE_RESCALED_DETERMINANT_FLOOR"
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["core_parent_status"] == "PARTIAL"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "does not bound the inverse operator" in artifact["CLAIM_BOUNDARY"]
    assert major["open_blockers"]


def test_chart_formulas_and_conservative_floors_pass() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    assert all(verification["checks"].values())
    assert verification["case_count"] == 92
    assert len(verification["deltas"]) == 4
    assert verification["ratio_grid"][0] == 1.0e-8
    assert verification["ratio_grid"][-1] == 1.0e8
    assert verification["maximum_log_determinant_formula_error"] < 1.0e-8
    assert verification["maximum_gap_identity_relative_error"] < 1.0e-8
    bounds = verification["analytic_bounds"]
    assert bounds["generic_determinant_floor_conservative"] > 0.0
    assert bounds["confluent_determinant_floor_conservative"] > 0.0
    assert bounds["jordan_determinant_floor_conservative"] > 0.0
    assert "abs(1-r^2)" in artifact["EQUATION_OR_MAPPING"]["generic_chart"]
    assert "bound_derivation" in artifact["EQUATION_OR_MAPPING"]


def test_recorded_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
