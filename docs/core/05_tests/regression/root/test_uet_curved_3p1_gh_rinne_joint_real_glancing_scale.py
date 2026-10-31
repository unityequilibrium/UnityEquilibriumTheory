from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_joint_real_glancing_scale.json"
)


def _artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_joint_path_screen_stays_partial_and_unlocks_nothing() -> None:
    artifact = _artifact()
    assert artifact["STATUS"] == "PASS_JOINT_REAL_PATH_SCREEN_ONLY"
    assert artifact["closure_level"] == "PARTIAL"
    assert artifact["major_result"]["closure_level"] == "PARTIAL"
    assert artifact["full_core_unlock"] is False
    assert artifact["gravity_unlock"] is False
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "no uniform complex-frequency Kreiss estimate" in artifact["CLAIM_BOUNDARY"]


def test_generic_jordan_and_confluent_paths_pass_declared_gates() -> None:
    artifact = _artifact()
    verification = artifact["VERIFICATION"]
    assert all(verification["checks"].values())
    generic = verification["generic_paths"]
    jordan = verification["exact_jordan_path"]
    confluent = verification["near_jordan_confluent_path"]
    assert len(generic) == 16
    assert len(jordan) == len(confluent) == 4
    assert all(row["matrix_rank"] == 30 for row in generic + jordan + confluent)
    assert all(row["scaled_sigma_min"] > 0.04 for row in generic)
    assert all(row["eq123_scaled_logdet_abs_error"] < 1.0e-8 for row in generic)
    assert all(row["analytic_scaled_logdet_abs_error"] < 1.0e-8 for row in jordan)
    offsets = [abs(row["confluent_reference_logdet_abs_offset"]) for row in confluent]
    assert offsets[-1] < offsets[0]
    assert offsets[-1] < 0.06


def test_recorded_source_hashes_match() -> None:
    for relative_path, expected in _artifact()["VERIFICATION"]["source_hashes"].items():
        actual = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual == expected
