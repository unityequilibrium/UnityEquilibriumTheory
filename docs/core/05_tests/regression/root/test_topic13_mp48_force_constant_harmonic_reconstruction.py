from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_mp48_force_constant_reconstruction_is_closed_without_promotion() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    reconstruction = lane["reconstruction"]
    assert lane["status"] == "PASS_SCOPED_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION"
    assert major["major_result_id"] == "T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert major["data_role"] == "INTERNAL_HARMONIC_SOURCE_RECONSTRUCTION_NOT_DING_PBTE"
    assert lane["source"]["primitive_cell_atoms"] == 4
    assert lane["source"]["supercell_atoms"] == 200
    assert reconstruction["force_constant_shape"] == [200, 200, 3, 3]
    assert reconstruction["q_grid_sample_count"] == 50
    assert reconstruction["q_grid_negative_eigenvalue_count_beyond_roundoff"] == 0
    assert reconstruction["gamma_acoustic_max_abs_frequency_THz"] <= 1.0e-5
    assert abs(reconstruction["q_grid_to_summary_max_frequency_relative_gap"]) <= 0.005
    assert all(lane["checks"].values())
    assert lane["holdout_accessed"] is False
    assert lane["target_fit_performed"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert "not Ding's PBTE C_src" in major["claim_boundary"]
