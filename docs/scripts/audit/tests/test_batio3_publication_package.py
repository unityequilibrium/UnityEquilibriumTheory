"""Packaging invariants, not new scientific calculations or physical tests."""
from copy import deepcopy
import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / "docs/scripts/audit/prepare_batio3_publication.py"
spec = importlib.util.spec_from_file_location("batio3_publication", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PublicationTests(unittest.TestCase):
    def test_only_four_provenance_fields_excluded_from_payload(self):
        a = {"metric": {"value": "1/3"}, **{k: "old" for k in m.META}}
        b = {"metric": {"value": "1/3"}, **{k: "new" for k in m.META}}
        self.assertEqual(m.digest(m.payload(a)), m.digest(m.payload(b)))
        b["metric"]["value"] = "1/2"
        self.assertNotEqual(m.digest(m.payload(a)), m.digest(m.payload(b)))

    def test_unlisted_metadata_is_not_silently_ignored(self):
        self.assertNotEqual(m.digest(m.payload({"generated_at": "a"})),
                            m.digest(m.payload({"generated_at": "b"})))

    def test_contract_identity_rebind_does_not_change_model(self):
        a = {"model": {"coupling": "g"}, "identities": ["working"]}
        b = deepcopy(a)
        b["identities"] = ["public-git-blob"]
        self.assertEqual(m.digest(m.semantics(a)), m.digest(m.semantics(b)))
        b["model"]["coupling"] = "g2"
        self.assertNotEqual(m.digest(m.semantics(a)), m.digest(m.semantics(b)))

    def test_unknown_review_cannot_disappear_as_metadata(self):
        a = {"review": {"status": "INCOMPLETE"}, "identities": []}
        b = {"review": {"status": "PASSED"}, "identities": []}
        self.assertNotEqual(m.digest(m.semantics(a)), m.digest(m.semantics(b)))

    def test_boundary_reference_hash_not_boundary_outcome_is_metadata(self):
        a = {"observation": {"system_partition": {"boundary_change": {
            "baseline_contract_sha256": "old", "outcome": "DIFFERENT"}}}}
        b = deepcopy(a)
        b["observation"]["system_partition"]["boundary_change"]["baseline_contract_sha256"] = "new"
        self.assertEqual(m.digest(m.semantics(a)), m.digest(m.semantics(b)))
        b["observation"]["system_partition"]["boundary_change"]["outcome"] = "EQUIVALENT"
        self.assertNotEqual(m.digest(m.semantics(a)), m.digest(m.semantics(b)))

    def test_text_normalization_and_binary_raw_hash(self):
        self.assertEqual(m.normalized_hash("a.md", b"a\r\nb\r"),
                         m.normalized_hash("a.md", b"a\nb\n"))
        self.assertNotEqual(m.normalized_hash("a.src", b"a\r\nb"),
                            m.normalized_hash("a.src", b"a\nb"))

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            m.target(ROOT, "../outside.json")

    def test_approval_not_implicitly_upgraded(self):
        with self.assertRaisesRegex(ValueError, "approval boundary"):
            m.verify_preservation(ROOT, {"approval": "PUSH_NOW"})

    def test_manifest_classifies_local_inputs_and_public_pins(self):
        data = m.load_json(ROOT / m.MANIFEST)
        self.assertEqual(len(data["historical_pins"]), 5)
        self.assertTrue(all(len(p["commit"]) == 40 for p in data["historical_pins"]))
        self.assertTrue(all(r["source_origin"] in {"COMMITTED_SOURCE", "LOCAL_WORKING_DEPENDENCY"}
                            for r in data["files"]))

    def test_publication_check_needs_no_local_research_commit(self):
        data = m.load_json(ROOT / m.MANIFEST)
        data["local_source_commit"] = "0" * 40
        result = m.check(ROOT, data)
        self.assertFalse(result["old_scientific_producers_executed"])
        self.assertFalse(result["push_performed"])

    def test_check_mode_is_read_only(self):
        data = m.load_json(ROOT / m.MANIFEST)
        paths = [ROOT / r["path"] for r in data["files"]]
        paths += [ROOT / m.MANIFEST, ROOT / m.SCRIPT, ROOT / m.TESTS]
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(["--check"]), 0)
        after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
