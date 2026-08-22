from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "docs/core/artifacts/t13_mp48_ding_csrc_response_mapping_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_mp48_ding_csrc_response_mapping_is_scoped_and_machine_readable() -> None:
    lane = load(LANE)
    major = lane["major_result"]
    mapping = lane["mapping_contract"]

    assert lane["status"] == "PASS_T13_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING"
    assert major["major_result_id"] == "T13_MP48_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING"
    assert major["closure_level"] == "CLOSED_FOR_LANE"
    assert mapping["selected_mesh"] == "35x35x14"
    assert len(mapping["rows"]) == 4
    assert all(
        math.isfinite(row["c_src_volumetric_J_per_m3_K"])
        and row["c_src_volumetric_J_per_m3_K"] > 0.0
        for row in mapping["rows"]
    )
    assert mapping["material_mapping_status"] == "OPEN"
    assert mapping["source_uncertainty_status"] == "OPEN"
    assert mapping["route_wide_convergence_status"] == "OPEN"
    assert mapping["ding_numeric_payload_present"] is False
    assert mapping["accepted_for_full_topic13"] is False
    assert lane["numeric_alpha_Phi_K_emitted"] is False
    assert lane["target_fit_performed"] is False
    assert lane["holdout_accessed"] is False
    assert all(lane["checks"].values())
    assert len(lane["source"]["ding_locators"]) == 2
    assert "not Ding PBTE C_src acceptance" in major["claim_boundary"]

def test_mp48_ding_csrc_response_mapping_projects_without_core_unlock() -> None:
    full = load(FULL_GATE)
    register = load(REGISTER)
    dependency = load(DEPENDENCY)

    projected = full["verification_status"]["source_package"]["mp48_ding_csrc_response_mapping"]
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["claim_promotion"] is False
    assert projected["major_result_id"] == "T13_MP48_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING"
    assert projected["closure_level"] == "CLOSED_FOR_LANE"
    assert projected["mapping_contract"]["accepted_for_full_topic13"] is False
    assert "T13_MP48_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING" in full["major_result"]["closure_summary"]["closed_lane_result_ids"]

    entry = next(
        item
        for item in register["entries"]
        if item["major_result_id"] == "T13_MP48_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING"
    )
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    dependency_lane = dependency["topic13_partial_evidence"]["source_lanes"]["mp48_ding_csrc_response_mapping"]
    assert dependency_lane["full_core_unlock"] is False
