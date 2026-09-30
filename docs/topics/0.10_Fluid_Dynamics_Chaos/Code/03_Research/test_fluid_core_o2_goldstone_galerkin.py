"""Finite Galerkin invariants, current frame, honest convergence and non-admission."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Goldstone_Galerkin.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_goldstone_galerkin_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_goldstone_galerkin_audit.json"


class GoldstoneGalerkinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))

    def test_source_fresh_selected_kernel_does_not_admit_transport_or_thermalization(self):
        a=self.fresh
        for f,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h,f)
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(a["source_AST_definition_hashes"],self.published["source_AST_definition_hashes"])
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(a["status"],"PASS_FINITE_GALERKIN_DIAGNOSTIC_ONLY")
        self.assertEqual(a["check_count"],454)
        self.assertTrue(all(v["pass"] for v in a["checks"].values()))
        for key in ("physical_heat_current_matched","full_interacting_collision_completed",
          "continuum_spectral_gap_established","thermalization_derived","physical_frequency_window_established",
          "collective_sound_damping_assigned","physical_UET_operator_admitted","physical_HeII_state_assigned",
          "physical_J04_executed","physical_J05_executed","physical_J06_executed","whole_Core_runtime_executed",
          "live_Phi_executed","claim_promotion","dependency_unlock","thresholds_relaxed","parameters_fitted"):
            self.assertIs(a[key],False,key)

    def test_shared_basis_conserves_four_modes_before_source_constraint(self):
        a=self.fresh
        for row in a["state_results"]:
            r=row["final"]
            self.assertEqual(r["resolved_total_nulls"],4)
            for name in ("scalar","vector"):
                G=np.asarray(r["Gram_"+name]);Q=np.asarray(r["collision_"+name])
                self.assertTrue(np.all(np.linalg.eigvalsh(G)>0))
                self.assertLess(np.linalg.norm(Q[:,0])/np.linalg.norm(Q),1e-8)
                self.assertEqual(r[name+"_spectrum"]["null_count"],1)
                self.assertEqual(r[name+"_spectrum"]["positive_count"],r["feature_order"]-1)
                self.assertEqual(r[name+"_spectrum"]["negative_resolved_count"],0)
            self.assertGreater(r["parent_loss_only_momentum_defect"],1e-4)
            self.assertGreater(r["phonon_number_form"],0)
            self.assertFalse(r["posterior_collision_projection_used"])
            self.assertFalse(r["interpolation_used"])
            self.assertFalse(r["artificial_diagonal_width_used"])
            self.assertIsNone(r["physical_thermalization_time"])

    def test_source_frame_and_resolvents_pass_but_cutoff_and_basis_targets_remain_open(self):
        a=self.fresh
        self.assertFalse(a["refinement_gate"]["target_pass"])
        self.assertEqual(a["refinement_gate"]["status"],"MEASURED_REFINEMENT_TARGETS_OPEN")
        for row in a["state_results"]:
            r=row["final"];targets=row["measured_targets"]
            self.assertGreater(r["curvature_projected_source_norm"],0)
            self.assertLess(r["linear_current_projected_relative_squared_norm"],1e-8)
            self.assertLess(r["source_momentum_constraint_error"],1e-8)
            self.assertGreater(r["unprojected_current_momentum_coefficient"],1e-4)
            self.assertTrue(targets["order"]["pass"])
            self.assertTrue(targets["source_representation"]["pass"])
            self.assertFalse(targets["cutoff"]["pass"])
            self.assertFalse(targets["basis"]["pass"])
            self.assertGreater(targets["basis"]["relative_change"],.18)
            for target in targets.values():
                self.assertEqual(target["threshold"],.01)
            R=np.array([q["real"] for q in r["frequency_response"]])
            self.assertTrue(np.all(np.diff(R)<0))
            self.assertTrue(all(q["imag"]>=0 for q in r["frequency_response"]))
            self.assertTrue(all(q["independent_spectral_error"]<1e-8 for q in r["frequency_response"]))
            self.assertLess(r["source_representation_relative_squared_error"],.01)
            self.assertGreater(r["source_weighted_basis_time"],0)

    def test_archived_first_results_and_false_admission_empty_or_relaxed_targets_fail_closed(self):
        a=self.fresh;record=a["first_execution_record"]
        old=json.loads((ROOT/record["artifact"]).read_text(encoding="utf-8"))
        archive=ROOT/record["verifier_source_archive"]
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),old["input_hashes"][SCRIPT.relative_to(ROOT).as_posix()])
        self.assertEqual(old["locked_verification"],a["locked_verification"])
        self.assertEqual(old["refinement_gate"],self.published["refinement_gate"])
        for prev,new in zip(old["state_results"],self.published["state_results"]):
            self.assertEqual(prev["final"]["current_response"],new["final"]["current_response"])
            self.assertEqual(prev["final"]["source_weighted_basis_time"],new["final"]["source_weighted_basis_time"])
        # Archived/published same-runtime values stay exact. Independent runtime
        # reruns compare numerical correspondence rather than platform bits.
        for published,fresh in zip(self.published["state_results"],a["state_results"]):
            for key in ("current_response","source_weighted_basis_time"):
                self.assertLess(abs(fresh["final"][key]/published["final"][key]-1),1e-8)
            for key in published["measured_targets"]:
                self.assertEqual(fresh["measured_targets"][key]["pass"],published["measured_targets"][key]["pass"])
        for mutation in ("physical_current","empty_temperatures","relaxed_basis_target"):
            p=json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation=="physical_current":p["admission"]["physical_heat_current"]=True
            elif mutation=="empty_temperatures":p["temperatures"]=[]
            else:p["verification"]["basis_response_refinement_relative_tolerance"]=.3
            with tempfile.TemporaryDirectory() as folder:
                source=Path(folder)/"bad.json";output=Path(folder)/"result.json"
                source.write_text(json.dumps(p),encoding="utf-8")
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                                   cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,run.stdout+run.stderr)
                result=json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(result["status"],"FINITE_GALERKIN_DIAGNOSTIC_FAIL")
                self.assertIs(result["physical_heat_current_matched"],False)
                self.assertIs(result["physical_UET_operator_admitted"],False)
                self.assertIs(result["dependency_unlock"],False)
                if mutation=="empty_temperatures":
                    self.assertFalse(result["shared_scalar_vector_Galerkin_basis_evaluated"])
                    self.assertFalse(result["refinement_gate"]["target_pass"])


if __name__=="__main__":
    unittest.main()
