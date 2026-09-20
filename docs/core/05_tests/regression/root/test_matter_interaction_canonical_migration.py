"""Regression coverage for the canonical matter-interaction source migration."""

from importlib import import_module
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]


def test_matter_interaction_legacy_import_is_a_facade() -> None:
    legacy = import_module("docs.core.matter_interaction_forward")
    canonical = import_module(
        "docs.core.03_lanes.mass_density.matter_interaction_forward"
    )

    assert legacy.MatterSource is canonical.MatterSource
    assert legacy.MatterInteractionForwardResult is canonical.MatterInteractionForwardResult
    assert legacy.__canonical_module__ == canonical.__name__
    assert (
        ROOT / "docs/core/03_lanes/mass_density/matter_interaction_forward.py"
    ).is_file()


def test_mass_density_package_exports_forward_interaction_contract() -> None:
    lane = import_module("docs.core.03_lanes.mass_density")

    assert lane.MatterSource is not None
    assert lane.MatterInteractionForwardConfig is not None
    assert lane.MatterInteractionForwardResult is not None
    assert "matter_to_interaction_forward" in lane.__all__
