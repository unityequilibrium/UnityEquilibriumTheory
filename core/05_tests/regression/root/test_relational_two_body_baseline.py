import unittest

from docs.core.relational_two_body_baseline import (
    RelationalBaselineConfig,
    circular_initial_state,
    delayed_observation,
    force_on_a,
    force_on_a_from_coordinate,
    galilean_boost,
    interaction_coordinate,
    interaction_energy,
    interaction_energy_from_coordinate,
    total_energy,
    total_momentum,
    trajectory,
)


class RelationalTwoBodyBaselineTests(unittest.TestCase):
    def setUp(self):
        self.config = RelationalBaselineConfig(steps=200)
        self.initial = circular_initial_state(self.config)

    def test_coordinate_reconstructs_standard_potential(self):
        self.assertAlmostEqual(
            interaction_energy_from_coordinate(self.initial, self.config),
            interaction_energy(self.initial, self.config),
            places=12,
        )

    def test_coordinate_derivative_reconstructs_standard_force(self):
        direct = force_on_a(self.initial, self.config)
        mapped = force_on_a_from_coordinate(self.initial, self.config)
        self.assertAlmostEqual(mapped[0], direct[0], places=12)
        self.assertAlmostEqual(mapped[1], direct[1], places=12)

    def test_verlet_preserves_energy_and_momentum_within_comparator_gate(self):
        states = trajectory(self.initial, self.config)
        initial_energy = total_energy(states[0], self.config)
        max_energy_drift = max(
            abs(total_energy(state, self.config) - initial_energy)
            for state in states
        )
        max_momentum = max(
            sum(component * component for component in total_momentum(state, self.config))
            ** 0.5
            for state in states
        )
        self.assertLessEqual(max_energy_drift, 1e-4)
        self.assertLessEqual(max_momentum, 1e-12)

    def test_common_boost_preserves_relative_C(self):
        states = trajectory(self.initial, self.config)
        boosted = trajectory(
            galilean_boost(self.initial, (0.37, -0.21)), self.config
        )
        max_error = max(
            abs(
                interaction_coordinate(state, self.config.separation_reference)
                - interaction_coordinate(other, self.config.separation_reference)
            )
            for state, other in zip(states, boosted)
        )
        self.assertLessEqual(max_error, 1e-10)

    def test_observer_receives_a_past_source_record(self):
        states = trajectory(self.initial, self.config)
        record = delayed_observation(states, 50, (5.0, 0.0), 10.0)
        self.assertGreater(record["delay"], 0.0)
        self.assertGreater(record["past_state_separation"], 1e-8)


if __name__ == "__main__":
    unittest.main()
