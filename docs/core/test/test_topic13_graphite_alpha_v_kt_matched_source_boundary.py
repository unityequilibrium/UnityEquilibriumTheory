from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/artifacts/t13_graphite_alpha_v_kt_matched_source_boundary_audit.json"
LOWITZER_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/lowitzer_2006_graphite_pvt_candidate_source_package.json"
LOWITZER_FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/lowitzer_2006_graphite_pvt_full_source_package.json"
LOWITZER_FULL_AUDIT_REL = "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json"
TOHEI_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/tohei_2006_graphite_alpha_v_kt_table_comparator_source_package.json"
FAROOQUI_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/farooqui_2022_ig210_thermophysical_source_package.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_current_alpha_v_kt_inventory_is_closed_as_a_scoped_boundary() -> None:
    audit = load(AUDIT_REL)
    assert audit["status"] == "PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_SOURCE_PAIR_LOCKED_MATERIAL_OPEN"
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(audit["checks"].values())
    assert audit["controlling_blocker"] == "material_regime_mapping_to_TTG_not_closed"
    assert audit["claim_boundary"].startswith("No Ding C_src")
    assert audit["source_pair_observations"]["hanfland_kt"]["same_state_alpha_V_available"] is False
    assert audit["source_pair_observations"]["bosak_elastic_bulk"]["thermal_K_T_claimed"] is False
    assert audit["source_pair_observations"]["tpg_alpha_v"]["same_specimen_for_both_axes"] is False
    assert audit["source_pair_observations"]["nelson_riley_alpha_v"]["same_specimen_alpha_V"] is False
    lowitzer = load(LOWITZER_REL)
    assert lowitzer["status"] == "SOURCE_SCREENED_ABSTRACT_ONLY_NO_CLOSURE"
    assert lowitzer["source"]["payload_state"] == "ABSTRACT_ONLY"
    assert audit["source_pair_observations"]["lowitzer_pvt_candidate"]["numeric_alpha_V_rows_available"] is False
    assert audit["source_pair_observations"]["lowitzer_pvt_candidate"]["numeric_K_T_rows_available"] is False
    assert audit["source_pair_observations"]["lowitzer_pvt_candidate"]["source_grade_uncertainty_available"] is False
    lowitzer_full = load(LOWITZER_FULL_REL)
    assert lowitzer_full["status"] == "SOURCE_LOCKED_THERMODYNAMIC_PAIR_COMPARATOR_MATERIAL_MAPPING_OPEN"
    assert lowitzer_full["pair_contract"]["same_grade_alpha_V_and_K_T_pair_closed"] is True
    assert lowitzer_full["pair_contract"]["Ding_material_regime_mapping_closed"] is False
    assert lowitzer_full["pair_contract"]["numeric_Ding_C_src_emitted"] is False
    lowitzer_full_audit = load(LOWITZER_FULL_AUDIT_REL)
    assert lowitzer_full_audit["status"] == "PASS_SCOPED_SOURCE_LOCKED_LOWITZER_ALPHA_V_K_T_PAIR"
    assert audit["source_pair_observations"]["lowitzer_full_pvt_pair"]["same_grade_alpha_V_and_K_T_pair_closed"] is True
    tohei = load(TOHEI_REL)
    assert tohei["status"] == "SOURCE_SCREENED_TABLE_COMPARATOR_NO_CLOSURE"
    assert tohei["pair_contract"]["numeric_table_alpha_V_present"] is True
    assert tohei["pair_contract"]["numeric_table_K_T_or_B0_present"] is True
    assert tohei["pair_contract"]["same_calculation_alpha_V_and_B0_pair_present"] is True
    assert tohei["pair_contract"]["same_specimen_experimental_alpha_V_and_K_T_pair_established"] is False
    assert tohei["pair_contract"]["source_grade_uncertainty_available"] is False
    assert audit["source_pair_observations"]["tohei_table_comparator"]["calculated_graphite_pair"] is True
    assert audit["source_pair_observations"]["tohei_table_comparator"]["experimental_same_specimen_pair"] is False
    farooqui = load(FAROOQUI_REL)
    assert farooqui["status"] == "SOURCE_LOCKED_IG210_THERMOPHYSICAL_COMPARATOR_KT_OPEN"
    assert farooqui["derived_comparator"]["same_grade_ig210_source"] is True
    assert farooqui["derived_comparator"]["row_count"] == 3
    assert farooqui["derived_comparator"]["same_state_K_T_present"] is False
    assert farooqui["derived_comparator"]["c_v_present"] is False
    assert farooqui["derived_comparator"]["alpha_Phi_K_calibration_emitted"] is False
    assert audit["source_pair_observations"]["farooqui_ig210_thermophysical"]["same_state_K_T_present"] is False


def test_alpha_v_kt_boundary_is_projected_without_full_topic13_promotion() -> None:
    full = load(FULL_REL)
    register = load(REGISTER_REL)
    dependency = load(DEPENDENCY_REL)
    projected = full["verification_status"]["source_package"][
        "graphite_alpha_v_kt_matched_source_boundary"
    ]

    assert projected["major_result_id"] == "T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["audit"]["path"] == AUDIT_REL
    assert projected["audit"]["sha256"] == sha256(AUDIT_REL)
    assert any(item["path"] == AUDIT_REL for item in full["evidence_artifacts"])
    assert "same_grade_alpha_V_and_K_T_missing" not in full["major_result"]["what_remains_open"]
    assert "material_regime_mapping_to_TTG_not_closed" in full["major_result"]["what_remains_open"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert any(
        item.get("major_result_id") == "T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY"
        for item in register["entries"]
    )
    assert dependency["decisions"]["CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"][
        "status"
    ] == "UNLOCKED"
