from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_gaussian_offshell_background_audit.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_offshell_background_boundary_passes() -> None:
    audit = load()
    assert audit["status"] == "PASS_ACTION_DERIVED_OFFSHELL_THERMAL_BACKREACTION_BOUNDARY"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_offshell_boundary_exposes_thermal_stationarity_blocker() -> None:
    audit = load()
    reference = audit["reference"]
    assert reference["right_one_sided_slope"] > reference["tadpole_threshold"]
    assert reference["left_status"] == "FloatingPointError"
    assert (
        "self_consistent_finite_temperature_phase_boundary_requires_thermal_self_energy_or_declared_renormalized_effective_action"
        in audit["major_result"]["open_blockers"]
    )
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
