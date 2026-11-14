"""Compatibility checks for the legacy observable-helper migration."""

from __future__ import annotations

import importlib

import docs.core.uet_observables as legacy


CANONICAL_NAME = "docs.core.03_lanes.review.uet_observables"


def test_observable_root_shim_forwards_public_helpers() -> None:
    canonical = importlib.import_module(CANONICAL_NAME)

    assert legacy.__canonical_module__ == CANONICAL_NAME
    assert legacy.get_hubble_at_redshift is canonical.get_hubble_at_redshift
    assert legacy.get_a0_at_redshift is canonical.get_a0_at_redshift
    assert legacy.calculate_informational_lag is canonical.calculate_informational_lag
    assert legacy.map_natural_will_to_stability is (
        canonical.map_natural_will_to_stability
    )


def test_observable_helper_remains_a_review_lane() -> None:
    canonical = importlib.import_module(CANONICAL_NAME)

    assert "UET 'MOND-Killer' Prediction" in canonical.get_a0_at_redshift.__doc__
    assert canonical.w_n_proxy(0.0) == 1e-4
