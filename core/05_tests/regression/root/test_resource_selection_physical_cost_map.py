import unittest

from docs.core.resource_selection_physical_cost_map import (
    PhysicalCostMapRecord,
    PhysicalCostMapValidationError,
    map_normalized_work_to_si,
)


class PhysicalCostMapTests(unittest.TestCase):
    def test_open_map_cannot_convert_to_si(self):
        record = PhysicalCostMapRecord(
            map_id="open-map",
            material_or_system="unspecified",
        )
        with self.assertRaises(PhysicalCostMapValidationError):
            map_normalized_work_to_si(0.25, 0.1, record)

    def test_fit_origin_is_rejected(self):
        record = PhysicalCostMapRecord(
            map_id="fit-map",
            material_or_system="test-material",
            behavior_energy_scale_j=2.0,
            maintenance_energy_scale_j=3.0,
            bath_temperature_k=300.0,
            source_locator="fit://target-data",
            source_hash="not-a-source-hash",
            uncertainty_record="missing-independent-uncertainty",
            measurement_operator_id="heat",
            parameter_origin="fit",
        )
        with self.assertRaises(PhysicalCostMapValidationError):
            record.validate_contract()

    def test_ready_test_fixture_maps_work_and_entropy(self):
        record = PhysicalCostMapRecord(
            map_id="fixture-map",
            material_or_system="test-material",
            behavior_energy_scale_j=2.0,
            maintenance_energy_scale_j=3.0,
            bath_temperature_k=300.0,
            source_locator="synthetic://physical-cost-contract",
            source_hash="fixture-hash",
            uncertainty_record="fixture-only",
            measurement_operator_id="integrated_heat_fixture",
            parameter_origin="test_fixture",
            status="TEST_ONLY",
        )
        result = map_normalized_work_to_si(0.25, 0.1, record)
        self.assertAlmostEqual(result.heat_j, 0.8, places=12)
        self.assertAlmostEqual(result.entropy_j_per_k, 0.8 / 300.0, places=12)
        self.assertEqual(result.measurement_operator_id, "integrated_heat_fixture")

    def test_dynamic_game_controls_remain_separate_after_fixture_map(self):
        from docs.core.uet_resource_selection import (
            ResourceSelectionConfig,
            simulate_resource_selection,
        )

        def run(matrix, behavior, maintenance):
            return simulate_resource_selection(
                ResourceSelectionConfig(
                    interaction_matrix=matrix,
                    behavior_cost=behavior,
                    maintenance_cost=maintenance,
                    cost_weight=0.0,
                ),
                horizon=10.0,
                dt=0.001,
            )

        record = PhysicalCostMapRecord(
            map_id="fixture-map",
            material_or_system="test-material",
            behavior_energy_scale_j=2.0,
            maintenance_energy_scale_j=3.0,
            bath_temperature_k=300.0,
            source_locator="synthetic://physical-cost-contract",
            source_hash="fixture-hash",
            uncertainty_record="fixture-only",
            measurement_operator_id="integrated_heat_fixture",
            parameter_origin="test_fixture",
        )
        low = run(((0.9, 0.8), (0.8, 0.9)), (0.02, 0.03), (0.01, 0.01))
        high = run(((0.9, 0.8), (0.8, 0.9)), (0.2, 0.3), (0.1, 0.1))
        cooperative = run(((0.9, 0.8), (0.8, 0.9)), (0.05, 0.05), (0.02, 0.02))
        conflict = run(((0.3, -0.9), (-0.9, 0.3)), (0.05, 0.05), (0.02, 0.02))
        low_heat = map_normalized_work_to_si(low.behavior_work, low.maintenance_work, record)
        high_heat = map_normalized_work_to_si(high.behavior_work, high.maintenance_work, record)
        cooperative_heat = map_normalized_work_to_si(cooperative.behavior_work, cooperative.maintenance_work, record)
        conflict_heat = map_normalized_work_to_si(conflict.behavior_work, conflict.maintenance_work, record)

        self.assertEqual(low.collective_compatibility, high.collective_compatibility)
        self.assertGreater(high_heat.heat_j, low_heat.heat_j)
        self.assertGreater(
            max(abs(a - b) for a, b in zip(cooperative.collective_compatibility, conflict.collective_compatibility)),
            1e-3,
        )
        self.assertAlmostEqual(cooperative_heat.heat_j, conflict_heat.heat_j, places=12)

    def test_negative_normalized_work_is_rejected(self):
        record = PhysicalCostMapRecord(
            map_id="fixture-map",
            material_or_system="test-material",
            behavior_energy_scale_j=2.0,
            maintenance_energy_scale_j=3.0,
            bath_temperature_k=300.0,
            source_locator="synthetic://physical-cost-contract",
            source_hash="fixture-hash",
            uncertainty_record="fixture-only",
            measurement_operator_id="integrated_heat_fixture",
            parameter_origin="test_fixture",
        )
        with self.assertRaises(PhysicalCostMapValidationError):
            map_normalized_work_to_si(-0.1, 0.1, record)

    def test_wrong_unit_lane_is_rejected(self):
        record = PhysicalCostMapRecord(
            map_id="normalized-map",
            material_or_system="test-material",
            unit_lane="normalized",
        )
        with self.assertRaises(PhysicalCostMapValidationError):
            record.validate_contract()


if __name__ == "__main__":
    unittest.main()
