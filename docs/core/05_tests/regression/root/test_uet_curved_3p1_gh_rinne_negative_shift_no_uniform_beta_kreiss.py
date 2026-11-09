from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_negative_shift_no_uniform_beta_kreiss.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_symbolic_witness_closes_only_family_uniform_kreiss_no_go() -> None:
    artifact = _artifact()
    result = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_CONSTRUCTIVE_NO_UNIFORM_BETA_KREISS_BOUND"
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "fixed beta" in result["claim_boundary"]
    assert "not refuted" in " ".join(result["what_remains_open"])


def test_exact_asymptotic_and_registered_boundary_matrix_witness() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    witness = verification["witness_path"]
    assert all(verification["checks"].values())
    assert all(verification["symbolic_checks"].values())
    assert [row["epsilon"] for row in witness] == [1.0e-2, 1.0e-3, 1.0e-4]
    assert all(row["amplitude_norm"] == 1.0 for row in witness)
    assert all(abs(row["normalized_mode_norm"] - 1.0) < 1.0e-14 for row in witness)
    assert all(row["other_source_data_max_abs"] < 1.0e-12 for row in witness)

    asymptotic_prefactor = 9.0 - 5.0 * math.sqrt(3.0)
    last = witness[-1]
    assert math.isclose(
        last["epsilon_times_lower_bound"], asymptotic_prefactor, rel_tol=2.0e-4
    )
    expected_component_prefactor = (9.0 * math.sqrt(2.0) + 5.0 * math.sqrt(6.0)) / 12.0
    assert math.isclose(
        artifact["EQUATION_OR_MAPPING"]["numeric_values"]["r_over_epsilon_limit"],
        expected_component_prefactor,
        rel_tol=1.0e-14,
    )


def test_source_matrix_svd_is_diagnostic_and_source_hashes_match() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    svd = verification["source_matrix_singular_values"]
    assert all(row["sigma_min"] > 0.0 for row in svd)
    assert all(row["inverse_norm_diagnostic"] > 0.0 for row in svd)
    assert all("diagnostic only" in row["role"] for row in svd)
    assert all(
        right["inverse_norm_diagnostic"] > left["inverse_norm_diagnostic"]
        for left, right in zip(svd, svd[1:])
    )
    for relative_path, expected in verification["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
