"""Regression check for the named Phi_E reference-normalization lane."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json"


def test_phi_e_reference_normalization_stays_separate_from_base_phi() -> None:
    value = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert value["status"] == "PASS_NAMED_PHI_E_REFERENCE_NORMALIZATION"
    assert value["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(value["checks"].values())
    assert value["numeric_base_alpha_Phi_K_emitted"] is False
    assert value["parameter_fitting_performed"] is False
    assert value["target_data_used"] is False
    assert value["xie_2026_accessed"] is False
