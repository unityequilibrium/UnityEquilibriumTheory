"""Scoped continuum-form bounds, exact algebra and fail-closed physical/source boundaries."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT = TOPIC / "Code/03_Research/Research_Fluid_Core_O2_Continuum_Form.py"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_continuum_form_contract.json"
ARTIFACT = TOPIC / "Result/artifacts/fluid_core_o2_continuum_form_audit.json"


class ContinuumFormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "fresh.json"
            run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT), "--output", str(output)],
                                 cwd=ROOT, capture_output=True, text=True)
            if run.returncode:
                raise AssertionError(run.stdout + run.stderr)
            cls.fresh = json.loads(output.read_text(encoding="utf-8"))
            cls.fresh_bytes = output.read_bytes()
        spec = importlib.util.spec_from_file_location("continuum_form_test", SCRIPT)
        cls.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.driver)

    def test_exact_vertex_negative_control_fresh_sources_and_no_formal_or_physical_unlock(self):
        a = self.fresh
        self.assertEqual(self.fresh_bytes, ARTIFACT.read_bytes())
        self.assertEqual(a["status"], "PASS_CONDITIONAL_CONTINUUM_FORM_DIAGNOSTIC_ONLY")
        self.assertTrue(all(v["pass"] for v in a["checks"].values()))
        for path, value in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), value, path)
        identity = a["exact_cubic_polynomial_identity"]
        self.assertEqual(identity["difference_monomial_count"], 0)
        self.assertGreater(identity["missing_parent_pressure_negative_control_monomial_count"], 0)
        self.assertEqual(identity["original_all_monomial_energy_powers"], [3])
        self.assertTrue(identity["negative_control_detected"])
        self.assertTrue(a["previous_package"]["refinement_gate"]["target_pass"])
        self.assertFalse(a["previous_package"]["refinement_gate"]["historical_unenriched_target_pass"])
        for key in ("formal_verification", "external_math_review", "continuum_current_upper_bound_established",
                    "current_response_divergence_established", "unbounded_K_domain_established",
                    "full_interacting_collision_completed", "positive_uniform_vector_gap_admitted",
                    "physical_heat_current_matched", "physical_UET_operator_admitted", "physical_HeII_state_assigned",
                    "physical_J04_executed", "physical_J05_executed", "physical_J06_executed",
                    "whole_Core_runtime_executed", "live_Phi_executed", "claim_promotion", "dependency_unlock",
                    "thresholds_relaxed", "parameters_fitted"):
            self.assertIs(a[key], False, key)
        self.assertFalse(a["derivation_scope"]["interval_certified"])
        self.assertFalse(a["derivation_scope"]["full_continuum_inverse_executed"])

    def test_bounded_trial_majorants_and_smooth_convergence_have_explicit_domain_constraints(self):
        for e in self.fresh["pointwise_event_diagnostics"]:
            self.assertGreater(e["minimum_triangle_factor"], 0)
            self.assertGreater(e["minimum_event_density"], 0)
            self.assertTrue(e["strict_vertex_positive_bracket"])
            self.assertLessEqual(e["maximum_vertex_to_majorant_ratio"], 1 + 1e-8)
            self.assertLessEqual(e["maximum_W_to_tight_majorant_ratio"], 1 + 1e-8)
            self.assertLess(e["vertex_identity_error"], 1e-8)
            self.assertLess(e["geometry_error"], 1e-9)
        for row in self.fresh["state_results"]:
            bounds = row["smooth_bound_sweep"]
            for name in ("smooth_G_upper", "smooth_Q_upper"):
                self.assertTrue(all(a[name] > b[name] > 0 for a, b in zip(bounds, bounds[1:])))
            a = row["parameters"]
            for epsilon in (0, -a["T"], a["K"] * 1.01):
                with self.assertRaisesRegex(ValueError, "epsilon"):
                    self.driver.measure_bounds(a, epsilon)
            with self.assertRaisesRegex(ValueError, "positive"):
                self.driver.parameters(a["T"], a["mu"], a["m2"], 0, 60)
        self.assertEqual(self.fresh["unit_powers"], {
            "w_density": 2, "W_density": 2, "W_prefactor": -3, "event_integral": 4,
            "G": 5, "Q": 6, "Rayleigh": 1, "vertex": 1})

    def test_soft_countersequence_projection_and_unit_scaling_do_not_assign_a_transport_time(self):
        for row in self.fresh["state_results"]:
            bumps = row["bump_countersequence"]
            rates = [b["analytic_bounds"]["rayleigh_upper"] for b in bumps]
            self.assertTrue(all(a > b > 0 for a, b in zip(rates, rates[1:])))
            # An explicit positive proposed lower gap above the last derived
            # symbolic upper formula is contradicted for this selected bump.
            proposed_gap = (rates[0] + rates[-1]) / 2
            self.assertLess(rates[-1], proposed_gap)
            for bump in bumps:
                bound = bump["analytic_bounds"]
                actual = bump["Gram_sweep"][-1]
                self.assertGreater(bound["projected_G_lower"], 0)
                self.assertGreaterEqual(actual["projected_G"], bound["projected_G_lower"])
                self.assertLessEqual(actual["G"] - actual["projected_G"], bound["projection_loss_upper"])
                self.assertIsNone(bound["physical_relaxation_time"])
                self.assertIsNone(bound["current_response_upper_bound"])
                for name in ("G", "projected_G", "momentum_G"):
                    last, before = bump["Gram_sweep"][-1][name], bump["Gram_sweep"][-2][name]
                    self.assertLess(self.driver.relative(last, before), .01)
        self.assertTrue(all(v["pass"] for k, v in self.fresh["checks"].items() if k.startswith("scale/")))
        self.assertIsNone(self.fresh["physical_relaxation_time"])
        self.assertIsNone(self.fresh["physical_frequency_window"])
        self.assertFalse(self.fresh["current_response_divergence_established"])

    def test_physical_formal_or_current_unlock_empty_states_and_relaxed_targets_fail_closed(self):
        for mutation in ("physical", "formal", "current", "empty", "relaxed", "changed_state", "stale_source"):
            p = json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation == "physical":
                p["admission"]["physical_heat_current"] = True
            elif mutation == "formal":
                p["admission"]["formal_verification"] = True
            elif mutation == "current":
                p["admission"]["source_weighted_current_upper_bound"] = True
            elif mutation == "empty":
                p["temperatures"] = []
            elif mutation == "relaxed":
                p["verification"]["refinement_relative_tolerance"] = .02
            elif mutation == "changed_state":
                p["mu"] = 1.29
            with tempfile.TemporaryDirectory(dir=ROOT, prefix=".continuum-audit-test-") as folder:
                source, output = Path(folder) / "bad.json", Path(folder) / "audit.json"
                if mutation == "stale_source":
                    prior = json.loads((ROOT / p["infrared_artifact"]).read_text(encoding="utf-8"))
                    prior["input_hashes"][next(iter(prior["input_hashes"]))] = "0" * 64
                    stale = Path(folder) / "stale.json"
                    stale.write_text(json.dumps(prior), encoding="utf-8")
                    p["infrared_artifact"] = stale.relative_to(ROOT).as_posix()
                source.write_text(json.dumps(p), encoding="utf-8")
                run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT), "--contract-json", str(source),
                                      "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
                self.assertNotEqual(run.returncode, 0, run.stdout + run.stderr)
                result = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(result["status"], "CONTINUUM_FORM_DIAGNOSTIC_FAIL")
                self.assertEqual(result["state_results"], [])
                self.assertFalse(result["selected_finite_cutoff_domain_internal_derivation_supported"])
                self.assertFalse(result["no_uniform_vector_gap_internal_derivation_supported"])
                self.assertFalse(result["continuum_current_upper_bound_established"])
                self.assertFalse(result["formal_verification"])
                self.assertFalse(result["physical_heat_current_matched"])
                self.assertFalse(result["dependency_unlock"])


if __name__ == "__main__":
    unittest.main()
