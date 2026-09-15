"""Regression coverage for the carrier/observer canonical source migration."""

from importlib import import_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def test_photon_baseline_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.photon_observer_baseline")
    canonical = import_module(
        "docs.core.03_lanes.carrier_observer.photon_observer_baseline"
    )

    assert legacy.PhotonBaselineConfig is canonical.PhotonBaselineConfig
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/carrier_observer/photon_observer_baseline.py"
    ).is_file()


def test_relational_baseline_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.relational_two_body_baseline")
    canonical = import_module(
        "docs.core.03_lanes.carrier_observer.relational_two_body_baseline"
    )

    assert legacy.TwoBodyState is canonical.TwoBodyState
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/carrier_observer/relational_two_body_baseline.py"
    ).is_file()


def test_carrier_observer_package_exports_both_comparators() -> None:
    lane = import_module("docs.core.03_lanes.carrier_observer")

    assert lane.PhotonBaselineConfig is not None
    assert lane.RelationalBaselineConfig is not None
    assert "PhotonBaselineConfig" in lane.__all__
    assert "RelationalBaselineConfig" in lane.__all__
