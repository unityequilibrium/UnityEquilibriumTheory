from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_Ding2022_TTG_Preprocessing_Boundary_Audit.py")
SPEC = importlib.util.spec_from_file_location("ding_ttg_preprocessing_boundary_audit", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load audit module: {MODULE_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class SupplementaryPreprocessingBoundaryTests(unittest.TestCase):
    def test_archived_pdfs_match_the_review_package_and_document_method(self) -> None:
        artifact = AUDIT.build_audit()
        checks = artifact["verification"]["checks"]
        self.assertTrue(checks["all_archived_supplement_hashes_match_review_package"])
        self.assertTrue(checks["methods_and_noise_evidence_present"])
        self.assertEqual(artifact["verification"]["page_counts"]["DING2022_MOESM1"], 23)
        self.assertEqual(artifact["status"], "PASS_SUPPLEMENTARY_METHOD_BOUNDARY")

    def test_documented_method_does_not_promote_missing_numeric_evidence(self) -> None:
        artifact = AUDIT.build_audit()
        verification = artifact["verification"]
        self.assertTrue(verification["checks"]["review_package_reports_no_numeric_payload_or_rows"])
        self.assertTrue(verification["checks"]["filter_parameter_search_reproduces_absence"])
        self.assertFalse(verification["numeric_rows_or_csrc_admitted"])
        self.assertFalse(verification["reported_error_used_for_calibration"])
        self.assertFalse(verification["pixel_and_waveform_uncertainty_combined"])
        self.assertFalse(verification["holdout_accessed"])
        self.assertFalse(verification["claim_promotion"])
        self.assertEqual(artifact["major_result"]["closure_level"], "CLOSED_FOR_LANE")


if __name__ == "__main__":
    unittest.main()
