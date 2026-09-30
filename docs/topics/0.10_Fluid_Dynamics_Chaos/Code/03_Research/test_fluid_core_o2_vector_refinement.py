"""Stable vector recurrences, independent coordinates and honest refinement boundaries."""
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
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Vector_Refinement.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_vector_refinement_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_vector_refinement_audit.json"


class VectorRefinementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))

    def test_source_fresh_diagnostic_does_not_admit_physical_transport(self):
        a=self.fresh
        for f,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h,f)
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(a["status"],"PASS_STABLE_VECTOR_DIAGNOSTIC_ONLY")
        self.assertTrue(all(v["pass"] for v in a["checks"].values()))
        for key in ("physical_heat_current_matched","full_interacting_collision_completed",
          "continuum_spectral_gap_established","thermalization_derived","physical_frequency_window_established",
          "collective_sound_damping_assigned","physical_UET_operator_admitted","physical_HeII_state_assigned",
          "physical_J04_executed","physical_J05_executed","physical_J06_executed","whole_Core_runtime_executed",
          "live_Phi_executed","claim_promotion","dependency_unlock","thresholds_relaxed","parameters_fitted"):
            self.assertIs(a[key],False,key)

    def test_same_span_and_shared_event_invariants_survive_stable_coordinates(self):
        a=self.fresh
        for bank in a["basis_banks"]:
            G=np.array(bank["G"]);Q=np.array(bank["Q"])
            self.assertTrue(np.all(np.linalg.eigvalsh(G)>0))
            self.assertLess(np.linalg.cond(G)-1,1e-8)
            self.assertLess(np.linalg.norm(Q[:,0])/np.linalg.norm(Q),1e-8)
            self.assertLess(bank["source_momentum_error"],1e-8)
            self.assertLess(bank["recurrence_evaluation_error"],1e-8)
            self.assertGreater(bank["minimum_triangle_factor"],0)
            for key in ("collision_kernel_changed","interpolation_used",
                        "posterior_collision_projection_used","basis_coefficients_fitted_to_response"):
                self.assertIs(bank[key],False,key)
        for row in a["state_results"]:
            self.assertTrue(all(v<1e-8 for v in row["same_span_correspondence"].values()))
            for family in row["families"].values():
                R=[v["R"] for v in family["basis_sweep"]]
                self.assertTrue(np.all(np.diff(R)>=-1e-8*max(R)))
                final=family["final"]
                self.assertEqual(final["full_spectrum"]["nulls"],1)
                self.assertEqual(final["full_spectrum"]["positive_resolved"],final["N"]-1)
                self.assertEqual(final["full_spectrum"]["negative_resolved"],0)
                self.assertLess(final["DC_spectral_error"],1e-8)
                self.assertTrue(all(v["spectral_error"]<1e-8 for v in final["frequency_response"]))
                self.assertIsNone(final["physical_time"])
            self.assertGreaterEqual(row["families"]["SOFT"]["final"]["R"],
                                    row["families"]["EVEN"]["final"]["R"]*(1-1e-8))

    def test_soft_plateau_cannot_hide_even_or_cross_family_failed_targets(self):
        a=self.fresh
        self.assertFalse(a["refinement_gate"]["target_pass"])
        self.assertFalse(a["refinement_gate"]["physical_admission"])
        self.assertEqual(a["controlling_measured_blocker"],
                         "stable_vector_basis_cross_family_or_cutoff_current_response_not_converged")
        for published,fresh in zip(self.published["state_results"],a["state_results"]):
            targets=fresh["measured_targets"]
            for kind in ("order","cutoff","basis","source"):
                self.assertTrue(targets["SOFT/"+kind]["pass"])
            self.assertTrue(targets["EVEN/order"]["pass"])
            self.assertTrue(targets["EVEN/source"]["pass"])
            for kind in ("EVEN/cutoff","EVEN/basis","cross_family"):
                self.assertFalse(targets[kind]["pass"])
            self.assertGreater(targets["cross_family"]["relative_change"],.15)
            self.assertLess(targets["cross_family"]["relative_change"],.25)
            for key,target in targets.items():
                self.assertEqual(target["threshold"],.01)
                self.assertEqual(target["pass"],published["measured_targets"][key]["pass"])
            for name in ("EVEN","SOFT"):
                old=published["families"][name]["final"];new=fresh["families"][name]["final"]
                for key in ("R","tau_basis"):
                    self.assertLess(abs(new[key]/old[key]-1),1e-8)

    def test_false_admission_empty_states_or_relaxed_refinement_fail_closed(self):
        for mutation in ("physical_current","empty_temperatures","relaxed_target"):
            p=json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation=="physical_current":p["admission"]["physical_heat_current"]=True
            elif mutation=="empty_temperatures":p["temperatures"]=[]
            else:p["verification"]["refinement_relative_tolerance"]=.3
            with tempfile.TemporaryDirectory() as folder:
                source=Path(folder)/"bad.json";output=Path(folder)/"result.json"
                source.write_text(json.dumps(p),encoding="utf-8")
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                                   cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,run.stdout+run.stderr)
                result=json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(result["status"],"STABLE_VECTOR_DIAGNOSTIC_FAIL")
                for key in ("physical_heat_current_matched","physical_UET_operator_admitted","dependency_unlock"):
                    self.assertIs(result[key],False)
                if mutation=="empty_temperatures":
                    self.assertFalse(result["stable_shared_vector_basis_evaluated"])
                    self.assertFalse(result["refinement_gate"]["target_pass"])


if __name__=="__main__":
    unittest.main()

