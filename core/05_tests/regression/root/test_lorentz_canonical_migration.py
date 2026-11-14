"""Compatibility checks for the canonical Lorentz family migration."""

from __future__ import annotations

import importlib

import docs.core.uet_lorentz as legacy


CANONICAL_NAME = "docs.core.02_equations.lorentz_noether.uet_lorentz"


def test_lorentz_root_shim_forwards_public_api() -> None:
    canonical = importlib.import_module(CANONICAL_NAME)

    assert legacy.__canonical_module__ == CANONICAL_NAME
    assert legacy.UETLorentz is canonical.UETLorentz
    assert legacy.LorentzMetric is canonical.LorentzMetric
    assert legacy.LorentzTransformation is canonical.LorentzTransformation
    assert legacy.SpacetimePoint is canonical.SpacetimePoint
