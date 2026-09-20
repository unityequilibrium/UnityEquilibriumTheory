from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_mp48_force_constant_csrc_mesh_convergence_is_machine_readable() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    assert lane["status"] == "PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE"
    assert major["major_result_id"] == "T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["mesh_policy"]["native_mesh"] == "5x5x2"
    assert lane["mesh_policy"]["continuum_convergence_required_for_Ding_acceptance"] is True
    assert lane["mesh_policy"]["acceptance_policy"] == "complete_three_pair_fine_tail_across_all_target_temperatures"
    assert lane["mesh_policy"]["coarse_mesh_steps_retained_as_diagnostic"] is True
    assert lane["mesh_policy"]["fine_tail_pair_count_is_complete"] is True
    assert lane["max_abs_relative_mesh_step"] > lane["mesh_policy"]["acceptance_tolerance_abs_relative_step"]
    assert lane["mesh_policy"]["fine_tail_meshes"] == ["20x20x8", "25x25x10", "30x30x12", "35x35x14"]
    assert lane["mesh_policy"]["fine_tail_converged"] is True
    assert lane["mesh_policy"]["fine_tail_max_abs_relative_step"] < lane["mesh_policy"]["acceptance_tolerance_abs_relative_step"]
    assert lane["mesh_policy"]["finest_pair_meshes"] == ["30x30x12", "35x35x14"]
    assert lane["mesh_policy"]["finest_pair_converged"] is True
    assert lane["mesh_policy"]["finest_pair_max_abs_relative_step"] < lane["mesh_policy"]["acceptance_tolerance_abs_relative_step"]
    assert "mp48_force_constant_C_src_mesh_convergence_missing" not in major["open_blockers"]
    assert "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing" in major["open_blockers"]
    assert lane["controlling_blocker"] == "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing"
    assert all(lane["checks"].values())
    assert lane["holdout_accessed"] is False
    assert lane["target_fit_performed"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert "not" in major["claim_boundary"]
