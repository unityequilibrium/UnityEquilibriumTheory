from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/day_2012_preferred_thermodynamic_table_source_package.json"
AUDIT_REL = "docs/core/artifacts/t13_day2012_preferred_thermodynamic_table_boundary_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_day_route_is_closed_only_as_a_scoped_boundary() -> None:
    package = load(PACKAGE_REL)
    audit = load(AUDIT_REL)
    assert audit["status"] == "PASS_SCOPED_DAY2012_THERMODYNAMIC_ASSESSMENT_BOUNDARY_NO_GO"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert package["table_transcription"]["graphite"]["B0_kbar"] == {"value": 338.0, "two_sigma": 30.0}
    assert package["table_transcription"]["graphite"]["thermal_expansion_a0_uncertainty_status"] == "NOT_REPORTED_IN_TABLE"
    assert audit["acceptance"]["accepted_for_full_topic13"] is False
    assert audit["acceptance"]["accepted_for_alpha_Phi_K_calibration"] is False
    assert package["source"]["license_or_terms"].startswith("Published article")
    assert package["source"]["preprocessing"].startswith("Manual transcription")
    assert audit["major_result"]["ontology"]["Phi"].startswith("effective response")
    assert len(audit["major_result"]["formula_contract"]) == 2


def test_day_route_is_projected_without_promoting_full_topic13() -> None:
    full = load(FULL_REL)
    lane = full["verification_status"]["source_package"]["day2012_preferred_thermodynamic_assessment_boundary"]
    assert lane["major_result_id"] == "T13_DAY2012_PREFERRED_THERMODYNAMIC_ASSESSMENT_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["audit"]["path"] == AUDIT_REL
    assert lane["audit"]["sha256"] == sha256(AUDIT_REL)
    assert any(item["path"] == AUDIT_REL for item in full["evidence_artifacts"])
    assert "same_grade_alpha_V_and_K_T_missing" not in full["major_result"]["what_remains_open"]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"]["what_remains_open"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
