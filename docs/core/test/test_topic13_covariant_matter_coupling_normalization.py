"""Regression checks for the Topic 13 matter-coupling normalization no-go."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json"


def test_matter_coupling_no_go_is_closed_only_as_a_scoped_no_go() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_NO_GO_COVARIANT_MATTER_COUPLING_NORMALIZATION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
    assert all(artifact["coupling_rescaling_witness"]["checks"].values())
    assert artifact["numeric_e0_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
    assert artifact["landauer_used_for_derivation"] is False


def test_matter_coupling_no_go_keeps_physical_anchor_open() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    blockers = artifact["major_result"]["open_blockers"]
    assert "physical_interaction_coefficient_provenance_and_SI_contract_missing" in blockers
    assert "base_Phi_to_Phi_E_energy_anchor_and_independent_alpha_Phi_K_missing" in blockers
    assert "matter_amplitude_to_density_C_mapping_not_derived" in blockers
