"""Tests for the Wave 9 orbit/GR/cosmology correspondence gate."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/orbit_cosmology_correspondence_gate.json"


def read() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_wave9_gate_retains_standard_baseline_without_promotion() -> None:
    artifact = read()
    assert artifact["status"] == "BLOCKED"
    assert artifact["local_baseline_status"].startswith("PASS_")
    assert all(artifact["checks"].values())


def test_wave9_forbids_global_open_and_derived_orbit_claims() -> None:
    artifact = read()
    boundary = artifact["claim_boundary"]
    assert "no UET orbital law" in boundary
    assert "global open-universe proof" in boundary
