"""Regression guards for source freshness and hidden transport/momentum errors."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT = TOPIC / "Code/03_Research/Research_Fluid_Vector_Variational_Origin.py"
RESULT = TOPIC / "Result/artifacts/fluid_vector_variational_origin_audit.json"


class VariationalOriginEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.published = json.loads(RESULT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/"audit.json"
            run = subprocess.run([sys.executable,str(SCRIPT),"--output",str(output)],
                                 cwd=ROOT,capture_output=True,text=True)
            if run.returncode:
                raise AssertionError(run.stdout+run.stderr)
            cls.fresh = json.loads(output.read_text())

    def test_source_fresh_action_audit_preserves_admission_boundary(self):
        for path,expected in self.published["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)
        self.assertEqual(self.fresh["input_hashes"],self.published["input_hashes"])
        self.assertEqual(self.fresh["status"],"PASS_CONDITIONAL_VARIATIONAL_REFERENCE_ONLY")
        self.assertEqual(self.fresh["reference_check_count"],72)
        for key in ("claim_promotion","dependency_unlock","physical_uet_operator_admitted"):
            self.assertIs(self.fresh[key],False)
        for row in self.fresh["grids"]:
            self.assertTrue(row["pass"])
            self.assertTrue(row["checks"]["action_finite_difference_finest"]["pass"])
            self.assertTrue(row["checks"]["integrated_by_parts_first_variation"]["pass"])

    def test_global_work_cannot_hide_missing_local_transport(self):
        floor=self.fresh["thresholds"]["negative_control_floor"]
        for row in self.fresh["grids"]:
            # This omitted term integrates to zero, so an energy-only check
            # cannot test the local kinematic equation.
            self.assertLess(row["checks"]["Q_transport_work_is_periodic_gauge"]["metric"],1e-12)
            self.assertGreater(row["details"]["omitted_Q_transport_local_defect"],floor)
            self.assertGreater(abs(row["details"]["omitted_Phi_transport_variation_defect"]),floor)
            self.assertTrue(row["checks"]["omitted_material_Q_transport_breaks_local_chain"]["pass"])

    def test_canonical_momentum_cannot_be_silently_identified_as_mechanical(self):
        floor=self.fresh["thresholds"]["negative_control_floor"]
        for row in self.fresh["grids"]:
            details=row["details"]
            self.assertGreater(abs(details["canonical_momentum_defect"]),floor)
            finite=details["velocity_finite_differences"][-1]["derivative"]
            canonical=details["canonical_velocity_pairing"]
            mechanical=details["mechanical_only_pairing"]
            self.assertLess(abs(finite-canonical)/max(1,abs(canonical)),1e-7)
            self.assertGreater(abs(finite-mechanical),floor)
            self.assertTrue(row["checks"]["Hamiltonian_reference_energy_alignment"]["pass"])


if __name__=="__main__":
    unittest.main()
