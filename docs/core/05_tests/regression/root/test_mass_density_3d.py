"""Tests for the candidate SI 3D mass-density measurement operator."""

from __future__ import annotations

import unittest

from docs.core.mass_density_3d import (
    MassDensity3DSource,
    gaussian_shape_3d,
    integrated_density_3d,
    mass_from_si_volume_density,
    normalized_shape_3d,
    si_volume_density_from_shape,
)


class MassDensity3DTests(unittest.TestCase):
    def setUp(self) -> None:
        self.shape, self.spacing = gaussian_shape_3d(grid_points=(15, 17, 19))
        self.source = MassDensity3DSource(
            mass_kg=3.0,
            length_scale_x_m=2.0,
            length_scale_y_m=3.0,
            length_scale_z_m=4.0,
            source_id="synthetic:mass-density-3d:v1",
            source_locator="synthetic://uet/mass-density/3d/v1",
            source_hash="synthetic-config-3d-v1",
            uncertainty_kg=0.15,
        )

    def test_normalized_shape_has_unit_integral(self) -> None:
        normalized = normalized_shape_3d(self.shape, self.spacing)
        self.assertAlmostEqual(
            integrated_density_3d(normalized, self.spacing), 1.0, places=12
        )

    def test_si_volume_density_integrates_to_declared_mass(self) -> None:
        density, physical_spacing = si_volume_density_from_shape(
            self.shape, self.spacing, self.source
        )
        self.assertTrue(self.source.prediction_ready())
        self.assertFalse(self.source.physical_mapping_ready())
        self.assertAlmostEqual(
            mass_from_si_volume_density(density, physical_spacing),
            self.source.mass_kg,
            places=12,
        )

    def test_volume_rescaling_preserves_mass_and_changes_density_scale(self) -> None:
        source_small = self.source
        source_large = MassDensity3DSource(
            mass_kg=source_small.mass_kg,
            length_scale_x_m=4.0,
            length_scale_y_m=6.0,
            length_scale_z_m=8.0,
            source_id="synthetic:mass-density-3d:v1:large",
            source_locator=source_small.source_locator,
            source_hash=source_small.source_hash,
        )
        density_small, spacing_small = si_volume_density_from_shape(
            self.shape, self.spacing, source_small
        )
        density_large, spacing_large = si_volume_density_from_shape(
            self.shape, self.spacing, source_large
        )
        self.assertAlmostEqual(
            mass_from_si_volume_density(density_small, spacing_small), 3.0, places=12
        )
        self.assertAlmostEqual(
            mass_from_si_volume_density(density_large, spacing_large), 3.0, places=12
        )
        peak_small = max(value for row in density_small for cell in row for value in cell)
        peak_large = max(value for row in density_large for cell in row for value in cell)
        self.assertAlmostEqual(peak_small / peak_large, 8.0, places=12)

    def test_fitted_source_is_not_prediction_ready(self) -> None:
        fitted = MassDensity3DSource(
            mass_kg=1.0,
            length_scale_x_m=1.0,
            length_scale_y_m=1.0,
            length_scale_z_m=1.0,
            source_id="same-data-fit:forbidden",
            source_locator="synthetic://forbidden",
            source_hash="synthetic-forbidden",
            fitted=True,
        )
        self.assertFalse(fitted.prediction_ready())


if __name__ == "__main__":
    unittest.main()
