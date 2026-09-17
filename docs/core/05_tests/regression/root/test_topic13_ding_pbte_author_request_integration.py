from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_author_request_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
ENERGY = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_author_request_is_integrated_without_changing_full_topic_status() -> None:
    audit = load(AUDIT)
    full = load(FULL)
    assert audit["status"] == "PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    branch = full["verification_status"]["alpha_Phi_K"]["named_energy_response_branch"]
    request = branch["pbte_author_request_package"]
    assert request["request_state"] == "REQUEST_PACKAGE_READY_NOT_SENT"
    assert request["sent"] is False
    assert request["response_received"] is False
    assert request["numeric_C_src_emitted"] is False
    assert request["numeric_alpha_Phi_K_emitted"] is False


def test_energy_bridge_and_register_expose_lane_result() -> None:
    energy = load(ENERGY)
    register = load(REGISTER)
    entries = {entry["major_result_id"]: entry for entry in register["entries"]}
    assert energy["pbte_numeric_input_availability"]["author_request_package"]["request_state"] == "REQUEST_PACKAGE_READY_NOT_SENT"
    assert entries["T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE"]["closure_level"] == "CLOSED_FOR_LANE"
    assert register["claim_promotion"] is False


def test_dependency_gate_records_request_without_unlock() -> None:
    dependency = load(DEPENDENCY)
    partial = dependency["topic13_partial_evidence"]
    assert partial["author_request_state"] == "REQUEST_PACKAGE_READY_NOT_SENT"
    assert partial["full_core_unlock"] is False
    assert dependency["status"] == "BLOCKED_DOWNSTREAM_MAJOR_RESULTS"
