"""Identity and non-promotion checks for the four historical Topic 10 waves."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load("topic10_historical_contracts", "docs/scripts/recovery/build_topic10_historical_contracts.py")
audit = load("topic10_contract_audit", "docs/scripts/audit/audit_calculation_completeness.py")


class Topic10HistoricalContractTests(unittest.TestCase):
    def test_generated_contracts_match_sources_and_remain_incomplete(self):
        for wave in generator.WAVES:
            with self.subTest(wave=wave["name"]):
                path = generator.OUT / ("historical_" + wave["name"] + ".json")
                stored = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(stored, generator.make_contract(wave))
                result = audit.validate_contract(stored, ROOT)
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["effective_status"], "INCOMPLETE")
                self.assertEqual(stored["output"]["claim_intent"], "DIAGNOSTIC")
                self.assertTrue(any(c["id"] == "physical_correspondence" and c["disposition"] == "UNKNOWN"
                                    for c in stored["components"]))

    def test_changed_source_identity_is_rejected(self):
        wave = generator.WAVES[0]
        target = ROOT / generator.TOPIC / "Code/03_Research" / wave["code"]
        read = Path.read_bytes

        def changed(path):
            data = read(path)
            return data + b"\n# altered test input\n" if path.resolve() == target.resolve() else data

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "input hash mismatch"):
                generator.make_contract(wave)

    def test_changed_origin_artifact_is_rejected(self):
        with patch.object(generator, "git", return_value=b"not the original artifact"):
            with self.assertRaisesRegex(ValueError, "differs from its originating commit"):
                generator.make_contract(generator.WAVES[0])

    def test_unreachable_origin_history_is_rejected(self):
        with patch.object(generator, "git", side_effect=subprocess.CalledProcessError(1, "git")):
            with self.assertRaises(subprocess.CalledProcessError):
                generator.make_contract(generator.WAVES[0])

    def test_all_historical_inputs_are_bound_and_physical_claims_stay_blocked(self):
        all_inputs = set()
        for wave in generator.WAVES:
            with self.subTest(wave=wave["name"]):
                path = ROOT / generator.TOPIC / "Result/artifacts" / wave["result"]
                data = json.loads(path.read_text(encoding="utf-8"))
                contract = generator.make_contract(wave)
                recorded = {p.replace("\\", "/") for p in data["input_hashes"]}
                identities = {i["path"] for i in contract["identities"] if i["kind"] == "working_file"}
                self.assertTrue(recorded <= identities)
                all_inputs.update(recorded)
                self.assertIs(data["claim_promotion"], False)
                self.assertIs(data["dependency_unlock"], False)
                self.assertTrue(data["admission"])
                self.assertTrue(all(value is False for value in data["admission"].values()))
        self.assertEqual(len(all_inputs), 123)

    def test_original_registry_and_results_remain_byte_identical(self):
        count = 0
        for wave in generator.WAVES:
            paths = [generator.TOPIC + "Result/artifacts/" + wave["result"]]
            if wave["name"] == "gapless_functional":
                paths.append(generator.REGISTRY)
            for path in paths:
                with self.subTest(path=path):
                    self.assertEqual((ROOT / path).read_bytes(), generator.git("show", f"{wave['commit']}:{path}"))
                    count += 1
        self.assertEqual(count, 5)


if __name__ == "__main__":
    unittest.main()
