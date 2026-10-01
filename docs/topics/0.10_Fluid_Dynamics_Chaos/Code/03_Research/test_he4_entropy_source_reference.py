"""Source-reference fidelity and entropy-offset transport/force regression guards."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT = TOPIC / "Code/03_Research/Research_He4_Entropy_Source_Reference.py"
CONTRACT = TOPIC / "Data/03_Research/he4_entropy_source_and_reference_contract.json"
RESULT = TOPIC / "Result/artifacts/he4_entropy_source_reference_audit.json"


class He4EntropySourceReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads(RESULT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "audit.json"
            run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT), "--output", str(output)],
                                 cwd=ROOT, capture_output=True, text=True)
            if run.returncode:
                raise AssertionError(run.stdout + run.stderr)
            cls.fresh = json.loads(output.read_text(encoding="utf-8"))

    def test_source_fresh_checks_preserve_physical_admission_boundary(self):
        for path, expected in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected, path)
        a = self.fresh
        self.assertEqual(a["input_hashes"], self.published["input_hashes"])
        self.assertEqual(a["locked_tolerances"], self.published["locked_tolerances"])
        self.assertEqual(set(a["checks"]), set(self.published["checks"]))
        self.assertTrue(all(c["pass"] for c in a["checks"].values()))
        self.assertEqual(a["status"], "PASS_SOURCE_AND_REFERENCE_COORDINATE_CHECKS_ONLY")
        self.assertEqual(a["check_count"], 116)
        self.assertIs(a["calorimetric_branch_reference_known"], True)
        for key in ("TN1334_entropy_anchor_resolved", "admitted_material_values_assigned",
                    "independent_validation_admitted", "physical_uet_operator_admitted",
                    "physical_prediction_executed", "physical_J05_executed", "physical_J06_executed",
                    "entropy_offset_fitted", "claim_promotion", "dependency_unlock"):
            self.assertIs(a[key], False)
        self.assertIsNone(a["physical_acceptance_threshold"])
        self.assertIn("TN1334_selected_edition_entropy_reference_transfer_unresolved", a["remaining_blockers"])

    def test_six_source_tokens_SI_and_nominal_differences_do_not_establish_reference_conversion(self):
        rows = self.fresh["source_rows"]
        self.assertEqual([r["fountain_s_J_kgK"] for r in rows], [335.7, 397.2, 466.2])
        self.assertEqual([r["calorimetric_s_J_kgK"] for r in rows], [335., 395., 463.])
        self.assertEqual([r["TN_minus_fountain_J_kgK"] for r in rows], [1.7, .9, .4])
        self.assertEqual([r["TN_minus_calorimetric_J_kgK"] for r in rows], [2.4, 3.1, 3.6])
        p = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertIs(p["nominal_comparison"]["same_physical_temperature_established"], False)
        self.assertIs(p["branches"]["calorimetric"]["independent_of_its_heat_capacity_input"], False)
        self.assertIsNone(p["branches"]["calorimetric"]["covariance"])
        self.assertEqual(p["primary_fountain_source"]["publication_date"], "1984-05-01")
        self.assertEqual(p["primary_fountain_source"]["review_bibliography_year"], 1983)

    def test_energy_only_pass_misses_reference_error_but_local_correspondence_and_modes_detect_it(self):
        a = self.fresh
        tolerance = a["locked_tolerances"]["identity_tolerance"]
        floor = a["locked_tolerances"]["negative_control_floor"]
        old_speeds = next(r["correct_characteristic_speeds"] for r in a["normalized_offset_controls"] if r["offset"] == 0)
        for row in a["normalized_offset_controls"]:
            for v, expected in zip(row["correct_characteristic_speeds"], old_speeds):
                self.assertAlmostEqual(v, expected, places=10)
            self.assertLessEqual(row["correct_reciprocal_work_defect"], tolerance)
            if row["offset"] == 0:
                continue
            wrong = row["negative_controls"]
            self.assertLessEqual(wrong["naive_own_work_defect"], tolerance)
            self.assertGreater(wrong["omit_both_normalized_speed_error"], floor)
            self.assertGreater(wrong["omit_entropy_flux_local_defect"], floor)
            self.assertGreater(wrong["omit_phase_force_local_defect"], floor)
            self.assertGreater(abs(wrong["naive_characteristic_speeds"][1] - old_speeds[1]), .1)

    def test_corrupt_units_or_anchor_claim_fails_closed(self):
        for corruption in ("units", "anchor"):
            with self.subTest(corruption=corruption):
                p = json.loads(CONTRACT.read_text(encoding="utf-8"))
                if corruption == "units":
                    p["source"]["SI_multiplier"] = "1"
                    key = "SI_multiplier_J_g_to_J_kg"
                else:
                    p["TN1334_entropy_anchor_resolved"] = True
                    key = "boundary_TN1334_entropy_anchor_resolved"
                with tempfile.TemporaryDirectory() as folder:
                    source = Path(folder) / "corrupt.json"
                    output = Path(folder) / "audit.json"
                    source.write_text(json.dumps(p), encoding="utf-8")
                    run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT), "--contract-json",
                                          str(source), "--output", str(output)],
                                         cwd=ROOT, capture_output=True, text=True)
                    self.assertNotEqual(run.returncode, 0)
                    result = json.loads(output.read_text(encoding="utf-8"))
                    self.assertEqual(result["status"], "SOURCE_OR_REFERENCE_CHECK_FAIL")
                    self.assertIs(result["checks"][key]["pass"], False)
                    self.assertIs(result["claim_promotion"], False)
                    self.assertIs(result["physical_prediction_executed"], False)


if __name__ == "__main__":
    unittest.main()
