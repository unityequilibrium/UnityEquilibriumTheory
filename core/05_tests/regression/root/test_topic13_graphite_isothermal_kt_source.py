from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_graphite_isothermal_kt_source_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_graphite_isothermal_kt_source_is_locked_without_material_match_promotion() -> None:
    lane = load(LANE)
    row = lane["source_row"]
    assert lane["status"] == "PASS_SCOPED_ISOTHERMAL_GRAPHITE_K_T_SOURCE"
    assert lane["major_result"]["major_result_id"] == "T13_GRAPHITE_ISOTHERMAL_KT_SOURCE"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["source"]["temperature_K"] == 300.0
    assert row["K_T_GPa"] == 33.8
    assert row["K_T_uncertainty_GPa"] == 3.0
    assert lane["thermodynamic_contract"]["isothermal_status"] == "DECLARED_BY_FIXED_T_PRESSURE_VOLUME_EOS"
    assert lane["thermodynamic_contract"]["Ding_material_regime_mapping_closed"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert all(lane["checks"].values())
