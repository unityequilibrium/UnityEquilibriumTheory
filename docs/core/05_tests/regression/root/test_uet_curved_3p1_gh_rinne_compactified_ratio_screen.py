from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_compactified_ratio_screen.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_compactified_ratio_screen_remains_partial_and_locked() -> None:
    artifact = _artifact()
    major = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_COMPACTIFIED_POSITIVE_REAL_RATIO_SCREEN"
    assert artifact["closure_level"] == "PARTIAL"
    assert major["closure_level"] == "PARTIAL"
    assert major["evidence_artifacts"]
    assert major["open_blockers"]
    assert major["controlling_blocker"] == artifact["CONTROLLING_BLOCKER"]
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "not a continuous all-ratio remainder proof" in artifact["CLAIM_BOUNDARY"]
    for evidence in major["evidence_artifacts"]:
        actual = hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest()
        assert actual == evidence["sha256"]


def test_ratio_shells_cover_extremes_and_contract_with_delta() -> None:
    verification = _artifact()["VERIFICATION"]
    assert all(verification["checks"].values())
    assert len(verification["summaries"]) == 4
    assert len(verification["cases"]) == 84
    for row in verification["summaries"]:
        assert row["case_count"] == 21
        assert row["ratio_min"] == 1.0e-8
        assert row["ratio_max"] == 1.0e8
        assert row["max_distance_over_delta"] < 24.0
    summaries = verification["summaries"]
    assert all(
        right["max_endpoint_distance"] < left["max_endpoint_distance"]
        for left, right in zip(summaries, summaries[1:])
    )
    assert max(row["principal_mode_residual"] for row in verification["cases"]) < 1.0e-8
    charts = {row["basis_chart"] for row in verification["cases"]}
    assert charts == {
        "unit_generic_eigenmodes",
        "normalized_confluent_divided_difference",
        "source_ode_consistent_jordan",
    }


def test_recorded_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
