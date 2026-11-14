import math
import unittest

from docs.core.persistence_energy_diagnostic import (
    PERSISTENCE_PRINCIPLE_ID,
    PERSISTENCE_PRINCIPLE_NAME_EN,
    PERSISTENCE_PRINCIPLE_NAME_TH,
    PERSISTENCE_PRINCIPLE_STATUS,
    PersistenceEnergyConfig,
    simulate_persistence_energy,
)


class PersistenceEnergyDiagnosticTests(unittest.TestCase):
    def test_named_principle_contract_is_stable(self):
        self.assertEqual(PERSISTENCE_PRINCIPLE_ID, "UET-PRINCIPLE-001")
        self.assertEqual(PERSISTENCE_PRINCIPLE_NAME_TH, "หลักการจัดสรรพลังงานร่วมเพื่อการดำรงอยู่ของระบบ")
        self.assertIn(
            "Cooperative Energy Allocation",
            PERSISTENCE_PRINCIPLE_NAME_EN,
        )
        self.assertEqual(PERSISTENCE_PRINCIPLE_STATUS, "CANDIDATE_PRINCIPLE")

    def test_same_endpoints_can_have_different_path_cost(self):
        steps = 1000
        horizon = 10.0
        dt = horizon / steps
        low = [
            0.5 * math.sin(2.0 * math.pi * index / steps)
            for index in range(steps + 1)
        ]
        high = [
            0.5 * math.sin(16.0 * math.pi * index / steps)
            for index in range(steps + 1)
        ]
        config = PersistenceEnergyConfig(
            initial_available_energy=1.0,
            sustain_threshold=0.2,
            behavior_cost_coefficient=0.1,
        )
        low_result = simulate_persistence_energy(low, dt, config)
        high_result = simulate_persistence_energy(high, dt, config)
        self.assertAlmostEqual(low[0], high[0], places=12)
        self.assertAlmostEqual(low[-1], high[-1], places=12)
        self.assertGreater(high_result.behavior_work, 10.0 * low_result.behavior_work)
        self.assertIsNone(low_result.persistence_time)
        self.assertIsNotNone(high_result.persistence_time)
        self.assertLess(high_result.persistence_time, horizon)

    def test_ledger_closes_and_path_power_is_nonnegative(self):
        trajectory = [0.25 * math.sin(2.0 * math.pi * i / 100.0) for i in range(101)]
        result = simulate_persistence_energy(trajectory, 0.1)
        self.assertLessEqual(abs(result.ledger_closure_residual), 1e-12)
        self.assertTrue(all(power >= 0.0 for power in result.behavior_power))

    def test_si_lane_is_blocked(self):
        with self.assertRaises(NotImplementedError):
            PersistenceEnergyConfig(unit_lane="SI")


if __name__ == "__main__":
    unittest.main()
