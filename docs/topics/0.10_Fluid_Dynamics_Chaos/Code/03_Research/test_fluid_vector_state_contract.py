"""Regression checks for evidence freshness and negative-control sensitivity."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "docs/core").is_dir())
TOPIC = ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos"
SCRIPT = TOPIC / "Code/03_Research/Research_Fluid_Vector_State_Contract.py"
RESULT = TOPIC / "Result/artifacts/fluid_vector_state_contract_audit.json"


class VectorReferenceEvidenceTests(unittest.TestCase):
    def test_published_candidate_evidence_is_fresh_and_bounded(self):
        artifact = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["status"], "PASS_NORMALIZED_VECTOR_REFERENCE_IDENTITIES_ONLY")
        self.assertFalse(artifact["claim_promotion"])
        self.assertFalse(artifact["dependency_unlock"])
        self.assertFalse(artifact["physical_uet_operator_admitted"])
        for path, expected in artifact["input_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), expected, path)
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch)/"current.json"
            run = subprocess.run([sys.executable, str(SCRIPT), "--output", str(output)],
                                 cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
            fresh = json.loads(output.read_text())
        self.assertEqual(fresh["input_hashes"], artifact["input_hashes"])
        self.assertEqual(fresh["reference_check_count"], artifact["reference_check_count"])
        for row in fresh["grids"]:
            self.assertTrue(row["pass"])
            for name in ("missing_force_must_fail_ledger", "wrong_sign_must_fail_ledger",
                         "rate_substitution_must_fail_ledger", "initial_rest_is_not_frozen_parent_evolution"):
                self.assertTrue(row["checks"][name]["pass"], name)

    def test_insensitive_initial_control_cannot_produce_a_pass(self):
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch)/"initial.json"
            run = subprocess.run([sys.executable, str(SCRIPT), "--initial-control-diagnostic",
                                  "--output", str(output)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stdout+run.stderr)
            artifact = json.loads(output.read_text())
        self.assertEqual(artifact["status"], "FAIL_REFERENCE_AUDIT")
        self.assertEqual(artifact["thresholds"]["control_version"], 1)
        expected = {"total_work_control_sensitive", "missing_force_must_fail_ledger",
                    "wrong_sign_must_fail_ledger"}
        for row in artifact["grids"]:
            failed = {name for name, check in row["checks"].items() if not check["pass"]}
            self.assertEqual(failed, expected)
            self.assertTrue(row["checks"]["closed_energy_ledger"]["pass"])


if __name__ == "__main__":
    unittest.main()
