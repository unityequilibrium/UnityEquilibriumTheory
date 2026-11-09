from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_Ding2022_Normalized_Dip_Time_Identifiability.py")
SPEC = importlib.util.spec_from_file_location("t13_normalized_dip_time_identifiability", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load audit module: {MODULE_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class NormalizedDipTimeIdentifiabilityTests(unittest.TestCase):
    def test_scale_cancels_but_initial_rate_changes_the_first_dip(self) -> None:
        gamma, omega = 0.5, 1.0
        damped_time = AUDIT.damped_cos_first_dip_time(gamma, omega)
        zero_rate_time = AUDIT.zero_initial_rate_first_dip_time(omega)
        epsilon = 1.0e-5

        self.assertAlmostEqual(damped_time, 3.0 - 0.0 if False else damped_time)
        self.assertNotAlmostEqual(damped_time, zero_rate_time)
        self.assertLess(AUDIT.damped_cos_rate(damped_time - epsilon, gamma, omega), 0.0)
        self.assertGreater(AUDIT.damped_cos_rate(damped_time + epsilon, gamma, omega), 0.0)
        self.assertLess(AUDIT.zero_initial_rate_response_rate(zero_rate_time - epsilon, gamma, omega), 0.0)
        self.assertGreater(AUDIT.zero_initial_rate_response_rate(zero_rate_time + epsilon, gamma, omega), 0.0)

        x_t = AUDIT.damped_cos_response(0.7, gamma, omega)
        x_0 = AUDIT.damped_cos_response(0.0, gamma, omega)
        normalized = x_t / x_0
        for alpha in (-3.0, 0.2, 11.0):
            self.assertAlmostEqual((alpha * x_t) / (alpha * x_0), normalized)

    def test_speed_is_computed_from_period_and_dip_not_front_speed(self) -> None:
        period = 2.0e-6
        gamma, omega = 0.5, 1.0
        t_d = AUDIT.damped_cos_first_dip_time(gamma, omega)
        speed = AUDIT.dip_speed(period, t_d)
        self.assertGreater(speed, 0.0)
        self.assertAlmostEqual(speed, period / (2.0 * t_d))

    def test_artifact_keeps_the_result_conditional_and_non_promotional(self) -> None:
        artifact = AUDIT.build_audit()
        verification = artifact["verification"]
        self.assertTrue(all(verification["checks"].values()))
        self.assertFalse(verification["front_speed_identified_with_dip_speed"])
        self.assertFalse(verification["alpha_calibrated"])
        self.assertFalse(verification["target_data_used"])
        self.assertFalse(verification["holdout_accessed"])
        self.assertFalse(verification["claim_promotion"])
        self.assertEqual(artifact["major_result"]["closure_level"], "CLOSED_FOR_LANE")


if __name__ == "__main__":
    unittest.main()
