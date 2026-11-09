from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_negative_shift_zero_transition.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_fixed_frequency_glancing_limit_closes_only_declared_lane() -> None:
    artifact = _artifact()
    result = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_FIXED_FREQUENCY_GLANCING_BLOCK_LIMIT"
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "zeta->0" in result["claim_boundary"]
    assert "imaginary axis" in result["claim_boundary"]


def test_block_limit_and_asymptotic_determinant_converge() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    cases = verification["cases"]
    assert all(verification["checks"].values())
    assert len(cases) == 15
    assert verification["frequency_values"] == [0.25, 0.5, 1.0, 2.0, 4.0]
    assert verification["negative_shift_magnitudes"] == [0.1, 0.01, 0.001]

    for zeta in verification["frequency_values"]:
        rows = [row for row in cases if row["zeta_real"] == zeta]
        assert [abs(row["beta"]) for row in rows] == [0.1, 0.01, 0.001]
        assert all(row["D_max_abs"] == 0.0 for row in rows)
        assert all(row["beta_E_to_analytic_limit_max_abs"] < 1.0e-10 for row in rows)
        residuals = [abs(row["determinant_beta20_residual"]) for row in rows]
        assert residuals[2] < residuals[1] < residuals[0]
        assert residuals[2] < 0.02
        assert rows[-1]["inverse_norm_difference"] < rows[0]["inverse_norm_difference"]


def test_source_hashes_match_and_orientation_is_recorded_not_promoted() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    ratios = [row["determinant_orientation_ratio"] for row in verification["cases"]]
    assert all(row["real"] == -1.0 and row["imag"] == 0.0 for row in ratios)
    for relative_path, expected in verification["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
