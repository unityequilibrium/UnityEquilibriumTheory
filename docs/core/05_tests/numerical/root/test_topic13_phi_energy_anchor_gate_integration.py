"""Integration checks for the Topic 13 Phi-energy-anchor no-go result."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import hashlib
import json
from pathlib import Path


ROOT = repo_root()
NO_GO_REL = "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_full_gate_exposes_scoped_no_go_without_promotion() -> None:
    full = load(FULL_REL)
    result = full["verification_status"]["phi_energy_anchor_identifiability"]
    assert result["status"] == "PASS_SCOPED_NO_GO"
    assert result["closure_level"] == "CLOSED_FOR_LANE"
    assert result["numeric_e0_emitted"] is False
    assert result["numeric_alpha_Phi_K_emitted"] is False
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False


def test_register_and_dependency_reference_no_go_artifact() -> None:
    register = load(REGISTER_REL)
    entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_PHI_ENERGY_ANCHOR_IDENTIFIABILITY_NO_GO")
    assert entry["closure_level"] == "CLOSED_FOR_LANE"
    no_go_evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == NO_GO_REL)
    assert no_go_evidence["sha256"] == sha256(NO_GO_REL)

    dependency = load(DEPENDENCY_REL)
    partial = dependency["topic13_partial_evidence"]["phi_energy_anchor_no_go"]
    assert partial["summary"]["full_core_unlock"] is False
    assert partial["sha256"] == sha256(NO_GO_REL)
    assert dependency["register"]["sha256"] == sha256(REGISTER_REL)
