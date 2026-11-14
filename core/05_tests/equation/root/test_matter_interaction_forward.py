import unittest

from docs.core.matter_interaction_forward import (
    MatterInteractionForwardConfig,
    MatterSource,
    matter_to_interaction_forward,
)
from docs.core.relational_two_body_baseline import (
    RelationalBaselineConfig,
    circular_initial_state,
)


class MatterInteractionForwardTests(unittest.TestCase):
    def setUp(self):
        self.config = RelationalBaselineConfig(steps=0)
        self.state = circular_initial_state(self.config)

    def test_forward_map_keeps_source_and_C_as_separate_layers(self):
        result = matter_to_interaction_forward(
            self.state,
            MatterSource(mass_a=1.0, mass_b=1.0),
        )
        self.assertAlmostEqual(result.density_integral, 2.0, places=6)
        self.assertAlmostEqual(
            result.interaction_energy,
            result.interaction_energy_from_coordinate,
            places=12,
        )
        self.assertEqual(result.mapping_status, "STANDARD_COMPARATOR_ONLY")
        self.assertEqual(
            result.extra_uet_response_status,
            "BLOCKED_MISSING_CONSTITUTIVE_LAW",
        )

    def test_common_source_rescaling_changes_amplitude_not_C(self):
        original = matter_to_interaction_forward(
            self.state,
            MatterSource(mass_a=1.0, mass_b=1.0),
        )
        scaled = matter_to_interaction_forward(
            self.state,
            MatterSource(mass_a=2.0, mass_b=2.0),
        )
        self.assertAlmostEqual(
            original.interaction_coordinate,
            scaled.interaction_coordinate,
            places=12,
        )
        self.assertAlmostEqual(scaled.density_integral / original.density_integral, 2.0)
        self.assertAlmostEqual(scaled.interaction_energy / original.interaction_energy, 4.0)
        self.assertAlmostEqual(
            scaled.force_on_a[0] / original.force_on_a[0],
            4.0,
        )
        self.assertAlmostEqual(
            scaled.acceleration_on_a[0] / original.acceleration_on_a[0],
            2.0,
        )

    def test_dimensional_lane_is_rejected_until_units_contract_exists(self):
        with self.assertRaises(ValueError):
            matter_to_interaction_forward(
                self.state,
                MatterSource(),
                MatterInteractionForwardConfig(unit_lane="SI"),
            )


if __name__ == "__main__":
    unittest.main()
