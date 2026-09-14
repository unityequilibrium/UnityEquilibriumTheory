import unittest

from docs.core.mass_density_correspondence import (
    MassDensityLaneConfig,
    integrated_density,
    mass_density_from_point_masses,
    max_relative_difference,
    normalized_shape,
)
from docs.core.relational_two_body_baseline import (
    RelationalBaselineConfig,
    circular_initial_state,
    interaction_coordinate,
)


class MassDensityCorrespondenceTests(unittest.TestCase):
    def setUp(self):
        self.config = RelationalBaselineConfig(steps=0)
        self.lane = MassDensityLaneConfig()
        self.state = circular_initial_state(self.config)

    def test_same_geometry_keeps_C_but_density_changes_with_mass(self):
        scaled = RelationalBaselineConfig(
            mass_a=2.0,
            mass_b=2.0,
            separation_reference=self.config.separation_reference,
            steps=0,
        )
        scaled_state = circular_initial_state(scaled)
        self.assertAlmostEqual(
            interaction_coordinate(self.state, 2.0),
            interaction_coordinate(scaled_state, 2.0),
            places=12,
        )
        density_a, _ = mass_density_from_point_masses(
            self.state, 1.0, 1.0, self.lane
        )
        density_b, _ = mass_density_from_point_masses(
            scaled_state, 2.0, 2.0, self.lane
        )
        self.assertGreater(max(abs(a - b) for a, b in zip(density_a, density_b)), 1e-6)

    def test_density_integral_recovers_declared_total_mass(self):
        density, dx = mass_density_from_point_masses(
            self.state, 1.0, 1.0, self.lane
        )
        self.assertAlmostEqual(integrated_density(density, dx), 2.0, places=6)

    def test_density_scales_linearly_and_shape_is_invariant(self):
        density_a, dx = mass_density_from_point_masses(
            self.state, 1.0, 1.0, self.lane
        )
        density_b, dx_b = mass_density_from_point_masses(
            self.state, 2.0, 2.0, self.lane
        )
        self.assertLessEqual(
            max_relative_difference(density_b, [2.0 * value for value in density_a]),
            1e-12,
        )
        self.assertLessEqual(
            max_relative_difference(
                normalized_shape(density_a, dx), normalized_shape(density_b, dx_b)
            ),
            1e-12,
        )


if __name__ == "__main__":
    unittest.main()
