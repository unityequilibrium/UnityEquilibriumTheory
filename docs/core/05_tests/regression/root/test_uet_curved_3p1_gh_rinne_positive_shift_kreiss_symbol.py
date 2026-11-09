from __future__ import annotations

import importlib
import json
from pathlib import Path


AUDIT = importlib.import_module(
    "docs.scripts.audit.audit_curved_3p1_gh_rinne_positive_shift_kreiss_symbol"
)
ROOT = Path(__file__).resolve().parents[5]
ARTIFACT = ROOT / (
    "docs/core/07_artifacts/verification/"
    "curved_3p1_gh_rinne_positive_shift_kreiss_symbol.json"
)


def test_positive_shift_grid_matches_published_determinant() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["STATUS"] == "PASS_SOURCE_MATCHED_POSITIVE_SHIFT_KREISS_SAMPLE"
    assert artifact["VERIFICATION"]["case_count"] == 627
    assert all(artifact["VERIFICATION"]["checks"].values())
    assert all(row["minimum_boundary_matrix_rank"] == 10 for row in artifact["VERIFICATION"]["per_beta"])
    assert artifact["VERIFICATION"]["maximum_abs_eq_122_determinant_log_offset"] < AUDIT.DETERMINANT_TOLERANCE
    assert artifact["VERIFICATION"]["maximum_abs_eq_122_determinant_phase_offset_radians"] < AUDIT.DETERMINANT_TOLERANCE


def test_shift_sign_and_incoming_mode_partition_are_explicit() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for row in artifact["VERIFICATION"]["per_beta"]:
        assert row["local_normal_shift"] == -row["beta"]
        assert row["incoming_modes"] == ["u1_minus"]
        assert row["u2_modes_are_outgoing"] is True
        assert row["boundary_regimes"] == ["U1_ONLY_INCOMING_SUBLUMINAL"]


def test_lane_closure_does_not_unlock_core_or_gravity() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["claim_promotion"] is False
    assert artifact["DEPENDENCY_UNLOCKED"].startswith("none;")
    assert "beta<0" in " ".join(artifact["WHAT_REMAINS_OPEN"])
    assert "not a new continuum proof" in artifact["CLAIM_BOUNDARY"]


def test_source_hashes_match_current_inputs() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    hashes = artifact["VERIFICATION"]["source_hashes"]
    for relative_path, expected in hashes.items():
        assert AUDIT._sha256(ROOT / relative_path) == expected

