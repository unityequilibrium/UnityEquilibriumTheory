"""Integration checks for the Topic 13 matter-coupling normalization no-go."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_matter_coupling_no_go_stays_in_dimensional_lane() -> None:
    full = load(FULL_REL)
    route = full["verification_status"]["dimensional_observable_map"][
        "covariant_matter_coupling_normalization_no_go"
    ]
    assert route["status"] == "PASS_SCOPED_NO_GO_COVARIANT_MATTER_COUPLING_NORMALIZATION"
    assert route["closure_level"] == "CLOSED_AS_NO_GO"
    assert route["numeric_e0_emitted"] is False
    assert route["numeric_alpha_Phi_K_emitted"] is False
    assert route["target_data_used"] is False
    assert route["xie_2026_accessed"] is False
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False


def test_matter_coupling_no_go_register_and_dependency_hashes_match() -> None:
    register = load(REGISTER_REL)
    result_id = "T13_COVARIANT_MATTER_COUPLING_NORMALIZATION_IDENTIFIABILITY_NO_GO"
    entry = next(item for item in register["entries"] if item.get("major_result_id") == result_id)
    assert entry["closure_level"] == "CLOSED_AS_NO_GO"
    evidence = next(item for item in entry["evidence_artifacts"] if item["path"] == ACTION_REL)
    assert evidence["sha256"] == sha256(ACTION_REL)

    dependency = load(DEPENDENCY_REL)
    route = dependency["topic13_partial_evidence"][
        "covariant_matter_coupling_normalization_no_go"
    ]
    assert route["summary"]["full_core_unlock"] is False
    assert route["sha256"] == sha256(ACTION_REL)
    assert dependency["register"]["sha256"] == sha256(REGISTER_REL)
