from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_aist_graphite_source_route_boundary_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def test_aist_route_is_closed_at_public_reproducibility_boundary() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert result["status"] == "PASS_SCOPED_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY"
    assert result["major_result"]["major_result_id"] == "T13_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["acceptance"]["route_closed_as_public_reproducibility_boundary"] is True
    assert result["acceptance"]["accepted_for_full_topic13"] is False
    assert result["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
    assert result["acceptance"]["accepted_as_alpha_phi_k_calibration"] is False


def test_aist_route_does_not_store_or_consume_numeric_payload() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    source = result["source"]
    assert source["numeric_payload_accessed"] is False
    assert source["numeric_payload_stored"] is False
    assert source["material_detail_opened"] is False
    assert source["material_state_verified"] is False
    assert source["terms"]["public_numeric_redistribution_permitted"] is False
    assert "Specific heat capacity at constant volume" in source["property_catalog_observed"]
    assert "Volumetric heat capacity" in source["property_catalog_observed"]
    assert result["acceptance"]["holdout_accessed"] is False


def test_full_gate_exposes_aist_boundary_without_promoting_source_or_topic() -> None:
    gate = json.loads(FULL_GATE.read_text(encoding="utf-8-sig"))
    lane = gate["verification_status"]["source_package"]["aist_graphite_source_route_boundary"]
    assert lane["major_result_id"] == "T13_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["status"] == "PASS_SCOPED_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY"
    assert lane["controlling_blocker"] == "aist_numeric_payload_not_publicly_redistributable"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
