import unittest

from docs.core.mass_density_amplitude import (
    MassDensityAmplitudeSource,
    amplitude_scaling_residual,
    augmented_density_from_geometry,
    normalized_geometry_density_shape,
)
from docs.core.mass_density_correspondence import (
    MassDensityLaneConfig,
    integrated_density,
    max_relative_difference,
)
from docs.core.relational_two_body_baseline import (
    RelationalBaselineConfig,
    circular_initial_state,
)


class MassDensityAmplitudeTests(unittest.TestCase):
    def setUp(self):
        self.lane = MassDensityLaneConfig()
        self.state = circular_initial_state(RelationalBaselineConfig(steps=0))

    def test_explicit_source_amplitude_closes_normalized_integral(self):
        source = MassDensityAmplitudeSource(
            amplitude=3.0,
            source_id="synthetic:two_body_total_mass:v1",
        )
        density, dx = augmented_density_from_geometry(self.state, self.lane, source)
        self.assertTrue(source.prediction_ready())
        self.assertAlmostEqual(integrated_density(density, dx), 3.0, places=12)

    def test_amplitude_is_separate_from_shape_and_scales_linearly(self):
        shape, dx = normalized_geometry_density_shape(self.state, self.lane)
        source_a = MassDensityAmplitudeSource(1.0, "synthetic:mass:a")
        source_b = MassDensityAmplitudeSource(2.0, "synthetic:mass:b")
        density_a, _ = augmented_density_from_geometry(self.state, self.lane, source_a)
        density_b, _ = augmented_density_from_geometry(self.state, self.lane, source_b)
        self.assertAlmostEqual(integrated_density(shape, dx), 1.0, places=12)
        self.assertLessEqual(amplitude_scaling_residual(density_a, density_b, 2.0), 1e-12)
        self.assertLessEqual(max_relative_difference(density_a, shape), 1e-12)

    def test_fit_flag_is_not_prediction_ready(self):
        source = MassDensityAmplitudeSource(
            amplitude=1.0,
            source_id="same-data-fit:forbidden",
            fitted=True,
        )
        self.assertFalse(source.prediction_ready())


if __name__ == "__main__":
    unittest.main()
