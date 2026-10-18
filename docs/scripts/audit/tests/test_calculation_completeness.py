"""Behavioral enforcement tests and explicit synthetic observer controls."""
from __future__ import annotations
import copy
import ast
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

    def partition(self):
        for row in self.c["components"]:
            if row["group"] in {"system_state", "propagation", "detector"}:
                row.update(disposition="MODELED", evidence=[self.path])
        self.c["components"].append(dict(id="backreaction", group="detector",
            disposition="NOT_APPLICABLE", reason="No feedback in this synthetic protocol", evidence=[]))
        self.c["observation"]["system_partition"] = dict(
            boundary="A/B model and separate receiver D; not all internal states are observed",
            systems=[dict(id=s, role="DETECTOR" if s == "D" else "SOURCE", state="declared state")
                     for s in ("A", "B", "D")],
            couplings=[dict(id="ab", source="A", target="B", kind="INTERNAL", component_id="system_state", map="declared coupling"),
                       dict(id="bd", source="B", target="D", kind="DETECTION", component_id="propagation", map="declared detection"),
                       *[dict(id="back_"+s, source="D", target=s, kind="BACKACTION", component_id="backreaction", map="absent by scoped model definition") for s in ("A", "B")]],
            observables=[dict(id="reading", detector_id="D", target_systems=["B"], quantity="selected response",
                              readout_map="readout from receiver state", component_id="detector")])
        return self.c["observation"]["system_partition"]

    def test_partition_selective_detection_without_source_feedback(self):
        g = self.partition()
        g["systems"].append(dict(id="hidden", role="AUXILIARY", state="unobserved internal state"))
        self.assertEqual(self.errors(), [])

    def relational_partition(self):
        g = self.c["observation"].get("system_partition") or self.partition()
        g.update(role_mode="RELATIONAL", accounting_component_id="system_state")
        for system in g["systems"]:
            system.pop("role")
            system["state_accounting"] = dict(kind="INDEPENDENT",
                state_ids=[system["id"]+".state"], owner_ids=[],
                rule="Each declared state and its energy contribution counted once")
        g["observables"][0].update(backaction_targets=["A", "B"],
            backaction_scope_reason="A/B jointly generate this receiver input; assess both")
        return g

    def test_relational_receiver_can_be_another_relationships_source(self):
        g = self.relational_partition()
        g["systems"].append(dict(id="E", state="second receiver",
            state_accounting=dict(kind="INDEPENDENT", state_ids=["E.state"], owner_ids=[], rule="own receiver storage")))
        g["couplings"] += [dict(id="de", source="D", target="E", kind="DETECTION", component_id="propagation", map="D supplies E"),
            dict(id="ed", source="E", target="D", kind="BACKACTION", component_id="backreaction", map="assessed absent in synthetic scope")]
        g["observables"].append(dict(id="second_reading", detector_id="E", target_systems=["D"],
            quantity="D state", readout_map="read E", component_id="detector",
            backaction_targets=["D"], backaction_scope_reason="D is the prepared system for this separate observation; no A/B claim"))
        self.assertEqual(self.errors(), [])

    def test_relational_nested_aggregate_is_not_an_extra_independent_state(self):
        g = self.relational_partition()
        g["systems"].append(dict(id="AB", state="joint description of A/B", categories=["coupled", "thermal"],
            state_accounting=dict(kind="AGGREGATE", state_ids=[], owner_ids=["A", "B"], rule="same A/B storage, never additive")))
        for s in g["systems"][:2]:
            s["parent_id"] = "AB"
        self.assertEqual(self.errors(), [])
        g["systems"][-1]["state_accounting"]["state_ids"] = ["extra_energy"]
        self.assertTrue(any("not new independent" in e for e in self.errors()))

    def test_relational_duplicate_independent_state_is_rejected(self):
        g = self.relational_partition()
        g["systems"][1]["state_accounting"]["state_ids"] = ["A.state"]
        self.assertTrue(any("duplicate independent state" in e for e in self.errors()))

    def test_relational_containment_cycle_and_unaccounted_child_rejected(self):
        g = self.relational_partition()
        for sid, parent in (("AB", "ALL"), ("ALL", "AB")):
            g["systems"].append(dict(id=sid, parent_id=parent, state="same subsystem view",
                state_accounting=dict(kind="AGGREGATE", state_ids=[], owner_ids=["A"], rule="no duplicate storage")))
        g["systems"][1]["parent_id"] = "AB"
        self.assertTrue(any("cyclic subsystem" in e for e in self.errors()))
        self.assertTrue(any("omits child" in e for e in self.errors()))

    def test_relational_view_requires_real_state_owners(self):
        g = self.relational_partition()
        g["systems"].append(dict(id="view", state="computed view",
            state_accounting=dict(kind="VIEW", state_ids=[], owner_ids=["absent"], rule="derived statistic")))
        self.assertTrue(any("must be an independent" in e for e in self.errors()))

    def test_relational_mode_is_explicit_and_no_fixed_role_is_silently_reused(self):
        g = self.relational_partition()
        g.pop("role_mode")
        self.assertTrue(any("legacy system needs role" in e for e in self.errors()))
        g["role_mode"] = "RELATIONAL"
        g["systems"][0]["role"] = "SOURCE"
        self.assertTrue(any("not system.role" in e for e in self.errors()))

    def test_relational_categories_do_not_waive_detection_or_backaction(self):
        g = self.relational_partition()
        g["systems"][1]["categories"] = ["external"]
        g["couplings"] = [e for e in g["couplings"] if e["kind"] != "DETECTION" and e["id"] != "back_B"]
        self.assertTrue(any("no declared detection path" in e for e in self.errors()))
        self.assertTrue(any("missing backaction assessment D->B" in e for e in self.errors()))
        g["observables"][0]["backaction_targets"] = ["A"]
        self.assertTrue(any("omits an observed target" in e for e in self.errors()))

    def test_relational_unknown_accounting_is_a_gap_not_complete(self):
        self.relational_partition()
        row = next(c for c in self.c["components"] if c["id"] == "system_state")
        row.update(disposition="UNKNOWN", owner="reviewer", next_action="justify state/energy accounting")
        self.c["review"]["status"] = "INCOMPLETE"
        self.assertIn("system_state", audit.validate_contract(self.c, self.root)["gaps"])
        self.c["review"]["status"] = "COMPLETE_FOR_SCOPE"
        self.assertTrue(any("unresolved" in e for e in self.errors()))

    def boundary_change(self):
        baseline = copy.deepcopy(self.c)
        path = "baseline.json"
        (self.root / path).write_text(json.dumps(baseline), encoding="utf-8")
        identity = dict(path=path, kind="working_file", role="evidence")
        identity["sha256"] = audit.identity_hash(self.root, identity)
        self.c["identities"].append(identity)
        g = self.relational_partition()
        g["boundary_change"] = dict(baseline_identity=path, baseline_contract_id=baseline["contract_id"],
            baseline_contract_sha256=audit.contract_hash(baseline), component_id="system_state",
            outcome="EQUIVALENT", explanation="same state ownership under a relabeling; formal example only")
        return g

    def test_boundary_change_checks_baseline_identity_and_mapping_evidence(self):
        g = self.boundary_change()
        self.assertEqual(self.errors(), [])
        g["boundary_change"]["baseline_contract_sha256"] = "0"*64
        self.assertTrue(any("baseline contract ID/hash mismatch" in e for e in self.errors()))
        g["boundary_change"].update(component_id="backreaction")
        self.assertTrue(any("boundary equivalence needs" in e for e in self.errors()))

    def test_boundary_change_invalidates_old_scope_review(self):
        self.relational_partition()
        self.c["review"]["scope_sha256"] = audit.review_payload_hash(self.c)
        self.c["observation"]["system_partition"]["boundary"] = "new time window and output accuracy"
        self.assertTrue(any("scope/model/config" in e for e in audit.validate_contract(self.c, self.root)["errors"]))

    def test_partition_requires_explicit_backaction_assessment_not_reciprocity(self):
        g = self.partition()
        g["couplings"] = [e for e in g["couplings"] if e["id"] != "back_A"]
        self.assertTrue(any("backaction assessment" in e for e in self.errors()))

    def test_partition_receiver_and_observable_are_distinct(self):
        g = self.partition()
        g["observables"][0]["id"] = "D"
        self.assertTrue(any("must differ" in e for e in self.errors()))
        g["observables"][0].update(id="reading", detector_id="A")
        self.assertTrue(any("not a detector" in e for e in self.errors()))

    def test_partition_cannot_observe_an_unconnected_or_omitted_channel(self):
        g = self.partition()
        component = next(c for c in self.c["components"] if c["id"] == "propagation")
        component.update(disposition="BOUNDED_OMISSION", bound=0.0, unit="1", joint_group="omitted_signal")
        self.c["error_budget"]["omission_limit"] = 0.0
        self.assertTrue(any("no declared detection path" in e for e in self.errors()))
        component.update(disposition="MODELED")
        g["couplings"] = [e for e in g["couplings"] if e["kind"] != "DETECTION"]
        self.assertTrue(any("no declared detection path" in e for e in self.errors()))

    def test_changed_nonformal_contract_needs_partition(self):
        self.c["profile"] = "SYNTHETIC"
        self.c["review"]["status"] = "INCOMPLETE"
        self.save_contract()
        path = "docs/core/calculation_contracts/formal.json"
        report = audit.build_report(self.root, [path])
        self.assertTrue(any("requires observation.system_partition" in e for e in report["errors"]))
        self.partition()
        self.save_contract()
        self.assertTrue(any("RELATIONAL role_mode" in e for e in audit.build_report(self.root, [path])["errors"]))
        self.relational_partition()
        self.save_contract()
        self.assertEqual(audit.build_report(self.root, [path])["errors"], [])

    def test_declared_source_can_be_unobserved(self):
        g = self.partition()
        g["systems"].append(dict(id="U", role="SOURCE", state="unobserved source state"))
        g["couplings"].append(dict(id="back_U", source="D", target="U", kind="BACKACTION",
            component_id="backreaction", map="no route in the declared synthetic model"))
        self.assertEqual(self.errors(), [])

    def test_partition_rejects_missing_references_and_duplicates(self):
        g = self.partition()
        g["systems"].append(copy.deepcopy(g["systems"][0]))
        g["couplings"][0].update(target="missing", component_id="missing")
        self.assertTrue(any("duplicate system" in e for e in self.errors()))
        self.assertTrue(any("unknown coupling" in e for e in self.errors()))

    def test_partition_unknown_backaction_remains_diagnostic_gap(self):
        self.partition()
        self.c["components"][-1].update(disposition="UNKNOWN", owner="reviewer", next_action="bound receiver feedback")
        self.c["review"]["status"] = "INCOMPLETE"
        r = audit.validate_contract(self.c, self.root)
        self.assertEqual(r["errors"], [])
        self.assertIn("backreaction", r["gaps"])

    def test_partition_formal_no_detector_exemption(self):
        self.c["observation"]["system_partition"] = dict(boundary="pure algebra", systems=[dict(id="x", role="SOURCE", state="symbol")],
            couplings=[], observables=[], no_detector_reason="No apparatus or measurement claim")
        self.assertEqual(self.errors(), [])

    def test_legacy_physical_partition_gap_is_not_silently_complete(self):
        self.c["profile"] = "PHYSICAL_COMPARISON"
        self.c["review"]["status"] = "INCOMPLETE"
        r = audit.validate_contract(self.c, self.root)
        self.assertEqual(r["errors"], [])
        self.assertIn("system_partition:legacy_unreviewed", r["gaps"])
        self.c["review"]["status"] = "COMPLETE_FOR_SCOPE"
        self.assertTrue(any("unresolved" in e for e in self.errors()))

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
        self.partition()
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

    def test_data_inputs_need_identity_not_result_payload_metadata(self):
        path = "docs/topics/0.99_Test/Data/input.json"
        p = self.root / path
        p.parent.mkdir(parents=True)
        p.write_text('{"observed":1}')
        self.assertTrue(audit.scientific_path(path))
        self.assertFalse(audit.result_path(path))
        self.assertTrue(any("classification/contract" in e for e in audit.build_report(self.root, [path])["errors"]))
        item = dict(path=path, kind="working_file", role="input")
        item["sha256"] = audit.identity_hash(self.root, item)
        self.c["identities"].append(item)
        self.c["review"]["scope_sha256"] = audit.review_payload_hash(self.c)
        self.save_contract()
        self.assertEqual(audit.build_report(self.root, [path])["errors"], [])
        p.write_text('{"observed":2}')
        self.assertTrue(any("STALE identity" in e for e in audit.build_report(self.root, [path])["errors"]))

    def test_shared_and_binary_input_discovery_is_not_artifact_classification(self):
        for p in ("docs/data/external/records/source_record.json", "docs/core/06_data/source_packages/input.h5",
                  "docs/topics/0.1_Test/Data/rows.csv", "docs/topics/0.1_Test/Data/modes.npz"):
            self.assertTrue(audit.scientific_path(p))
            self.assertFalse(audit.result_path(p))

    def test_tsv_text_hash_normalizes_line_endings_but_binary_hash_does_not(self):
        for suffix, equal in ((".tsv", True), (".h5", False)):
            path = "input" + suffix
            item = dict(path=path, kind="working_file")
            (self.root/path).write_bytes(b"x\r\n")
            before = audit.identity_hash(self.root, item)
            (self.root/path).write_bytes(b"x\n")
            self.assertEqual(before == audit.identity_hash(self.root, item), equal)

    def test_ci_contract_checks_are_fail_visible_and_history_complete(self):
        pr = (audit.ROOT / ".github/workflows/pr-validation.yml").read_text(encoding="utf-8-sig")
        nightly = (audit.ROOT / ".github/workflows/nightly-research-audit.yml").read_text(encoding="utf-8-sig")
        self.assertIn("scripts|data/external", pr)
        self.assertIn("pr-validation|nightly-research-audit", pr)
        self.assertIn('audit_calculation_completeness.py --changed "$BASE_SHA" --check', pr)
        self.assertIn("fetch-depth: 0", nightly)
        for text in (pr, nightly):
            step = text.split("python docs/scripts/audit/audit_calculation_completeness.py", 1)[0].rsplit("run: |", 1)[1]
            self.assertIn("set -euo pipefail", step)

    def test_inventory_read_only_deterministic(self):
        self.save_contract()
        before = {str(p):p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        a, b = audit.build_report(self.root), audit.build_report(self.root)
        self.assertEqual(a, b)
        self.assertEqual(a["summary"]["contracts"], 1)
        self.assertEqual(before, {str(p):p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def write_inventory_baseline(self, paths):
        p = self.root / audit.BASELINE
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dict(routes=[dict(route_id="family", owner="CORE", paths=paths,
            claim_boundary="declared normalized family")], legacy_paths=[])), encoding="utf-8")

    def test_inventory_partial_contract_never_certifies_entire_route(self):
        self.save_contract()
        self.write_inventory_baseline([self.path, "docs/core/unreviewed.py"])
        (self.root / "docs/core/unreviewed.py").write_text("# another unreviewed implementation")
        result = audit.build_report(self.root)
        family = next(r for r in result["routes"] if r["route_id"] == "family")
        scoped = next(r for r in result["routes"] if r["route_id"] == "contract:TEST")
        self.assertEqual(family["contract_ids"], ["TEST"])
        self.assertEqual(family["review_status"], "UNREVIEWED")
        self.assertIn("docs/core/unreviewed.py", family["uncovered_paths"])
        self.assertEqual(family["adoption"]["action"], "REVIEW_MODEL_OR_CODE")
        self.assertEqual(scoped["adoption"]["action"], "REUSE_SCOPED_EVIDENCE")

    def test_inventory_explicit_migration_aliases_not_filename_guesses(self):
        self.save_contract()
        old = "docs/core/old_example.py"
        self.write_inventory_baseline([old])
        p = self.root / audit.MIGRATION_MAP
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dict(files=[dict(canonical_path=self.path, current_path=self.path, legacy_paths=[old])])), encoding="utf-8")
        family = next(r for r in audit.build_report(self.root)["routes"] if r["route_id"] == "family")
        self.assertEqual(family["resolved_paths"], [self.path])
        self.assertEqual(family["missing_paths"], [])
        self.assertEqual(family["contract_ids"], ["TEST"])
        self.assertEqual(family["coverage_scope"], "RELATED_ONLY_NOT_PACKAGE_COVERAGE")

    def test_inventory_ambiguous_alias_is_error_not_arbitrary_coverage(self):
        self.save_contract()
        old = "docs/core/old.py"
        self.write_inventory_baseline([old])
        p = self.root / audit.MIGRATION_MAP
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dict(files=[dict(canonical_path=target, legacy_paths=[old])
            for target in (self.path, "docs/core/different.py")])), encoding="utf-8")
        report = audit.build_report(self.root)
        self.assertTrue(any("ambiguous migration alias" in e for e in report["errors"]))
        family = next(r for r in report["routes"] if r["route_id"] == "family")
        self.assertEqual(family["contract_ids"], [])

    def test_inventory_discovers_topic_without_verification_spec_and_loose_sources(self):
        folder = self.root / "docs/topics/0.99_New_Topic"
        folder.mkdir(parents=True)
        (folder / "README.md").write_text("# provisional idea")
        formal = self.root / "docs/core/01_contracts/new_proposition.md"
        formal.parent.mkdir(parents=True)
        formal.write_text("# a mathematical proposition")
        report = audit.build_report(self.root)
        topic = next(r for r in report["routes"] if r["route_id"] == folder.name)
        self.assertIn("docs/topics/0.99_New_Topic/VERIFICATION_SPEC.md", topic["missing_paths"])
        group = next(r for r in report["routes"] if r["route_id"] == "unassigned:CORE")
        self.assertIn(formal.relative_to(self.root).as_posix(), group["resolved_paths"])
        self.assertEqual(group["adoption"]["action"], "REVIEW_MODEL_OR_CODE")
        self.assertFalse(group["adoption"]["claim_promotion"])

    def test_inventory_unknown_and_invalid_contracts_never_request_blind_reruns(self):
        self.c["review"]["status"] = "INCOMPLETE"
        self.c["components"][0].update(disposition="UNKNOWN", owner="reviewer", next_action="supply matching physical state")
        self.save_contract()
        route = next(r for r in audit.build_report(self.root)["routes"] if r["route_id"] == "contract:TEST")
        self.assertEqual(route["adoption"]["action"], "WAIT_FOR_PREREQUISITE")
        self.assertIn(self.c["components"][0]["id"], route["adoption"]["reason"])
        (self.root / self.path).write_text("# a changed input")
        report = audit.build_report(self.root)
        route = next(r for r in report["routes"] if r["route_id"] == "contract:TEST")
        self.assertEqual(route["adoption"]["action"], "REVIEW_MODEL_OR_CODE")

    def test_inventory_formal_public_lineage_gap_is_not_a_new_physics_job(self):
        self.c["review"]["status"] = "INCOMPLETE"
        row = next(c for c in self.c["components"] if c["id"] == "processing")
        row.update(disposition="UNKNOWN", reason="Clean public lineage integration of the pinned research commit remains open.",
            owner="repo-ops", next_action="review the publication lineage")
        self.save_contract()
        scoped = next(r for r in audit.build_report(self.root)["routes"] if r["route_id"] == "contract:TEST")
        self.assertEqual(scoped["adoption"]["action"], "UPDATE_METADATA")
        row["reason"] = "Unknown numerical processing changes the physical conclusion"
        self.save_contract()
        scoped = next(r for r in audit.build_report(self.root)["routes"] if r["route_id"] == "contract:TEST")
        self.assertEqual(scoped["adoption"]["action"], "WAIT_FOR_PREREQUISITE")

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
    def test_admission_products_keep_physical_unknowns_after_relational_adoption(self):
        for name in ("physical_route_admission", "readout_admission"):
            path = audit.ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/{name}.json"
            contract = audit.load_json(path)
            self.assertEqual(contract["review"]["status"], "INCOMPLETE")
            self.assertNotEqual(contract["output"]["claim_intent"], "PHYSICAL_ACCEPTANCE")
            partition = contract["observation"]["system_partition"]
            self.assertEqual(partition["role_mode"], "RELATIONAL")
            self.assertTrue(any(c["group"] == "detector" and c["disposition"] == "UNKNOWN"
                                for c in contract["components"]))
            self.assertEqual(audit.validate_contract(contract)["errors"], [])

    def test_pilot_builder_and_saved_partition_agree(self):
        builder = audit.ROOT / "docs/scripts/audit/build_calculation_contract_pilots.py"
        tree = ast.parse(builder.read_text(encoding="utf-8-sig"))
        values = [ast.literal_eval(node.value) for node in ast.walk(tree)
                  if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                  and any(isinstance(target, ast.Subscript)
                          and isinstance(target.value, ast.Subscript)
                          and isinstance(target.value.value, ast.Name)
                          and target.value.value.id == "c"
                          and isinstance(target.slice, ast.Constant)
                          and target.slice.value == "system_partition" for target in node.targets)]
        saved = audit.load_json(audit.ROOT / "docs/core/00_governance/calculation_contracts/matter_space_observer.json")
        self.assertEqual(values, [saved["observation"]["system_partition"]])
        baselines = [ast.literal_eval(node.args[1]) for node in ast.walk(tree)
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                     and node.func.attr == "insert" and len(node.args) == 2
                     and isinstance(node.args[1], ast.Dict)]
        self.assertIn(saved["identities"][0], baselines)

    def test_core_relational_pilot_keeps_source_state_and_physical_gap(self):
        saved = audit.load_json(audit.ROOT / "docs/core/00_governance/calculation_contracts/matter_space_observer.json")
        graph = saved["observation"]["system_partition"]
        self.assertEqual(graph["role_mode"], "RELATIONAL")
        independent = {sid for s in graph["systems"] for sid in s["state_accounting"]["state_ids"]}
        self.assertEqual(independent, {"matter_space.C", "matter_space.Phi", "matter_space.Pi", "candidate.receiver_state"})
        self.assertFalse(next(s for s in graph["systems"] if s["id"] == "source_system")["state_accounting"]["state_ids"])
        result = audit.validate_contract(saved)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["effective_status"], "INCOMPLETE")
        self.assertIn("detector", result["gaps"])

    def test_topic13_admission_graphs_preserve_unknown_state_and_operator(self):
        path = audit.ROOT / "docs/scripts/audit/build_calculation_contract_pilots.py"
        spec = importlib.util.spec_from_file_location("pilot_builder", path)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        for name in ("he4_observation", "nonlinear_physical"):
            saved = audit.load_json(audit.ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/{name}.json")
            graph = saved["observation"]["system_partition"]
            expected = builder.unadmitted_measurement_partition(graph["systems"][0]["state"], graph["observables"][0]["quantity"])
            self.assertEqual(graph, expected)
            result = audit.validate_contract(saved)
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["effective_status"], "INCOMPLETE")
            self.assertTrue({"system_state", "detector", "drive_environment"} <= set(result["gaps"]))
            self.assertFalse(saved["data_policy"]["independent_validation"])
            self.assertEqual(saved["output"]["claim_intent"], "DIAGNOSTIC")

    def test_formal_invariant_and_graphite_design_do_not_invent_apparatus(self):
        for name in ("nonlinear_formal", "graphite_preparation_prediction"):
            saved = audit.load_json(audit.ROOT / f"docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/{name}.json")
            self.assertEqual(saved["profile"], "FORMAL")
            self.assertFalse(saved["data_policy"]["uses_observations"])
            result = audit.validate_contract(saved)
            self.assertEqual(result["errors"], [])
            self.assertNotIn("system_partition:legacy_unreviewed", result["gaps"])

    def test_astronomy_contracts_are_offline_products_not_raw_instrument_reductions(self):
        path = audit.ROOT / "docs/scripts/audit/build_calculation_contract_pilots.py"
        spec = importlib.util.spec_from_file_location("astronomy_builder", path)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        for topic in builder.ASTRONOMY_INPUTS:
            saved = audit.load_json(audit.ROOT / f"docs/topics/{topic}/calculation_contracts/observation_coverage.json")
            self.assertEqual(builder.adopt_offline_product(copy.deepcopy(saved), topic), saved)
            graph = saved["observation"]["system_partition"]
            self.assertEqual({s["id"] for s in graph["systems"]}, {"data_product", "analysis"})
            self.assertEqual(graph["role_mode"], "RELATIONAL")
            self.assertTrue(any(i["kind"] == "git_blob" and i["commit"] == builder.ASTRONOMY_CODE_COMMIT for i in saved["identities"]))
            result = audit.validate_contract(saved)
            self.assertEqual(result["errors"], [])
            self.assertEqual(result["effective_status"], "INCOMPLETE")
            self.assertIn("correction:upstream-frame-and-instrument-processing", result["gaps"])
            if topic.startswith("0.26_"):
                self.assertIn("processing", result["gaps"])
                self.assertIn("claim_class D", next(c["reason"] for c in saved["components"] if c["id"] == "processing"))

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
