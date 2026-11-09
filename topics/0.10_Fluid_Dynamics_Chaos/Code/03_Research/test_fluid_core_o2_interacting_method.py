"""Normal source reuse cannot admit a condensed interacting or material state."""
import copy
from fractions import Fraction
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
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Core_O2_Interacting_Method.py"
CONTRACT=TOPIC/"Data/03_Research/fluid_core_o2_interacting_method_contract.json"
ARTIFACT=TOPIC/"Result/artifacts/fluid_core_o2_interacting_method_audit.json"


class InteractingMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.published=json.loads(ARTIFACT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"fresh.json";runs=[]
            for _ in range(2):
                run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                                   cwd=ROOT,capture_output=True,text=True)
                if run.returncode:raise AssertionError(run.stdout+run.stderr)
                runs.append(output.read_bytes())
            if runs[0]!=runs[1]:raise AssertionError("fresh same-runtime outputs differ")
            cls.fresh=json.loads(runs[0])
        spec=importlib.util.spec_from_file_location("interacting_method_regression",SCRIPT)
        cls.driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.driver)

    def test_fresh_original_sources_and_unpromoted_method_matrix(self):
        a=self.fresh
        self.assertEqual(a["status"],self.driver.PASS)
        self.assertEqual((a["check_count"],a["passing_check_count"]),(156,156))
        for field in ("input_hashes","source_AST_definition_hashes","locked_verification","conditional_algebra"):
            self.assertEqual(a[field],self.published[field])
        self.assertEqual(list(a["checks"]),list(self.published["checks"]))
        for path,h in a["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),h)
        self.assertEqual(set(a["source_AST_definition_hashes"]),set(self.p["core_sources"]))
        self.assertTrue(a["normal_branch_and_conditional_algebra_supported"])
        self.assertEqual(set(a["method_gate"].values()),{"NOT_STARTED"})
        self.assertFalse(any(a["admission"].values()))
        for field in ("full_condensed_interacting_state_computed","full_Noether_Ward_completed",
                      "physical_J04_executed","physical_J05_executed","physical_J06_executed",
                      "physical_heat_current_matched","physical_material_frame_admitted",
                      "formal_verification","external_math_review","whole_Core_runtime_executed",
                      "useful_relative_error_certified","claim_promotion","dependency_unlock",
                      "parameters_fitted","thresholds_relaxed"):
            self.assertIs(a[field],False,field)

    def test_selected_normal_rejections_are_not_condensed_no_go_and_normal_control_is_separate(self):
        a=self.fresh
        self.assertEqual(len(a["normal_branch_probes"]),12)
        self.assertEqual(a["normal_branch_probes"],self.published["normal_branch_probes"])
        messages={"thermal":"no self-consistent Hartree solution in the normal branch",
                  "renormalized":"no renormalized Hartree solution in the normal branch"}
        for v in a["normal_branch_probes"]:
            self.assertTrue(v["rejected"]);self.assertEqual(v["error_type"],"ValueError")
            self.assertEqual(v["message"],messages[v["method"]])
            self.assertIn(v["T"],(.002,.004));self.assertEqual(v["mu"],1.28)
            self.assertIn(v["order"],(64,128,256))
        self.assertEqual(len(a["normal_controls"]),6)
        for v,old in zip(a["normal_controls"],self.published["normal_controls"]):
            self.assertEqual((v["temperature"],v["chemical_potential"]),(.2,.3))
            self.assertGreater(v["dressed_mass_sq"],.3**2)
            self.assertLessEqual(abs(v["gap_residual"]),1e-8)
            field="pressure_stationarity_residual" if v["method"]=="thermal" else "functional_stationarity_residual"
            self.assertLessEqual(abs(v[field]),1e-8)
            self.assertLessEqual(self.driver.relative(v["energy_density"],
                -v["pressure"]+.2*v["entropy_density"]+.3*v["charge_density"]),1e-8)
            self.assertEqual(v["momentum_cutoff"],60.)
            self.assertFalse(v["physical_kubo_coefficient_included"]);self.assertFalse(v["physical_si_mapping_included"])
            for field in ("dressed_mass_sq","pressure","charge_density","entropy_density","energy_density"):
                self.assertTrue(math.isclose(v[field],old[field],rel_tol=1e-8,abs_tol=0),field)
        for key,c in a["checks"].items():
            if "last_order_refinement" in key:self.assertLessEqual(c["value"],.01)

    def test_exact_independent_residuals_show_stationarity_goldstone_tradeoff_and_units(self):
        f=Fraction;mu=f(128,100);mass=f(1);coupling=f(1,100);plus=f(1,20)
        for minus in (f(-1,100),f(0),f(1,100)):
            v,r=self.driver.witness(mu,mass,coupling,plus,minus)
            g,s=self.driver.witness(mu,mass,coupling,plus,minus,True)
            self.assertEqual([r[n] for n in ("R_rho","R_Y","R_D")],[0,0,0])
            self.assertEqual(r["R_G"],-2*coupling*minus)
            self.assertEqual([s[n] for n in ("R_rho","R_Y","R_G")],[0,0,0])
            self.assertEqual(s["R_D"],-coupling*minus)
            self.assertEqual(r["determinant_zero"]==0,minus==0)
            # Independently vary all residual state inputs; the identity must
            # also hold without either witness substitution.
            off=dict(x=f(19,8),Y=f(7,4),D=f(5,11))
            o=self.driver.residuals(mu,mass,coupling,**off,plus=plus,minus=minus)
            self.assertEqual(o["R_G"],o["R_rho"]-2*o["R_D"]-2*coupling*minus)
            self.assertNotEqual(o["R_G"],o["R_rho"]-o["R_D"]-2*coupling*minus)
            scale=f(3)
            b=self.driver.residuals(scale*mu,scale**2*mass,coupling,
                                   **{k:scale**2*x for k,x in off.items()},
                                   plus=scale**2*plus,minus=scale**2*minus)
            for field,power in (("R_rho",2),("R_Y",2),("R_D",2),("R_G",2),("determinant_zero",4)):
                self.assertEqual(b[field],scale**power*o[field])
        self.assertEqual(self.fresh["unit_powers"],{"residuals":2,"determinant_zero":4})

    def test_changed_method_admission_threshold_branch_or_stale_source_fail_before_computation(self):
        mutations=[]
        for field in ("condensed_interacting_state","full_Noether_Ward","physical_J04","physical_heat_current","formal_verification"):
            p=copy.deepcopy(self.p);p["admission"][field]=True;mutations.append(p)
        p=copy.deepcopy(self.p);p["method_gate"]["Goldstone_source_Ward"]="PASS";mutations.append(p)
        p=copy.deepcopy(self.p);p["verification"]["gap_absolute_tolerance"]=1e-6;mutations.append(p)
        p=copy.deepcopy(self.p);p["selected_states"][0]["mu"]=.3;mutations.append(p)
        p=copy.deepcopy(self.p);p["normal_control"]["T"]=.4;mutations.append(p)
        with tempfile.TemporaryDirectory(dir=ROOT,prefix=".interacting-test-") as folder:
            old=json.loads((ROOT/self.p["prior_density_artifact"]).read_text(encoding="utf-8"))
            old["input_hashes"][next(iter(old["input_hashes"]))]="0"*64
            path=Path(folder)/"stale.json";path.write_text(json.dumps(old),encoding="utf-8")
            p=copy.deepcopy(self.p);p["prior_density_artifact"]=path.relative_to(ROOT).as_posix();mutations.append(p)
            for p in mutations:
                a=self.driver.audit(p,CONTRACT)
                self.assertEqual(a["status"],self.driver.FAIL)
                self.assertEqual(a["normal_controls"],[]);self.assertEqual(a["normal_branch_probes"],[])
                self.assertEqual(a["conditional_algebra"],[])
                self.assertFalse(a["normal_branch_and_conditional_algebra_supported"])
                self.assertFalse(a["claim_promotion"]);self.assertFalse(a["dependency_unlock"])


if __name__=="__main__":unittest.main()
