"""Tests for suite discovery and honest process-result classification."""

from __future__ import annotations

from pathlib import Path

from topics import run_all_tests as runner


def test_topic_without_tests_is_incomplete_not_pass(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    topic = root / "topics" / "0.40_Example"
    topic.mkdir(parents=True)

    suites, missing = runner.topic_suite(topic, root)

    assert suites == []
    assert missing == ["0.40_Example: no pytest regression suite discovered"]


def test_topic_gaps_are_advisory_but_other_gaps_block() -> None:
    missing = ["0.40_Example: no pytest regression suite discovered",
               "0.24_Example: limited suite: synthetic only",
               "docs/scripts/standard/check_schema.py: required checker missing",
               "changed files do not map to a Core/shared test suite or numbered Topic"]
    assert runner.blocking_gaps(missing) == missing[2:]
    assert all(runner.is_advisory_topic_gap(entry) for entry in missing[:2])


def test_incomplete_coverage_exit_code_takes_precedence_over_failures() -> None:
    assert runner._program_exit_code(failed=0, incomplete=False) == 0
    assert runner._program_exit_code(failed=1, incomplete=False) == 1
    assert runner._program_exit_code(failed=1, incomplete=True) == 2


def test_profile_software_tests_do_not_close_topic_coverage(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    topic = root / "topics" / runner.PROFILE_CHECK_TOPICS[0]
    topic.mkdir(parents=True)
    (topic / "test_profile.py").write_text("def test_profile(): assert True\n", encoding="utf-8")
    suites, missing = runner.topic_suite(topic, root)
    assert len(suites) == 1
    assert any("limited suite" in message and "engine/research" in message for message in missing)
    assert any("thermal-stability" in message for message in missing)
    # limited-suite gaps are reported but advisory (owner decision 2026-11-18)
    assert runner.blocking_gaps(missing) == []
    assert runner._program_exit_code(failed=0, incomplete=bool(runner.blocking_gaps(missing))) == 0


def test_nested_profile_outcome_is_read_without_becoming_physical_validation(tmp_path: Path) -> None:
    name = runner.PROFILE_CHECK_TOPICS[0]
    path = tmp_path / runner.LEGACY_RESULT_READOUTS[name]["path"]
    path.parent.mkdir(parents=True)
    path.write_text('{"metadata":{"status":"FAIL"}}', encoding="utf-8")
    result = runner.legacy_topic_results([{"topic": name}], tmp_path)
    assert result["errors"] == []
    assert result["items"][0]["outcome"] == "FAIL"
    assert result["records_read_not_rerun"] is True
    path.write_text('{"metadata":{}}', encoding="utf-8")
    assert runner.legacy_topic_results([{"topic": name}], tmp_path)["errors"]


def test_ai_synthetic_suite_does_not_close_live_benchmark_or_engine_coverage(tmp_path: Path):
    root = tmp_path / "repo"
    topic = root / "topics/0.24_Artificial_Intelligence"
    topic.mkdir(parents=True)
    (topic / "test_synthetic.py").write_text("def test_case(): assert True\n", encoding="utf-8")
    suites, missing = runner.topic_suite(topic, root)
    assert len(suites) == 1
    assert len(missing) == 1
    assert "synthetic scaling/sparsity" in missing[0]
    assert "AI engine paths" in missing[0]
    assert runner.blocking_gaps(missing) == []


def test_profile_only_scope_reopens_if_code_is_added_or_missing(tmp_path: Path) -> None:
    for name, locator in runner.PROFILE_ONLY_CODE.items():
        topic = tmp_path / name
        source = topic / locator
        source.parent.mkdir(parents=True)
        assert runner.topic_scope_gap(topic) is not None
        source.write_text("def run_simulation(): pass\n", encoding="utf-8")
        assert runner.topic_scope_gap(topic) is None
        unreviewed = topic / "Code/new_engine.py"
        unreviewed.write_text("def evolve(): pass\n", encoding="utf-8")
        assert "need review" in runner.topic_scope_gap(topic)
        unreviewed.unlink()
        assert runner.topic_scope_gap(topic) is None
        (topic / "Code/new_engine.js").write_text("evolve();\n", encoding="utf-8")
        assert "need review" in runner.topic_scope_gap(topic)
        source.unlink()
        assert runner.topic_scope_gap(topic) is not None


def test_profile_shared_change_selects_all_consumers_without_core_rerun(tmp_path: Path, monkeypatch) -> None:
    from types import SimpleNamespace

    root = tmp_path / "repo"
    for name in runner.PROFILE_CHECK_TOPICS:
        topic = root / "topics" / name
        topic.mkdir(parents=True)
        (topic / "test_profile.py").write_text("def test_profile(): assert True\n", encoding="utf-8")
        if name in runner.PROFILE_ONLY_CODE:
            source = topic / runner.PROFILE_ONLY_CODE[name]
            source.parent.mkdir(parents=True)
            source.write_text("def run_simulation(): pass\n", encoding="utf-8")
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: SimpleNamespace(
        returncode=0, stdout="topics/_profile_thresholds.py\n", stderr=""))
    suites, inventory, missing = runner.changed_suites("BASE", root)
    assert {item["topic"] for item in inventory} == set(runner.PROFILE_CHECK_TOPICS)
    assert {suite.suite_id for suite in suites} == {
        "runner-tests", *(f"topic:{name}" for name in runner.PROFILE_CHECK_TOPICS)}
    assert "core-tests" not in {suite.suite_id for suite in suites}
    assert len(missing) == len(runner.PROFILE_CHECK_TOPICS) - len(runner.PROFILE_ONLY_CODE)


def test_test_filename_discovery_is_narrow(tmp_path: Path) -> None:
    topic = tmp_path / "topic"
    (topic / "Code" / "03_Research").mkdir(parents=True)
    (topic / "tests").mkdir()
    (topic / "tests" / "test_model.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (topic / "Code" / "03_Research" / "casimir_test.py").write_text(
        "from pathlib import Path\nPath('output.json').write_text('{}')\n", encoding="utf-8"
    )
    (topic / "Code" / "03_Research" / "Research_run.py").touch()
    (topic / "Code" / "03_Research" / "Engine_run.py").touch()

    assert [path.name for path in runner.pytest_files(topic)] == ["test_model.py"]


def test_code_inventory_separates_test_modules_and_exposes_unreviewed_risk(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    topic = root / "topics" / "0.40_Example"
    code = topic / "Code" / "03_Research"
    code.mkdir(parents=True)
    (code / "test_model.py").write_text("from pathlib import Path\ndef test_ok(): assert True\n", encoding="utf-8")
    (code / "Research_emit.py").write_text(
        "from pathlib import Path\nif __name__ == '__main__': Path('result.json').write_text('{}')\n",
        encoding="utf-8",
    )
    (code / "casimir_test.py").write_text(
        "from pathlib import Path\nPath('result.json').write_text('{}')\n",
        encoding="utf-8",
    )

    record = runner.topic_inventory_record(topic, root)
    by_name = {Path(item["path"]).name: item for item in record["code_file_inventory"]}

    assert record["pytest_modules"] == 1
    assert record["grid_script_count_not_auto_run"] == 2
    assert by_name["test_model.py"]["classification"] == "PYTEST_TEST_MODULE"
    assert by_name["Research_emit.py"]["classification"] == "UNCLASSIFIED_NON_TEST_CODE"
    assert by_name["Research_emit.py"]["invocation_status"].startswith("candidate only")
    assert by_name["Research_emit.py"]["overwrite_risk"] == "POTENTIAL_WRITE"
    assert by_name["Research_emit.py"]["output_location"] == "UNKNOWN; static source scan is not an exhaustive path audit"
    assert by_name["casimir_test.py"]["classification"] == "UNCLASSIFIED_NON_TEST_CODE"
    assert by_name["casimir_test.py"]["overwrite_risk"] == "POTENTIAL_WRITE"


def test_registered_research_outcome_is_copied_without_reclassification(tmp_path: Path) -> None:
    results = tmp_path / "docs" / "standard" / "results"
    results.mkdir(parents=True)
    (results / "R_example.json").write_text(
        '{"result_id":"R_example","claim_id":"C_example","level":"FAILED","outcome":"FAIL","date":"2026-11-14"}',
        encoding="utf-8",
    )

    inventory = runner.registered_research_results(tmp_path)

    assert inventory["records_read_not_rerun"] is True
    assert inventory["counts"]["FAIL"] == 1
    assert inventory["items"][0]["outcome"] == "FAIL"
    assert inventory["items"][0]["level"] == "FAILED"


def test_legacy_model_failure_readout_never_uses_run_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(runner, "LEGACY_RESULT_READOUTS", {"example": {
        "path": "result.json", "outcome_field": "model_gate_status", "suite_scope": "fixture"}})
    path = tmp_path / "result.json"
    path.write_text('{"run_status":"PASS","model_gate_status":"FAIL"}', encoding="utf-8")
    result = runner.legacy_topic_results([{"topic": "example"}], tmp_path)
    assert result["items"][0]["outcome"] == "FAIL"
    assert result["errors"] == []
    path.write_text('{"run_status":"PASS"}', encoding="utf-8")
    result = runner.legacy_topic_results([{"topic": "example"}], tmp_path)
    assert result["items"] == []
    assert result["errors"]


def test_limited_result_reporting_suite_does_not_close_whole_topic(tmp_path: Path, monkeypatch) -> None:
    topic = tmp_path / "topics" / "example"
    topic.mkdir(parents=True)
    (topic / "test_report.py").write_text("def test_report(): assert True\n", encoding="utf-8")
    monkeypatch.setattr(runner, "LEGACY_RESULT_READOUTS", {"example": {"suite_scope": "reporting only"}})
    suites, gaps = runner.topic_suite(topic, tmp_path)
    assert len(suites) == 1
    assert gaps == ["example: limited suite: reporting only"]


def test_pytest_nonzero_cannot_be_overridden_by_pass_text() -> None:
    suite = runner.Suite("fixture", "pytest", ["pytest"], ["tests"])

    status, _ = runner._classify(suite, 1, "1 passed, 1 failed")

    assert status == "FAIL"


def test_pytest_empty_collection_is_incomplete() -> None:
    suite = runner.Suite("fixture", "pytest", ["pytest"], ["tests"])

    status, _ = runner._classify(suite, 5, "no tests ran", collected=0)

    assert status == "INCOMPLETE"


def test_pytest_success_without_outcomes_and_all_xfail_are_incomplete() -> None:
    suite = runner.Suite("fixture", "pytest", ["pytest"], ["tests"])
    for output in ("SUCCESS", "", "2 xfailed"):
        status, _ = runner._classify(suite, 0, output, collected=2)
        assert status == "INCOMPLETE"


def test_pytest_uses_final_summary_not_traceback_or_captured_fixture_text() -> None:
    output = ('assert "999 passed, 77 failed" in fixture\n'
              '999 passed\n'
              '== 1 failed, 2 passed, 8 subtests passed, 1 warning in 2.5s ==\n')
    counts = runner._pytest_counts(output)
    assert counts["passed"] == 2
    assert counts["failed"] == 1
    assert sum(counts.values()) == 3


def test_pytest_success_cannot_hide_unaccounted_collected_tests() -> None:
    suite = runner.Suite("fixture", "pytest", ["pytest"], ["tests"])
    status, counts = runner._classify(suite, 0, "2 passed in 1.0s", collected=3)
    assert status == "INCOMPLETE"
    assert counts["passed"] == 2


def test_deferred_tests_remain_visible_without_automatic_execution(tmp_path: Path) -> None:
    topic = tmp_path / "0.40_Example"
    for relative in ("legacy/test_previous.py", "archive/test_previous.py", "Code/check_custom.py"):
        path = topic / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("def test_contract(): assert True\n", encoding="utf-8")
    assert runner.pytest_files(topic) == []
    candidates = runner.deferred_test_candidates(topic)
    assert len(candidates) == 3
    assert all("require review" in item["reason"] for item in candidates)


def test_physics_checker_zero_exit_does_not_hide_skipped_tests() -> None:
    suite = runner.Suite("physics-tests", "physics", ["checker"], [],
                         success_pattern=r"check_physics_tests: physics=\d+")
    status, counts = runner._classify(suite, 0,
        "check_physics_tests: physics=194 bookkeeping=0\n193 passed, 1 skipped")
    assert status == "INCOMPLETE"
    assert counts["skipped"] == 1
    assert runner._classify(suite, 0, "check_physics_tests: physics=194")[0] == "INCOMPLETE"


def test_pytest_skip_is_visible_and_prevents_full_pass() -> None:
    suite = runner.Suite("fixture", "pytest", ["pytest"], ["tests"])

    status, counts = runner._classify(suite, 0, "1 passed, 1 skipped", collected=2)

    assert status == "INCOMPLETE"
    assert counts["skipped"] == 1


def test_runtime_pytest_errors_are_reported_separately_and_fail_the_suite() -> None:
    suite = runner.Suite("fixture", "pytest", ["pytest"], ["tests"])

    status, counts = runner._classify(suite, 1, "3 passed, 2 errors", collected=5)

    assert status == "FAIL"
    assert counts["passed"] == 3
    assert counts["errors"] == 2


def test_unittest_counts_are_reported_and_skips_prevent_full_pass() -> None:
    suite = runner.Suite("fixture", "unittest", ["python", "-m", "unittest"], ["tests"])
    output = "Ran 3 tests in 0.001s\n\nOK (skipped=1)\n"

    status, counts = runner._classify(suite, 0, output)

    assert status == "INCOMPLETE"
    assert counts["passed"] == 2
    assert counts["skipped"] == 1


def test_unittest_runtime_errors_are_not_hidden_by_success_text() -> None:
    suite = runner.Suite("fixture", "unittest", ["python", "-m", "unittest"], ["tests"])
    output = "Ran 4 tests in 0.001s\n\nFAILED (failures=1, errors=1)\n"

    status, counts = runner._classify(suite, 1, output)

    assert status == "FAIL"
    assert counts["failed"] == 1
    assert counts["errors"] == 1
    assert counts["passed"] == 2


def test_check_script_failure_text_with_zero_exit_is_not_pass() -> None:
    suite = runner.Suite("fixture", "check", ["check.py"], ["check.py"])

    status, _ = runner._classify(suite, 0, "FAIL: missing input")

    assert status == "INCOMPLETE"


def test_check_script_needs_its_declared_success_record() -> None:
    suite = runner.Suite("fixture", "check", ["check.py"], ["check.py"],
                         success_pattern=r"^fixture: 0 errors$")

    assert runner._classify(suite, 0, "SUCCESS")[0] == "INCOMPLETE"
    assert runner._classify(suite, 0, "fixture: 0 errors")[0] == "PASS"


def test_research_fail_text_is_not_inferred_from_test_runner_output() -> None:
    suite = runner.Suite("fixture", "check", ["report.py"], ["report.py"])

    status, _ = runner._classify(suite, 0, "Registered result outcome: INCONCLUSIVE",
                                 )

    assert status == "INCOMPLETE"


def test_topic_selector_supports_numeric_id() -> None:
    topic = Path("topics/0.13_Thermodynamic_Bridge")

    assert runner.resolve_topic("0.13", [topic]) == topic


def test_full_inventory_includes_the_runner_self_tests(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "repo"
    directories = [
        root / "core" / "05_tests",
        root / "topics" / "tests",
        root / "docs" / "scripts" / "standard" / "tests",
        root / "docs" / "scripts" / "audit" / "tests",
    ]
    for directory in directories:
        directory.mkdir(parents=True)
    for script in (
        "docs/scripts/standard/check_schema.py",
        "docs/scripts/standard/check_preregistration.py",
        "docs/scripts/audit/audit_calculation_completeness.py",
        "docs/scripts/standard/check_physics_tests.py",
    ):
        target = root / script
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    monkeypatch.setattr(runner, "topic_directories", lambda _root: [])
    monkeypatch.setattr(
        runner,
        "pytest_files",
        lambda directory: [directory / "test_fixture.py"] if directory in directories else [],
    )

    suites, inventory, _ = runner.all_suites(root)

    assert "runner-tests" in {suite.suite_id for suite in suites}
    assert inventory == []


def test_list_mode_reports_gaps_without_becoming_a_test_failure(monkeypatch, capsys) -> None:
    missing = ["0.40_Example: no pytest regression suite discovered"]
    monkeypatch.setattr(runner, "all_suites", lambda: ([], [], missing))

    assert runner.main(["--list", "--all"]) == 0
    assert "INCOMPLETE: 0.40_Example" in capsys.readouterr().out


def test_human_report_separates_software_and_research_outcomes() -> None:
    report = {
        "revision": "abc123",
        "working_tree_dirty": True,
        "created_utc": "2026-11-14T00:00:00Z",
        "environment": {"python": "Python 3.12", "platform": "test", "cwd": "."},
        "request": {"all": True, "topic": None, "changed_base": None},
        "program_exit_code": 2,
        "topic_inventory": [{"topic": "0.1_Example"}],
        "results": [{
            "suite_id": "topic:0.1_Example", "status": "FAIL", "collected": 2,
            "passed": 1, "failed": 1, "errors": 0, "skipped": 0,
            "xfailed": 0, "xpassed": 0, "duration_seconds": 1.25,
            "command": ["python", "-m", "pytest"], "stdout_log": "stdout.log",
            "stderr_log": "stderr.log", "note": "diagnostic",
        }],
        "uncovered_or_missing": ["0.2_Example: no pytest regression suite discovered"],
        "registered_research_results": {"counts": {"PASS": 1, "FAIL": 1, "INCONCLUSIVE": 0}},
    }

    rendered = runner._render_markdown_report(report)

    assert "software test/check failed" in rendered
    assert "no producer was rerun" in rendered
    assert "Program exit code: `2`" in rendered
    assert "ADVISORY (does not change the exit code): 0.2_Example" in rendered
    assert "| FAIL | 1 |" in rendered
