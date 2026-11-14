"""Guards for thermodynamic path ambiguity and forbidden two-fluid shortcuts."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Two_Fluid_EOS_Reference.py"
RESULT=TOPIC/"Result/artifacts/fluid_two_fluid_eos_reference_audit.json"


class TwoFluidEOSReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(RESULT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/"audit.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(out)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(out.read_text(encoding="utf-8"))

    def test_source_fresh_standard_reference_preserves_physical_boundary(self):
        for path,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),h,path)
        self.assertEqual(self.fresh["input_hashes"],self.published["input_hashes"])
        self.assertEqual(self.fresh["thresholds"],self.published["thresholds"])
        self.assertEqual(self.fresh["status"],
                         "PASS_STANDARD_TWO_FLUID_AND_PATH_UNDERDETERMINATION_REFERENCE_ONLY")
        self.assertTrue(all(v["pass"] for v in self.fresh["checks"].values()))
        for key in ("claim_promotion","dependency_unlock","physical_uet_operator_admitted",
                    "physical_prediction_executed","numerical_HeII_data_ingested"):
            self.assertIs(self.fresh[key],False)
        inputs=json.loads((TOPIC/"Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json").read_text(encoding="utf-8"))
        self.assertTrue(all(row["value"] is None and row["uncertainty"] is None
                            for row in inputs["required_inputs"]))

    def test_finite_expansion_forbids_silent_zero_mass_flow_or_single_entropy_velocity(self):
        a=self.fresh;th=a["thermodynamics"]
        self.assertGreater(th["c_p"],th["c_v"])
        self.assertGreater(a["finite_expansion_clamped_momentum_coefficient"],.5)
        self.assertGreater(abs(th["speed_squared"][0]-th["slow_reduced_estimate_squared"]),1e-3)
        zero=a["zero_expansion_control"]["thermodynamics"]
        self.assertAlmostEqual(zero["c_p"],zero["c_v"])
        self.assertAlmostEqual(zero["speed_squared"][0],zero["v_entropy_squared"])
        for key in ("common_velocity_entropy_error_work_detected",
                    "common_velocity_entropy_error_local_flux_detected",
                    "superfluid_sign_error_work_detected",
                    "superfluid_sign_error_instability_detected"):
            row=a["checks"][key]
            self.assertGreater(row["metric"],row["minimum"])
        for row in a["mode_records"]:
            negative=[v for v in row["modes"] if v["imag"]<0]
            positive=[v for v in row["modes"] if v["imag"]>0]
            self.assertEqual(len(negative),2)
            self.assertEqual(len(positive),2)

    def test_same_local_saturation_path_does_not_identify_fixed_pressure_EOS(self):
        first,second=self.fresh["path_EOS_witnesses"]
        for key in ("rho_prime","s_prime","T_prime","p_prime"):
            self.assertAlmostEqual(first["common_path"][key],second["common_path"][key])
        self.assertNotEqual(first["properties"]["kappa_T"],second["properties"]["kappa_T"])
        self.assertGreater(abs(first["thermodynamics"]["speed_squared"][0]-
                               second["thermodynamics"]["speed_squared"][0]),1e-3)
        for row in (first,second):
            self.assertGreater(row["properties"]["c_p"],1.5)
            self.assertGreater(row["properties"]["c_p"],row["properties"]["c_v"])
            self.assertGreater(abs(row["omitted_heat_correction_temperature_tangent"]-1),.01)
            self.assertAlmostEqual(row["common_path"]["T_prime"],1)
            self.assertAlmostEqual(row["common_path"]["p_prime"],.3)


if __name__=="__main__":
    unittest.main()
