from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_fluctuation_spectrum_audit.json"


def load() -> dict:
    return json.loads(AUDIT.read_text(encoding="utf-8-sig"))


def test_quadratic_fluctuation_spectrum_passes() -> None:
    audit = load()
    assert audit["status"] == "PASS_T0_QUADRATIC_FLUCTUATION_SPECTRUM"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False


def test_spectrum_keeps_finite_temperature_boundary_explicit() -> None:
    audit = load()
    assert audit["major_result"]["data_role"] == "ACTION_DERIVED_T0_SPECTRUM_NOT_FINITE_TEMPERATURE_TRANSPORT"
    assert "finite_temperature_normal_component_not_derived" in audit["major_result"]["open_blockers"]
    assert audit["holdout_policy"]["xie_2026_accessed"] is False
    assert audit["holdout_policy"]["alpha_fit_used"] is False
