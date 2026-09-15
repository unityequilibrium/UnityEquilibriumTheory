from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_uet_o2_condensate_goldstone_ideal_lane_audit.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_condensate_goldstone_ideal_lane_passes() -> None:
    audit = load()
    assert audit["status"] == "PASS_T0_CONDENSATE_GOLDSTONE_IDEAL_LANE"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_condensate_lane_keeps_finite_temperature_and_physical_transport_open() -> None:
    audit = load()
    assert audit["boundary"]["temperature_scope"] == "T_ZERO_PURE_SUPERFLUID_ONLY"
    assert audit["boundary"]["normal_component"] == "OPEN_NOT_DERIVED"
    assert audit["boundary"]["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS"
    assert audit["synthetic_mode_control"]["physical_transport_claim"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
