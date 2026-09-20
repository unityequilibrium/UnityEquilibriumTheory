"""Compatibility checks for the canonical thermal dimensional bridges."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path


def test_dimensional_bridge_legacy_and_canonical_exports_are_identical() -> None:
    legacy = import_module("docs.core.thermal_dimensional_bridge")
    canonical = import_module(
        "docs.core.03_lanes.thermal.thermal_dimensional_bridge"
    )

    assert legacy.ConditionalThermalInputs is canonical.ConditionalThermalInputs
    assert (
        legacy.alpha_phi_k_from_local_equilibrium
        is canonical.alpha_phi_k_from_local_equilibrium
    )
    assert legacy.__canonical_module__ == canonical.__name__


def test_energy_response_bridge_legacy_and_canonical_exports_are_identical() -> None:
    legacy = import_module("docs.core.thermal_energy_response_bridge")
    canonical = import_module(
        "docs.core.03_lanes.thermal.thermal_energy_response_bridge"
    )

    assert legacy.EnergyResponseInputs is canonical.EnergyResponseInputs
    assert legacy.alpha_phi_e_k is canonical.alpha_phi_e_k
    assert legacy.__canonical_module__ == canonical.__name__


def test_canonical_thermal_files_and_package_exports_exist() -> None:
    root = Path(__file__).resolve().parents[5]
    assert (
        root
        / "docs"
        / "core"
        / "03_lanes"
        / "thermal"
        / "thermal_dimensional_bridge.py"
    ).is_file()
    assert (
        root
        / "docs"
        / "core"
        / "03_lanes"
        / "thermal"
        / "thermal_energy_response_bridge.py"
    ).is_file()

    package = import_module("docs.core.03_lanes.thermal")
    for name in (
        "ConditionalThermalInputs",
        "alpha_phi_k_from_local_equilibrium",
        "EnergyResponseInputs",
        "alpha_phi_e_k",
    ):
        assert hasattr(package, name)
        assert name in package.__all__
