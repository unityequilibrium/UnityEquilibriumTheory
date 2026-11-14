"""Compatibility checks for the migrated mass-density family."""

from __future__ import annotations

import importlib

from docs.core import mass_density_3d as legacy_3d
from docs.core import mass_density_amplitude as legacy_amplitude
from docs.core import mass_density_correspondence as legacy_correspondence
from docs.core import mass_density_dimensional as legacy_dimensional


def test_mass_density_root_modules_forward_to_canonical_sources() -> None:
    names = {
        "correspondence": "docs.core.03_lanes.mass_density.mass_density_correspondence",
        "amplitude": "docs.core.03_lanes.mass_density.mass_density_amplitude",
        "dimensional": "docs.core.03_lanes.mass_density.mass_density_dimensional",
        "three_d": "docs.core.03_lanes.mass_density.mass_density_3d",
    }
    canonical = {key: importlib.import_module(name) for key, name in names.items()}

    assert legacy_correspondence.__canonical_module__ == names["correspondence"]
    assert legacy_amplitude.__canonical_module__ == names["amplitude"]
    assert legacy_dimensional.__canonical_module__ == names["dimensional"]
    assert legacy_3d.__canonical_module__ == names["three_d"]
    assert legacy_correspondence.MassDensityLaneConfig is canonical["correspondence"].MassDensityLaneConfig
    assert legacy_amplitude.MassDensityAmplitudeSource is canonical["amplitude"].MassDensityAmplitudeSource
    assert legacy_dimensional.SIDensityAmplitudeSource is canonical["dimensional"].SIDensityAmplitudeSource
    assert legacy_3d.MassDensity3DSource is canonical["three_d"].MassDensity3DSource


def test_mass_density_package_exports_declared_surface() -> None:
    package = importlib.import_module("docs.core.03_lanes.mass_density")

    for name in (
        "MassDensityLaneConfig",
        "MassDensityAmplitudeSource",
        "SIDensityAmplitudeSource",
        "MassDensity3DSource",
        "si_volume_density_from_shape",
    ):
        assert name in package.__all__
