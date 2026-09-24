from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_Ding2022_Fig1d_Pixel_Quality_Audit.py")
SPEC = importlib.util.spec_from_file_location("ding_pixel_quality_audit", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load audit module: {MODULE_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class PixelQualityAuditTests(unittest.TestCase):
    def test_contiguous_clusters_keep_separated_components_distinct(self) -> None:
        self.assertEqual(
            AUDIT.contiguous_clusters([12, 10, 11, 31]),
            [
                {"y_min": 10, "y_max": 12, "pixel_count": 3},
                {"y_min": 31, "y_max": 31, "pixel_count": 1},
            ],
        )

    def test_source_replay_finds_large_blue_mask_steps_only(self) -> None:
        artifact = AUDIT.build_audit()
        checks = artifact["verification"]["checks"]
        self.assertTrue(checks["source_png_hash_matches_manifest"])
        self.assertTrue(checks["source_csv_hash_matches_manifest"])
        self.assertTrue(checks["pixel_digitization_replay_matches_existing_csv"])
        series = artifact["verification"]["series"]
        self.assertEqual(series["red_trace"]["gross_discontinuity_count"], 0)
        self.assertEqual(series["green_trace"]["gross_discontinuity_count"], 0)
        self.assertGreater(series["blue_trace"]["gross_discontinuity_count"], 0)
        self.assertEqual(artifact["verification"]["blue_trace_suspect_pixel_x_range"], [562, 595])
        largest = max(
            item["step_over_pairwise_uncertainty_bound"]
            for item in series["blue_trace"]["gross_discontinuities"]
        )
        self.assertGreater(largest, 41.0)

    def test_audit_does_not_promote_or_modify_source_lane(self) -> None:
        artifact = AUDIT.build_audit()
        verification = artifact["verification"]
        self.assertFalse(verification["holdout_accessed"])
        self.assertFalse(verification["source_data_modified"])
        self.assertFalse(verification["source_lane_status_changed"])
        self.assertFalse(verification["claim_promotion"])
        record = artifact["major_result"]
        self.assertEqual(record["topic"], "0.13_Thermodynamic_Bridge")
        self.assertIn("equation_or_mapping", record)
        self.assertIn("open_blockers", record)
        self.assertIn("claim_boundary", record)


if __name__ == "__main__":
    unittest.main()
