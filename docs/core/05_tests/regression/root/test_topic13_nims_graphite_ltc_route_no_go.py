from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_nims_graphite_ltc_route_no_go.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def test_nims_graphite_route_is_closed_as_a_source_no_go() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert result["status"] == "PASS_SCOPED_NIMS_GRAPHITE_ROUTE_NO_GO"
    assert result["major_result"]["major_result_id"] == "T13_NIMS_GRAPHITE_LTC_ROUTE_NO_GO"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["acceptance"]["route_closed_as_no_go"] is True
    assert result["acceptance"]["accepted_for_full_topic13"] is False
    assert result["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
    assert result["source"]["numeric_payload_consumed"] is False
    assert result["source"]["query_results"][0]["records_found"] == 0
    assert result["source"]["query_results"][1]["records_found"] == 0
    assert result["source"]["query_results"][5]["exact_elemental_carbon_formula_matches"] == 0
    assert result["source"]["query_results"][6]["returned_collection_titles"] == ["MDR XAFS DB"]


def test_full_gate_exposes_nims_route_no_go_without_csrc_promotion() -> None:
    gate = json.loads(FULL_GATE.read_text(encoding="utf-8-sig"))
    lane = gate["verification_status"]["source_package"]["nims_graphite_ltc_route_no_go"]
    assert lane["major_result_id"] == "T13_NIMS_GRAPHITE_LTC_ROUTE_NO_GO"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["status"] == "PASS_SCOPED_NIMS_GRAPHITE_ROUTE_NO_GO"
    assert lane["controlling_blocker"] == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
