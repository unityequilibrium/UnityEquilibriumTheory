from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_perez_castaneda_hopg_source_boundary_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_hopg_source_boundary_is_material_locked_and_comparator_only() -> None:
    result = load(ARTIFACT)
    assert result["status"] == "PASS_SCOPED_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY"
    assert result["major_result"]["major_result_id"] == "T13_PEREZ_CASTANEDA_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["source"]["local_sha256"] == "f5056e3804275336deca634da84a47fec1e91876ff65ab62a84596a5ad3ebd4a"
    assert result["source"]["local_bytes"] == 1141942
    assert result["source"]["page_count"] == 21
    assert result["source"]["material_identity"]["ding_ttg_match"] is False


def test_hopg_boundary_preserves_method_error_without_emitting_rows() -> None:
    result = load(ARTIFACT)
    uncertainty = result["source"]["uncertainty_boundary"]
    assert uncertainty["method_comparison_relative_bound"] == 0.03
    assert uncertainty["is_row_level_standard_uncertainty"] is False
    assert result["acceptance"]["numeric_rows_emitted"] == 0
    assert result["acceptance"]["figure_only_payload"] is True
    assert result["acceptance"]["accepted_for_full_topic13"] is False
    assert result["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
    assert result["acceptance"]["accepted_as_alpha_phi_k_calibration"] is False


def test_full_gate_exposes_hopg_boundary_without_unlocking_topic13() -> None:
    gate = load(FULL_GATE)
    lane = gate["verification_status"]["source_package"]["perez_castaneda_hopg_specific_heat_source_boundary"]
    assert lane["major_result_id"] == "T13_PEREZ_CASTANEDA_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["status"] == "PASS_SCOPED_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY"
    assert lane["controlling_blocker"] == "figure_only_numeric_payload_and_Ding_PBTE_response_mapping_missing"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
