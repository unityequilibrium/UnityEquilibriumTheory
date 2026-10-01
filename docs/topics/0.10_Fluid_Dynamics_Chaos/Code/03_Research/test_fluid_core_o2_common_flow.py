"""Core source identity, conditional composition rejection and false-admission guards."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Common_Flow.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_common_flow_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_common_flow_composition_audit.json"


class CoreO2CommonFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:
                raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))

    def test_source_fresh_execution_pass_keeps_composition_failure_and_admission_boundary(self):
        for p,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
        a=self.fresh
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(a["AST_definition_hashes"],self.published["AST_definition_hashes"])
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(set(a["checks"]),set(self.published["checks"]))
        self.assertTrue(all(c["pass"] for c in a["checks"].values()))
        self.assertEqual(a["check_count"],69)
        self.assertEqual(a["status"],"PASS_SOURCE_COMPOSITION_DIAGNOSTIC_ONLY")
        self.assertEqual(a["condensed_composition_gate"]["status"],"FAIL_REQUIRED_COMMON_FLOW_IDENTITY")
        self.assertIs(a["condensed_composition_gate"]["target_pass"],False)
        self.assertEqual(len(a["condensed_composition_gate"]["failed_points"]),3)
        for key in ("whole_Core_runtime_executed","complete_flow_master_function_derived",
                    "phase_stiffness_repaired_to_force_identity","physical_HeII_state_assigned",
                    "physical_UET_operator_admitted","physical_prediction_executed",
                    "physical_J04_executed","physical_J05_executed","physical_J06_executed",
                    "claim_promotion","dependency_unlock"):
            self.assertIs(a[key],False)

    def test_normal_control_passes_but_condensed_defect_exceeds_observed_numerical_spread(self):
        a=self.fresh
        tol=a["locked_verification"]["composition_relative_tolerance"]
        refine=a["locked_verification"]["refinement_relative_tolerance"]
        for row in a["source_state_results"]:
            f=row["final"]
            for changes in row["component_refinement_changes"].values():
                self.assertLessEqual(max(changes.values()),refine)
            if row["point"]["branch"]=="normal":
                self.assertLess(f["relative_composition_residual"],tol)
                self.assertEqual(f["tree_phase_stiffness"],0)
                self.assertIs(row["composition_target"]["pass"],True)
            else:
                self.assertGreater(f["relative_composition_residual"],tol+row["observed_refinement_spread_relative"])
                self.assertIs(row["composition_target"]["pass"],False)
                self.assertIs(row["composition_target"]["exceeds_threshold_plus_observed_spread"],True)
                self.assertGreater(f["tree_phase_stiffness"],0)
        # The script must not contain or output a stiffness replacement fitted to w.
        self.assertNotIn("repaired_phase_stiffness",a)

    def test_zero_temperature_phase_EOS_and_spectrum_bridge_has_distinct_inertia_units(self):
        a=self.fresh
        last=a["tree_Goldstone_control"][-1]
        self.assertAlmostEqual(last["source_E_over_k_squared"],last["analytic_tree_sound_squared"],places=9)
        self.assertAlmostEqual(last["analytic_tree_sound_squared"],.6384/3.9152,places=12)
        self.assertTrue(a["checks"]["tree_phase_charge_inertia"]["pass"])
        self.assertTrue(a["checks"]["stiffness_without_mu_squared_error_detected"]["pass"])
        self.assertTrue(a["checks"]["omit_entropy_in_normal_inertia_detected"]["pass"])
        self.assertTrue(a["checks"]["consistent_two_fluid_common_boost_positive_control"]["pass"])

    def test_false_physical_admission_fails_diagnostic_instead_of_unlocking(self):
        p=json.loads(CONTRACT.read_text(encoding="utf-8"))
        p["admission"]["physical_UET_operator"]=True
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/"corrupt.json"
            output=Path(folder)/"result.json"
            source.write_text(json.dumps(p),encoding="utf-8")
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(run.returncode,0)
            a=json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(a["status"],"SOURCE_COMPOSITION_DIAGNOSTIC_FAIL")
            self.assertIs(a["checks"]["boundary/physical_UET_operator"]["pass"],False)
            self.assertIs(a["physical_UET_operator_admitted"],False)
            self.assertIs(a["dependency_unlock"],False)


if __name__=="__main__":
    unittest.main()
