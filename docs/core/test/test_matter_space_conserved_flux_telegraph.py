"""Tests for the named conserved finite-cone flux branch."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path

import pytest

from docs.core.uet_matter_space_flux_telegraph import FluxTelegraphConfig


ARTIFACT = (
    canonical_artifact_path("matter_space_conserved_flux_telegraph_verification.json")
)


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_named_branch_passes_its_declared_internal_contract() -> None:
    artifact = load()
    assert artifact["status"] == "PASS"
    assert artifact["branch_id"] == "T13-CAUSAL-FLUX-TELEGRAPH-001"
    checks = artifact["verification"]["checks"]
    assert all(checks.values())
    assert artifact["verification"]["full_default_operator_replaced"] is False
    assert artifact["verification"]["xie_2026_accessed"] is False


def test_named_branch_keeps_original_gradient_class_outside_scope() -> None:
    artifact = load()
    assert artifact["config"]["kappa_C"] == 0.0
    assert "original kappa_C>0 class remains blocked" in artifact["units"]["kappa_C"]
    assert "does not pass the original kappa_C>0" in artifact["claim_boundary"]


def test_nonzero_gradient_coefficient_is_rejected() -> None:
    with pytest.raises(ValueError, match="requires kappa_C=0"):
        FluxTelegraphConfig(kappa_C=0.01)
