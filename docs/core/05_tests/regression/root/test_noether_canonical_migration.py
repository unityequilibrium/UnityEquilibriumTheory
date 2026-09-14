"""Compatibility checks for the canonical Noether family migration."""

from __future__ import annotations

import importlib

import docs.core.uet_noether as legacy_noether
import docs.core.uet_noether_phase_field_map as legacy_map


NOETHER_CANONICAL = "docs.core.02_equations.lorentz_noether.uet_noether"
MAP_CANONICAL = (
    "docs.core.02_equations.lorentz_noether.uet_noether_phase_field_map"
)


def test_noether_root_shims_forward_public_api() -> None:
    canonical_noether = importlib.import_module(NOETHER_CANONICAL)
    canonical_map = importlib.import_module(MAP_CANONICAL)

    assert legacy_noether.__canonical_module__ == NOETHER_CANONICAL
    assert legacy_noether.UETNoether is canonical_noether.UETNoether
    assert legacy_noether.NoetherCurrent is canonical_noether.NoetherCurrent
    assert legacy_noether.LEGACY_NOETHER_EVIDENCE_STATUS == (
        canonical_noether.LEGACY_NOETHER_EVIDENCE_STATUS
    )
    assert legacy_map.__canonical_module__ == MAP_CANONICAL
    assert (
        legacy_map.NoetherPhaseFieldMapConfig
        is canonical_map.NoetherPhaseFieldMapConfig
    )
    assert legacy_map.noether_phase_field_map_contract is (
        canonical_map.noether_phase_field_map_contract
    )


def test_noether_map_facade_keeps_public_class_identity() -> None:
    from docs.core import NoetherPhaseFieldMapConfig

    assert NoetherPhaseFieldMapConfig is legacy_map.NoetherPhaseFieldMapConfig
