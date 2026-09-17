"""Compatibility checks for the migrated persistence family."""

from __future__ import annotations

import importlib

from docs.core import persistence_energy_diagnostic as legacy_persistence
from docs.core import resource_selection_physical_cost_map as legacy_cost_map
from docs.core import resource_selection_thermal_bridge as legacy_thermal


def test_persistence_root_modules_forward_to_canonical_sources() -> None:
    names = {
        "persistence": "docs.core.03_lanes.persistence.persistence_energy_diagnostic",
        "cost_map": "docs.core.03_lanes.persistence.resource_selection_physical_cost_map",
        "thermal": "docs.core.03_lanes.persistence.resource_selection_thermal_bridge",
    }
    canonical = {key: importlib.import_module(name) for key, name in names.items()}

    assert legacy_persistence.__canonical_module__ == names["persistence"]
    assert legacy_cost_map.__canonical_module__ == names["cost_map"]
    assert legacy_thermal.__canonical_module__ == names["thermal"]
    assert legacy_persistence.PersistenceEnergyConfig is canonical["persistence"].PersistenceEnergyConfig
    assert legacy_cost_map.PhysicalCostMapRecord is canonical["cost_map"].PhysicalCostMapRecord
    assert legacy_thermal.ResourceThermalBridgeConfig is canonical["thermal"].ResourceThermalBridgeConfig


def test_persistence_package_exports_declared_surface() -> None:
    package = importlib.import_module("docs.core.03_lanes.persistence")

    for name in (
        "PersistenceEnergyConfig",
        "PhysicalCostMapRecord",
        "ResourceThermalBridgeConfig",
        "simulate_persistence_energy",
        "map_normalized_work_to_si",
    ):
        assert name in package.__all__
