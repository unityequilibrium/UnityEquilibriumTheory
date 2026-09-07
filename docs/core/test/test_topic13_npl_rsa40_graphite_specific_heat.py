from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "docs/core/artifacts/t13_npl_rsa40_graphite_specific_heat_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "npl_rsa40_graphite_specific_heat_source_package.json"
)
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_npl_cp_uncertainty_lane_is_source_locked_without_cv_or_alpha_promotion() -> None:
    lane = load(LANE)
    package = load(PACKAGE)
    full = load(FULL)
    register = load(REGISTER)
    projected = full["verification_status"]["source_package"][
        "npl_graphite_cp_uncertainty_comparator"
    ]
    assert lane["status"] == "PASS_SCOPED_NPL_CP_UNCERTAINTY_COMPARATOR_CV_OPEN"
    assert lane["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["numeric_cp_emitted"] is True
    assert lane["cv_emitted"] is False
    assert lane["uncertainty_grade_volumetric_cp_emitted"] is False
    assert lane["source"]["local_hash_observed"] == package["source"]["local_raw_sha256"]
    assert lane["source_rows"][0]["value_J_per_kg_K"] == 710.6
    assert lane["source_rows"][0]["standard_uncertainty_J_per_kg_K"] == 0.7
    assert projected["major_result_id"] == "T13_NPL_GRAPHITE_CP_UNCERTAINTY_COMPARATOR"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["sha256"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert "alpha_Phi_K_independent_calibration_missing" in full["major_result"]["what_remains_open"]
    assert "c_v_source_uncertainty_not_closed" in full["major_result"]["what_remains_open"]
    assert any(
        item["path"] == "docs/core/artifacts/t13_npl_rsa40_graphite_specific_heat_audit.json"
        for item in full["evidence_artifacts"]
    )
    assert any(
        item["major_result_id"] == "T13_NPL_GRAPHITE_CP_UNCERTAINTY_COMPARATOR"
        for item in register["entries"]
    )
