"""Source-derived local tensor, ideal-mode work and explicit thermalization boundary."""
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
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Ideal_Modes.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_ideal_modes_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_ideal_modes_audit.json"


class LocalIdealModesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))

    def test_source_fresh_local_reference_keeps_microphysics_and_material_admission_open(self):
        a=self.fresh
        for f,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h,f)
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(a["source_AST_definition_hashes"],self.published["source_AST_definition_hashes"])
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(a["status"],"PASS_LOCAL_IDEAL_REFERENCE_ONLY")
        self.assertEqual(a["check_count"],171)
        self.assertTrue(all(q["pass"] for q in a["checks"].values()))
        self.assertTrue(a["assumptions"]["ideal_local_equilibrium_entropy_conservation"])
        for key in ("microscopic_entropy_conservation_derived","thermalization_derived",
                    "physical_frequency_window_established","complete_nonlinear_operator_derived",
                    "whole_Core_runtime_executed","live_Phi_executed","physical_UET_operator_admitted",
                    "physical_HeII_state_assigned","physical_normal_density_assigned","physical_prediction_executed",
                    "physical_J04_executed","physical_J05_executed","physical_J06_executed",
                    "claim_promotion","dependency_unlock","thresholds_relaxed","mode_coefficients_fitted"):
            self.assertIs(a[key],False,key)

    def test_source_tensor_variation_and_entrainment_do_not_relabel_residual_pressure_sector(self):
        a=self.fresh;r=a["locked_verification"]
        for row in a["state_results"]:
            ref=row["reference"];label=str(row["point"]["T"])
            self.assertLess(ref["thermal_charge_sector_derivative"],0)
            self.assertGreater(ref["ideal_normal_charge_coefficient"],0)
            self.assertGreater(ref["ideal_normal_inertia"],0)
            self.assertAlmostEqual(ref["ideal_normal_inertia"],
                ref["mu"]*ref["ideal_normal_charge_coefficient"]+ref["T"]*ref["s"],places=12)
            for probe in row["source_metric_derivative_controls"]:
                self.assertLess(probe["current_relative_error"],r["source_metric_relative_tolerance"])
                self.assertLess(probe["stress_relative_error"],r["source_metric_relative_tolerance"])
            self.assertTrue(a["checks"][label+"/entrainment_inverse"]["pass"])
            self.assertTrue(a["checks"][label+"/two_current_stress"]["pass"])
            self.assertTrue(a["checks"][label+"/omit_Ts_inertia_error_detected"]["pass"])
            E=np.asarray(row["entrainment_matrix"])
            self.assertTrue(np.all(np.linalg.eigvalsh(E)>0))
            self.assertTrue(np.all(np.isfinite(row["local_thermal_conjugate"])))

    def test_independent_operator_coordinates_work_and_two_pairs_are_eligible_under_ideal_assumption(self):
        a=self.fresh;tol=a["locked_verification"]["algebra_covariance_work_pole_tolerance"]
        self.assertEqual(len(a["state_results"]),3)
        for row in a["state_results"]:
            A=np.asarray(row["linear_operator"]);S=np.asarray(row["energy_Hessian"])
            M=np.asarray(row["generalized_M"]);L=np.asarray(row["generalized_L"])
            self.assertTrue(np.all(np.linalg.eigvalsh(S)>0))
            self.assertLess(np.linalg.norm(S@A-A.T@S)/np.linalg.norm(S@A),tol)
            values=np.sort_complex(np.linalg.eigvals(A))
            alternate=np.sort_complex(np.linalg.eigvals(np.linalg.solve(M,L)))
            self.assertLess(np.max(abs(values-alternate)),tol)
            self.assertLess(np.max(abs(values.imag)),tol)
            self.assertGreater(values[2].real,0)
            self.assertGreater(values[3].real,values[2].real)
            self.assertLess(values[3].real,1)
            self.assertLess(np.max(abs(values.real+values.real[::-1])),tol)
            self.assertTrue(all(q["relative_residual"]<tol for q in row["local_work_controls"]))
            neg=row["negative_controls"]
            self.assertGreater(neg["entropy_velocity_work_defect"],1e-7)
            self.assertGreater(neg["wrong_Josephson_growth"],1e-7)
            self.assertGreater(neg["omit_Ts_inertia_relative_defect"],1e-7)
            for mode in row["modes"]:
                self.assertGreater(abs(mode["entropy_current_real"]),0)
                self.assertGreater(mode["relative_velocity_magnitude"],0)
                self.assertLess(mode["eigen_residual"],tol)

    def test_unsupported_thermalization_empty_states_and_false_operator_admission_fail_closed(self):
        for mutation in ("thermalization","empty_states","physical_operator"):
            p=json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation=="thermalization":p["assumptions"]["thermalization_derived"]=True
            elif mutation=="empty_states":p["states"]=[]
            else:p["admission"]["physical_two_fluid_operator"]=True
            with tempfile.TemporaryDirectory() as folder:
                source=Path(folder)/"bad.json";output=Path(folder)/"result.json"
                source.write_text(json.dumps(p),encoding="utf-8")
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                    cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,run.stdout+run.stderr)
                a=json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(a["status"],"LOCAL_IDEAL_REFERENCE_FAIL")
                self.assertIs(a["thermalization_derived"],False)
                self.assertIs(a["physical_frequency_window_established"],False)
                self.assertIs(a["physical_UET_operator_admitted"],False)
                self.assertIs(a["dependency_unlock"],False)
                if mutation=="empty_states":
                    self.assertFalse(a["checks"]["three_locked_states"]["pass"])
                    self.assertFalse(a["conditional_ideal_acoustic_pairs_checked"])


if __name__=="__main__":
    unittest.main()
