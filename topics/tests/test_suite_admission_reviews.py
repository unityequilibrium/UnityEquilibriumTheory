"""Bookkeeping/safety tests for reviewed deferred sources, not physics evidence."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from topics import run_all_tests as runner


def reviewed_fixture(tmp_path: Path, source_name="demo.py"):
    topic = tmp_path / "topics/0.40_Fixture"
    source = topic / source_name
    source.parent.mkdir(parents=True)
    source.write_text("def test_demo(): return True\n", encoding="utf-8", newline="\n")
    config = {"version": 1, "reviews": {f"{topic.name}/{source_name}": {
        "source_sha256_lf": hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "role": "fixture demonstration", "decision": "NOT_ADMITTED",
        "evidence_symbols": ["test_demo"], "reason": "returns True without enforcing results",
        "reopen_when": "reviewed failure contract and output isolation",
    }}}
    path = tmp_path / "topics/test_suite_config.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return topic, source, path, config


def test_current_review_is_visible_and_cannot_enable_execution(tmp_path):
    topic, source, _, _ = reviewed_fixture(tmp_path, "test_demo.py")
    assert runner.pytest_files(topic) == []
    candidate, = runner.deferred_test_candidates(topic)
    assert candidate["admission_review"]["status"] == "CURRENT_REVIEW"
    assert candidate["admission_review"]["decision"] == "NOT_ADMITTED"
    suites, gaps = runner.topic_suite(topic, tmp_path)
    assert not suites
    assert gaps


def test_review_survives_rename_and_withholds_topic_execution(tmp_path):
    topic, source, _, _ = reviewed_fixture(tmp_path)
    source.rename(topic / "test_renamed.py")
    candidates = runner.deferred_test_candidates(topic)
    missing = next(item for item in candidates if item["path"] == "demo.py")
    assert missing["admission_review"]["status"] == "MISSING_SOURCE"
    assert any(item["path"] == "test_renamed.py" for item in candidates)
    assert runner.pytest_files(topic) == []
    suites, gaps = runner.topic_suite(topic, tmp_path)
    assert suites == []
    assert any("MISSING_SOURCE" in gap for gap in gaps)


def test_source_change_requires_review_not_a_label_change(tmp_path):
    topic, source, _, _ = reviewed_fixture(tmp_path)
    source.write_text("def differently_named(): return True\n", encoding="utf-8")
    candidate, = runner.deferred_test_candidates(topic)
    assert candidate["admission_review"]["status"] == "STALE_REVIEW"
    assert runner.topic_suite(topic, tmp_path)[0] == []


def test_cross_topic_rename_cannot_turn_a_denied_producer_into_a_test(tmp_path):
    topic, source, _, _ = reviewed_fixture(tmp_path)
    other = tmp_path / "topics/0.41_Other"
    other.mkdir()
    source.rename(other / "test_renamed.py")
    assert runner.pytest_files(other) == []
    assert runner.topic_suite(topic, tmp_path)[0] == []


def test_review_identity_is_portable_but_does_not_change_source_bytes(tmp_path):
    topic, source, _, _ = reviewed_fixture(tmp_path)
    source.write_bytes(source.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    before = source.read_bytes()
    candidate, = runner.deferred_test_candidates(topic)
    assert candidate["admission_review"]["status"] == "CURRENT_REVIEW"
    assert source.read_bytes() == before


def test_reviewed_source_is_not_labeled_unclassified_or_lost_from_counts(tmp_path):
    topic, _, _, _ = reviewed_fixture(tmp_path, "Code/03_Research/test_demo.py")
    record = runner.topic_inventory_record(topic, tmp_path)
    assert record["pytest_modules"] == 0
    assert record["grid_script_count_not_auto_run"] == 1
    source, = record["code_file_inventory"]
    assert source["classification"] == "REVIEWED_NOT_ADMITTED"
    assert source["admission_review"]["role"] == "fixture demonstration"


@pytest.mark.parametrize("mutation", ["enable", "traversal", "no_topic_path", "bad_version"])
def test_invalid_or_execution_enabling_configuration_fails_closed(tmp_path, mutation):
    topic, _, path, config = reviewed_fixture(tmp_path)
    locator, = config["reviews"]
    if mutation == "enable":
        config["reviews"][locator]["decision"] = "RUN"
    elif mutation == "traversal":
        config["reviews"]["0.40_Fixture/../../outside.py"] = config["reviews"].pop(locator)
    elif mutation == "no_topic_path":
        config["reviews"]["0.40_Fixture.py"] = config["reviews"].pop(locator)
    else:
        config["version"] = True
    path.write_text(json.dumps(config), encoding="utf-8")
    reviews, errors = runner.load_suite_reviews(tmp_path)
    assert reviews == {}
    assert errors
    assert runner.topic_suite(topic, tmp_path)[0] == []


def test_deleted_required_configuration_is_not_an_exemption(tmp_path, monkeypatch):
    topic, _, path, _ = reviewed_fixture(tmp_path)
    path.unlink()
    monkeypatch.setattr(runner, "REPO_ROOT", tmp_path)
    assert runner.load_suite_reviews(tmp_path)[1]
    assert runner.topic_suite(topic, tmp_path)[0] == []


def test_duplicate_configuration_keys_are_rejected(tmp_path):
    _, _, path, _ = reviewed_fixture(tmp_path)
    path.write_text('{"version":1,"version":1,"reviews":{}}', encoding="utf-8")
    assert runner.load_suite_reviews(tmp_path)[1]


@pytest.mark.parametrize("changed_path", ["topics/test_suite_config.json", ".gitattributes", ".gitignore",
                                          ".github/workflows/pr-validation.yml",
                                          ".github/workflows/nightly-research-audit.yml",
                                          ".github/workflows/main-validation.yml"])
def test_configuration_change_selects_shared_consumers(tmp_path, monkeypatch, changed_path):
    from types import SimpleNamespace
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs:
                        SimpleNamespace(returncode=0, stdout=f"{changed_path}\n", stderr=""))
    monkeypatch.setattr(runner, "topic_directories", lambda root: [])
    shared = runner.Suite("fixture-shared", "pytest", ["pytest"], ["tests"])
    monkeypatch.setattr(runner, "all_suites", lambda root: ([shared], [], []))
    suites, _, missing = runner.changed_suites("baseline", tmp_path)
    assert suites == [shared]
    assert missing == []


def test_repository_reviews_identify_real_source_symbols_without_importing_them():
    reviews, errors = runner.load_suite_reviews(runner.REPO_ROOT)
    assert not errors
    assert reviews
    for locator, review in reviews.items():
        source = runner.REPO_ROOT / "topics" / locator
        assert hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == review["source_sha256_lf"]
        tree = ast.parse(source.read_text(encoding="utf-8-sig"))
        symbols = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        symbols.update(f"{cls.name}.{method.name}" for cls in tree.body if isinstance(cls, ast.ClassDef)
                       for method in cls.body if isinstance(method, ast.FunctionDef))
        assert set(review["evidence_symbols"]) <= symbols
