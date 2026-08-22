from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / (
    "topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def test_payload_acceptance_controller_is_projected_into_full_gate() -> None:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    controller = gate["verification_status"]["source_package"][
        "ding_pbte_payload_acceptance_controller"
    ]
    assert controller["status"] == "BLOCKED_DING_PBTE_PAYLOAD_NOT_RECEIVED"
    assert controller["payload_present"] is False
    assert controller["numeric_C_src_accepted"] is False
    assert controller["numeric_alpha_Phi_K_emitted"] is False
    assert controller["holdout_accessed"] is False
    assert controller["audit"]["path"] == (
        "docs/core/artifacts/t13_ding_pbte_payload_acceptance_audit.json"
    )

    evidence_paths = {item["path"] for item in gate["evidence_artifacts"]}
    assert controller["audit"]["path"] in evidence_paths
    assert gate["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert gate["claim_promotion"] is False
    assert gate["major_result"]["dependency_unlocked"].startswith("Gravity/GR remains blocked")
