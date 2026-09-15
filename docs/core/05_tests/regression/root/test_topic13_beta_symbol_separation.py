"""Regression checks for Topic 13 beta-symbol separation."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json"


def test_beta_symbol_no_go_is_closed_only_for_the_lane() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_SCOPED_NO_GO_BETA_SYMBOL_IDENTIFICATION"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert all(artifact["algebraic_witness"]["checks"].values())
    assert artifact["numeric_beta_UET_emitted"] is False
    assert artifact["numeric_e0_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["source_rows_consumed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False


def test_beta_symbol_no_go_preserves_future_derivation_requirements() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    blockers = artifact["major_result"]["open_blockers"]
    assert "declared_beta_UET_action_term_and_units_missing" in blockers
    assert "finite_temperature_coefficient_provenance_independent_of_Landauer_missing" in blockers
    assert "non_circular_UET_bridge_EOS_transport_KMS_entropy_derivation_missing" in blockers
    assert artifact["legacy_wording"]["accepted_as_derivation"] is False
