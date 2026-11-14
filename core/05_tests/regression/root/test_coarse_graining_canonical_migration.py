"""Compatibility checks for the migrated coarse-graining contract."""

from __future__ import annotations

import importlib

from docs.core import uet_coarse_graining as legacy_coarse_graining


def test_coarse_graining_root_module_forwards_to_ontology_contract() -> None:
    canonical_name = (
        "docs.core.01_contracts.ontology.uet_coarse_graining"
    )
    canonical = importlib.import_module(canonical_name)
    package = importlib.import_module("docs.core.01_contracts.ontology")

    assert legacy_coarse_graining.__canonical_module__ == canonical_name
    assert legacy_coarse_graining.CoarseGrainingRecord is canonical.CoarseGrainingRecord
    assert legacy_coarse_graining.coarse_grain is canonical.coarse_grain
    assert package.coarse_grain is canonical.coarse_grain
    assert package.CoarseGrainingRecord is canonical.CoarseGrainingRecord
