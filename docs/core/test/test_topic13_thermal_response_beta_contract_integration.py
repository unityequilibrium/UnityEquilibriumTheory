"""Integration checks for the named Topic 13 finite-temperature beta contract."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
ACTION_REL = "docs/core/artifacts/t13_thermal_response_beta_contract_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_named_beta_contract_is_closed_for_lane_only() -> None:
    full = load(FULL_REL)
    route = full["verification_status"]["thermal_response_beta_contract"]
    assert route["status"] == "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT"
    assert route["closure_level"] == "CLOSED_FOR_LANE"
    assert route["numeric_beta_T13_emitted"] is False
    assert route["parameter_fitting_performed"] is False
    assert route["source_rows_consumed"] is False
    assert route["target_data_used"] is False
    assert route["xie_2026_accessed"] is False
    assert full["verification_status"]["non_circular_bridge"]["status"] == "BLOCKED"
    assert full["verification_status"]["non_circular_bridge"]["formal_boundary_closure_level"] == "CLOSED_FOR_LANE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False


def test_named_beta_contract_register_and_dependency_hashes_match() -> None:
    register = load(REGISTER_REL)
    result_id = "T13_THERMAL_RESPONSE_BETA_CONTRACT"
    entry = next(item for item in register["entries"] if item.get("major_result_id") == result_id)
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == ACTION_REL)
    assert evidence["sha256"] == sha256(ACTION_REL)

    dependency = load(DEPENDENCY_REL)
    route = dependency["topic13_partial_evidence"]["thermal_response_beta_contract"]
    assert route["summary"]["full_core_unlock"] is False
    assert route["sha256"] == sha256(ACTION_REL)
    assert dependency["register"]["sha256"] == sha256(REGISTER_REL)
