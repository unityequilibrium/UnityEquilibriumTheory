from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

import pytest

from docs.core.thermal_energy_response_bridge import (
    EnergyResponseInputs,
    alpha_phi_e_k,
    alpha_phi_e_uncertainty_K,
    delta_tq_from_delta_u,
    named_energy_response_branch_contract,
    phi_e_from_delta_u,
)


ROOT = repo_root()
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "graphite_heat_capacity_source_package.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_named_energy_branch_closes_algebra_without_base_phi_identity() -> None:
    inputs = EnergyResponseInputs(2.0e6, 5.0e5)
    phi_e = phi_e_from_delta_u(5.0e5, inputs.e0_J_per_m3)
    delta_tq = delta_tq_from_delta_u(5.0e5, inputs.cv_J_per_m3_K)
    assert phi_e == 0.25
    assert delta_tq == alpha_phi_e_k(inputs) * phi_e
    assert named_energy_response_branch_contract()["base_Phi_identity"] == "not asserted"


def test_energy_branch_requires_both_uncertainties_for_numeric_error() -> None:
    with pytest.raises(ValueError):
        alpha_phi_e_uncertainty_K(EnergyResponseInputs(2.0e6, 5.0e5))
    inputs = EnergyResponseInputs(2.0e6, 5.0e5, 1.0e5, 5.0e4)
    assert alpha_phi_e_uncertainty_K(inputs) == pytest.approx(0.4472135954999579)


def test_energy_branch_rejects_invalid_dimensional_inputs() -> None:
    with pytest.raises(ValueError):
        alpha_phi_e_k(EnergyResponseInputs(0.0, 5.0e5))
    with pytest.raises(ValueError):
        delta_tq_from_delta_u(1.0, 0.0)


def test_energy_branch_artifact_keeps_source_and_holdout_boundaries() -> None:
    artifact = load(AUDIT)
    package = load(PACKAGE)
    assert artifact["status"] == "PASS_NAMED_BRANCH_OPEN_INPUTS"
    assert all(artifact["checks"].values())
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert artifact["numeric_calibration"]["alpha_Phi_K"] is None
    assert artifact["conditional_inputs"]["base_Phi_to_Phi_E"]["status"] == "OPEN_DERIVATION_OR_CALIBRATION"
    assert package["holdout_policy"]["xie_2026_accessed"] is False
    assert package["required_quantity_contract"]["conversion_status"] == "OPEN_CP_TO_CV_AND_MOLAR_TO_VOLUMETRIC"
