from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_Ding2022_Fig1d_Legend_Contamination_Audit.py")
SPEC = importlib.util.spec_from_file_location("ding_legend_contamination_audit", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load audit module: {MODULE_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class LegendContaminationAuditTests(unittest.TestCase):
    def test_legend_exclusion_removes_the_flagged_blue_jumps(self) -> None:
        artifact = AUDIT.build_audit()
        verification = artifact["verification"]
        self.assertEqual(artifact["status"], "PASS_LEGEND_CONTAMINATION_DIAGNOSTIC_ONLY")
        self.assertEqual(verification["baseline"]["large_adjacent_jump_count"], 10)
        self.assertEqual(verification["challenger"]["large_adjacent_jump_count"], 0)
        self.assertEqual(verification["challenger"]["legend_blue_pixels_excluded"], 30)
        self.assertEqual(verification["challenger"]["blue_row_count"], 159)
        self.assertEqual(len(verification["challenger"]["columns_without_nonlegend_blue_pixel"]), 13)

    def test_audit_preserves_source_and_claim_boundaries(self) -> None:
        artifact = AUDIT.build_audit()
        verification = artifact["verification"]
        self.assertTrue(all(verification["checks"].values()))
        self.assertFalse(verification["challenger"]["threshold_changed"] if "threshold_changed" in verification["challenger"] else False)
        self.assertFalse(verification["challenger"]["interpolation_or_smoothing"])
        self.assertFalse(verification["challenger"]["written_over_source_csv"])
        self.assertFalse(verification["measured_points_separated_from_simulation"])
        self.assertFalse(verification["dip_time_or_velocity_inferred"])
        self.assertFalse(verification["holdout_accessed"])
        self.assertFalse(verification["source_data_modified"])
        self.assertFalse(verification["claim_promotion"])
        self.assertEqual(artifact["major_result"]["closure_level"], "PARTIAL")


if __name__ == "__main__":
    unittest.main()
