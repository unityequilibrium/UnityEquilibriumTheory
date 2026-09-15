from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_alpha_phi_k_identifiability_audit.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_normalized_phi_scale_no_go_is_recorded_without_alpha_value() -> None:
    artifact = load(AUDIT)
    assert artifact["status"] == "NO_GO_FOR_ALPHA_FROM_NORMALIZED_LANE"
    assert all(artifact["checks"].values())
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["witness"]["alpha_witness_role"] == "algebraic witness only; not an external input or fit"


def test_topic13_alpha_gate_preserves_dimensional_blocker() -> None:
    gate = load(GATE)
    alpha = gate["verification_status"]["alpha_Phi_K"]
    assert alpha["status"] == "BLOCKED"
    assert alpha["independent_calibration_or_derivation"] is False
    assert alpha["identifiability_status"] == "NO_GO_FROM_NORMALIZED_PHI"
    assert gate["controlling_blocker"] == (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )
    assert gate["claim_promotion"] is False
