"""Regression checks for the Topic 13 covariant field-normalization no-go."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json"


def test_field_rescaling_no_go_is_closed_only_for_the_lane() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["field_rescaling_witness"]["checks"].values())
    assert artifact["numeric_e0_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False


def test_no_go_preserves_the_physical_normalization_requirements() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    blockers = artifact["major_result"]["open_blockers"]
    assert "source_locked_physical_field_residue_or_observable_amplitude_missing" in blockers
    assert "system_specific_SI_coefficient_and_energy_density_contract_missing" in blockers
    assert "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing" in blockers
