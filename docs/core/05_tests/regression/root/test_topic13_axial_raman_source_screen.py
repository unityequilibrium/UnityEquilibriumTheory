"""Regression checks for the bounded Topic 13 axial-Raman source screen."""

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[4] / "scripts/audit/audit_topic13_axial_raman_source_screen.py"
SPEC = importlib.util.spec_from_file_location("axial_raman_source_screen", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AxialRamanSourceScreenTests(unittest.TestCase):
    def test_screen_finds_no_accepted_matched_state_row(self):
        artifact = MODULE.build_artifact()
        self.assertEqual(artifact["decision"]["accepted_row_count"], 0)
        self.assertFalse(artifact["decision"]["matched_state_axial_raman_source_found"])

    def test_each_route_is_explicitly_not_accepted(self):
        artifact = MODULE.build_artifact()
        for source in artifact["sources"]:
            self.assertNotEqual(source["disposition"], "ACCEPTED_CALIBRATION_ROW")
            self.assertTrue(source["primary_locator"].startswith("https://"))

    def test_holdout_and_claim_promotion_remain_closed(self):
        artifact = MODULE.build_artifact()
        self.assertFalse(artifact["integrity"]["xie_2026_accessed"])
        self.assertFalse(artifact["integrity"]["claim_promotion"])
        self.assertFalse(artifact["integrity"]["full_core_unlock"])

    def test_full_topic13_gate_is_not_promoted(self):
        artifact = MODULE.build_artifact()
        self.assertEqual(artifact["status"], "PASS_SCOPED_AXIAL_RAMAN_SOURCE_SCREEN_NO_ACCEPTED_ROW")
        self.assertTrue(artifact["integrity"]["full_gate_status_unchanged"])


if __name__ == "__main__":
    unittest.main()
