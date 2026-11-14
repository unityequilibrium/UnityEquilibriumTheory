"""Compatibility checks for the migrated hyperbolic phase comparator."""

from __future__ import annotations

import importlib

from docs.core import uet_hyperbolic_phase_field as legacy_phase
from docs.core import uet_hyperbolic_phase_field_bridge as legacy_bridge


def test_hyperbolic_phase_root_modules_forward_to_canonical_implementations() -> None:
    canonical_phase_name = (
        "docs.core.02_equations.matter_space.uet_hyperbolic_phase_field"
    )
    canonical_bridge_name = (
        "docs.core.02_equations.matter_space.uet_hyperbolic_phase_field_bridge"
    )
    canonical_phase = importlib.import_module(canonical_phase_name)
    canonical_bridge = importlib.import_module(canonical_bridge_name)

    assert legacy_phase.__canonical_module__ == canonical_phase_name
    assert legacy_bridge.__canonical_module__ == canonical_bridge_name
    assert (
        legacy_phase.HyperbolicPhaseFieldConfig
        is canonical_phase.HyperbolicPhaseFieldConfig
    )
    assert (
        legacy_bridge.fixed_light_cone_feasibility
        is canonical_bridge.fixed_light_cone_feasibility
    )
