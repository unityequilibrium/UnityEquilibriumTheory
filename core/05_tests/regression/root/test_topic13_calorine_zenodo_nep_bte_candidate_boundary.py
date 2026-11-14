from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_zenodo_nep_bte_candidate_boundary_audit.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def test_calorine_route_is_source_located_but_not_accepted_for_full_topic13() -> None:
    result = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert result["status"] == "PASS_SCOPED_CALORINE_NEP_BTE_CANDIDATE_BOUNDARY"
    assert result["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert result["acceptance"]["accepted_for_full_topic13"] is False
    assert result["acceptance"]["accepted_as_independent_csrc_reproduction"] is False
    assert result["acceptance"]["candidate_route_ready_for_future_rerun"] is True
    assert result["acceptance"]["numeric_alpha_phi_k_emitted"] is False
    assert result["acceptance"]["target_fit_performed"] is False
    assert result["acceptance"]["holdout_accessed"] is False
    assert result["source"]["tutorial_declared_controls"]["transport_solver"] == "RTA via --bterta"


def test_full_gate_exposes_calorine_boundary_in_source_package_lane() -> None:
    gate = json.loads(FULL_GATE.read_text(encoding="utf-8-sig"))
    lane = gate["verification_status"]["source_package"]["calorine_zenodo_nep_bte_candidate_boundary"]
    assert lane["major_result_id"] == "T13_CALORINE_ZENODO_NEP_BTE_CANDIDATE_BOUNDARY"
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert lane["status"] == "PASS_SCOPED_CALORINE_NEP_BTE_CANDIDATE_BOUNDARY"
    assert lane["controlling_blocker"] == "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing"
