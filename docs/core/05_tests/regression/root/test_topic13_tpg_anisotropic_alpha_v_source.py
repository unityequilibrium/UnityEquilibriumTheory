from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import pytest


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_tpg_anisotropic_alpha_v_source_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_tpg_anisotropic_alpha_v_source_is_locked_without_same_specimen_promotion() -> None:
    lane = load(LANE)
    row = lane["source_row"]
    derived = lane["derived_comparator"]
    assert lane["status"] == "PASS_SCOPED_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR"
    assert lane["major_result"]["major_result_id"] == "T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert row["alpha_a_per_K"] == pytest.approx(-1.04e-6)
    assert row["alpha_c_per_K"] == pytest.approx(26.84e-6)
    assert derived["alpha_V_per_K"] == pytest.approx(24.76e-6)
    assert derived["alpha_V_uncertainty_per_K"] == pytest.approx(4.565085979e-7)
    assert derived["same_specimen_alpha_V"] is False
    assert derived["K_T_emitted"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert all(lane["checks"].values())
