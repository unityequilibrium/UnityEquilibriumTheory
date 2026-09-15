"""Artifact-boundary tests for the changing-C split bridge."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path


ARTIFACT = (
    canonical_artifact_path("matter_space_causal_split_verification.json")
)


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_split_ledger_passes_without_passing_causal_cone() -> None:
    artifact = load()
    assert artifact["split_bridge_status"] == "PASS_WITHIN_DECLARED_TOLERANCE"
    assert artifact["shared_ledger_status"] == "PASS"
    assert artifact["changing_C_causal_cone_status"] == "BLOCKED"
    assert artifact["full_candidate_status"] == "BLOCKED"


def test_split_contract_exposes_parabolic_c_scope() -> None:
    artifact = load()
    assert artifact["contract"]["matter_lane"] == "conserved_parabolic_subcycle"
    assert artifact["contract"]["trace_feedback"] is False
    assert "response cone" in artifact["claim_boundary"]
