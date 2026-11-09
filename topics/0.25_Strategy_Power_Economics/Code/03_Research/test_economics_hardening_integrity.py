from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
TOPIC = HERE.parents[2]
REPO = HERE.parents[5]
COMMON_PATH = HERE.parent / "economic_hardening_common.py"

spec = importlib.util.spec_from_file_location("economic_hardening_common", COMMON_PATH)
common = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(common)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


class EconomicsHardeningIntegrityTests(unittest.TestCase):
    def test_bootstrap_is_seeded_and_uses_replacement(self) -> None:
        deltas = [0.1, -0.2, 0.4, -0.1, 0.3, -0.5]
        first = common.moving_block_bootstrap_interval(deltas, block_size=2, draws=200, seed=17)
        second = common.moving_block_bootstrap_interval(deltas, block_size=2, draws=200, seed=17)
        self.assertEqual(first, second)
        self.assertEqual(first["sampling"], "circular_moving_blocks_with_replacement")
        self.assertEqual(first["seed"], 17)

    def test_machine_registries_are_utf8_without_bom(self) -> None:
        paths = [
            TOPIC / "Data/03_Research/uet_economics_research_register.json",
            TOPIC / "Data/03_Research/uet_economics_warn_gate_registry.json",
        ]
        for path in paths:
            self.assertFalse(path.read_bytes().startswith(b"\xef\xbb\xbf"), path)
    def test_retired_identity_and_twenty_gate_contract(self) -> None:
        formula = load_json(TOPIC / "Data/03_Research/uet_us_economics_formula_gate.json")
        warn = load_json(TOPIC / "Data/03_Research/uet_economics_warn_gate_registry.json")
        retired = [item for item in formula["formulae"] if item["formula_id"] == "BOOK-HEURISTIC-001"]
        self.assertEqual(len(retired), 1)
        self.assertEqual(retired[0]["status"], "RETIRED_AS_IDENTITY")
        self.assertEqual(len(warn["gates"]), 20)
        self.assertEqual(len({item["gate_id"] for item in warn["gates"]}), 20)

    def test_global_panel_is_blocked_without_complete_cases(self) -> None:
        gate = load_json(TOPIC / "Result/artifacts/0_25_global_panel_integrity_gate.json")
        self.assertEqual(gate["status"], "BLOCKED")
        self.assertEqual(gate["complete_case_rows"], 0)
        self.assertEqual(gate["controller"], "GLOBAL_COMPLETE_CASE_PANEL_UNAVAILABLE")
        for item in gate["invalidated_downstream_artifacts"]:
            artifact = load_json(REPO / item["path"])
            self.assertEqual(artifact["status"], "INVALID_SUPERSEDED")

    def test_alignment_gate_preserves_claim_boundary(self) -> None:
        gate = load_json(TOPIC / "Result/artifacts/0_25_book_topic_alignment_gate.json")
        self.assertEqual(gate["status"], "PASS_WITH_BOUNDARY")
        self.assertTrue(gate["checks"]["twenty_warn_gates_declared"])
        self.assertTrue(gate["checks"]["retired_identity_is_explicit"])
        self.assertEqual(gate["controlling_blocker"], "SYSTEMATIC_LITERATURE_REVIEW_INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
