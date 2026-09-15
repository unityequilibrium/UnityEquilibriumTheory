"""Regression coverage for the canonical impact/effect source migration."""

from importlib import import_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def test_impact_effect_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.uet_impact_effect")
    canonical = import_module(
        "docs.core.03_lanes.carrier_observer.uet_impact_effect"
    )

    assert legacy.ImpactRecord is canonical.ImpactRecord
    assert legacy.CarrierRecord is canonical.CarrierRecord
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/carrier_observer/uet_impact_effect.py"
    ).is_file()


def test_carrier_observer_package_exports_impact_effect_contract() -> None:
    lane = import_module("docs.core.03_lanes.carrier_observer")

    assert lane.ImpactRecord is not None
    assert lane.CarrierRecord is not None
    assert lane.EffectRecord is not None
    assert lane.ReceiverDynamics is not None
    assert "impact_to_effect" in lane.__all__
