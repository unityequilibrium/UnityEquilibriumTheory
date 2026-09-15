"""Compatibility checks for the migrated Topic 13 support family."""

from __future__ import annotations

import importlib

from docs.core import t13_formal_thermodynamic_bridge_integration as legacy_formal
from docs.core import t13_thermal_bridge_scale_dependency as legacy_scale
from docs.core import topic13_closure_record_contract as legacy_contract


def test_topic13_support_root_modules_forward_to_canonical_sources() -> None:
    names = {
        "formal": "docs.core.03_lanes.topic13_support.t13_formal_thermodynamic_bridge_integration",
        "scale": "docs.core.03_lanes.topic13_support.t13_thermal_bridge_scale_dependency",
        "contract": "docs.core.03_lanes.topic13_support.topic13_closure_record_contract",
    }
    canonical = {key: importlib.import_module(name) for key, name in names.items()}

    assert legacy_formal.__canonical_module__ == names["formal"]
    assert legacy_scale.__canonical_module__ == names["scale"]
    assert legacy_contract.__canonical_module__ == names["contract"]
    assert legacy_formal.formal_thermodynamic_bridge_witness is canonical["formal"].formal_thermodynamic_bridge_witness
    assert legacy_scale.build_scale_dependency_witness is canonical["scale"].build_scale_dependency_witness
    assert legacy_contract.topic13_closure_record_schema is canonical["contract"].topic13_closure_record_schema


def test_topic13_support_package_exports_declared_surface() -> None:
    package = importlib.import_module("docs.core.03_lanes.topic13_support")

    for name in (
        "formal_thermodynamic_bridge_witness",
        "build_scale_dependency_witness",
        "topic13_closure_record_schema",
        "validate_physical_transport_record",
    ):
        assert name in package.__all__
