"""Behavioral enforcement tests and explicit synthetic observer controls."""
from __future__ import annotations
import copy
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "audit_calculation_completeness.py"
spec = importlib.util.spec_from_file_location("calculation_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ContractTests(unittest.TestCase):
    def setUp(self):
        # Keep temporary fixtures inside the writable checkout on desktop sandboxes.
        self.tmp = tempfile.TemporaryDirectory(prefix=".calculation_contract_test_", dir=audit.ROOT)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        schema = self.root / audit.SCHEMA
        schema.parent.mkdir(parents=True)
        schema.write_bytes((audit.ROOT / audit.SCHEMA).read_bytes())
        self.path = "docs/core/02_equations/example.py"
        file = self.root / self.path
        file.parent.mkdir(parents=True)
        file.write_text("# controlled model\n")
        item = dict(path=self.path, kind="working_file", role="code")
        item["sha256"] = audit.identity_hash(self.root, item)
        self.c = dict(schema_version="uet-calculation-contract-v1", contract_id="TEST", profile="FORMAL",
            review=dict(status="COMPLETE_FOR_SCOPE", reviewer="test", rationale="bounded algebra", coverage_evidence=[self.path]),
            question="Does the declared identity hold?",
            output=dict(quantity="identity", unit="1", domain="finite inputs", accuracy="exact", claim_intent="FORMAL_RESULT"),
            model=dict(formula_ids=["identity"], assumptions="finite", approximation="none", initial_boundary="algebraic",
                drive_environment="not relevant to identity", parameters="fixed"),
            data_policy=dict(uses_observations=False, calibration_ids=[], comparison_ids=[], independent_validation=False, holdout_policy="none"),
            observation={k:"not applicable to this formal identity" for k in ("source_state", "generated_trace", "carrier",
                "observer_state", "readout", "backaction", "frame", "time_convention", "product_level")},
            components=[dict(id=g, group=g, disposition="NOT_APPLICABLE", reason="bounded algebra has no apparatus", evidence=[])
                for g in sorted(audit.GROUPS)],
            error_budget={k:"exact formal scope" for k in ("numerical", "approximation", "measurement", "systematic", "omissions", "dependence", "acceptance")},
            identities=[item], entrypoints=[self.path], evidence=[self.path], claim_boundary="formal only", next_action="reuse unchanged evidence")
        self.c["observation"]["corrections"] = []
        self.c["error_budget"].update(unit="1", omission_limit=None)
        self.c["review"]["scope_sha256"] = audit.review_payload_hash(self.c)

    def errors(self):
        # Each mutated scenario is reviewed afresh, except the explicit stale-review test.
        self.c["review"]["scope_sha256"] = audit.review_payload_hash(self.c)
        return audit.validate_contract(self.c, self.root)["errors"]

    def test_changed_model_scope_invalidates_old_review(self):
        self.c["model"]["approximation"] = "a different approximation"
        r = audit.validate_contract(self.c, self.root)
        self.assertEqual(r["effective_status"], "STALE")
        self.assertTrue(any("scope/model/config" in e for e in r["errors"]))

    def save_contract(self):
        p = self.root / "docs/core/calculation_contracts/formal.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.c))

    def test_formal_instrument_exemption(self):
        self.assertEqual(self.errors(), [])

    def test_schema_changes_and_invented_evidence_do_not_silently_pass(self):
        self.assertTrue(audit.schema_errors("anything", {"maxLength": 2}))
        self.c["components"][0].update(disposition="MODELED", evidence=["missing-proof.json"])
        self.assertTrue(any("unidentified evidence" in e for e in self.errors()))

    def test_missing_field_and_duplicate_component(self):
        del self.c["model"]["parameters"]
        self.assertTrue(self.errors())
        self.c["model"]["parameters"] = "fixed"
        self.c["components"].append(copy.deepcopy(self.c["components"][0]))
        self.assertIn("duplicate component IDs", self.errors())

    def test_unknown_diagnostic_continues_but_complete_rejected(self):
        c = self.c["components"][0]
        c["disposition"] = "UNKNOWN"
        self.assertTrue(self.errors())
        c.update(owner="EVIDENCE", next_action="obtain calibration")
        self.c["review"]["status"] = "INCOMPLETE"
        self.assertEqual(self.errors(), [])
        self.assertEqual(audit.artifact_metadata(self.c, self.root)["contract_review_status"], "INCOMPLETE")

    def test_parent_gate_not_bypassed(self):
        self.c["profile"] = "PHYSICAL_COMPARISON"
        self.c["output"]["claim_intent"] = "PHYSICAL_ACCEPTANCE"
        self.assertTrue(self.errors())
        (self.root / "gate.json").write_text('{"status":"BLOCKED"}')
        item = dict(path="gate.json", kind="working_file", role="evidence")
        item["sha256"] = audit.identity_hash(self.root, item)
        self.c["identities"].append(item)
        self.c["error_budget"].update(omission_limit=0, acceptance_evidence="gate.json")
        self.c["physical_gates"] = [dict(path="gate.json", field="status", accepted=["PASS"])]
        self.assertTrue(any("physical gate blocks" in e for e in self.errors()))
        self.c["physical_gates"][0]["accepted"] = ["BLOCKED"]
        self.assertTrue(any("cannot be whitelisted" in e for e in self.errors()))

    def test_explicit_physical_acceptance_contract_can_pass_structural_review(self):
        self.c["profile"] = "PHYSICAL_COMPARISON"
        self.c["output"]["claim_intent"] = "PHYSICAL_ACCEPTANCE"
        self.c["data_policy"].update(uses_observations=True, comparison_ids=["independent-observed-row"])
        (self.root / "gate.json").write_text('{"status":"PASS"}')
        item = dict(path="gate.json", kind="working_file", role="evidence")
        item["sha256"] = audit.identity_hash(self.root, item)
        self.c["identities"].append(item)
        self.c["error_budget"].update(acceptance_limit=0.1, omission_limit=0.01, acceptance_evidence="gate.json")
        self.c["physical_gates"] = [dict(path="gate.json", field="status", accepted=["PASS"])]
        self.assertEqual(self.errors(), [])

    def test_stale_hash_and_line_endings(self):
        file = self.root / self.path
        file.write_bytes(b"# controlled model\r\n")
        self.assertEqual(self.errors(), [])
        file.write_bytes(b"# changed physics\n")
        self.assertEqual(audit.validate_contract(self.c, self.root)["effective_status"], "STALE")
        with self.assertRaises(ValueError): audit.artifact_metadata(self.c, self.root)

    def test_missing_git_identity_has_no_fallback(self):
        self.c["identities"][0].update(kind="git_blob", commit="a"*40)
        self.assertTrue(any("identity unavailable" in e for e in self.errors()))

    def test_unmerged_local_evidence_is_visible_gap_not_pass(self):
        self.c["identities"][0].update(kind="git_blob", commit="a"*40, availability="LOCAL_ONLY")
        self.c["review"]["status"] = "INCOMPLETE"
        r = audit.validate_contract(self.c, self.root)
        self.assertEqual(r["errors"], [])
        self.assertEqual(r["effective_status"], "INCOMPLETE")
        self.assertTrue(any("unavailable-local-evidence" in x for x in r["gaps"]))
        self.c["review"]["status"] = "COMPLETE_FOR_SCOPE"
        self.assertTrue(self.errors())

    def test_omission_bound_unit_and_total(self):
        c = self.c["components"][0]
        c.update(disposition="BOUNDED_OMISSION", evidence=[self.path], bound=0.03, unit="1", joint_group="joint")
        self.c["error_budget"]["omission_limit"] = 0.02
        self.assertTrue(any("omission budget" in e for e in self.errors()))
        self.c["error_budget"]["omission_limit"] = 0.04
        self.assertEqual(self.errors(), [])
        c["unit"] = "m"
        self.assertTrue(any("output unit" in e for e in self.errors()))

    def test_correlated_group_not_independent_quadrature(self):
        for c in self.c["components"][:2]:
            c.update(disposition="BOUNDED_OMISSION", evidence=[self.path], bound=0.03, unit="1", joint_group="joint")
        self.c["error_budget"]["omission_limit"] = 0.04
        self.assertEqual(self.errors(), [])
        self.c["components"][1]["bound"] = 0.02
        self.assertTrue(any("inconsistent joint" in e for e in self.errors()))

    def test_upstream_correction_not_reapplied(self):
        c = dict(id="doppler", state="APPLIED_UPSTREAM", evidence=self.path)
        self.c["observation"]["corrections"] = [c, {**c, "state":"APPLY_HERE"}]
        self.assertTrue(any("reapplied" in e for e in self.errors()))
        self.c["observation"]["corrections"] = [{**c, "state":"UNKNOWN"}]
        self.c["review"]["status"] = "INCOMPLETE"
        r = audit.validate_contract(self.c, self.root)
        self.assertEqual(r["errors"], [])
        self.assertIn("correction:doppler", r["gaps"])

    def test_unit_frame_transform_evidence(self):
        self.c["observation"].update(comparison_unit="m", comparison_frame="other")
        self.assertEqual(len(self.errors()), 2)
        self.c["observation"].update(unit_conversion_evidence=self.path, frame_transform_evidence=self.path)
        self.assertEqual(self.errors(), [])

    def test_calibration_reuse_and_profile_relabeling(self):
        self.c["data_policy"].update(uses_observations=True, independent_validation=True,
            calibration_ids=["same"], comparison_ids=["same"], independence_evidence=self.path)
        self.assertTrue(any("reused" in e for e in self.errors()))
        self.assertTrue(any("labeled" in e for e in self.errors()))

    def test_dissipation_not_full_state(self):
        self.c["observation"].update(trace_scope="dissipation_history", trace_used_as_complete_state=True)
        self.assertTrue(any("complete observable" in e for e in self.errors()))

    def test_changed_scientific_path_classification(self):
        (self.root / "docs/core/new.py").write_text("x=1")
        r = audit.build_report(self.root, ["docs/core/new.py", "docs/core/test_new.py"])
        self.assertEqual(len(r["errors"]), 1)

    def test_inventory_read_only_deterministic(self):
        self.save_contract()
        before = {str(p):p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        a, b = audit.build_report(self.root), audit.build_report(self.root)
        self.assertEqual(a, b)
        self.assertEqual(a["summary"]["contracts"], 1)
        self.assertEqual(before, {str(p):p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_new_result_exact_contract_metadata(self):
        self.save_contract()
        path = self.root / "docs/core/07_artifacts/verification/new.json"
        path.parent.mkdir(parents=True)
        path.write_text('{"contract_id":"TEST"}')
        rel = path.relative_to(self.root).as_posix()
        self.assertTrue(any("exact contract" in e for e in audit.build_report(self.root, [rel])["errors"]))
        path.write_text(json.dumps(audit.artifact_metadata(self.c, self.root)))
        self.assertEqual(audit.build_report(self.root, [rel])["errors"], [])
        # A pre-standard artifact is grandfathered only while unchanged.
        baseline = self.root / audit.BASELINE
        baseline.write_text(json.dumps(dict(routes=[], legacy_paths=[rel])))
        path.write_text('{"old_result":true}')
        self.assertTrue(any("exact contract" in e for e in audit.build_report(self.root, [rel])["errors"]))

    def test_path_escape_duplicate_json_nan(self):
        with self.assertRaises(ValueError): audit.repo_path(self.root, "../outside")
        p = self.root / "bad.json"
        for text in ('{"x":NaN}', '{"x":1,"x":2}'):
            p.write_text(text)
            with self.assertRaises(ValueError): audit.load_json(p)


class ObserverControls(unittest.TestCase):
    def test_velocity_raw_signal_and_frame_recovery(self):
        emitted = 100.0
        for beta in (-0.02, 0.0, 0.03):
            factor = math.sqrt((1-beta)/(1+beta))
            raw = emitted*factor
            self.assertAlmostEqual(raw/factor, emitted, places=12)
            if beta:
                self.assertNotEqual(raw, emitted)
                self.assertGreater(abs(raw/factor/factor-emitted), 0.1)

    def test_receiver_state_readout_and_coupled_energy(self):
        source, receiver, readings = 10.0, 0.0, []
        for _ in range(2):
            readings.append(2.0/(1+receiver))
            source -= 1.0
            receiver += 1.0
            self.assertEqual(source+receiver, 10.0)
        self.assertNotEqual(readings[0], readings[1])
        before = (source, receiver)
        metadata = dict(label="another observer name")
        self.assertTrue(metadata)
        self.assertEqual(before, (source, receiver))

    def test_reversible_observable_not_dissipation_trace(self):
        times = (0, math.pi/2, math.pi)
        records = [math.cos(t) for t in times]
        energy = [(math.cos(t)**2+math.sin(t)**2)/2 for t in times]
        self.assertEqual(energy, [0.5]*3)
        self.assertGreater(max(records)-min(records), 1)
        self.assertNotEqual(records, [0.0]*3)


if __name__ == "__main__": unittest.main()
