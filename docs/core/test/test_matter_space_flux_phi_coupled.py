from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import numpy as np
import pytest

from docs.core.uet_matter_space_flux_phi import (
    FLUX_PHI_COUPLED_OPERATOR_MODE,
    FluxPhiCoupledConfig,
    flux_phi_coupled_step,
)
from docs.core.uet_matter_space_flux_telegraph import FluxTelegraphConfig


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/matter_space_flux_phi_coupled_verification.json"
GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_coupled_branch_artifact_passes_without_claim_promotion() -> None:
    artifact = load(ARTIFACT)
    assert artifact["status"] == "PASS"
    assert all(artifact["verification"]["checks"].values())
    assert artifact["verification"]["xie_2026_accessed"] is False
    assert artifact["verification"]["full_original_conserved_gradient_candidate_pass"] is False
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"


def test_topic13_gate_records_coupled_lane_and_keeps_full_candidate_blocked() -> None:
    gate = load(GATE)
    causal = gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    assert causal["named_coupled_branch_pass"] is True
    assert causal["named_coupled_branch_closure_level"] == "CLOSED_FOR_LANE"
    assert causal["lane_status"] == "PASS"
    assert causal["lane_closure_level"] == "CLOSED_FOR_LANE"
    assert causal["full_candidate_pass"] is False
    assert gate["claim_promotion"] is False
    assert gate["controlling_blocker"] == (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )


def test_coupled_step_uses_named_operator_and_no_trace_backreaction() -> None:
    config = FluxPhiCoupledConfig()
    n = 9
    center = n // 2
    C = np.zeros(n)
    C[center] = 0.1
    flux = np.zeros(n + 1)
    Phi = np.zeros(n)
    previous = np.zeros(n)
    dt = 0.4e-3 / config.C.characteristic_speed
    next_C, next_flux, next_Phi, old_Phi, ledger = flux_phi_coupled_step(
        C, flux, Phi, previous, dt, 1.0e-3, config
    )
    assert ledger["operator_mode"] == FLUX_PHI_COUPLED_OPERATOR_MODE
    assert ledger["trace_backreaction"] is False
    assert ledger["field_clipping_applied"] is False
    assert ledger["cone_padding_applied"] is False
    assert ledger["parameter_fitting_applied"] is False
    assert next_C.shape == C.shape
    assert next_flux.shape == flux.shape
    assert next_Phi.shape == Phi.shape
    assert old_Phi.shape == Phi.shape


def test_coupled_branch_rejects_original_gradient_class() -> None:
    with pytest.raises(ValueError):
        FluxPhiCoupledConfig(
            C=FluxTelegraphConfig(kappa_C=1.0),
        )
