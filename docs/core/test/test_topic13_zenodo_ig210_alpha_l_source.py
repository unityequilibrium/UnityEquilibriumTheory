from docs.core.core_paths import repo_root
import json
import unittest
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/t13_zenodo_ig210_alpha_l_source_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "zenodo_5799133_ig210_alpha_l_source_package.json"
)


class Topic13ZenodoIg210AlphaLSourceTests(unittest.TestCase):
    def test_source_lane_is_closed_only_for_ig210_comparator(self):
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        self.assertEqual(artifact["status"], "PASS_SCOPED_IG210_ALPHA_L_SOURCE")
        self.assertEqual(artifact["major_result"]["closure_level"], "CLOSED_FOR_LANE")
        self.assertTrue(all(artifact["checks"].values()))
        self.assertEqual(artifact["row_summary"]["count"], 15)
        self.assertTrue(artifact["row_summary"]["alpha_v_is_conditional"])
        self.assertFalse(artifact["numeric_alpha_Phi_K_emitted"])
        self.assertFalse(artifact["full_core_unlock"])
        self.assertFalse(package["derived_comparator"]["same_state_K_T_present"])

    def test_holdout_and_calibration_boundaries_are_explicit(self):
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        self.assertFalse(artifact["holdout_accessed"])
        self.assertFalse(artifact["target_fit_performed"])
        self.assertFalse(package["holdout_policy"]["xie_2026_accessed"])
        self.assertFalse(package["holdout_policy"]["alpha_Phi_K_fit_used"])
        self.assertEqual(package["uncertainty_contract"]["coverage_factor"], 2)
        self.assertAlmostEqual(package["uncertainty_contract"]["relative_fraction"], 0.10)


if __name__ == "__main__":
    unittest.main()
