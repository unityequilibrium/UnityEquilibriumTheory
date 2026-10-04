"""Tree spatial current correspondence, source conventions and admission restraint."""
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
SCRIPT = TOPIC / "Code/03_Research/Research_Fluid_Core_O2_Current_Ward.py"
CONTRACT = TOPIC / "Data/03_Research/fluid_core_o2_current_ward_contract.json"
ARTIFACT = TOPIC / "Result/artifacts/fluid_core_o2_current_ward_audit.json"


class CurrentWardTests(unittest.TestCase):
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
        spec = importlib.util.spec_from_file_location("current_ward_regression", SCRIPT)
        cls.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.driver)

    def test_fresh_source_identity_and_tree_scope_do_not_promote_heat_material_or_formal_state(self):
        a = self.fresh
        self.assertEqual(a["status"], "PASS_TREE_SPATIAL_CURRENT_WARD_REFERENCE_ONLY")
        self.assertEqual(a["check_count"], 303)
        self.assertEqual(a["passing_check_count"], 303)
        for name in ("input_hashes", "source_AST_definition_hashes", "locked_verification"):
            self.assertEqual(a[name], self.published[name])
        self.assertEqual(list(a["checks"]), list(self.published["checks"]))
        for name, sha in a["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), sha)
        self.assertTrue(a["selected_tree_grandcanonical_flux_correspondence_supported"])
        self.assertTrue(a["selected_tree_spatial_Noether_Ward_supported"])
        for name in ("physical_heat_current_matched", "physical_material_frame_admitted", "charge_density_backreaction_completed",
                     "interacting_Noether_current_completed", "useful_relative_error_certified", "full_continuum_inverse_executed",
                     "formal_verification", "external_math_review", "interval_certified", "whole_Core_runtime_executed",
                     "physical_UET_operator_admitted", "physical_HeII_state_assigned", "live_Phi_executed",
                     "physical_J04_executed", "physical_J05_executed", "physical_J06_executed", "claim_promotion",
                     "dependency_unlock", "thresholds_relaxed", "parameters_fitted"):
            self.assertIs(a[name], False, name)
        prior = json.loads((ROOT / self.p["current_bound_artifact"]).read_text(encoding="utf-8"))
        self.assertEqual(prior["passing_check_count"], 289)
        self.assertFalse(prior["physical_heat_current_matched"])

    def test_direct_field_root_and_ward_controls_detect_index_charge_and_omission_errors(self):
        executions = roots = points = 0
        for row, old in zip(self.fresh["state_results"], self.published["state_results"]):
            mu = row["parameters"]["mu"]
            for p, previous in zip(row["mode_points"], old["mode_points"]):
                points += 1
                executions += p["source_control_count"]
                roots += len(p["flow_derivative_sweep"])
                m = p["mode"]
                for name, value in m.items():
                    self.assertTrue(math.isclose(value, previous["mode"][name], rel_tol=1e-8, abs_tol=0), name)
                self.assertGreater(m["action_per_amplitude_squared"], 0)
                self.assertLess(self.driver.relative(m["physical_energy_flux"], p["k"]), 1e-8)
                self.assertLess(self.driver.relative(m["grand_flux"], m["E"] * m["group_velocity"]), 1e-8)
                self.assertLess(self.driver.relative(m["charge_flux"], -m["E_h"]), 1e-8)
                self.assertLess(self.driver.relative(m["physical_energy_flux"], m["grand_flux"] + mu * m["charge_flux"]), 1e-8)
                self.assertGreater(m["charge_flux"], 0) if p["branch"] == "lower" else self.assertLess(m["charge_flux"], 0)
                for value in p["maximum_source_errors"].values():
                    self.assertLessEqual(value, 1e-8)
                self.assertLess(p["source_final"]["unraised_stress_weight"], 0)
                for v in p["flow_derivative_sweep"]:
                    self.assertLessEqual(v["relative_error"], 1e-5)
        self.assertEqual((points, executions, roots), (16, 288, 36))
        for name, check in self.fresh["checks"].items():
            if "negative_control" in name:
                self.assertGreater(check["metric"], .001, name)

    def test_projected_grand_current_matches_old_source_without_assuming_charge_density_or_heat_frame(self):
        for row, old in zip(self.fresh["state_results"], self.published["state_results"]):
            for v, previous in zip(row["projection_sweep"], old["projection_sweep"]):
                self.assertGreater(v["source_G"], 0)
                self.assertTrue(math.isclose(v["source_G"], previous["source_G"], rel_tol=1e-8, abs_tol=0))
                for name in ("old_source_correspondence_error", "projected_charge_grand_identity_error", "total_energy_projected_relative_norm"):
                    self.assertLessEqual(v[name], 1e-8)
            sweep = row["projection_sweep"]
            self.assertLess(self.driver.relative(sweep[-1]["source_G"], sweep[-2]["source_G"]), .01)
            soft = next(p for p in row["mode_points"] if p["branch"] == "lower" and p["parent_over_thermal_k"] == .1)
            self.assertLess(soft["thermodynamic_mode_charge"], 0)
            self.assertGreater(soft["mode"]["charge_flux"], 0)
            self.assertFalse(soft["complete_density_backreaction"])
        self.assertEqual(self.fresh["unit_powers"], {"Nwave": 3, "j_N": 3, "T_flux": 4, "J_N": 0, "J_E": 1, "J_G": 1, "source_G": 5})
        self.assertIsNone(self.fresh["physical_frequency_window"])
        self.assertIsNone(self.fresh["physical_relaxation_time"])
        with self.assertRaises(ValueError):
            self.driver.mode(1, self.fresh["state_results"][0]["parameters"], "undeclared")

    def test_false_admission_changed_controls_and_stale_prior_input_fail_closed(self):
        mutations = []
        for name in ("physical_heat_current", "physical_material_frame", "full_charge_density_backreaction", "interacting_Noether_current",
                     "formal_verification", "useful_relative_error_certificate"):
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
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".current-ward-test-") as folder:
            stale = json.loads((ROOT / self.p["current_bound_artifact"]).read_text(encoding="utf-8"))
            stale["input_hashes"][next(iter(stale["input_hashes"]))] = "0" * 64
            source = Path(folder) / "stale.json"
            source.write_text(json.dumps(stale), encoding="utf-8")
            p = copy.deepcopy(self.p)
            p["current_bound_artifact"] = source.relative_to(ROOT).as_posix()
            mutations.append(p)
            for p in mutations:
                a = self.driver.audit(p, CONTRACT)
                self.assertEqual(a["status"], "TREE_CURRENT_WARD_REFERENCE_FAIL")
                self.assertEqual(a["state_results"], [])
                self.assertFalse(a["selected_tree_grandcanonical_flux_correspondence_supported"])
                self.assertFalse(a["physical_heat_current_matched"])


if __name__ == "__main__":
    unittest.main()
