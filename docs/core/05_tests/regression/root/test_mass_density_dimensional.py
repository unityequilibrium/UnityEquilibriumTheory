import unittest

from docs.core.mass_density_correspondence import MassDensityLaneConfig, integrated_density
from docs.core.mass_density_dimensional import (
    SIDensityAmplitudeSource,
    augmented_si_line_density,
)
from docs.core.relational_two_body_baseline import (
    RelationalBaselineConfig,
    circular_initial_state,
)


class MassDensityDimensionalTests(unittest.TestCase):
    def setUp(self):
        self.lane = MassDensityLaneConfig()
        self.state = circular_initial_state(RelationalBaselineConfig(steps=0))

    def test_si_line_density_integrates_to_declared_kg_amplitude(self):
        source = SIDensityAmplitudeSource(
            amplitude_kg=2.5,
            length_scale_m=4.0,
            source_id="synthetic:si-line-density:v1",
            uncertainty_kg=0.1,
        )
        line_density, dx_m = augmented_si_line_density(self.state, self.lane, source)
        self.assertTrue(source.prediction_ready())
        self.assertAlmostEqual(integrated_density(line_density, dx_m), 2.5, places=12)

    def test_length_scale_changes_density_units_but_not_total_mass(self):
        source_a = SIDensityAmplitudeSource(2.0, 2.0, "synthetic:length:a")
        source_b = SIDensityAmplitudeSource(2.0, 4.0, "synthetic:length:b")
        density_a, dx_a = augmented_si_line_density(self.state, self.lane, source_a)
        density_b, dx_b = augmented_si_line_density(self.state, self.lane, source_b)
        self.assertAlmostEqual(integrated_density(density_a, dx_a), 2.0, places=12)
        self.assertAlmostEqual(integrated_density(density_b, dx_b), 2.0, places=12)
        self.assertAlmostEqual(max(density_a) / max(density_b), 2.0, places=12)

    def test_fitted_source_is_not_prediction_ready(self):
        source = SIDensityAmplitudeSource(1.0, 1.0, "same-data-fit:forbidden", fitted=True)
        self.assertFalse(source.prediction_ready())


if __name__ == "__main__":
    unittest.main()
