"""Independent soft enrichment, smooth trial limit and immutable failed-source boundaries."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Infrared_Trials.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_infrared_trials_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_infrared_trials_audit.json"

class InfraredTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))
        spec=importlib.util.spec_from_file_location("infrared_test_driver",SCRIPT)
        cls.driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.driver)

    def test_fresh_sources_geometry_archive_and_unchanged_physical_collision_tail(self):
        a=self.fresh
        for f,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h,f)
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(list(a["checks"]),list(self.published["checks"]))
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(a["status"],"PASS_ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_ONLY")
        self.assertTrue(all(q["pass"] for q in a["checks"].values()))
        self.assertFalse(a["kernel_AST_hashes"]["full_function_unchanged"])
        self.assertEqual(a["kernel_AST_hashes"]["prior_collision_tail"],a["kernel_AST_hashes"]["current_collision_tail"])
        record=a["first_execution_record"];first=json.loads((ROOT/record["artifact"]).read_text(encoding="utf-8"))
        archived=ROOT/record["verifier_source_archive"]
        self.assertEqual(hashlib.sha256(archived.read_bytes()).hexdigest(),first["input_hashes"][SCRIPT.relative_to(ROOT).as_posix()])
        self.assertEqual(first["locked_verification"],a["locked_verification"])
        self.assertEqual(first["status"],"ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_FAIL")
        self.assertTrue(first["execution_errors"])
        for key in ("continuum_collision_form_domain_established","continuum_current_upper_bound_established",
          "physical_heat_current_matched","full_interacting_collision_completed","continuum_spectral_gap_established",
          "thermalization_derived","physical_frequency_window_established","collective_sound_damping_assigned",
          "physical_UET_operator_admitted","physical_HeII_state_assigned","physical_J04_executed",
          "physical_J05_executed","physical_J06_executed","whole_Core_runtime_executed",
          "live_Phi_executed","claim_promotion","dependency_unlock","thresholds_relaxed","parameters_fitted"):
            self.assertIs(a[key],False,key)

    def test_enriched_agreement_and_discrete_bounds_do_not_relabel_old_failed_targets(self):
        a=self.fresh
        self.assertTrue(a["refinement_gate"]["target_pass"])
        self.assertFalse(a["refinement_gate"]["historical_unenriched_target_pass"])
        self.assertFalse(a["refinement_gate"]["continuum_current_closed"])
        self.assertFalse(a["previous_failed_package"]["refinement_gate"]["target_pass"])
        for published,fresh in zip(self.published["state_results"],a["state_results"]):
            self.assertLess(fresh["measured_targets"]["enriched_cross_family"]["relative_change"],.001)
            self.assertLessEqual(fresh["EVEN"]["R"],fresh["HYBRID"]["R"]*(1+1e-8))
            self.assertLessEqual(fresh["HYBRID"]["R"],fresh["SOFT"]["R"]*(1+1e-8))
            values=[q["R"] for q in fresh["hybrid_basis_sweep"]]
            self.assertTrue(np.all(np.diff(values)>=-1e-8*max(values)))
            for target in fresh["measured_targets"].values():
                self.assertEqual(target["threshold"],.01);self.assertTrue(target["pass"])
            self.assertTrue(all(v<1e-8 for v in fresh["immutable_correspondence"].values()))
            for family in ("EVEN","HYBRID","SOFT"):
                self.assertLess(abs(fresh[family]["R"]/published[family]["R"]-1),1e-8)
                self.assertIsNone(fresh[family]["physical_time"])

    def test_smooth_origin_and_near_collinear_precision_repair_do_not_clip_events(self):
        a=self.fresh
        self.assertGreater(sum(b["high_precision_gap_events"] for b in a["basis_banks"]),0)
        for b in a["basis_banks"]:
            self.assertLess(b["raw_momentum_error"],1e-8)
            self.assertLess(b["max_event_geometry_error"],1e-9)
            self.assertGreater(b["minimum_triangle_factor"],0)
            if b["family"]=="SMOOTH":
                origin=self.driver.evaluate_basis(np.array([0.]),b["basis"])
                self.assertTrue(np.all(origin==0))
                self.assertGreater(b["basis"]["epsilon"],0)
        for row in a["state_results"]:
            self.assertLess(row["measured_targets"]["smooth_order"]["relative_change"],1e-5)
            self.assertLess(row["measured_targets"]["smooth_to_hybrid"]["relative_change"],1e-5)
        mu=1.28;r=mu*mu-1.;B=r+2*mu*mu
        k=1e-6;p=np.array([1e-11]);q=np.nextafter(k-p,0);before=q.copy()
        self.assertLessEqual(float(p[0]+q[0]-k),0)
        factors,P,Q,repaired=self.driver.stable_geometry(k,p,q,{"mu":mu,"r":r,"B":B})
        self.assertEqual(repaired,1);self.assertTrue(np.all(factors>0))
        self.assertTrue(np.array_equal(q,before))
        self.assertLess(abs(float(np.linalg.norm(P,axis=1)[0])/p[0]-1),1e-8)
        self.assertLess(np.linalg.norm(P+Q-np.array([0.,0.,k]))/k,1e-8)
        with self.assertRaisesRegex(ValueError,"inconsistent tree parameters"):
            self.driver.stable_geometry(k,p,q,{"mu":mu,"r":r,"B":B*1.001})

    def test_false_physical_or_continuum_admission_empty_or_relaxed_targets_fail_closed(self):
        for mutation in ("physical","continuum","empty","relaxed"):
            p=json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation=="physical":p["admission"]["physical_heat_current"]=True
            elif mutation=="continuum":p["admission"]["continuum_collision_form_domain"]=True
            elif mutation=="empty":p["temperatures"]=[]
            else:p["verification"]["refinement_relative_tolerance"]=.02
            with tempfile.TemporaryDirectory() as folder:
                source=Path(folder)/"bad.json";output=Path(folder)/"result.json"
                source.write_text(json.dumps(p),encoding="utf-8")
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                                   cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,run.stdout+run.stderr)
                result=json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(result["status"],"ENRICHED_SMOOTH_TRIAL_DIAGNOSTIC_FAIL")
                self.assertFalse(result["shared_enriched_smooth_vector_trials_evaluated"])
                self.assertFalse(result["refinement_gate"]["target_pass"])
                self.assertFalse(result["physical_heat_current_matched"])
                self.assertFalse(result["continuum_collision_form_domain_established"])
                self.assertFalse(result["dependency_unlock"])

if __name__=="__main__":
    unittest.main()
