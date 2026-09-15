"""Regression checks for the Topic 13 Phi-energy-anchor structural no-go."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_phi_energy_anchor_identifiability_no_go.json"


def test_structural_no_go_is_scoped_and_passing() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["witness"]["target_or_holdout_used"] is False
    assert artifact["checks"]["normalized_observable_invariant_under_phi_scale"] is True
    assert artifact["checks"]["dimensional_temperature_witness_invariant"] is True
    assert artifact["checks"]["e0_to_alpha_values_are_distinct"] is True
    assert artifact["controlling_blocker"] == "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing"
