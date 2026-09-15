from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_one_loop_uv_boundary_audit.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_uv_boundary_audit_passes() -> None:
    audit = load()
    assert audit["status"] == "PASS_THERMAL_UV_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_thermal_tail_and_vacuum_boundary_are_separate() -> None:
    audit = load()
    assert audit["thermal_tail"]["relative_threshold"] == 1.0e-10
    assert max(audit["thermal_tail"]["relative_to_reference"].values()) <= 1.0e-10
    assert audit["vacuum_boundary"]["zero_point_term_included"] is False
    assert audit["vacuum_boundary"]["renormalized_action_claimed"] is False
    assert audit["controlling_blocker"] == "vacuum_counterterm_and_renormalized_one_loop_response_not_closed"
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
