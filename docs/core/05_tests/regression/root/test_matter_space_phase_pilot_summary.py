"""Tests for the provenance-preserving canonical phase-pilot export."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/matter_space_phase_pilot.json"


def read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_export_preserves_internal_and_dependency_status() -> None:
    artifact = read()
    assert artifact["status"] == "INTERNAL_DIAGNOSTIC"
    assert artifact["verification_status"] == "PASS"
    assert artifact["dependency_status"] == "BLOCKED"
    assert artifact["topic_status_impact"] == "NONE"
    assert artifact["source_artifact"]["sha256"]


def test_export_preserves_trace_invariance_and_causal_blocker() -> None:
    artifact = read()
    diagnostics = artifact["diagnostics"]
    assert diagnostics["same_complete_state_different_trace_history"]["physical_difference"] == 0.0
    assert diagnostics["causal_arrival"]["new_causal_claim"] is False
    assert "structure-factor" in " ".join(artifact["claim_boundary"])
