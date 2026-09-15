from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_condensate_gaussian_thermal_audit.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_gaussian_finite_temperature_lane_passes() -> None:
    audit = load()
    assert audit["status"] == "PASS_ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_gaussian_lane_keeps_full_thermal_closure_open() -> None:
    audit = load()
    reference = audit["reference"]
    assert reference["fixed_tree_level_background"] is True
    assert "thermal_background_backreaction_and_self_consistent_phase_boundary_not_closed" in audit["major_result"]["open_blockers"]
    assert "normal_two_fluid_current_and_physical_Kubo_coefficient_missing" in audit["major_result"]["open_blockers"]
    assert reference["quadrature_order"] == 256
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
