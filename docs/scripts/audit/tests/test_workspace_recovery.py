"""Regression checks for immutable recovery inventory and historical JSON."""
import base64
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorkspaceRecoveryTests(unittest.TestCase):
    def test_inventory_covers_checkpoint_without_promoting_ambiguous_rows(self):
        audit = load("recovery_inventory", "docs/scripts/recovery/build_workspace_recovery_inventory.py")
        data = json.loads(audit.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(len(data["records"]), 467)
        self.assertEqual(len({x["checkpoint_path"] for x in data["records"]}), 467)
        self.assertTrue(all(x["source_blob"] and x["source_commit"] == audit.CHECKPOINT for x in data["records"]))
        self.assertTrue(all(x["blocker"] and x["next_action"] for x in data["records"] if x["disposition"] == "blocked"))
        self.assertEqual(sum(x["disposition"] == "superseded" for x in data["records"]), 5)
        self.assertTrue(all(x["canonical_baseline_blob"] for x in data["records"] if x["disposition"] == "superseded"))

    def test_invalid_historical_outputs_round_trip_and_stay_invalid(self):
        audit = load("invalid_historical_json", "docs/scripts/recovery/repair_invalid_historical_json.py")
        for path, expected in audit.PATHS.items():
            with self.subTest(path=path):
                obj = json.loads(audit.envelope(path, expected))
                self.assertEqual(obj["status"], "INVALID_HISTORICAL_OUTPUT")
                self.assertEqual(hashlib.sha256(base64.b64decode(obj["original_bytes_base64"])).hexdigest(), expected)
                with self.assertRaises(json.JSONDecodeError):
                    json.loads(base64.b64decode(obj["original_bytes_base64"]))

    def test_wrong_history_identity_is_rejected(self):
        audit = load("invalid_historical_json_mismatch", "docs/scripts/recovery/repair_invalid_historical_json.py")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            audit.envelope(next(iter(audit.PATHS)), "0" * 64)

    def test_pages_math_only_changes_disposable_copy(self):
        pages = load("pages_math", "docs/scripts/recovery/prepare_pages_math.py")
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            originals = {}
            for name in pages.COUNTS:
                source = ROOT / "docs" / name
                target = dest / name
                target.parent.mkdir(parents=True, exist_ok=True)
                originals[name] = source.read_bytes()
                target.write_bytes(originals[name])
            pages.prepare(dest)
            for name, expected in pages.COUNTS.items():
                result = (dest / name).read_bytes()
                self.assertEqual(result.count(b"<!-- {% raw %} -->"), expected)
                restored = result.replace(b"<!-- {% raw %} -->\n", b"")
                restored = restored.replace(b"\n<!-- {% endraw %} -->", b"")
                self.assertEqual(restored, originals[name])
                self.assertEqual((ROOT / "docs" / name).read_bytes(), originals[name])
        with self.assertRaises(ValueError):
            pages.prepare(ROOT / "docs")

    def test_gr_subresult_does_not_promote_blocked_program(self):
        from docs.scripts.audit import audit_uet_gr_causal_nonclosed

        verification, formula, _, program = audit_uet_gr_causal_nonclosed.build_artifacts()
        self.assertEqual(verification["status"], "PASS")
        self.assertEqual(formula["status"], "WARN")
        self.assertEqual(program["status"], "BLOCKED")
        self.assertEqual(program["claim_promotion"], "BLOCKED")
        spec = ROOT / "docs/core/01_contracts/UET_GR_NONCLOSED_RESEARCH_SPEC.md"
        spec_hash = hashlib.sha256(spec.read_bytes()).hexdigest()
        self.assertIn(spec_hash, verification["source_hashes"].values())


if __name__ == "__main__":
    unittest.main()
