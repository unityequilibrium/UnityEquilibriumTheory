"""Integration checks for the covariant action SI-anchor boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/artifacts/t13_covariant_action_si_anchor_route_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_action_route_is_exposed_as_lane_only() -> None:
    full = load(FULL_REL)
    route = full["verification_status"]["covariant_action_si_anchor_route"]
    assert route["status"] == "PASS_ROUTE_IDENTIFIED_SI_BLOCKED"
    assert route["closure_level"] == "CLOSED_FOR_LANE"
    assert route["numeric_e0_emitted"] is False
    assert route["numeric_alpha_Phi_K_emitted"] is False
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
    assert "system_specific_SI_contract_missing" not in full["major_result"]["what_remains_open"]
    assert "covariant_Phi_to_normalized_Phi_map_missing" not in full["major_result"]["what_remains_open"]
    assert "Ding numeric C_src(T)" in full["next_action"]
    assert "system_specific_SI_contract_missing" in route["open_blockers"]


def test_action_route_register_and_dependency_hashes_match() -> None:
    register = load(REGISTER_REL)
    entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_COVARIANT_ACTION_SI_ANCHOR_ROUTE")
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == ACTION_REL)
    assert evidence["sha256"] == sha256(ACTION_REL)

    dependency = load(DEPENDENCY_REL)
    route = dependency["topic13_partial_evidence"]["covariant_action_si_anchor_route"]
    assert route["summary"]["full_core_unlock"] is False
    assert route["sha256"] == sha256(ACTION_REL)
    assert dependency["register"]["sha256"] == sha256(REGISTER_REL)
