"""Contract tests for the read-only historical snapshot recovery record."""

import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("Research_T13_Historical_Snapshot_Recovery.py")
SPEC = importlib.util.spec_from_file_location("snapshot_recovery", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_record_matches_funding_plan_without_promoting_g0():
    record = json.loads(MODULE.RECORD.read_text(encoding="utf-8"))
    assert all(MODULE.verify_record(record).values())
    assert record["dependency_unlocked"] == []
    assert record["data_role"] == "PROVENANCE_OBSERVATION_NOT_PHYSICAL_VALIDATION"
    evidence = record["evidence_artifacts"][0]
    assert MODULE.sha256(MODULE.ROOT / evidence["path"]) == evidence["sha256"]


def test_a_changed_hash_cannot_pass_as_recovered():
    record = json.loads(MODULE.RECORD.read_text(encoding="utf-8"))
    record["records"][0]["observed_sha256"] = "0" * 64
    assert not MODULE.verify_record(record)["recorded_hashes_match_plan"]
