"""Leading density response, fixed derivative domain and preserved wiring failures."""
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

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Density_Backreaction.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_density_backreaction_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_density_backreaction_audit.json"

class DensityBackreactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(CONTRACT.read_text(encoding="utf-8"));cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json";data=[]
            for _ in range(2):
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],cwd=ROOT,capture_output=True,text=True)
                if run.returncode:raise AssertionError(run.stdout+run.stderr)
                data.append(output.read_bytes())
            if data[0]!=data[1]:raise AssertionError("fresh same-runtime outputs differ")
            cls.fresh=json.loads(data[0])
        spec=importlib.util.spec_from_file_location("density_backreaction_regression",SCRIPT)
        cls.driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.driver)

    def test_fresh_sources_and_historical_failure_identity_keep_leading_not_full_scope(self):
        a=self.fresh
        self.assertEqual(a["status"],"PASS_LEADING_MEAN_DENSITY_GAUSSIAN_SUBSET_ONLY")
        self.assertEqual((a["check_count"],a["passing_check_count"]),(398,398))
        for name in ("input_hashes","source_AST_definition_hashes","locked_verification"):
            self.assertEqual(a[name],self.published[name])
        self.assertEqual(list(a["checks"]),list(self.published["checks"]))
        for path,sha in a["input_hashes"].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha)
        for field,status in (("first_binding_failure","INPUT_SOURCE_BINDING_FAILURE"),("uncentered_failure","UNCENTERED_SOURCE_VARIATION_FAILURE")):
            old=json.loads((ROOT/self.p[field]).read_text(encoding="utf-8"))
            self.assertEqual(old["status"],status);self.assertEqual(old["completed_scientific_states"],0)
            self.assertFalse(old["artifact_produced"])
        self.assertTrue(a["leading_mean_density_backreaction_supported"])
        self.assertTrue(a["fixed_domain_Gaussian_density_Legendre_supported"])
        for field in ("full_interacting_density_backreaction_completed","full_nonlinear_wave_solved","interacting_Noether_current_completed",
                      "self_consistent_thermal_gap_solved","paper_low_T_accuracy_admitted","physical_heat_current_matched",
                      "physical_material_frame_admitted","physical_UET_operator_admitted","physical_HeII_state_assigned",
                      "formal_verification","external_math_review","interval_certified","whole_Core_runtime_executed",
                      "physical_J04_executed","physical_J05_executed","physical_J06_executed","live_Phi_executed",
                      "useful_relative_error_certified","claim_promotion","dependency_unlock","parameters_fitted","thresholds_relaxed"):
            self.assertIs(a[field],False,field)

    def test_source_eom_action_density_and_independent_mu_variations_need_mean_response(self):
        sets=derivatives=points=0
        for row,old in zip(self.fresh["state_results"],self.published["state_results"]):
            for p,previous in zip(row["mode_points"],old["mode_points"]):
                points+=1;sets+=p["source_coefficient_sets"];derivatives+=len(p["mu_derivative_sweep"])
                d=p["density"]
                for name,value in d.items():self.assertTrue(math.isclose(value,previous["density"][name],rel_tol=1e-8,abs_tol=0),name)
                self.assertLess(d["shift_per_amplitude_squared"],0)
                for value in p["maximum_conditioned_errors"].values():self.assertLessEqual(value,1e-8)
                self.assertGreater(abs(p["source_final"]["raw"][3]),.001)
                self.assertLess(abs(p["source_final"]["corrected"][3])/abs(d["radial_force_coefficient"]),1e-8)
                self.assertGreater(self.driver.conditioned(d["q_raw_coefficient"],d["q_corrected_coefficient"],d["q_raw_coefficient"]),.001)
                for v in p["mu_derivative_sweep"]:self.assertLessEqual(v["relative_error"],1e-5)
                # The conditioned source bound is explicit; it is not a claim of
                # 1e-8 relative precision after a large soft-charge cancellation.
                self.assertGreaterEqual(d["charge_cancellation_condition"],0)
                self.assertGreaterEqual(p["corrected_charge_source_actual_relative_error"],0)
        self.assertEqual((points,sets,derivatives),(16,192,48))

    def test_thermal_subset_fixed_domain_legendre_and_units_do_not_admit_paper_regime(self):
        for row,old in zip(self.fresh["state_results"],self.published["state_results"]):
            self.assertLess(row["paper_T_squared_over_lambda_mu_squared"],.001)
            for v,previous in zip(row["thermal_sweep"],old["thermal_sweep"]):
                self.assertEqual(v["fixed_K"],row["parameters"]["K"])
                self.assertGreater(v["q_raw"],0);self.assertLess(v["q_corrected"],0);self.assertLess(v["mean_shift"],0)
                self.assertGreater(v["P"],0);self.assertGreater(v["U_grand"],0)
                for name in ("P","q_corrected","U_grand","mean_shift","entropy"):
                    self.assertTrue(math.isclose(v[name],previous[name],rel_tol=1e-8,abs_tol=0),name)
            for v in row["thermal_derivatives"]:
                self.assertEqual(v["fixed_K"],row["parameters"]["K"])
                self.assertLess(self.driver.rel(v["q_finite"],row["thermal_sweep"][-1]["q_corrected"]),1e-5)
                self.assertLess(self.driver.rel(v["s_finite"],row["thermal_sweep"][-1]["entropy"]),1e-5)
        self.assertEqual(self.fresh["unit_powers"]["thermal_q"],3)
        self.assertEqual(self.fresh["unit_powers"]["thermal_P"],4)
        self.assertIsNone(self.fresh["physical_frequency_window"]);self.assertIsNone(self.fresh["physical_relaxation_time"])

    def test_changed_scope_domain_threshold_and_stale_prior_sources_fail_closed(self):
        mutations=[]
        for name in ("full_interacting_density_backreaction","self_consistent_thermal_gap","paper_low_T_accuracy","physical_heat_current","formal_verification"):
            p=copy.deepcopy(self.p);p["admission"][name]=True;mutations.append(p)
        for field,value in (("temperatures",[]),("mu",1.3)):
            p=copy.deepcopy(self.p);p[field]=value;mutations.append(p)
        for field,value in (("source_conditioned_tolerance",1e-6),("derivative_domain","moving_cutoff")):
            p=copy.deepcopy(self.p);p["verification"][field]=value;mutations.append(p)
        with tempfile.TemporaryDirectory(dir=ROOT,prefix=".density-test-") as folder:
            old=json.loads((ROOT/self.p["prior_ward_artifact"]).read_text(encoding="utf-8"))
            old["input_hashes"][next(iter(old["input_hashes"]))]="0"*64
            path=Path(folder)/"stale.json";path.write_text(json.dumps(old),encoding="utf-8")
            p=copy.deepcopy(self.p);p["prior_ward_artifact"]=path.relative_to(ROOT).as_posix();mutations.append(p)
            for p in mutations:
                a=self.driver.audit(p,CONTRACT)
                self.assertEqual(a["status"],"LEADING_MEAN_DENSITY_DIAGNOSTIC_FAIL")
                self.assertEqual(a["state_results"],[])
                self.assertFalse(a["leading_mean_density_backreaction_supported"])
                self.assertFalse(a["physical_heat_current_matched"])

if __name__=="__main__":unittest.main()
