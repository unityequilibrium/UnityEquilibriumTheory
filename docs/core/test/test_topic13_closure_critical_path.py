import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/artifacts/t13_closure_critical_path_audit.json"


class Topic13ClosureCriticalPathTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with ARTIFACT.open("r", encoding="utf-8") as handle:
            cls.payload = json.load(handle)

    def test_critical_path_is_machine_readable_and_conservative(self):
        payload = self.payload
        self.assertEqual(payload["schema_version"], "t13-closure-critical-path-v1")
        self.assertEqual(payload["major_result"]["closure_level"], "CLOSED_FOR_LANE")
        self.assertEqual(payload["critical_path"]["required_subresult_count"], 37)
        self.assertEqual(payload["critical_path"]["open_subresult_count"], 10)
        self.assertEqual(payload["critical_path"]["closed_for_lane"], 21)
        self.assertEqual(payload["critical_path"]["closed_as_no_go"], 6)
        self.assertEqual(payload["critical_path"]["closed_for_core"], 0)
        self.assertFalse(payload["critical_path"]["full_core_unlock"])
        self.assertFalse(payload["critical_path"]["claim_promotion"])

    def test_open_rows_preserve_complete_package_dependencies(self):
        payload = self.payload
        package_ids = {item["package_id"] for item in payload["input_packages"]}
        self.assertEqual(package_ids, {
            "T13_INPUT_DING_TTG_SOURCE",
            "T13_INPUT_BASE_PHI_SI_ALPHA_BETA",
            "T13_INPUT_PHYSICAL_TRANSPORT_MATCH",
        })
        self.assertEqual(len(payload["open_subresults"]), 10)
        self.assertTrue(all(
            item["required_input_packages"]
            and set(item["required_input_packages"]).issubset(package_ids)
            for item in payload["open_subresults"]
        ))
        heat_flux = next(item for item in payload["open_subresults"] if item["subresult_id"] == "physical_heat_flux_entropy_map")
        self.assertEqual(set(heat_flux["required_input_packages"]), package_ids)
        eos = next(item for item in payload["open_subresults"] if item["subresult_id"] == "physical_source_backed_eos")
        self.assertEqual(len(eos["required_input_packages"]), 2)
        self.assertTrue(all(not item["accepted_for_core"] for item in payload["input_packages"]))

    def test_replay_and_holdout_guards_are_explicit(self):
        payload = self.payload
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["holdout_integrity"]["holdout_accessed"])
        self.assertFalse(payload["holdout_integrity"]["target_fit_performed"])
        self.assertFalse(payload["critical_path"]["rerun_existing_gates_without_new_input"])
        self.assertTrue(payload["critical_path"]["external_state_change_required"])


if __name__ == "__main__":
    unittest.main()
