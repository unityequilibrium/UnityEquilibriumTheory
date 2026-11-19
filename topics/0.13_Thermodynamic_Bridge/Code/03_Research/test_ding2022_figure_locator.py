"""Software check: the Ding 2022 digitization reads the tracked figure.

Bookkeeping only (input locator and recorded hash), not a physics test.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ding2022_digitization", HERE / "Research_Ding2022_Figure_Digitization.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class DingFigureLocatorTests(unittest.TestCase):
    def test_figure_resolves_to_an_existing_file(self):
        self.assertTrue(m.RAW.is_file(), m.RAW)

    def test_figure_matches_the_recorded_input_hash(self):
        manifest = json.loads(m.MANIFEST_PATH.read_text(encoding="utf-8"))
        recorded = [a for a in manifest["input_assets"] if a["path"] == m.RAW_RELATIVE]
        self.assertEqual(len(recorded), 1)
        self.assertEqual(hashlib.sha256(m.RAW.read_bytes()).hexdigest(), recorded[0]["sha256"])

    def test_current_topic_copy_takes_precedence_only_when_present(self):
        current = m.TOPIC / m.RAW_RELATIVE
        self.assertEqual(m.RAW, current if current.is_file() else m.LEGACY_RAW)


if __name__ == "__main__":
    unittest.main()
