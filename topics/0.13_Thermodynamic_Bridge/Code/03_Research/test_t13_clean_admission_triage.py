"""Bounded tests for historical-to-clean admission triage."""

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_T13_Clean_Admission_Triage.py")
SPEC = importlib.util.spec_from_file_location("clean_admission_triage", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_field_diff_detects_claim_change():
    before = {"major_result": {"closure_level": "PARTIAL", "evidence_artifacts": [{"path": "old"}]}}
    after = {"major_result": {"closure_level": "CLOSED_FOR_CORE", "evidence_artifacts": [{"path": "new"}]}}
    pointers = MODULE.changes(before, after)
    assert "/major_result/closure_level" in pointers
    assert "/major_result/evidence_artifacts/0/path" in pointers
    assert MODULE.classify("/major_result/closure_level") == "CLAIM_OR_GATE"
    assert MODULE.classify("/major_result/evidence_artifacts/0/path") == "REFERENCE_TOKEN"


def test_saved_record_matches_current_clean_checkout_without_unlock():
    record = json.loads(MODULE.RECORD.read_text(encoding="utf-8"))
    assert all(MODULE.verify_saved(record).values())
    assert record["counts"]["SERIALIZATION_ONLY_DIFFERENCE"] == 2
    assert record["counts"]["JSON_FIELD_DIFFERENCE"] == 2
    assert record["counts"]["MISSING_AT_RECORDED_PATH"] == 4


def test_changed_clean_hash_is_not_admitted():
    record = json.loads(MODULE.RECORD.read_text(encoding="utf-8"))
    record["records"][0]["clean_sha256"] = "0" * 64
    assert not MODULE.verify_saved(record)["clean_hashes_current"]
