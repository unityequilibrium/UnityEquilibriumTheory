"""Flow curvature independence, real source identities and fail-closed state boundaries."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Flow_Hessian.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_flow_hessian_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_flow_hessian_audit.json"


class FlowHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text(encoding="utf-8"))

    def test_source_fresh_independent_curvature_pass_does_not_admit_material_operator(self):
        a=self.fresh
        for p,h in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),h,p)
        self.assertEqual(a["input_hashes"],self.published["input_hashes"])
        self.assertEqual(a["source_AST_definition_hashes"],self.published["source_AST_definition_hashes"])
        self.assertEqual(a["locked_verification"],self.published["locked_verification"])
        self.assertEqual(a["check_count"],98)
        self.assertTrue(all(q["pass"] for q in a["checks"].values()))
        self.assertEqual(a["status"],"PASS_APPROXIMATE_FLOW_HESSIAN_REFERENCE_ONLY")
        self.assertTrue(a["scalar_correspondence_gate"]["target_pass"])
        previous=json.loads((TOPIC/"Result/artifacts/fluid_core_o2_common_flow_composition_audit.json").read_text(encoding="utf-8"))
        self.assertFalse(previous["condensed_composition_gate"]["target_pass"])
        self.assertEqual(len(previous["condensed_composition_gate"]["failed_points"]),3)
        for key in ("whole_Core_runtime_executed","phase_stiffness_fitted_to_enthalpy","thermal_gap_equation_solved",
            "full_two_fluid_stress_entrainment_derived","physical_normal_density_assigned","physical_HeII_state_assigned",
            "physical_UET_operator_admitted","physical_prediction_executed","physical_J04_executed",
            "physical_J05_executed","physical_J06_executed","claim_promotion","dependency_unlock","thresholds_relaxed"):
            self.assertIs(a[key],False,key)
        initial=a["initial_execution_record"]
        self.assertEqual(initial["check_count"],96)
        self.assertEqual(hashlib.sha256((ROOT/initial["verifier_source_archive"]).read_bytes()).hexdigest(),
                         initial["original_verifier_sha256"])

    def test_phase_correction_has_no_enthalpy_or_static_proxy_dependency(self):
        spec=importlib.util.spec_from_file_location("flow_hessian_independence_probe",SCRIPT)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        p=json.loads(CONTRACT.read_text(encoding="utf-8"))
        base=module.load_adapter(ROOT/p["source_adapter"])
        original=json.loads((ROOT/p["source_contract"]).read_text(encoding="utf-8"))
        ns,_=base.source_functions(original)
        args=(p,base,ns,.08,1.28,128,70)
        expected=module.implicit_phase(*args)
        def forbidden(*args,**kwargs):raise AssertionError("phase curvature must not read target state/proxy")
        base.state=forbidden
        ns["transverse"]["formal_transverse_quasiparticle_response"]=forbidden
        ns["EOS"]["quasiparticle_pressure"]=forbidden
        actual=module.implicit_phase(*args)
        self.assertEqual(actual,expected)
        self.assertLess(actual["thermal_phase_correction"],0)

    def test_two_independent_curvatures_explain_declared_shortcut_defect_and_detect_missing_terms(self):
        a=self.fresh;r=a["locked_verification"]
        self.assertEqual(len(a["state_results"]),3)
        for row in a["state_results"]:
            T=row["point"]["T"];label=str(T)
            implicit=row["implicit_final"]
            self.assertLess(implicit["thermal_phase_correction"],0)
            self.assertGreater(implicit["flow_phase_stiffness"],0)
            self.assertLess(row["correction_relative_difference"],r["flow_correction_relative_tolerance"])
            self.assertLess(row["composition_target"]["relative_residual"],r["composition_relative_tolerance"])
            self.assertGreater(row["source_zero_flow"]["relative_composition_residual"],r["composition_relative_tolerance"])
            # Signed thermal correction removes the actual old signed composition defect.
            old=row["source_zero_flow"]
            self.assertAlmostEqual(old["composition_residual"]+1.28**2*implicit["thermal_phase_correction"],0,places=9)
            for key in ("pure_Doppler_correction_error_detected","omitted_occupation_curvature_detected","tree_only_mismatch_retained"):
                self.assertTrue(a["checks"][label+"/"+key]["pass"])
            for row2 in row["flow_step_sweep"]:
                self.assertLess(row2["determinant_relative"],r["determinant_relative_tolerance"])
                self.assertLess(row2["pressure_parity_relative"],r["pressure_parity_relative_tolerance"])

    def test_empty_states_and_false_material_admission_fail_closed(self):
        for mutation in ("empty_states","false_admission"):
            p=json.loads(CONTRACT.read_text(encoding="utf-8"))
            if mutation=="empty_states":p["states"]=[]
            else:p["admission"]["physical_normal_density"]=True
            with tempfile.TemporaryDirectory() as folder:
                source=Path(folder)/"bad.json";output=Path(folder)/"result.json"
                source.write_text(json.dumps(p),encoding="utf-8")
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--contract-json",str(source),"--output",str(output)],
                    cwd=ROOT,capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,run.stdout+run.stderr)
                a=json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(a["status"],"FLOW_HESSIAN_REFERENCE_FAIL")
                if mutation=="empty_states":
                    self.assertFalse(a["scalar_correspondence_gate"]["target_pass"])
                    self.assertFalse(a["checks"]["states_match_original_condensed_points"]["pass"])
                else:self.assertFalse(a["checks"]["boundary/physical_normal_density"]["pass"])
                self.assertIs(a["physical_normal_density_assigned"],False)
                self.assertIs(a["physical_UET_operator_admitted"],False)
                self.assertIs(a["dependency_unlock"],False)


if __name__=="__main__":
    unittest.main()
