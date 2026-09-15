"""Compatibility checks for the canonical Topic 13 thermal contracts."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def test_phi_e_reference_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.thermal_phi_e_reference_normalization")
    canonical = import_module(
        "docs.core.03_lanes.thermal.thermal_phi_e_reference_normalization"
    )

    assert legacy.PhiEReferenceInputs is canonical.PhiEReferenceInputs
    assert (
        legacy.reference_energy_density_J_per_m3
        is canonical.reference_energy_density_J_per_m3
    )
    assert legacy.phi_e_reference_contract is canonical.phi_e_reference_contract
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT
        / "docs/core/03_lanes/thermal/thermal_phi_e_reference_normalization.py"
    ).is_file()


def test_response_beta_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.thermal_response_beta_contract")
    canonical = import_module(
        "docs.core.03_lanes.thermal.thermal_response_beta_contract"
    )

    assert legacy.ThermalResponseBetaInputs is canonical.ThermalResponseBetaInputs
    assert legacy.a_phi_of_temperature is canonical.a_phi_of_temperature
    assert legacy.thermal_response_beta_contract is canonical.thermal_response_beta_contract
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/thermal/thermal_response_beta_contract.py"
    ).is_file()


def test_thermal_package_exports_the_two_contract_lanes_without_alias_collision() -> None:
    package = import_module("docs.core.03_lanes.thermal")

    for name in (
        "PhiEReferenceInputs",
        "alpha_phi_e_K",
        "phi_e_from_delta_u_reference",
        "phi_e_reference_contract",
        "ThermalResponseBetaInputs",
        "thermal_response_beta_contract",
        "beta_free_energy_density_J_per_m3",
        "beta_entropy_density_J_per_m3_K",
        "validate_thermal_response_beta_inputs",
    ):
        assert hasattr(package, name)
        assert name in package.__all__

    assert package.phi_e_from_delta_u is not package.phi_e_from_delta_u_reference
    assert package.free_energy_density_J_per_m3 is not package.beta_free_energy_density_J_per_m3
    assert package.entropy_density_J_per_m3_K is not package.beta_entropy_density_J_per_m3_K
