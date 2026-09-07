from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_causal_named_branch_core_compatibility.json"
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_named_causal_branch_is_core_compatible_without_global_promotion() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS_CAUSAL_NAMED_BRANCH_CORE_COMPATIBILITY"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_CORE"
    assert all(artifact["checks"].values())
    assert artifact["baseline_preservation"]["baseline_replaced"] is False
    assert artifact["holdout_policy"]["xie_2026_accessed"] is False


def test_full_gate_requires_the_named_branch_core_exception() -> None:
    gate = load(GATE)
    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    assert causal["full_candidate_pass"] is False
    assert causal["named_coupled_branch_core_compatibility_pass"] is True
    assert causal["named_coupled_branch_core_compatibility_closure_level"] == "CLOSED_FOR_CORE"
    assert causal["causal_core_exception_pass"] is True
    assert causal["baseline_replaced"] is False
    assert gate["claim_promotion"] is False
