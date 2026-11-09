"""Regression checks for scoped Topic 13 NIMS reanalysis status handling."""

import importlib.util
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[4]
    / "topics/0.13_Thermodynamic_Bridge/Code/03_Research/"
    / "Research_T13_NIMS_Force_Displacement_Reanalysis.py"
)
SPEC = importlib.util.spec_from_file_location("t13_nims_force_reanalysis", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NimsForceDisplacementReanalysisTests(unittest.TestCase):
    def test_scoped_analysis_can_warn_without_promoting_full_topic(self):
        checks = {"source_hash_matches": True, "candidate_rows_reproduced": True}
        scope_controls = {
            "accepted_for_full_topic13": False,
            "claim_promotion": False,
        }

        passed, status = MODULE.assess_scoped_result(checks, scope_controls)

        self.assertTrue(passed)
        self.assertEqual(
            status,
            "WARN_SCOPED_NIMS_HARMONIC_CV_REANALYSIS_UNSTABLE_MODES_AND_UNCERTAINTY_OPEN",
        )

    def test_scientific_check_failure_still_fails(self):
        checks = {"source_hash_matches": False}
        scope_controls = {
            "accepted_for_full_topic13": False,
            "claim_promotion": False,
        }

        passed, status = MODULE.assess_scoped_result(checks, scope_controls)

        self.assertFalse(passed)
        self.assertEqual(status, "FAIL_NIMS_FORCE_DISPLACEMENT_REANALYSIS")

    def test_accidental_claim_promotion_fails_the_scope_contract(self):
        checks = {"source_hash_matches": True}
        scope_controls = {
            "accepted_for_full_topic13": False,
            "claim_promotion": True,
        }

        passed, status = MODULE.assess_scoped_result(checks, scope_controls)

        self.assertFalse(passed)
        self.assertEqual(status, "FAIL_NIMS_FORCE_DISPLACEMENT_REANALYSIS")


if __name__ == "__main__":
    unittest.main()
