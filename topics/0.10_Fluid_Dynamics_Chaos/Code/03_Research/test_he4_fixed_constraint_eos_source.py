"""Source fidelity, physical admission and corrupted-import regression guards."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT = TOPIC / "Code/03_Research/Research_He4_Fixed_Constraint_EOS_Source.py"
SOURCE = TOPIC / "Data/03_Research/he4_tn1334_fixed_constraint_eos_source_candidate.json"
RESULT = TOPIC / "Result/artifacts/he4_tn1334_fixed_constraint_eos_source_audit.json"


class He4FixedConstraintSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads(RESULT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "audit.json"
            run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT), "--output", str(out)],
                                 cwd=ROOT, capture_output=True, text=True)
            if run.returncode:
                raise AssertionError(run.stdout + run.stderr)
            cls.fresh = json.loads(out.read_text(encoding="utf-8"))

    def test_source_fresh_candidate_does_not_admit_physics(self):
        a = self.fresh
        for path, digest in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)
        self.assertEqual(a["input_hashes"], self.published["input_hashes"])
        self.assertEqual(a["printing_rule"], self.published["printing_rule"])
        self.assertEqual(set(a["checks"]), set(self.published["checks"]))
        self.assertTrue(all(row["pass"] for row in a["checks"].values()))
        self.assertEqual(a["status"], "PASS_SOURCE_CANDIDATE_PRINTING_COMPATIBILITY_ONLY")
        for key in ("admitted_material_values_assigned", "independent_validation_admitted",
                    "physical_uet_operator_admitted", "physical_prediction_executed",
                    "physical_J05_executed", "physical_J06_executed",
                    "claim_promotion", "dependency_unlock", "printing_intervals_are_physical_uncertainty"):
            self.assertIs(a[key], False)
        self.assertIsNone(a["physical_acceptance_threshold"])
        self.assertIn("absolute_entropy_anchor_for_selected_edition_unresolved", a["remaining_blockers"])

    def test_SI_conversion_and_distinct_derivative_constraints(self):
        row = self.fresh["rows"][1]
        values = row["SI_central_values"]
        self.assertEqual(values["P_Pa"], 1128.0)
        self.assertEqual(values["rho_kg_m3"], 145.3)
        self.assertEqual(values["s_J_kgK"], 398.1)
        self.assertEqual(values["cp_J_kgK"], 2193.0)
        self.assertAlmostEqual(values["alpha_p_per_K"], -.007003 / 1.7)
        self.assertAlmostEqual(values["kappa_T_per_Pa"], .0001429 / 1128, places=17)
        self.assertEqual(row["SI_printing_intervals"]["T_K"], {"lo": "1.6995", "hi": "1.7005"})
        p = json.loads(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(p["column_contract"]["cp_J_gK"]["constraint"], "T ds/dT at fixed pressure")
        self.assertEqual(p["column_contract"]["cv_J_gK"]["constraint"], "T ds/dT at fixed specific volume")
        self.assertIs(p["column_contract"]["gruneisen"]["UET_Phi_equivalence"], False)
        self.assertTrue(all(v is None for v in p["rows"][1]["transport"].values()))

    def test_printing_compatibility_is_not_exact_point_identity_and_controls_detect_errors(self):
        row = self.fresh["rows"][1]
        v = row["SI_central_values"]
        point_derived = v["T_K"] * v["alpha_p_per_K"] ** 2 / (v["rho_kg_m3"] * v["kappa_T_per_Pa"])
        self.assertGreater(abs((v["cp_J_kgK"] - v["cv_J_kgK"]) - point_derived), .1)
        self.assertTrue(row["printing_diagnostics"]["cp_minus_cv"]["printing_intervals_overlap"])
        for row in self.fresh["rows"]:
            self.assertTrue(all(v["printing_intervals_overlap"] for v in row["printing_diagnostics"].values()))
        self.assertEqual(set(self.fresh["negative_controls"]),
                         {"MPa_as_Pa", "alpha_times_T_as_alpha", "P_kappa_as_kappa",
                          "vapor_density", "blank_transport_as_zero"})
        self.assertTrue(all(v["detected"] for v in self.fresh["negative_controls"].values()))

    def test_corrupt_phase_or_blank_import_fails_instead_of_promoting_candidate(self):
        for corruption in ("vapor", "zero_transport"):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as folder:
                package = json.loads(SOURCE.read_text(encoding="utf-8"))
                if corruption == "vapor":
                    package["rows"][1]["phase"] = "vapor"
                    expected = "tn1334-liquid-1.700K_liquid_phase"
                else:
                    package["rows"][1]["transport"]["ordinary_conductivity_W_mK"] = 0
                    expected = "tn1334-liquid-1.700K_transport_unknown_not_zero"
                source = Path(folder) / "candidate.json"
                out = Path(folder) / "audit.json"
                source.write_text(json.dumps(package), encoding="utf-8")
                run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT),
                                      "--source-json", str(source), "--output", str(out)],
                                     cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
                artifact = json.loads(out.read_text(encoding="utf-8"))
                self.assertIs(artifact["checks"][expected]["pass"], False)
                self.assertEqual(artifact["status"], "SOURCE_CANDIDATE_PRINTING_DIAGNOSTIC_FAIL")
                self.assertIs(artifact["claim_promotion"], False)


if __name__ == "__main__":
    unittest.main()
