import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_calorine_model_form_state_spread_comparison_audit.json"
FULL_GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def test_calorine_model_form_state_spread_is_comparator_only() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_SCOPED_CALORINE_MODEL_FORM_STATE_SPREAD"
    assert audit["major_result"]["major_result_id"] == (
        "T13_CALORINE_MODEL_FORM_STATE_SPREAD_COMPARISON"
    )
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["comparison"]["mesh"] == [10, 10, 5]
    assert audit["comparison"]["temperatures_K"] == [200.0, 300.0]
    assert len(audit["comparison"]["rows"]) == 2
    assert all("relative_spread_to_baseline" in row for row in audit["comparison"]["rows"])
    assert audit["checks"]["source_input_hashes_match"] is True
    assert audit["checks"]["baseline_no_fit_target_alpha_or_holdout"] is True
    assert audit["checks"]["variant_no_fit_target_alpha_or_holdout"] is True
    assert audit["checks"]["comparison_is_not_source_grade_uncertainty"] is True
    assert audit["checks"]["comparison_is_not_pure_model_form_error"] is True
    assert audit["numeric_C_src_emitted"] is False
    assert audit["numeric_alpha_Phi_K_emitted"] is False
    assert audit["acceptance_for_full_topic13"] is False
    assert audit["claim_promotion"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False


def test_calorine_model_form_state_spread_is_projected_without_unlock() -> None:
    audit = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    full_gate = json.loads(FULL_GATE.read_text(encoding="utf-8-sig"))
    register = json.loads(REGISTER.read_text(encoding="utf-8-sig"))
    dependency = json.loads(DEPENDENCY.read_text(encoding="utf-8-sig"))
    lane = full_gate["verification_status"]["source_package"][
        "calorine_model_form_state_spread_comparison"
    ]
    assert lane["major_result_id"] == "T13_CALORINE_MODEL_FORM_STATE_SPREAD_COMPARISON"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert full_gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full_gate["claim_promotion"] is False
    entry = next(
        item
        for item in register["entries"]
        if item["major_result_id"] == "T13_CALORINE_MODEL_FORM_STATE_SPREAD_COMPARISON"
    )
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    assert dependency["topic13_partial_evidence"]["source_lanes"]["calorine_model_form_state_spread_comparison"]["full_core_unlock"] is False
