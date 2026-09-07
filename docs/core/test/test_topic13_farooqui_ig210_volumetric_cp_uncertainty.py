from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "farooqui_2022_ig210_thermophysical_source_package.json"
)
ARTIFACT_PATH = ROOT / (
    "docs/core/artifacts/"
    "t13_farooqui_ig210_volumetric_cp_uncertainty_audit.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_volumetric_cp_rows_are_source_derived_with_conservative_bounds() -> None:
    package = load(PACKAGE_PATH)
    artifact = load(ARTIFACT_PATH)
    assert artifact["status"] == "PASS_SCOPED_FAROOQUI_IG210_VOLUMETRIC_CP_UNCERTAINTY"
    for source_row, derived in zip(package["source_rows"], artifact["derived_rows"]):
        expected = source_row["density_kg_per_m3"] * source_row[
            "specific_heat_Cp_J_per_kg_K"
        ]
        assert math.isclose(
            derived["volumetric_Cp_J_per_m3_K"], expected, rel_tol=0.0, abs_tol=1.0e-9
        )
        interval = derived["conservative_expanded_interval_J_per_m3_K"]
        assert interval["lower"] < expected < interval["upper"]
        assert derived["uncertainty_contract"]["standard_uncertainty_emitted"] is False


def test_lane_does_not_close_cv_or_ding_mapping() -> None:
    artifact = load(ARTIFACT_PATH)
    major = artifact["major_result"]
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert "same_state_IG210_isothermal_K_T_missing" in major["what_remains_open"]
    assert "C_p_to_C_v_correction_not_closed" in major["what_remains_open"]
    assert artifact["numeric_C_v_emitted"] is False
    assert artifact["numeric_Ding_C_src_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False


def test_holdout_and_fit_controls_remain_closed() -> None:
    artifact = load(ARTIFACT_PATH)
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["target_curve_used"] is False
    assert artifact["parameter_fitting_performed"] is False
