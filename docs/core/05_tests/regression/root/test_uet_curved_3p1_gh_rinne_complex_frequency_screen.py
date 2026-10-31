from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_complex_frequency_screen.json"
)
HIGH_ENDPOINT_ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_high_frequency_transfer_endpoint.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_complex_frequency_screen_stays_partial_and_locked() -> None:
    artifact = _artifact()
    assert artifact["STATUS"] == "PASS_COMPLEX_FREQUENCY_ENDPOINT_SCREEN"
    assert artifact["status"] == artifact["STATUS"]
    assert artifact["closure_level"] == "PARTIAL"
    assert artifact["major_result"]["closure_level"] == "PARTIAL"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "not a continuous all-frequency Kreiss operator-norm proof" in artifact["CLAIM_BOUNDARY"]
    assert artifact["CONTROLLING_BLOCKER"] == (
        "zero_frequency_transfer_extension_and_compactified_continuous_transfer_bound_unproved"
    )
    high_endpoint = json.loads(HIGH_ENDPOINT_ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["VERIFICATION"]["high_frequency_endpoint_result"]["sha256"] == hashlib.sha256(
        HIGH_ENDPOINT_ARTIFACT.read_bytes()
    ).hexdigest()
    assert high_endpoint["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["full_core_unlock"] is False


def test_complex_frequency_endpoints_and_jordan_chart_are_screened() -> None:
    verification = _artifact()["VERIFICATION"]
    assert all(verification["checks"].values())
    assert len(verification["low_frequency_cases"]) == 60
    assert len(verification["glancing_cases"]) == 30
    assert len(verification["high_frequency_cases"]) == 45
    assert len(verification["high_frequency_parameter_sweep_cases"]) == 120
    assert len(verification["jordan_approach_cases"]) == 20
    assert verification["maximum_principal_mode_residual"] < 1.0e-7
    assert verification["maximum_source_eq123_log_abs_determinant_error"] < 1.0e-6
    assert max(row["relative_spread"] for row in verification["zeta_to_zero_direction_spreads"]) < 5.0e-8
    assert verification["jordan_error_by_offset"][-1]["maximum_frobenius_distance"] < 1.0e-6
    assert max(
        row["maximum_abs_norm_error_to_candidate"]
        for row in verification["high_frequency_errors"]
        if row["radius"] == max(verification["high_frequency_radii"])
    ) < 1.0e-10
    assert max(
        row["maximum_abs_norm_error_to_candidate"]
        for row in verification["high_frequency_parameter_sweep_errors"]
        if row["radius"] == max(verification["high_frequency_parameter_sweep_radii"])
    ) < 2.0e-9


def test_registered_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
