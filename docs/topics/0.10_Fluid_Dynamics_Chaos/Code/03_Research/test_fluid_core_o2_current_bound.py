"""Current-bound scope, source-frame obstruction, soft dual norm and immutable controls."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT = TOPIC / "Code/03_Research/Research_Fluid_Core_O2_Current_Bound.py"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_current_bound_contract.json"
ARTIFACT = TOPIC / "Result/artifacts/fluid_core_o2_current_bound_audit.json"


class CurrentBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.published = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "fresh.json"
            snapshots = []
            for _ in range(2):
                run = subprocess.run([sys.executable, "-W", "error", str(SCRIPT), "--output", str(out)],
                                     cwd=ROOT, capture_output=True, text=True)
                if run.returncode:
                    raise AssertionError(run.stdout + run.stderr)
                snapshots.append(out.read_bytes())
            if snapshots[0] != snapshots[1]:
                raise AssertionError("fresh same-runtime outputs differ")
            cls.fresh = json.loads(snapshots[0])
        spec = importlib.util.spec_from_file_location("current_bound_regression", SCRIPT)
        cls.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.driver)

    def test_current_bound_is_conditional_and_prior_domain_no_gap_and_hashes_are_preserved(self):
        a = self.fresh
        self.assertEqual(a["status"], "PASS_CONDITIONAL_SELECTED_CURRENT_BOUND_ONLY")
        self.assertEqual(a["check_count"], a["passing_check_count"])
        self.assertEqual(a["input_hashes"], self.published["input_hashes"])
        self.assertEqual(a["locked_verification"], self.published["locked_verification"])
        self.assertEqual(list(a["checks"]), list(self.published["checks"]))
        for name, sha in a["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), sha)
        self.assertTrue(a["selected_current_upper_bound_internal_derivation_supported"])
        self.assertTrue(a["selected_current_finiteness_internal_derivation_supported"])
        for key in ("continuum_current_upper_bound_established", "useful_relative_error_certified", "formal_verification",
                    "external_math_review", "interval_certified", "full_continuum_inverse_executed",
                    "strong_Hilbert_inverse_established", "positive_uniform_vector_gap_admitted",
                    "current_response_divergence_established", "physical_heat_current_matched",
                    "physical_UET_operator_admitted", "physical_HeII_state_assigned", "physical_J04_executed",
                    "physical_J05_executed", "physical_J06_executed", "whole_Core_runtime_executed", "live_Phi_executed",
                    "claim_promotion", "dependency_unlock", "thresholds_relaxed", "parameters_fitted"):
            self.assertIs(a[key], False, key)
        prior = json.loads((ROOT / self.p["continuum_artifact"]).read_text(encoding="utf-8"))
        self.assertTrue(prior["no_uniform_vector_gap_internal_derivation_supported"])
        self.assertFalse(prior["continuum_current_upper_bound_established"])

    def test_analytic_patch_constants_are_positive_and_do_not_use_sampled_minima(self):
        for fresh, old in zip(self.fresh["state_results"], self.published["state_results"]):
            b = fresh["analytic_constants"]
            for name in ("eta", "sigma", "nu", "beta", "alpha", "C_P", "D", "B_upper", "R_upper"):
                self.assertGreater(b[name], 0)
                self.assertTrue(math.isclose(b[name], old["analytic_constants"][name], rel_tol=1e-8, abs_tol=0), name)
            # Exact Jensen graph coefficients combine to3972/K. Sampling never
            # sets alpha; it is the preregistered analytic beta*sigma formula.
            self.assertTrue(math.isclose(b["C_P"] * fresh["parameters"]["K"], 3972, rel_tol=1e-14))
            self.assertEqual(b["alpha"], b["beta"] * b["sigma"])
            self.assertTrue(math.isclose(b["R_upper"], 2 * b["C_P"] * b["B_upper"] / b["alpha"], rel_tol=1e-14))
            for event in fresh["patch_events"]:
                for name in ("minimum_sin2_over_sigma", "minimum_vertex_over_lower", "minimum_W_over_beta_p",
                             "minimum_W_sin2_over_alpha_p", "minimum_angular_bound_ratio"):
                    self.assertGreaterEqual(event[name], 1 - 1e-8)
                self.assertLess(event["raw_momentum_collision_error"], 1e-9)
            exact = fresh["exact_gap_polynomial_identity"]
            self.assertEqual(exact["difference_monomial_count"], 0)
            self.assertGreater(exact["wrong_factor_negative_control_monomial_count"], 0)

    def test_exact_frame_is_required_and_soft_source_dual_is_integrable_without_physical_time(self):
        for row in self.fresh["state_results"]:
            b = row["analytic_constants"]
            for v in row["current_sweep"]:
                self.assertLess(v["source_frame_error"], 1e-8)
                self.assertGreater(v["unprojected_momentum_overlap"], 0)
                self.assertIs(v["unprojected_source_bound_possible"], False)
                self.assertGreater(v["B_J"], 0)
                self.assertLess(v["B_J"], b["B_upper"])
                self.assertLess(v["soft_dual_integrand_over_k_limit_errors"][-1], .01)
            for name in ("dbar", "source_G", "B_J", "momentum_G"):
                first, last = row["current_sweep"][-2][name], row["current_sweep"][-1][name]
                self.assertLess(abs(last - first) / max(abs(first), abs(last)), .01)
            a = copy.deepcopy(row["parameters"])
            a["c"] *= 1.1
            with self.assertRaisesRegex(ValueError, "positive condensed"):
                self.driver.lower_constants(a)
            a = copy.deepcopy(row["parameters"])
            a["K"] *= 1e6
            with self.assertRaisesRegex(ValueError, "underflowed"):
                self.driver.lower_constants(a)
        self.assertIsNone(self.fresh["physical_relaxation_time"])
        self.assertIsNone(self.fresh["physical_frequency_window"])
        self.assertEqual(self.fresh["unit_powers"]["R_upper"], 4)
        self.assertEqual(self.fresh["unit_powers"]["B_J"], 6)

    def test_false_admission_changed_controls_and_stale_sources_fail_closed(self):
        mutations = []
        for name in ("physical_heat_current", "formal_verification", "useful_relative_error_certificate", "strong_Hilbert_inverse"):
            p = copy.deepcopy(self.p)
            p["admission"][name] = True
            mutations.append(p)
        for name, value in (("temperatures", []), ("mu", 1.3)):
            p = copy.deepcopy(self.p)
            p[name] = value
            mutations.append(p)
        p = copy.deepcopy(self.p)
        p["verification"]["algebra_relative_tolerance"] = 1e-6
        mutations.append(p)
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".current-bound-test-") as folder:
            stale = json.loads((ROOT / self.p["continuum_artifact"]).read_text(encoding="utf-8"))
            stale["input_hashes"][next(iter(stale["input_hashes"]))] = "0" * 64
            source = Path(folder) / "stale.json"
            source.write_text(json.dumps(stale), encoding="utf-8")
            p = copy.deepcopy(self.p)
            p["continuum_artifact"] = source.relative_to(ROOT).as_posix()
            mutations.append(p)
            for p in mutations:
                a = self.driver.audit(p, CONTRACT)
                self.assertEqual(a["status"], "SELECTED_CURRENT_BOUND_DIAGNOSTIC_FAIL")
                self.assertEqual(a["state_results"], [])
                self.assertFalse(a["selected_current_finiteness_internal_derivation_supported"])
                self.assertFalse(a["selected_current_upper_bound_internal_derivation_supported"])
                self.assertFalse(a["physical_heat_current_matched"])


if __name__ == "__main__":
    unittest.main()
