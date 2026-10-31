from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_rescaled_transfer_factorization.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_factorization_result_is_partial_and_does_not_unlock_dependencies() -> None:
    artifact = _artifact()
    major = artifact["major_result"]
    assert artifact["STATUS"] == "PASS_RESCALED_TRANSFER_FACTORIZATION_SCREEN"
    assert artifact["closure_level"] == "PARTIAL"
    assert major["closure_level"] == "PARTIAL"
    assert major["evidence_artifacts"]
    assert major["open_blockers"]
    assert major["controlling_blocker"] == artifact["CONTROLLING_BLOCKER"]
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "uniform invertibility and Lipschitz constants are not proved" in artifact["CLAIM_BOUNDARY"]

    for evidence in major["evidence_artifacts"]:
        actual = hashlib.sha256((ROOT / evidence["path"]).read_bytes()).hexdigest()
        assert actual == evidence["sha256"]


def test_transfer_factorization_and_row_projector_identity_pass() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    assert all(verification["checks"].values())
    assert len(verification["cases"]) == 84
    assert verification["maximum_factorization_error"] < 1.0e-10
    assert verification["maximum_projector_identity_error"] < 1.0e-12
    assert all(row["rescaled_boundary_sigma_min"] > 0.0 for row in verification["cases"])
    assert all(row["finite"] for row in verification["cases"])
    summaries = verification["summaries"]
    assert len(summaries) == 4
    assert all(
        right["maximum_gauge_block_distance"] < left["maximum_gauge_block_distance"]
        for left, right in zip(summaries, summaries[1:])
    )
    assert all(
        right["maximum_gauge_block_distance_over_delta"]
        <= left["maximum_gauge_block_distance_over_delta"] + 1.0e-12
        for left, right in zip(summaries, summaries[1:])
    )


def test_recorded_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
