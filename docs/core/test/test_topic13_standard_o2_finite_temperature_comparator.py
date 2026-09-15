from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_standard_o2_finite_temperature_comparator_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_standard_o2_finite_temperature_comparator_passes() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_standard_o2_comparator_does_not_close_uet_thermal_lane() -> None:
    audit = load(AUDIT)
    major = audit["major_result"]
    assert major["data_role"] == "STANDARD_THERMAL_QFT_COMPARATOR_NOT_UET_CLOSURE"
    assert "finite_temperature_UET_effective_action_not_derived" in major["open_blockers"]
    assert "physical_Kubo_coefficient_record_missing" in major["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
