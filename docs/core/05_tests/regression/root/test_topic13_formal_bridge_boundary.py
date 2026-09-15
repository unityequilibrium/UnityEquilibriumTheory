"""Integration checks for the Topic 13 formal bridge-boundary result."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
ACTION = "docs/core/07_artifacts/topic13/t13_formal_bridge_boundary_audit.json"
FULL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_formal_boundary_closes_only_the_lane() -> None:
    action = load(ACTION)
    assert action["status"] == "PASS_FORMAL_NONCIRCULAR_BRIDGE_BOUNDARY"
    assert action["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert action["numeric_alpha_Phi_K_emitted"] is False
    assert action["parameter_fitting_performed"] is False
    assert action["target_data_used"] is False
    assert action["xie_2026_accessed"] is False
    assert action["physical_bridge_status"]["alpha_Phi_K"] == "OPEN_CALIBRATION"


def test_formal_boundary_is_linked_without_downstream_unlock() -> None:
    action = load(ACTION)
    full = load(FULL)
    route = full["verification_status"]["eos_transport_kms_entropy"]["formal_non_circular_bridge_boundary"]
    assert route["major_result_id"] == action["major_result"]["major_result_id"]
    assert route["closure_level"] == "CLOSED_FOR_LANE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False

    register = load(REGISTER)
    entry = next(item for item in register["entries"] if item["major_result_id"] == action["major_result"]["major_result_id"])
    evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == ACTION)
    assert evidence["sha256"] == digest(ACTION)

    dependency = load(DEPENDENCY)
    partial = dependency["topic13_partial_evidence"]["formal_non_circular_bridge_boundary"]
    assert partial["sha256"] == digest(ACTION)
    assert partial["summary"]["full_core_unlock"] is False
    assert dependency["claim_promotion"] is False
