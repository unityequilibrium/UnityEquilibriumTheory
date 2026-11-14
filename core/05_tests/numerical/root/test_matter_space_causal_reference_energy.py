"""Tests for the quadratic causal-reference energy artifact."""
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path


ARTIFACT = canonical_artifact_path(
    "matter_space_causal_reference_energy_verification.json", "verification"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_reference_energy_identity_passes_without_promoting_full_candidate():
    artifact = load_artifact()
    assert artifact["audit_status"] == "PASS"
    assert artifact["reference_status"] == "PASS"
    assert artifact["full_coupled_candidate_status"] == "BLOCKED"
    metrics = artifact["reference"]["metrics"]
    assert metrics["max_relative_identity_residual"] <= metrics["threshold"]
    assert metrics["energy_increase_steps"] == 0


def test_artifact_declares_reference_scope_and_claim_boundary():
    artifact = load_artifact()
    assert artifact["reference"]["identity"]["scope"] == "quadratic_reference_lane"
    assert "full nonlinear coupled operator" in artifact["claim_boundary"]
