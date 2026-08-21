from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_alpha_phi_k_calibration_candidate_audit.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_candidate_search_is_scoped_and_emits_no_alpha() -> None:
    artifact = load(AUDIT)
    assert artifact["status"] == "PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD"
    assert artifact["candidate_count"] == 11
    assert artifact["eligible_candidate_count"] == 0
    assert artifact["holdout_accessed"] is False
    assert artifact["target_fit_performed"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    calorine = next(
        item
        for item in artifact["candidates"]
        if item["path"].endswith("calorine_legacy_nep2_pbte_reproduction_source_package.json")
    )
    assert calorine["eligible_paired_record"] is False
    assert calorine["controlling_blocker"] == "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing"


def test_candidate_eligibility_requires_semantic_record_values() -> None:
    artifact = load(AUDIT)
    assert artifact["eligible_candidate_count"] == 0
    assert all(
        item["semantic_eligible_record_count"] == 0
        for item in artifact["candidates"]
    )
    assert all(
        item["eligible_paired_record"] is False
        for item in artifact["candidates"]
    )

def test_full_gate_exposes_candidate_search_without_unlocking_alpha() -> None:
    gate = load(FULL)
    alpha = gate["verification_status"]["alpha_Phi_K"]
    assert alpha["candidate_search_status"] == "PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD"
    assert alpha["candidate_count"] == 11
    assert alpha["eligible_candidate_count"] == 0
    assert alpha["candidate_search_holdout_accessed"] is False
    assert alpha["candidate_search_fit_performed"] is False
    assert alpha["status"] == "BLOCKED"
    assert gate["claim_promotion"] is False
