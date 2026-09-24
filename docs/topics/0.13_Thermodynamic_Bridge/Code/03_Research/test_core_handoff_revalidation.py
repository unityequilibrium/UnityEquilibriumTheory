import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "t13_handoff", Path(__file__).with_name("Research_Core_Handoff_Revalidation.py"))
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
differences = _module.differences


def test_numeric_status_and_hash_changes_are_not_ignored():
    old = {"status": "PASS", "metric": 1., "source_hashes": {"a/b": "old"}}
    new = {"status": "FAIL", "metric": 2., "source_hashes": {"a/b": "new"}}
    assert {r["path"] for r in differences(old, new)} == {"/status", "/metric", "/source_hashes/a~1b"}


def test_missing_null_and_types_are_distinct():
    assert differences({}, {"key": None})[0]["missing_from"] == "before"
    assert differences(True, 1)
    assert differences([1], [1, 2])


def test_timestamp_is_not_silently_filtered_by_comparator():
    assert differences({"generated_at": "a"}, {"generated_at": "b"})
    assert differences({"checks": [True, False]}, {"checks": [True, False]}) == []
