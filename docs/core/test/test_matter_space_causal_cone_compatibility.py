"""Tests for the changing-C response-cone compatibility audit."""

from __future__ import annotations
from docs.core.core_paths import canonical_artifact_path

import json
from pathlib import Path


ARTIFACT = (
    canonical_artifact_path("matter_space_causal_cone_compatibility.json")
)


def load() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_changing_c_cone_is_blocked_by_observed_domain_of_dependence() -> None:
    artifact = load()
    assert artifact["audit_status"] == "BLOCKED"
    assert artifact["response_cone_status"] == "BLOCKED"
    assert artifact["structural_blocker"] == (
        "conserved_C_gradient_term_has_unbounded_k4_characteristic_speed"
    )
    assert artifact["discrete_probe"]["observed_C_radius_cells"] > 1
    assert artifact["discrete_probe"]["observed_Phi_radius_cells"] > 1


def test_cattaneo_extension_does_not_bound_k4_group_speed() -> None:
    artifact = load()
    dispersion = artifact["continuum_diagnostic"]["cattaneo_extension"]
    assert dispersion["kappa_C"] > 0.0
    assert dispersion["high_k_group_speed_is_unbounded"] is True
    assert dispersion["asymptotic_group_speed"] == "2*sqrt(M_C*kappa_C/tau_C)*k"


def test_claim_boundary_preserves_ledger_pass_without_cone_pass() -> None:
    artifact = load()
    assert artifact["shared_ledger_status"] == "PASS"
    assert artifact["full_candidate_status"] == "BLOCKED"
    assert "does not establish a finite changing-C cone" in artifact["claim_boundary"]
