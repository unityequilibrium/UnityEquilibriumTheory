"""Evidence guards: reject invalid complex preview and distinguish diffusion from sound."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=next(p for p in Path(__file__).resolve().parents if (p/"docs/core").is_dir())
TOPIC=ROOT/"docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT=TOPIC/"Code/03_Research/Research_Fluid_Second_Sound_Mode_Eligibility.py"
RESULT=TOPIC/"Result/artifacts/fluid_second_sound_mode_eligibility_audit.json"


class SecondSoundModeEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published=json.loads(RESULT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/"audit.json"
            run=subprocess.run([sys.executable,"-W","error",str(SCRIPT),"--output",str(output)],
                               cwd=ROOT,capture_output=True,text=True)
            if run.returncode:
                raise AssertionError(run.stdout+run.stderr)
            cls.fresh=json.loads(output.read_text())

    def test_source_fresh_bounded_exclusion_and_invalid_preview_retention(self):
        for path,expected in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)
        self.assertEqual(self.fresh,self.published)
        self.assertTrue(self.fresh["pass"])
        self.assertEqual(self.fresh["candidate_disposition"],
                         "NOT_ELIGIBLE_AS_HYDRODYNAMIC_SECOND_SOUND_OPERATOR_UNDER_DECLARED_ASSUMPTIONS")
        for key in ("claim_promotion","dependency_unlock",
                    "physical_uet_operator_admitted","physical_prediction_executed"):
            self.assertIs(self.fresh[key],False)
        revision=self.fresh["harness_revision"]
        self.assertIs(revision["thresholds_relaxed"],False)
        self.assertIs(revision["initial_nominal_pass_accepted"],False)
        preview=json.loads((ROOT/revision["retained_diagnostic"]).read_text())
        self.assertEqual(preview["status"],"INVALID_COMPLEX_METRIC_PREVIEW_NOT_ACCEPTED")
        self.assertEqual(preview["original_payload"]["reference_check_count"],123)

    def test_long_wave_class_does_not_confuse_diffusion_advection_or_massless_wave(self):
        rows=self.fresh["wavenumber_records"]
        gap=min((v["real"]**2+v["imag"]**2)**.5
                for v in self.fresh["equilibrium"]["fast_roots_k0"])
        for row in rows:
            k=row["k"]
            ordered=sorted(row["scalar_modes"],
                           key=lambda v:v["real"]**2+v["imag"]**2)
            self.assertLess(abs(ordered[0]["imag"]),1e-12)
            self.assertLess(ordered[0]["real"],0)
            self.assertGreater(min((v["real"]**2+v["imag"]**2)**.5
                                   for v in ordered[1:]),gap/2)
            sound=row["reference_modes"]
            self.assertLess(sound[0]["imag"]*sound[1]["imag"],0)
            self.assertAlmostEqual(abs(sound[0]["imag"])/k,
                                   self.fresh["separate_two_fluid_reference"]["ideal_phase_speed"])
            self.assertAlmostEqual(row["apparent_bulk_advection_speed"],.37)
            self.assertGreater(row["massless_undamped_control_speed"],0)
        predicted=self.fresh["equilibrium"]["predicted_diffusive_coefficient"]
        self.assertLess(abs(rows[-1]["slow_coefficient"]-predicted),
                        abs(rows[0]["slow_coefficient"]-predicted))
        self.assertLess(abs(rows[-1]["slow_coefficient"]-predicted),1e-3)

    def test_imaginary_work_and_wrong_sign_instability_are_detectable(self):
        checks=self.fresh["checks"]
        self.assertLess(checks["complex_norm_pure_imaginary_control"]["metric"],1e-12)
        self.assertGreater(checks["imaginary_matrix_work_defect_detected"]["metric"],.5)
        for row in self.fresh["wavenumber_records"]:
            prefix="k="+str(row["k"])+"/"
            for suffix in ("wrong_counterflow_sign_work_detected",
                           "wrong_counterflow_sign_instability_detected"):
                item=checks[prefix+suffix]
                self.assertGreater(item["metric"],item["minimum"])
                self.assertTrue(item["pass"])
            self.assertLess(checks[prefix+"ideal_reference_positive_work_symmetrizer"]["metric"],1e-12)
            self.assertLess(checks[prefix+"diffusive_reference_work_loss"]["metric"],1e-12)


if __name__=="__main__":
    unittest.main()
