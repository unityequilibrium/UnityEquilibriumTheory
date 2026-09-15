"""Regression checks for the named Topic 13 finite-temperature beta contract."""

from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path

from docs.core.thermal_response_beta_contract import (
    ThermalResponseBetaInputs,
    a_phi_of_temperature,
    beta_t13_from_stiffness_slope,
    da_phi_dT_per_K,
    entropy_density_J_per_m3_K,
    free_energy_density_J_per_m3,
    thermal_response_beta_contract,
)


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_thermal_response_beta_contract_audit.json"


def test_beta_t13_unit_and_derivative_contract() -> None:
    inputs = ThermalResponseBetaInputs(300.0, 1.2, 0.18, 0.4, 0.3)
    assert a_phi_of_temperature(300.0, inputs) == 1.2
    assert beta_t13_from_stiffness_slope(300.0, da_phi_dT_per_K(inputs)) == 0.18
    finite_difference = -(
        free_energy_density_J_per_m3(300.001, 0.2, 0.7, inputs, 2.5)
        - free_energy_density_J_per_m3(299.999, 0.2, 0.7, inputs, 2.5)
    ) / 0.002
    assert abs(finite_difference - entropy_density_J_per_m3_K(0.7, inputs, 2.5)) <= 1.0e-10
    contract = thermal_response_beta_contract()
    assert contract["beta_th_identity"] == "not used"
    assert contract["beta_core_identity"].startswith("not asserted")
    assert contract["beta_wave_identity"].startswith("not asserted")


def test_beta_t13_contract_remains_lane_only() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))
    assert artifact["status"] == "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT"
    assert artifact["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert all(artifact["checks"].values())
    assert artifact["numeric_beta_T13_emitted"] is False
    assert artifact["numeric_e0_emitted"] is False
    assert artifact["numeric_alpha_Phi_K_emitted"] is False
    assert artifact["parameter_fitting_performed"] is False
    assert artifact["source_rows_consumed"] is False
    assert artifact["target_data_used"] is False
    assert artifact["xie_2026_accessed"] is False
