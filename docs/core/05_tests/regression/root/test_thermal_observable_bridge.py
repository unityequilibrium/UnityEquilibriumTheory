import unittest

from docs.core.thermal_observable_bridge import (
    ThermalObservableBridgeConfig,
    run_thermal_observable_bridge,
)


class ThermalObservableBridgeTests(unittest.TestCase):
    def test_same_C_path_work_but_different_thermal_gain_changes_proxy(self):
        base = run_thermal_observable_bridge(
            ThermalObservableBridgeConfig(
                time_steps=2000,
                C_to_temperature_gain=0.2,
            )
        )
        scaled = run_thermal_observable_bridge(
            ThermalObservableBridgeConfig(
                time_steps=2000,
                C_to_temperature_gain=0.4,
            )
        )
        self.assertAlmostEqual(base.C_path_work, scaled.C_path_work, places=12)
        self.assertGreater(scaled.fourier_entropy_proxy, base.fourier_entropy_proxy)
        self.assertGreater(scaled.cattaneo_entropy_proxy, base.cattaneo_entropy_proxy)

    def test_entropy_sources_are_nonnegative_and_temperature_positive(self):
        result = run_thermal_observable_bridge(
            ThermalObservableBridgeConfig(time_steps=2000)
        )
        self.assertGreater(result.minimum_temperature, 0.0)
        self.assertGreaterEqual(result.minimum_fourier_entropy_source, -1e-12)
        self.assertGreaterEqual(result.minimum_cattaneo_entropy_source, -1e-12)

    def test_si_lane_is_blocked(self):
        with self.assertRaises(NotImplementedError):
            ThermalObservableBridgeConfig(unit_lane="SI")


if __name__ == "__main__":
    unittest.main()
