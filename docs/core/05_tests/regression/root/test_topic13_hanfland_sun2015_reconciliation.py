"""Tests for the conditional source-model calculation and claim boundary."""

import json
import unittest
from pathlib import Path

from docs.scripts.audit.audit_topic13_hanfland_sun2015_reconciliation import assess

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"


class HanflandSun2015ReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hanfland = json.loads(
            (DATA / "hanfland_1989_raman_deformation_source_package.json").read_text(
                encoding="utf-8"
            )
        )
        cls.sun = json.loads(
            (DATA / "sun_2015_graphite_raman_strain_model_source_package.json").read_text(
                encoding="utf-8"
            )
        )

    def test_reported_percent_slope_reproduces_gamma_prime_sign_and_rounding(self):
        row = assess(self.hanfland, self.sun)["conditional_decomposition"]
        self.assertAlmostEqual(
            row["gamma_prime_from_reported_shift"], -0.01308447181066, places=12
        )
        self.assertLess(row["gamma_prime_rounding_residual"], 0.00005)
        self.assertGreater(row["D_c_over_x"], 0.0)

    def test_table_and_abstract_slope_routes_remain_separate(self):
        rows = assess(self.hanfland, self.sun)["conditional_decomposition"]
        self.assertAlmostEqual(
            rows["table_log_slope"]["conditional_gamma_nominal"],
            2.079341736694678,
            places=12,
        )
        self.assertAlmostEqual(
            rows["abstract_absolute_slope"]["conditional_gamma_nominal"],
            2.0896963915395164,
            places=12,
        )
        interval = rows["table_log_slope"]["conditional_gamma_rectangular_sensitivity"]
        self.assertAlmostEqual(interval[0], 1.9369298429319373, places=12)
        self.assertAlmostEqual(interval[1], 2.227221686746988, places=12)

    def test_model_prediction_is_route_sensitive_not_a_model_rejection(self):
        comparison = assess(self.hanfland, self.sun)["cross_source_reconciliation"]
        self.assertFalse(comparison["overlap_with_table_interval"])
        self.assertTrue(comparison["overlap_with_abstract_interval"])
        self.assertIn("prevent rejecting the model", comparison["interpretation"])

    def test_model_prior_does_not_increase_observational_rank_or_close_alpha(self):
        result = assess(self.hanfland, self.sun)
        rank = result["identifiability"]
        boundary = result["claim_boundary"]
        self.assertEqual(rank["single_mode_observational_rank"], 1)
        self.assertEqual(rank["observational_nullity"], 1)
        self.assertEqual(rank["empirical_rank_gain"], 0)
        self.assertFalse(rank["DFT_gamma_prime_is_an_observation"])
        self.assertIsNone(boundary["alpha_Phi_K"])
        self.assertFalse(boundary["TTG_validation"])
        self.assertFalse(boundary["full_topic13_closure"])

    def test_invalid_modulus_is_rejected_without_regularization(self):
        hanfland = json.loads(json.dumps(self.hanfland))
        next(
            row for row in hanfland["rows"]
            if row["row_id"] == "axial_modulus_c"
        )["value"] = 0.0
        with self.assertRaises(ValueError):
            assess(hanfland, self.sun)


if __name__ == "__main__":
    unittest.main()
