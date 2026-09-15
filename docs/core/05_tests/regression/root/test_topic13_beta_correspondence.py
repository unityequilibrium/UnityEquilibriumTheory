from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
AUDIT = ROOT / "docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json"
FULL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_beta_correspondence_no_go_closes_only_the_structural_question() -> None:
    audit = load(AUDIT)
    assert audit["status"] == "PASS_SCOPED_NO_GO_ACTION_BETA_T13_CORRESPONDENCE"
    assert audit["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(audit["checks"].values())
    assert audit["claim_promotion"] is False
    assert audit["holdout_policy"]["xie_2026_accessed"] is False


def test_beta_correspondence_has_no_inferred_physical_values() -> None:
    audit = load(AUDIT)
    assert audit["input_records"]["action_beta_units"] == "natural mass dimension two"
    assert audit["input_records"]["normalized_beta_units"] == "dimensionless local stiffness-temperature slope"
    assert all(item["inferred_beta_t13_from_bridge"] is None for item in audit["scale_witnesses"])
    assert all(item["inferred_alpha_phi_k"] is None for item in audit["scale_witnesses"])


def test_beta_correspondence_is_exposed_under_bridge_without_unlock() -> None:
    full = load(FULL)
    route = full["verification_status"]["non_circular_bridge"][
        "beta_action_normalized_correspondence_no_go"
    ]
    assert route["status"] == "PASS_SCOPED_NO_GO_ACTION_BETA_T13_CORRESPONDENCE"
    assert route["closure_level"] == "CLOSED_AS_NO_GO"
    assert full["status"] == "BLOCKED_OPEN_T13_FULL_BRIDGE"
    assert full["major_result"]["closure_level"] == "PARTIAL"
    assert full["claim_promotion"] is False
