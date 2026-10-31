from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_joint_real_kreiss_operator.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_state_transfer_screen_is_partial_and_unlocks_nothing() -> None:
    artifact = _artifact()
    major = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_JOINT_REAL_KREISS_OPERATOR_SCREEN"
    assert artifact["closure_level"] == "PARTIAL"
    assert major["closure_level"] == "PARTIAL"
    assert major["evidence_artifacts"]
    assert major["open_blockers"]
    assert major["controlling_blocker"] == artifact["CONTROLLING_BLOCKER"]
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "no continuous all-ratio" in artifact["CLAIM_BOUNDARY"]

    for evidence in major["evidence_artifacts"]:
        actual = hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest()
        assert actual == evidence["sha256"]


def test_endpoint_operator_and_joint_grid_converge_as_recorded() -> None:
    verification = _artifact()["VERIFICATION"]
    assert all(verification["checks"].values())
    endpoint = _artifact()["EQUATION_OR_MAPPING"]["endpoint"]
    assert endpoint["gram_eigenvalues"] == sorted(endpoint["gram_eigenvalues"])
    assert abs(endpoint["kreiss_operator_norm"] - 2 * (3 + 7**0.5) ** 0.5) < 1.0e-12
    assert abs(
        endpoint["zero_shift_full_operator_norm_at_reference"]
        - endpoint["kreiss_operator_norm"]
    ) < 2.0e-6
    assert endpoint["zero_shift_non_gauge_max_column_norm_at_reference"] < 1.0e-6
    assert endpoint["corrected_jordan_non_gauge_max_column_norm_at_reference"] < 1.0e-6
    assert endpoint["zero_shift_gram_max_abs_error"] < 2.0e-6
    assert endpoint["corrected_jordan_gram_max_abs_error"] < 2.0e-6

    summaries = verification["grid_summaries"]
    assert len(summaries) == 4
    assert all(row["sample_count"] == 25 for row in summaries)
    lower = [row["kreiss_norm_min"] for row in summaries]
    upper = [row["kreiss_norm_max"] for row in summaries]
    distance = [row["max_frobenius_distance_to_zero_shift_reference"] for row in summaries]
    assert all(right > left for left, right in zip(lower, lower[1:]))
    assert all(right < left for left, right in zip(upper, upper[1:]))
    assert all(right < left for left, right in zip(distance, distance[1:]))

    cases = verification["grid_cases"]
    assert len(cases) == 100
    assert all(row["state_operator_shape"] == [40, 30] for row in cases)
    assert all(row["principal_mode_residual"] < 1.0e-8 for row in cases)
    basis = verification["basis_invariance_cases"]
    assert len(basis) == 9
    assert max(row["max_abs_operator_difference"] for row in basis) < 1.0e-10


def test_recorded_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
