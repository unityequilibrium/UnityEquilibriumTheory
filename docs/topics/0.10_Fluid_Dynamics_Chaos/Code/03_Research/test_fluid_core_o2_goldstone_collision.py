"""Microscopic-channel normalization, source identity and transport non-admission."""
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
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Goldstone_Collision.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_goldstone_collision_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_goldstone_collision_audit.json"


class GoldstoneCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))

    def test_fresh_source_channel_preserves_physical_non_admission(self):
        a=self.fresh
        for f,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),h,f)
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(a["source_AST_definition_hashes"],self.published["source_AST_definition_hashes"])
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(a["status"],"PASS_LEADING_GOLDSTONE_CHANNEL_ONLY")
        self.assertTrue(all(v["pass"] for v in a["checks"].values()))
        for key in ("finite_temperature_rate_emitted","thermalization_derived","collision_spectral_gap_established",
          "physical_frequency_window_established","collective_two_fluid_sound_damping_assigned",
          "whole_Core_runtime_executed","live_Phi_executed","complete_nonlinear_operator_derived",
          "physical_UET_operator_admitted","physical_HeII_state_assigned","physical_prediction_executed",
          "physical_J04_executed","physical_J05_executed","physical_J06_executed",
          "claim_promotion","dependency_unlock","thresholds_relaxed","parameters_fitted"):
            self.assertIs(a[key],False,key)

    def test_on_shell_rates_match_leading_k5_and_NR_pole_normalization(self):
        a=self.fresh
        for row in a["state_results"]:
            coefficient=row["parameters"]["leading_occupation_coefficient"]
            for r in row["rates"]:
                final=r["final"]
                self.assertGreater(final["occupation_rate"],0)
                self.assertLess(abs(final["rate_over_k5"]/coefficient-1),.001)
                self.assertLess(final["max_on_shell_error"],1e-11)
                self.assertEqual(2*final["pole_amplitude_damping"],final["occupation_rate"])
                self.assertLess(final["rate_over_energy"],.001)
                self.assertTrue(-1<final["cosine_interval"][0]<=final["cosine_interval"][1]<1)
        nr=a["nonrelativistic_coefficient_controls"]
        self.assertGreater(nr[0]["relative_error"],nr[1]["relative_error"])
        self.assertGreater(nr[1]["relative_error"],nr[2]["relative_error"])
        self.assertLess(nr[-1]["relative_error"],.001)
        self.assertTrue(a["checks"]["factor_two_error_detected"]["pass"])
        self.assertTrue(a["checks"]["full_four_momentum_soft_vertex"]["pass"])

    def test_balanced_triads_conserve_energy_momentum_but_have_extra_nulls(self):
        a=self.fresh;g=a["disconnected_triad_diagnostic"]
        B=np.array(g["incidence"]);C=np.array(g["normalized_operator"])
        self.assertLess(np.min(np.linalg.eigvalsh(C)),1e-10)
        self.assertGreaterEqual(np.min(np.linalg.eigvalsh(C)),-1e-10)
        self.assertGreater(g["null_mode_count"],4)
        self.assertFalse(g["connected_continuum"])
        self.assertIsNone(g["transport_time"])
        self.assertGreater(np.linalg.norm(B@np.ones(B.shape[1])),0)
        for row in a["state_results"]:
            for r in row["rates"]:
                for t in r["triads"]:
                    self.assertLess(t["balance"]["relative_error"],1e-11)
                    self.assertGreater(t["balance"]["off_shell_relative_defect"],1e-4)

    def test_first_failure_is_retained_and_unsupported_thermalization_fails_closed(self):
        a=self.fresh;record=a["first_execution_record"]
        old=json.loads((ROOT/record["artifact"]).read_text(encoding="utf-8"))
        archive=ROOT/record["verifier_source_archive"]
        script_key=SCRIPT.relative_to(ROOT).as_posix()
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(),old["input_hashes"][script_key])
        self.assertEqual(old["passing_check_count"],153)
        self.assertEqual(old["locked_verification"],a["locked_verification"])
        self.assertEqual(sum(not x["pass"] for x in old["checks"].values()),6)
        for prev,new in zip(old["state_results"],a["state_results"]):
            for r0,r1 in zip(prev["rates"],new["rates"]):
                self.assertLess(abs(r0["final"]["occupation_rate"]/r1["final"]["occupation_rate"]-1),1e-12)
        for mutation in ("thermalization","empty_couplings","physical_operator"):
            p=json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation=="thermalization":p["admission"]["thermalization"]=True
            elif mutation=="empty_couplings":p["exploratory_couplings"]=[]
            else:p["admission"]["physical_two_fluid_operator"]=True
            with tempfile.TemporaryDirectory() as folder:
                source=Path(folder)/"bad.json";output=Path(folder)/"result.json"
                source.write_text(json.dumps(p),encoding="utf-8")
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                                   cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,run.stdout+run.stderr)
                result=json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(result["status"],"LEADING_GOLDSTONE_CHANNEL_FAIL")
                self.assertIs(result["thermalization_derived"],False)
                self.assertIs(result["physical_UET_operator_admitted"],False)
                self.assertIs(result["dependency_unlock"],False)
                if mutation=="empty_couplings":
                    self.assertFalse(result["leading_tree_cubic_channel_checked"])


if __name__=="__main__":
    unittest.main()
