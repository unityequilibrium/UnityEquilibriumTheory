"""Dependency and claim-boundary tests for the Wave 3--10 program artifact."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/uet_wave3_wave10_research_program.json"


def read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wave_range_and_dependency_gate_are_present() -> None:
    artifact = read()
    waves = artifact["waves"]
    assert [item["wave"] for item in waves] == list(range(11))
    assert artifact["status"] == "BLOCKED"
    assert artifact["foundation_gate"]["status"] in {"BLOCKED", "FAIL", "WARN"}
    assert all(item["effective_status"] != "PASS" for item in waves[4:])


def test_two_arm_causal_decision_is_explicit() -> None:
    artifact = read()
    decision = artifact["causal_decision"]
    assert "parabolic" in decision["conserved_C"]
    assert "non-conserved telegraph" in decision["finite_cone_C"]
    assert "unbounded" in decision["conserved_Cattaneo"]
    assert "does not promote" in decision["reference_lane"]


def test_claim_boundary_blocks_universal_identifications() -> None:
    artifact = read()
    blocked = set(artifact["claim_boundary"]["blocked"])
    assert "C is universal mass" in blocked
    assert "R_gen is an independent substance" in blocked
    assert "UET derives GR" in blocked
    assert "dark-matter replacement" in blocked
