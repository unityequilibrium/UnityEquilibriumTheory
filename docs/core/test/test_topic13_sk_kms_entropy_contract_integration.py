"""Integration checks for the formal Topic 13 SK/KMS/entropy result."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
ACTION = "docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json"
FULL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_formal_interface_is_closed_for_lane_only() -> None:
    action = load(ACTION)
    assert action["status"] == "PASS_NAMED_SK_KMS_ENTROPY_INTERFACE_CONTRACT"
    assert action["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert action["physical_coefficient_evidence"] == "BLOCKED_NOT_PROVIDED"
    assert action["full_SK_KMS_completion"] == "INTERFACE_ONLY_NOT_FULL_MATCH"
    assert action["numeric_transport_coefficients_emitted"] is False
    assert action["xie_2026_accessed"] is False


def test_formal_interface_hashes_and_dependency_boundary_are_linked() -> None:
    action = load(ACTION)
    full = load(FULL)
    assert full["verification_status"]["sk_kms_entropy_interface"]["closure_level"] == "CLOSED_FOR_LANE"
    assert full["claim_promotion"] is False
    register = load(REGISTER)
    entry = next(item for item in register["entries"] if item["major_result_id"] == action["major_result"]["major_result_id"])
    assert entry["evidence_artifacts"][0]["sha256"] == digest(ACTION)
    dependency = load(DEPENDENCY)
    route = dependency["topic13_partial_evidence"]["sk_kms_entropy_interface"]
    assert route["sha256"] == digest(ACTION)
    assert route["summary"]["full_core_unlock"] is False
    assert dependency["register"]["sha256"] == digest(REGISTER)
