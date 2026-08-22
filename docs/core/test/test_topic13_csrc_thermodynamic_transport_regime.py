from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_csrc_transport_decomposition_quantifies_separate_mesh_sensitivity() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS_SCOPED_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["claim_promotion"] is False
    assert artifact["checks"]["transport_change_exceeds_csrc_change"] is True
    pair = artifact["latest_mesh_pair"]
    assert pair["max_C_src_relative_change"] > 0.0
    assert pair["max_kappa_relative_change"] > pair["max_C_src_relative_change"]
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False
    assert artifact["holdout_policy"]["numeric_alpha_Phi_K_emitted"] is False


def test_csrc_transport_decomposition_is_projected_without_full_topic_unlock() -> None:
    artifact = load(ARTIFACT)
    gate = load(GATE)
    lane = gate["verification_status"]["source_package"][
        "csrc_thermodynamic_transport_regime_decomposition"
    ]
    assert lane["major_result_id"] == artifact["major_result"]["major_result_id"]
    assert lane["closure_level"] == "CLOSED_FOR_LANE"
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing" in gate[
        "major_result"
    ]["what_remains_open"]
