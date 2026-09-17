from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_one_loop_normal_branch_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_action_derived_one_loop_normal_branch_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_one_loop_normal_branch_keeps_excluded_physics_open() -> None:
    audit = load(AUDIT)
    state = audit["state"]
    blockers = audit["major_result"]["open_blockers"]
    assert state["vacuum_counterterm_included"] is False
    assert state["condensate_contribution_included"] is False
    assert state["normal_two_fluid_completion"] is False
    assert "physical_Kubo_coefficient_record_missing" in blockers
    assert "alpha_Phi_K_missing" in blockers
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
