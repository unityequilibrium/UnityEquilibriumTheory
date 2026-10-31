from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_negative_shift_joint_limit.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_joint_limit_closes_only_the_uniform_determinant_floor_subresult() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    determinant = verification["joint_path_determinant"]
    matrix = verification["registered_matrix_path"]

    assert artifact["STATUS"] == "PASS_NO_UNIFORM_DETERMINANT_FLOOR_JOINT_LIMIT_IDENTIFIED"
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert all(verification["determinant_checks"].values())
    assert all(verification["matrix_checks"].values())
    assert len(determinant) == 4
    assert abs(determinant[-1]["ratio_to_C_epsilon5"] - 1.0) < 1.0e-5
    assert [row["boundary_matrix_rank"] for row in matrix] == [30] * 4
    assert all(
        right["row_equilibrated_sigma_min_over_sigma_max"]
        < left["row_equilibrated_sigma_min_over_sigma_max"]
        for left, right in zip(matrix, matrix[1:])
    )
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    open_items = " ".join(artifact["WHAT_REMAINS_OPEN"])
    assert "uniform Kreiss" in open_items
    assert "not a complete inverse-map/Kreiss failure proof" in artifact["CLAIM_BOUNDARY"]


def test_joint_limit_formula_and_diagnostics_are_finite_and_decreasing() -> None:
    verification = _artifact()["VERIFICATION"]
    coefficient = verification["asymptotic_coefficient"]
    assert math.isclose(coefficient, 4.0 / (math.sqrt(3.0) - 1.0) ** 26, rel_tol=1.0e-12)

    determinant = verification["joint_path_determinant"]
    assert all(math.isfinite(row["eq123_log_abs_determinant"]) for row in determinant)
    assert all(
        right["eq123_log_abs_determinant"] < left["eq123_log_abs_determinant"]
        for left, right in zip(determinant, determinant[1:])
    )
    assert all(
        math.isfinite(row["row_equilibrated_sigma_min_over_sigma_max"])
        for row in verification["registered_matrix_path"]
    )


def test_all_registered_source_hashes_match() -> None:
    artifact = _artifact()
    for relative_path, expected in artifact["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
