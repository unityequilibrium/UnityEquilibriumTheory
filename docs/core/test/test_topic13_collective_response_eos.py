"""Regression checks for the named Topic 13 collective-response EOS lane."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

from docs.core.thermal_collective_response_eos import (
    CollectiveResponseEOSInputs,
    chemical_potentials,
    local_stability,
)
from docs.core.thermal_response_beta_contract import ThermalResponseBetaInputs


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_collective_response_eos_stability_audit.json"


def test_collective_response_eos_reciprocity_and_stability() -> None:
    inputs = CollectiveResponseEOSInputs(
        thermal=ThermalResponseBetaInputs(300.0, 1.2, 0.18, 0.4, 0.3),
        a_c=1.1,
        b_c=0.5,
    )
    mu_c, mu_phi = chemical_potentials(300.0, 0.2, 0.4, inputs)
    assert isinstance(mu_c, float)
    assert isinstance(mu_phi, float)
    stability = local_stability(300.0, 0.2, 0.4, inputs)
    assert stability["mixed_derivatives_equal"] is True
    assert stability["locally_stable"] is True


def test_collective_response_eos_contract_remains_lane_only() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_NAMED_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["numeric_coefficients_emitted"] is False
    assert artifact["numeric_e0_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["source_rows_consumed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
