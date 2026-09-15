"""Artifact-boundary tests for the causal discrete-gradient packet."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path


ARTIFACT = (
    canonical_artifact_path("matter_space_causal_discrete_gradient_verification.json")
)


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_partial_causal_closure_does_not_promote_full_operator() -> None:
    artifact = load()
    assert artifact["audit_status"] == "BLOCKED"
    assert artifact["partial_closure_status"] == "PASS"
    assert artifact["full_coupled_candidate_status"] == "BLOCKED"
    assert artifact["controlling_blocker"] == "matter_C_shared_ledger_integration_missing"


def test_artifact_records_causal_scope_and_no_trace_feedback() -> None:
    artifact = load()
    contract = artifact["contract"]
    assert contract["C_during_step"] == "frozen"
    assert contract["required_cfl"] == 1.0
    assert contract["trace_feedback"] is False
    assert "changing-C full operator" in artifact["claim_boundary"]
