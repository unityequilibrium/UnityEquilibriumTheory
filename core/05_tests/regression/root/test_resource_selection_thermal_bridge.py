import unittest

from docs.core.resource_selection_thermal_bridge import (
    ResourceThermalBridgeConfig,
    run_resource_selection_thermal_bridge,
)
from docs.core.uet_resource_selection import ResourceSelectionConfig


class ResourceSelectionThermalBridgeTests(unittest.TestCase):
    def setUp(self):
        self.cooperative = ResourceSelectionConfig(
            interaction_matrix=((0.9, 0.8), (0.8, 0.9)),
            behavior_cost=(0.02, 0.03),
            maintenance_cost=(0.01, 0.01),
        )
        self.conflict = ResourceSelectionConfig(
            interaction_matrix=((0.3, -0.9), (-0.9, 0.3)),
            behavior_cost=(0.12, 0.15),
            maintenance_cost=(0.03, 0.04),
        )

    def test_declared_ledger_closes_and_entropy_proxy_is_nonnegative(self):
        result = run_resource_selection_thermal_bridge(
            self.cooperative, self.conflict, horizon=10.0, dt=0.001
        )
        for summary in (result.cooperative, result.conflict):
            self.assertGreaterEqual(summary.bath_entropy_proxy, 0.0)
            self.assertAlmostEqual(summary.ledger_closure_residual, 0.0, places=12)

    def test_conflict_lane_has_greater_dissipation_and_shorter_persistence(self):
        result = run_resource_selection_thermal_bridge(
            self.cooperative, self.conflict, horizon=10.0, dt=0.001
        )
        self.assertGreater(
            result.conflict.dissipated_work_proxy,
            result.cooperative.dissipated_work_proxy,
        )
        self.assertIsNone(result.cooperative.persistence_time)
        self.assertIsNotNone(result.conflict.persistence_time)

    def test_scale_is_declared_not_inferred(self):
        result = run_resource_selection_thermal_bridge(
            self.cooperative,
            self.conflict,
            horizon=10.0,
            dt=0.001,
            config=ResourceThermalBridgeConfig(
                behavior_to_work_scale=2.0,
                maintenance_to_work_scale=3.0,
                bath_temperature=4.0,
            ),
        )
        self.assertEqual(result.mapping_status, "BLOCKED_OPEN_SI_WORK_HEAT_ENTROPY_MAP")
        self.assertEqual(result.status, "PASS_WITH_OPEN_THERMAL_MAPPING")


if __name__ == "__main__":
    unittest.main()