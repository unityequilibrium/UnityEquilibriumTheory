"""Compatibility checks for the migrated GR correspondence contract."""

from __future__ import annotations

import importlib

from docs.core import uet_gr_correspondence as legacy_correspondence


def test_gr_correspondence_root_module_forwards_to_contract() -> None:
    canonical_name = (
        "docs.core.01_contracts.correspondence.uet_gr_correspondence"
    )
    canonical = importlib.import_module(canonical_name)
    package = importlib.import_module("docs.core.01_contracts.correspondence")

    assert legacy_correspondence.__canonical_module__ == canonical_name
    assert legacy_correspondence.GRBenchmarkRecord is canonical.GRBenchmarkRecord
    assert (
        legacy_correspondence.gr_correspondence_contract
        is canonical.gr_correspondence_contract
    )
    assert package.minkowski_null_control is canonical.minkowski_null_control
