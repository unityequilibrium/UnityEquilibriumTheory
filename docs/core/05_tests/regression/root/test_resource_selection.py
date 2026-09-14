import unittest

from docs.core.uet_resource_selection import (
    ResourceSelectionConfig,
    ResourceSelectionStabilityError,
    simulate_resource_selection,
)


class ResourceSelectionTests(unittest.TestCase):
    def test_simplex_and_compatibility_are_derived(self):
        result = simulate_resource_selection(
            ResourceSelectionConfig(),
            horizon=1.0,
            dt=0.001,
        )
        self.assertLessEqual(result.probability_simplex_drift, 1e-12)
        self.assertGreaterEqual(result.minimum_probability, -1e-14)
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in result.collective_compatibility))

    def test_ledger_closes_without_clipping(self):
        result = simulate_resource_selection(
            ResourceSelectionConfig(input_power=0.05),
            horizon=1.0,
            dt=0.001,
        )
        self.assertLessEqual(abs(result.ledger_closure_residual), 1e-12)
        self.assertTrue(all(value >= 0.0 for value in result.behavior_power))
        self.assertTrue(all(value >= 0.0 for value in result.maintenance_power))

    def test_cooperative_configuration_persists_longer(self):
        cooperative = ResourceSelectionConfig(
            interaction_matrix=((0.9, 0.8), (0.8, 0.9)),
            behavior_cost=(0.02, 0.03),
            maintenance_cost=(0.01, 0.01),
        )
        conflict = ResourceSelectionConfig(
            interaction_matrix=((0.3, -0.9), (-0.9, 0.3)),
            behavior_cost=(0.12, 0.15),
            maintenance_cost=(0.03, 0.04),
        )
        coop_result = simulate_resource_selection(cooperative, 10.0, 0.001)
        conflict_result = simulate_resource_selection(conflict, 10.0, 0.001)
        self.assertGreater(
            coop_result.available_resource[-1],
            conflict_result.available_resource[-1],
        )
        self.assertIsNone(coop_result.persistence_time)
        self.assertIsNotNone(conflict_result.persistence_time)

    def test_cost_and_interaction_controls_are_separable(self):
        matrix = ((0.9, 0.8), (0.8, 0.9))
        low_cost = simulate_resource_selection(
            ResourceSelectionConfig(
                interaction_matrix=matrix,
                behavior_cost=(0.02, 0.03),
                maintenance_cost=(0.01, 0.01),
                cost_weight=0.0,
            ),
            horizon=10.0,
            dt=0.001,
        )
        high_cost = simulate_resource_selection(
            ResourceSelectionConfig(
                interaction_matrix=matrix,
                behavior_cost=(0.2, 0.3),
                maintenance_cost=(0.1, 0.1),
                cost_weight=0.0,
            ),
            horizon=10.0,
            dt=0.001,
        )
        self.assertEqual(low_cost.collective_compatibility, high_cost.collective_compatibility)
        self.assertGreater(low_cost.available_resource[-1], high_cost.available_resource[-1])

        same_cost_cooperative = simulate_resource_selection(
            ResourceSelectionConfig(
                interaction_matrix=((0.9, 0.8), (0.8, 0.9)),
                behavior_cost=(0.05, 0.05),
                maintenance_cost=(0.02, 0.02),
                cost_weight=0.0,
            ),
            horizon=10.0,
            dt=0.001,
        )
        same_cost_conflict = simulate_resource_selection(
            ResourceSelectionConfig(
                interaction_matrix=((0.3, -0.9), (-0.9, 0.3)),
                behavior_cost=(0.05, 0.05),
                maintenance_cost=(0.02, 0.02),
                cost_weight=0.0,
            ),
            horizon=10.0,
            dt=0.001,
        )
        self.assertGreater(
            max(
                abs(a - b)
                for a, b in zip(
                    same_cost_cooperative.collective_compatibility,
                    same_cost_conflict.collective_compatibility,
                )
            ),
            1e-3,
        )
        self.assertAlmostEqual(
            same_cost_cooperative.available_resource[-1],
            same_cost_conflict.available_resource[-1],
            places=12,
        )

    def test_no_fallback_for_unstable_step(self):
        with self.assertRaises(ResourceSelectionStabilityError):
            simulate_resource_selection(
                ResourceSelectionConfig(
                    interaction_matrix=((1.0, -1.0), (-1.0, 1.0)),
                    initial_probabilities=(0.9, 0.1),
                    selection_weight=1000.0,
                    cost_weight=1000.0,
                ),
                horizon=1.0,
                dt=1.0,
            )

    def test_normalized_lane_is_explicit(self):
        with self.assertRaises(NotImplementedError):
            ResourceSelectionConfig(unit_lane="SI")


if __name__ == "__main__":
    unittest.main()
