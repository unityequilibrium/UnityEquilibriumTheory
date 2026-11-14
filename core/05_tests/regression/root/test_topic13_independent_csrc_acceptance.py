from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def test_independent_csrc_contract_keeps_current_routes_blocked() -> None:
    artifact = load("docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json")
    acceptance = artifact["acceptance"]

    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert acceptance["raw_author_numeric_C_src_available"] is False
    assert acceptance["accepted_independent_reproduction_available"] is False
    assert acceptance["accepted_for_full_topic13"] is False
    assert acceptance["status"] == "BLOCKED"
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["target_fit_performed"] is False
    assert artifact["holdout_accessed"] is False


def test_full_gate_exposes_independent_route_without_promoting_it() -> None:
    gate = load(
        "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
    )
    source = gate["verification_status"]["source_package"]

    assert source["independent_reproduction_route_ready"] is False
    assert source["independent_reproduction_acceptance_status"] == "BLOCKED"
    assert source["status"] == "BLOCKED"
    assert gate["claim_promotion"] is False
