"""Run the repository's declared, safe test suites without treating research output as a test.

Examples (run from any directory):
  python topics/run_all_tests.py --list --all
  python topics/run_all_tests.py --topic 0.13
  python topics/run_all_tests.py --changed origin/main
  python topics/run_all_tests.py --all

The runner discovers pytest test modules only. Engine, Research, Proof and
Competitor scripts are inventoried but are not executed automatically because
many are producers or write result files. Their classification is not implied
by their filename.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOPICS_ROOT = REPO_ROOT / "topics"
TOPIC_PATTERN = re.compile(r"^0\.\d+_")
PYTEST_FILE = re.compile(r"(?:^test_.*\.py$|.*_test\.py$)")
PYTEST_SUMMARY = re.compile(r"(?:(\d+)(?:/\d+)?\s+tests?\s+collected|no tests collected)", re.I)
PYTEST_COUNTS = re.compile(r"(?:(\d+) passed)?(?:,?\s*(\d+) failed)?(?:,?\s*(\d+) errors?)?(?:,?\s*(\d+) skipped)?(?:,?\s*(\d+) xfailed)?(?:,?\s*(\d+) xpassed)?")
COLLECTION_ERROR = re.compile(r"ERROR collecting|errors? during collection|ImportError while importing|no tests ran", re.I)
GRID_PHASES = {"01_Engine", "02_Proof", "03_Research", "04_Competitor"}
# Reviewed readout configuration, not a new research-status registry.
LEGACY_RESULT_READOUTS = {
    "0.19_Gravity_GR": {
        "path": "topics/0.19_Gravity_GR/Result/artifacts/0_19_gravity_gr_verification.json",
        "outcome_field": "status",
        "suite_scope": "synthetic constant-checkpoint failure/reporting tests only; real engine/CODATA comparison and other gravity paths remain unreviewed",
    },
    "0.4_Superconductivity_Superfluids": {
        "path": "topics/0.4_Superconductivity_Superfluids/Result/artifacts/0_4_superconductivity_superfluids_verification.json",
        "outcome_field": "model_gate_status",
        "suite_scope": "decision-helper and saved-result reporting only; benchmark, input provenance and other Topic paths remain unreviewed",
    },
}
READ_CALLS = {"open", "read", "read_text", "read_bytes", "read_csv", "read_excel", "read_json", "load", "loadtxt", "genfromtxt", "glob", "rglob", "iterdir"}
WRITE_CALLS = {"write", "write_text", "write_bytes", "to_csv", "to_excel", "to_json", "save", "savefig", "dump", "mkdir", "unlink", "rename", "replace"}


@dataclass
class Suite:
    suite_id: str
    kind: str
    command: list[str]
    paths: list[str]
    topic: str | None = None
    timeout_seconds: int = 1800
    success_pattern: str | None = None


@dataclass
class SuiteResult:
    suite_id: str
    kind: str
    topic: str | None
    command: list[str]
    status: str
    returncode: int | None
    duration_seconds: float
    collected: int | None = None
    passed: int | None = None
    failed: int | None = None
    errors: int | None = None
    skipped: int | None = None
    xfailed: int | None = None
    xpassed: int | None = None
    stdout_log: str | None = None
    stderr_log: str | None = None
    note: str | None = None


def topic_directories(root: Path = REPO_ROOT) -> list[Path]:
    return sorted(
        (path for path in (root / "topics").iterdir()
         if path.is_dir() and TOPIC_PATTERN.match(path.name)),
        key=lambda path: tuple(int(piece) for piece in path.name.split("_", 1)[0].split(".")),
    )


def _module_defines_tests(path: Path) -> bool:
    """Do not execute a producer merely because its filename ends in ``_test``."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        # Keep malformed candidates visible so pytest reports the collection error.
        return True
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            return True
        if isinstance(node, ast.ClassDef):
            is_unittest_case = any(
                (isinstance(base, ast.Name) and base.id == "TestCase")
                or (isinstance(base, ast.Attribute) and base.attr == "TestCase")
                for base in node.bases
            )
            has_test_method = any(
                isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                and member.name.startswith("test_") for member in node.body
            )
            if has_test_method and (node.name.startswith("Test") or is_unittest_case):
                return True
    return False


def pytest_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        path for path in directory.rglob("*.py")
        if PYTEST_FILE.match(path.name)
        and not any(part in {"__pycache__", ".venv", "archive", "legacy"} for part in path.parts)
        and _module_defines_tests(path)
    )


def deferred_test_candidates(directory: Path) -> list[dict[str, str]]:
    """Expose historical/custom-name tests without executing unreviewed code."""
    selected = set(pytest_files(directory))
    candidates = []
    for path in sorted(directory.rglob("*.py")):
        if path in selected or any(part in {"__pycache__", ".venv", "raw", "1_raw", "private"}
                                   for part in path.relative_to(directory).parts):
            continue
        if _module_defines_tests(path):
            candidates.append({
                "path": path.relative_to(directory).as_posix(),
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "reason": "test-like AST; execution safety and invocation require review, not exempt by folder name",
            })
    return candidates


def grid_script_inventory(topic: Path) -> dict[str, int]:
    counts = {phase: 0 for phase in sorted(GRID_PHASES)}
    tests = set(pytest_files(topic))
    code = topic / "Code"
    if not code.is_dir():
        return counts
    for path in code.rglob("*.py"):
        if path in tests:
            continue
        relative_parts = path.relative_to(code).parts
        phase = next((part for part in relative_parts if part in GRID_PHASES), None)
        if phase:
            counts[phase] += 1
    return counts


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def code_file_inventory(topic: Path, root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Describe Code/*.py files without executing them or inferring safety.

    Directory and filename patterns are hints only. Unknown invocation, data
    requirements, outputs, and write risk stay explicit rather than being
    silently treated as safe tests.
    """
    code = topic / "Code"
    if not code.is_dir():
        return []
    tests = set(pytest_files(topic))
    stdlib = getattr(sys, "stdlib_module_names", set())
    inventory: list[dict[str, Any]] = []
    for path in sorted(code.rglob("*.py")):
        try:
            source = path.read_text(encoding="utf-8-sig", errors="replace")
            tree = ast.parse(source, filename=str(path))
            parse_error = None
        except (OSError, SyntaxError) as exc:
            source = ""
            tree = None
            parse_error = f"{type(exc).__name__}: {exc}"

        relative = path.relative_to(root).as_posix()
        phase = next((part for part in path.relative_to(code).parts if part in GRID_PHASES), None)
        is_test = path in tests
        imports: set[str] = set()
        reads: set[str] = set()
        writes: set[str] = set()
        main_guard = False
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".", 1)[0])
                elif isinstance(node, ast.Call):
                    name = _call_name(node)
                    if name in READ_CALLS:
                        reads.add(name)
                    if name in WRITE_CALLS:
                        writes.add(name)
                    if name == "open":
                        mode = next((kw.value.value for kw in node.keywords
                                     if kw.arg == "mode" and isinstance(kw.value, ast.Constant)), None)
                        if mode is None and len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                            mode = node.args[1].value
                        if isinstance(mode, str) and any(flag in mode for flag in "wax+"):
                            writes.add("open(write-mode)")
                elif isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) \
                        and node.left.id == "__name__" and any(
                            isinstance(item, ast.Constant) and item.value == "__main__" for item in node.comparators
                        ):
                    main_guard = True

        external_imports = sorted(name for name in imports if name not in stdlib and name not in {
            "core", "topics", "docs", "services_and_experiments",
        })
        if is_test:
            invocation = f"topics/run_all_tests.py --topic {topic.name.split('_', 1)[0]}"
            invocation_status = "included in discovered pytest suite"
            classification = "PYTEST_TEST_MODULE"
        else:
            invocation = f"python {relative}" if main_guard else None
            invocation_status = "candidate only; not executed, arguments and safety unreviewed" if main_guard else "no safe invocation declared"
            classification = "UNCLASSIFIED_NON_TEST_CODE"
        role_hints = []
        if phase:
            role_hints.append(f"directory:{phase}")
        lowered = path.stem.lower()
        if any(token in lowered for token in ("check", "audit", "verify", "validate")):
            role_hints.append("filename:checker-or-audit-candidate")
        if phase == "04_Competitor":
            role_hints.append("directory:comparator-candidate")
        if any(token in lowered for token in ("history", "snapshot", "recovery")):
            role_hints.append("filename:history-or-recovery-candidate")
        inventory.append({
            "path": relative,
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
            "classification": classification,
            "role_hints_not_verified": role_hints,
            "invocation": invocation,
            "invocation_status": invocation_status,
            "static_imports_not_guaranteed_available": external_imports,
            "input_requirements": "UNKNOWN; possible static read calls: " + (", ".join(sorted(reads)) or "none detected"),
            "output_location": "UNKNOWN; static source scan is not an exhaustive path audit",
            "static_write_calls": sorted(writes),
            "overwrite_risk": "POTENTIAL_WRITE" if writes else "UNKNOWN_NOT_PROVEN_READ_ONLY",
            "source_parse_error": parse_error,
        })
    return inventory


def topic_inventory_record(topic: Path, root: Path = REPO_ROOT, coverage_note: str | None = None) -> dict[str, Any]:
    test_files = pytest_files(topic)
    scripts = code_file_inventory(topic, root)
    phase_counts = {phase: 0 for phase in sorted(GRID_PHASES)}
    for item in scripts:
        if item["classification"] == "PYTEST_TEST_MODULE":
            continue
        phase = next((hint.split(":", 1)[1] for hint in item["role_hints_not_verified"]
                      if hint.startswith("directory:")), None)
        if phase in phase_counts:
            phase_counts[phase] += 1
    return {
        "topic": topic.name,
        "deferred_test_candidates": deferred_test_candidates(topic),
        "pytest_modules": len(test_files),
        "grid_scripts_not_auto_run": phase_counts,
        "grid_script_count_not_auto_run": sum(
            item["classification"] == "UNCLASSIFIED_NON_TEST_CODE" for item in scripts
        ),
        "code_file_inventory": scripts,
        "coverage_note": coverage_note or (
            "declared pytest regression suite discovered" if test_files
            else "no pytest regression suite; non-test files inventoried but not executed"
        ),
        "suite_scope_limit": LEGACY_RESULT_READOUTS.get(topic.name, {}).get("suite_scope"),
    }


def resolve_topic(selector: str, topics: list[Path]) -> Path | None:
    normalized = selector.strip().replace("\\", "/").rstrip("/")
    if normalized.startswith("topics/"):
        normalized = normalized.split("/", 1)[1]
    matches = [
        topic for topic in topics
        if topic.name == normalized or topic.name.split("_", 1)[0] == normalized
    ]
    return matches[0] if len(matches) == 1 else None


def _pytest_suite(suite_id: str, paths: list[str], topic: str | None = None) -> Suite:
    return Suite(suite_id, "pytest", [sys.executable, "-m", "pytest", "-q", *paths], paths, topic)


def all_suites(root: Path = REPO_ROOT) -> tuple[list[Suite], list[dict[str, Any]], list[str]]:
    topics = topic_directories(root)
    suites: list[Suite] = []
    uncovered: list[dict[str, Any]] = []
    missing: list[str] = []

    core_tests = pytest_files(root / "core" / "05_tests")
    if core_tests:
        core_paths = ["core/05_tests"]
        suites.append(_pytest_suite("core-tests", core_paths))
    else:
        missing.append("core/05_tests: no pytest-compatible test modules found")

    runner_tests = pytest_files(root / "topics" / "tests")
    if runner_tests:
        suites.append(_pytest_suite("runner-tests", ["topics/tests"]))
    else:
        missing.append("topics/tests: no pytest-compatible runner test modules found")

    standard_tests = pytest_files(root / "docs" / "scripts" / "standard" / "tests")
    if standard_tests:
        suites.append(_pytest_suite("standard-tool-tests", ["docs/scripts/standard/tests"]))
    else:
        missing.append("docs/scripts/standard/tests: no pytest-compatible test modules found")

    audit_tests = root / "docs" / "scripts" / "audit" / "tests"
    if audit_tests.is_dir():
        suites.append(Suite(
            "calculation-audit-tests", "unittest",
            [sys.executable, "-m", "unittest", "discover", "-s", "docs/scripts/audit/tests", "-p", "test_*.py", "-v"],
            ["docs/scripts/audit/tests"],
        ))
    else:
        missing.append("docs/scripts/audit/tests: directory missing")

    for topic in topics:
        files = pytest_files(topic)
        uncovered.append(topic_inventory_record(topic, root))
        if files:
            relative = [path.relative_to(root).as_posix() for path in files]
            suites.append(_pytest_suite(f"topic:{topic.name}", relative, topic.name))
            if topic.name in LEGACY_RESULT_READOUTS:
                missing.append(f"{topic.name}: limited suite: {LEGACY_RESULT_READOUTS[topic.name]['suite_scope']}")
        else:
            missing.append(f"{topic.name}: no pytest regression suite discovered")

    for suite_id, script, args, success_pattern in (
        ("research-schema", "docs/scripts/standard/check_schema.py", [], r"^check_schema: 0 error\(s\)$"),
        ("test-preregistration", "docs/scripts/standard/check_preregistration.py", [], r"^check_preregistration: 0 error\(s\)$"),
        ("calculation-completeness", "docs/scripts/audit/audit_calculation_completeness.py", ["--check"], r'^\{"contracts":\d+,"discovered_routes":\d+,"errors":0,'),
        ("physics-tests", "docs/scripts/standard/check_physics_tests.py", ["core/05_tests/physics", "--min-physics", "1"], r"^check_physics_tests: physics=[1-9]\d* "),
    ):
        if (root / script).is_file():
            suites.append(Suite(suite_id, "physics" if suite_id == "physics-tests" else "check", [sys.executable, script, *args], [script, *args],
                                success_pattern=success_pattern))
        else:
            missing.append(f"{script}: required checker missing")

    return suites, uncovered, missing


def topic_suite(topic: Path, root: Path = REPO_ROOT) -> tuple[list[Suite], list[str]]:
    files = pytest_files(topic)
    if not files:
        return [], [f"{topic.name}: no pytest regression suite discovered"]
    relative = [path.relative_to(root).as_posix() for path in files]
    gaps = []
    if topic.name in LEGACY_RESULT_READOUTS:
        gaps.append(f"{topic.name}: limited suite: {LEGACY_RESULT_READOUTS[topic.name]['suite_scope']}")
    return [_pytest_suite(f"topic:{topic.name}", relative, topic.name)], gaps


def changed_suites(base: str, root: Path = REPO_ROOT) -> tuple[list[Suite], list[dict[str, Any]], list[str]]:
    proc = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", base, "--"],
        capture_output=True, text=True,
    )
    if proc.returncode:
        return [], [], [f"cannot read changed paths from {base}: {proc.stderr.strip()}"]
    changed = sorted(set(proc.stdout.splitlines()))
    if not changed:
        return [], [], [f"no changed paths found relative to {base}"]

    topics = topic_directories(root)
    suites: dict[str, Suite] = {}
    missing: list[str] = []
    topic_paths = {topic.name: topic for topic in topics}
    changed_topic_names = {
        topic.name for topic in topics
        if any(path.startswith((f"topics/{topic.name}/", f"docs/topics/{topic.name}/")) for path in changed)
    }
    core_or_shared = any(
        path.startswith((
            "core/", "docs/core/", "docs/scripts/core/", "docs/scripts/standard/",
            "docs/scripts/audit/", "docs/meta/", "docs/standard/", "docs/repo_paths.py",
        ))
        or path in {"docs/STANDARD.md", "topics/run_all_tests.py", "topics/run_full_verification.py"}
        for path in changed
    )

    if core_or_shared:
        selected, inventory, missing_all = all_suites(root)
        for suite in selected:
            suites[suite.suite_id] = suite
        return list(suites.values()), inventory, missing_all

    for name in sorted(changed_topic_names):
        topic = topic_paths[name]
        selected, gaps = topic_suite(topic, root)
        suites.update({suite.suite_id: suite for suite in selected})
        missing.extend(gaps)
    if not changed_topic_names:
        missing.append("changed files do not map to a Core/shared test suite or numbered Topic")
    inventory = [topic_inventory_record(topic, root, "affected topic")
                 for topic in topics if topic.name in changed_topic_names]
    return list(suites.values()), inventory, missing


def _write_log(report_dir: Path, suite_id: str, label: str, content: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", suite_id)
    path = report_dir / "logs" / f"{safe}.{label}.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _pytest_count(output: str) -> int | None:
    match = PYTEST_SUMMARY.search(output)
    if not match or match.group(0).lower().startswith("no tests"):
        return 0 if match else None
    return int(match.group(1))


def _pytest_counts(output: str) -> dict[str, int]:
    counts = {key: 0 for key in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")}
    # Tracebacks and captured stdout can contain fixture text like "999 passed".
    # Only the last complete framework summary is an outcome source; subtest
    # counts and warnings are not additional top-level test outcomes.
    label = r"(?:passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?|subtests? (?:passed|failed|skipped))"
    summary = re.compile(
        rf"\s*=*\s*(\d+\s+{label}(?:,\s*\d+\s+{label})*)"
        r"(?:\s+in\s+[\d.]+s(?:\s+\([\d:]+\))?)?\s*=*\s*"
    )
    summaries = [match.group(1) for line in output.splitlines()
                 if (match := summary.fullmatch(line))]
    if not summaries:
        return counts
    for number, label in re.findall(r"\b(\d+)\s+(passed|failed|errors?|skipped|xfailed|xpassed)\b", summaries[-1]):
        counts["errors" if label.startswith("error") else label] += int(number)
    return counts


def _unittest_counts(output: str) -> tuple[int | None, dict[str, int]]:
    ran = re.search(r"Ran\s+(\d+)\s+tests?", output)
    summary = re.search(r"(?:FAILED|OK)\s*(?:\(([^)]*)\))?", output)
    details = summary.group(1) if summary and summary.group(1) else ""
    counts = {key: 0 for key in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")}
    labels = {
        "failures": "failed",
        "errors": "errors",
        "skipped": "skipped",
        "expected failures": "xfailed",
        "unexpected successes": "xpassed",
    }
    for label, key in labels.items():
        match = re.search(rf"(?:^|,\s*){re.escape(label)}=(\d+)", details)
        if match:
            counts[key] = int(match.group(1))
    ran_count = int(ran.group(1)) if ran else None
    if ran_count is not None:
        counts["passed"] = max(0, ran_count - sum(counts[key] for key in ("failed", "errors", "skipped", "xfailed", "xpassed")))
    return ran_count, counts


def _classify(suite: Suite, returncode: int, output: str, collected: int | None = None) -> tuple[str, dict[str, int]]:
    counts = _pytest_counts(output) if suite.kind == "pytest" else {}
    if suite.kind == "pytest":
        if returncode == 5 or collected == 0 or COLLECTION_ERROR.search(output):
            return "INCOMPLETE", counts
        if returncode != 0 or counts.get("failed", 0) or counts.get("errors", 0) or counts.get("xpassed", 0):
            return "FAIL", counts
        if counts.get("skipped", 0) or counts.get("xfailed", 0) or not counts.get("passed", 0):
            return "INCOMPLETE", counts
        if collected is not None and sum(counts.values()) != collected:
            return "INCOMPLETE", counts
        return "PASS", counts

    if suite.kind == "unittest":
        ran, counts = _unittest_counts(output)
        if ran in (None, 0):
            return "INCOMPLETE", counts
        if returncode != 0 or counts["failed"] or counts["errors"] or counts["xpassed"]:
            return "FAIL", counts
        if counts["skipped"]:
            return "INCOMPLETE", counts
        return "PASS", counts

    if returncode != 0:
        return "FAIL", {}
    if suite.success_pattern is None or not re.search(suite.success_pattern, output, re.M):
        return "INCOMPLETE", {}
    if suite.kind == "physics":
        # This checker runs pytest internally; its zero exit does not mean
        # every requested physical test executed (pytest permits skips).
        counts = _pytest_counts(output)
        if counts["failed"] or counts["errors"] or counts["xpassed"]:
            return "FAIL", counts
        if counts["skipped"] or counts["xfailed"] or not counts["passed"]:
            return "INCOMPLETE", counts
        return "PASS", counts
    return "PASS", {}


def run_suite(suite: Suite, report_dir: Path) -> SuiteResult:
    started = time.monotonic()
    collected: int | None = None
    collection_output = ""
    if suite.kind == "pytest":
        collect_command = [sys.executable, "-m", "pytest", "--collect-only", "-q", *suite.paths]
        try:
            collect = subprocess.run(
                collect_command, cwd=REPO_ROOT, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=suite.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            stdout_log = _write_log(report_dir, suite.suite_id, "collect.stdout", str(output))
            return SuiteResult(suite.suite_id, suite.kind, suite.topic, collect_command,
                               "INCOMPLETE", None, time.monotonic() - started,
                               stdout_log=stdout_log, note="pytest collection timed out")
        collection_output = collect.stdout + collect.stderr
        collected = _pytest_count(collection_output)
        _write_log(report_dir, suite.suite_id, "collect.stdout", collect.stdout)
        _write_log(report_dir, suite.suite_id, "collect.stderr", collect.stderr)
        if collect.returncode != 0 or collected in (None, 0) or COLLECTION_ERROR.search(collection_output):
            return SuiteResult(
                suite.suite_id, suite.kind, suite.topic, collect_command, "INCOMPLETE",
                collect.returncode, time.monotonic() - started, collected=collected,
                stdout_log=_write_log(report_dir, suite.suite_id, "stdout", collect.stdout),
                stderr_log=_write_log(report_dir, suite.suite_id, "stderr", collect.stderr),
                note="collection failed or found no tests; suite execution was not reported as a pass",
            )

    try:
        proc = subprocess.run(
            suite.command, cwd=REPO_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=suite.timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return SuiteResult(
            suite.suite_id, suite.kind, suite.topic, suite.command, "INCOMPLETE", None,
            time.monotonic() - started, collected=collected,
            stdout_log=_write_log(report_dir, suite.suite_id, "stdout", stdout),
            stderr_log=_write_log(report_dir, suite.suite_id, "stderr", stderr),
            note=f"command timed out after {suite.timeout_seconds}s",
        )

    output = proc.stdout + proc.stderr
    if suite.kind == "unittest":
        collected, _ = _unittest_counts(output)
    status, counts = _classify(suite, proc.returncode, output, collected)
    return SuiteResult(
        suite.suite_id, suite.kind, suite.topic, suite.command, status,
        proc.returncode, time.monotonic() - started, collected=collected,
        passed=counts.get("passed"), failed=counts.get("failed"),
        errors=counts.get("errors"),
        skipped=counts.get("skipped"), xfailed=counts.get("xfailed"),
        xpassed=counts.get("xpassed"),
        stdout_log=_write_log(report_dir, suite.suite_id, "stdout", proc.stdout),
        stderr_log=_write_log(report_dir, suite.suite_id, "stderr", proc.stderr),
        note="output is diagnostic only; scientific claim status is not inferred from process success",
    )


def _render_markdown_report(report: dict[str, Any]) -> str:
    request = report["request"]
    results = report["results"]
    research = report["registered_research_results"]
    summary = {
        key: sum(item.get(key) or 0 for item in results)
        for key in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")
    }
    lines = [
        "# Core and Topic test-run report",
        "",
        "> Software regression report only. It does not validate UET physics or upgrade research claims.",
        "",
        "## Run identity",
        "",
        f"- Revision: `{report['revision']}`" + (" (working tree dirty)" if report["working_tree_dirty"] else ""),
        f"- Started: {report['created_utc']}",
        f"- Python: `{report['environment']['python'].splitlines()[0]}`",
        f"- Request: `{('--all' if request['all'] else '--topic ' + str(request['topic']) if request['topic'] else '--changed ' + str(request['changed_base']))}`",
        f"- Numbered Topics discovered: {len(report['topic_inventory'])}",
        f"- Program exit code: `{report.get('program_exit_code', 'not recorded')}`",
        "",
        "## Test suites actually run",
        "",
        "| Suite | Status | Collected/run | Passed | Failed | Errors | Skipped | Seconds |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in results:
        count = item.get("collected")
        if count is None:
            count = "—"
        seconds = f"{item['duration_seconds']:.1f}"
        lines.append(
            f"| `{item['suite_id']}` | **{item['status']}** | {count} | "
            f"{item.get('passed') if item.get('passed') is not None else '—'} | "
            f"{item.get('failed') if item.get('failed') is not None else '—'} | "
            f"{item.get('errors') if item.get('errors') is not None else '—'} | "
            f"{item.get('skipped') if item.get('skipped') is not None else '—'} | {seconds} |"
        )
    lines.extend([
        "",
        "Aggregate pytest/unittest outcomes: " + ", ".join(f"{key}={value}" for key, value in summary.items()) + ".",
        "",
        "## Commands and logs",
        "",
    ])
    for item in results:
        command = " ".join(str(part) for part in item["command"])
        lines.extend([
            f"- `{item['suite_id']}` — `{command}`",
            f"  - stdout: `{item.get('stdout_log') or 'not produced'}`",
            f"  - stderr: `{item.get('stderr_log') or 'not produced'}`",
        ])
        if item.get("note"):
            lines.append(f"  - note: {item['note']}")
    lines.extend(["", "## Topics without an automatic regression suite", ""])
    gaps = [entry for entry in report["uncovered_or_missing"] if "no pytest regression suite" in entry]
    if gaps:
        lines.extend(f"- INCOMPLETE: {entry}" for entry in gaps)
    else:
        lines.append("None in the requested scope.")
    lines.extend(["", "## Deferred test candidates (not executed)", ""])
    for topic in report["topic_inventory"]:
        for candidate in topic.get("deferred_test_candidates", []):
            lines.append(f"- `{topic['topic']}/{candidate['path']}`: {candidate['reason']}; source `{candidate['source_sha256']}`")
    other_gaps = [entry for entry in report["uncovered_or_missing"] if entry not in gaps]
    if other_gaps:
        lines.extend(["", "## Other coverage gaps", ""])
        lines.extend(f"- INCOMPLETE: {entry}" for entry in other_gaps)
    lines.extend([
        "",
        "## Registered research outcomes (read only)",
        "",
        "These records were copied from `docs/standard/results/*.json`; no producer was rerun and no research outcome was inferred from software tests.",
        "",
        "| Outcome | Count |",
        "|---|---:|",
    ])
    lines.extend(f"| {key} | {value} |" for key, value in research["counts"].items())
    lines.extend(["", "## Legacy Topic result readouts (not v2 registration or a rerun)", ""])
    for item in report.get("legacy_topic_results", {}).get("items", []):
        lines.append(f"- `{item['topic']}`: **{item['outcome']}**, copied from `{item['path']}` field `{item['outcome_field']}`. Scope: {item['suite_scope']}")
    lines.extend([
        "",
        "## Overall interpretation",
        "",
        "Suite `FAIL` means a software test/check failed. `INCOMPLETE` means the requested coverage could not be completed. Neither status is a scientific verdict. A research `FAIL` remains a research result and is not changed by this report.",
        "",
        f"JSON details: `report.json`.",
        "",
    ])
    return "\n".join(lines)


def _revision(root: Path) -> str:
    proc = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def _dirty(root: Path) -> bool:
    proc = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True)
    return bool(proc.stdout.strip()) if proc.returncode == 0 else True


def _print_inventory(inventory: list[dict[str, Any]], verbose: bool = False) -> None:
    for item in inventory:
        phase_counts = item.get("grid_scripts_not_auto_run", {})
        phase_summary = ", ".join(f"{phase}={count}" for phase, count in phase_counts.items() if count)
        if not phase_summary:
            phase_summary = "none"
        print(
            f"  {item['topic']}: pytest modules={item['pytest_modules']}; "
            f"non-automatic Code scripts={item.get('grid_script_count_not_auto_run', 0)} ({phase_summary}); "
            f"{item['coverage_note']}"
        )
        for candidate in item.get("deferred_test_candidates", []):
            print(f"    DEFERRED: {candidate['path']}; {candidate['reason']}")
        if not verbose:
            continue
        for source in item.get("code_file_inventory", []):
            hints = ",".join(source["role_hints_not_verified"]) or "none"
            imports = ",".join(source["static_imports_not_guaranteed_available"]) or "none detected"
            reads = source["input_requirements"].split(": ", 1)[-1]
            writes = ",".join(source["static_write_calls"]) or "none detected; read-only not proven"
            invocation = source["invocation"] or "not declared"
            print(
                f"    CODE {source['path']} | {source['classification']} | hints={hints} | "
                f"command={invocation} ({source['invocation_status']}) | imports={imports} | "
                f"input-read-hints={reads} | output=UNKNOWN | writes={writes} | "
                f"overwrite-risk={source['overwrite_risk']}"
            )


def registered_research_results(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Read registered research outcomes verbatim; never infer them from tests."""
    result_root = root / "docs" / "standard" / "results"
    items = []
    paths = sorted(result_root.glob("*.json")) if result_root.is_dir() else []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            record = json.loads(path.read_text(encoding="utf-8-sig"))
            items.append({
                "path": relative,
                "result_id": record.get("result_id"),
                "claim_id": record.get("claim_id"),
                "level": record.get("level"),
                "outcome": record.get("outcome", "UNKNOWN"),
                "date": record.get("date"),
            })
        except (OSError, json.JSONDecodeError) as exc:
            items.append({"path": relative, "outcome": "UNREADABLE", "error": f"{type(exc).__name__}: {exc}"})
    counts = {outcome: sum(item.get("outcome") == outcome for item in items)
              for outcome in ("PASS", "FAIL", "INCONCLUSIVE")}
    counts["OTHER_OR_UNREADABLE"] = len(items) - sum(counts.values())
    return {"source": "docs/standard/results/*.json", "records_read_not_rerun": True,
            "counts": counts, "items": items}


def _program_exit_code(failed: int, incomplete: bool) -> int:
    """Coverage gaps take precedence so a partial failing run is never coded as 1."""
    if incomplete:
        return 2
    return 1 if failed else 0


def legacy_topic_results(inventory: list[dict[str, Any]], root: Path = REPO_ROOT) -> dict[str, Any]:
    items, errors = [], []
    for topic in inventory:
        config = LEGACY_RESULT_READOUTS.get(topic["topic"])
        if config is None:
            continue
        try:
            path = root / config["path"]
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            outcome = payload[config["outcome_field"]]
            if outcome not in {"PASS", "FAIL", "INCONCLUSIVE"}:
                raise ValueError("unknown outcome; no implicit conversion permitted")
            items.append({"topic": topic["topic"], **config, "outcome": outcome,
                          "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{topic['topic']}: legacy result readout unavailable: {exc}")
    return {"records_read_not_rerun": True, "items": items, "errors": errors}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run safe, discovered UET regression suites with explicit coverage.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--all", action="store_true", help="Core, repository checks and all numbered Topics")
    modes.add_argument("--topic", metavar="ID_OR_NAME", help="Only the selected Topic's pytest suite")
    modes.add_argument("--changed", metavar="BASE_REF", help="Affected Core/shared checks and Topic suites")
    parser.add_argument("--list", action="store_true", help="List planned commands without executing them")
    parser.add_argument("--verbose", action="store_true", help="Include per-file static inventory in --list output")
    parser.add_argument("--report-dir", type=Path, help="Directory for the JSON report and command logs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.all:
        suites, inventory, missing = all_suites()
    elif args.topic:
        topics = topic_directories()
        topic = resolve_topic(args.topic, topics)
        if topic is None:
            suites, inventory, missing = [], [], [f"topic selector is missing or ambiguous: {args.topic}"]
        else:
            suites, missing = topic_suite(topic)
            inventory = [topic_inventory_record(topic, REPO_ROOT,
                                                "selected topic" if suites else "no pytest regression suite")]
    else:
        suites, inventory, missing = changed_suites(args.changed)

    if args.list:
        print("Discovered topics and suite inventory:")
        _print_inventory(inventory, verbose=args.verbose)
        print("Planned commands:")
        for suite in suites:
            print(f"  [{suite.suite_id}] ({suite.kind}) {' '.join(suite.command)}")
            print("    environment: project Python; run cwd: repository root; logs/report: .uet-run-reports/<run>/")
        if missing:
            print("Not covered / incomplete:")
            for item in missing:
                print(f"  INCOMPLETE: {item}")
        # Listing is an inventory operation, not a coverage claim. Missing
        # suites remain printed as INCOMPLETE, but should not make a read-only
        # plan query look like a failed test run.
        return 0

    report_dir = args.report_dir
    if report_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        report_dir = REPO_ROOT / ".uet-run-reports" / f"{stamp}-{_revision(REPO_ROOT)[:10]}"
    elif not report_dir.is_absolute():
        report_dir = REPO_ROOT / report_dir
    if report_dir.exists() and any(report_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite a non-empty report directory: {report_dir}")
    report_dir.mkdir(parents=True, exist_ok=True)

    results: list[SuiteResult] = []
    for suite in suites:
        print(f"RUN  {suite.suite_id}", flush=True)
        result = run_suite(suite, report_dir)
        results.append(result)
        print(f"{result.status:10} {result.suite_id} ({result.duration_seconds:.1f}s)", flush=True)

    legacy_readouts = legacy_topic_results(inventory)
    missing.extend(legacy_readouts["errors"])
    failed = sum(result.status == "FAIL" for result in results)
    incomplete = bool(missing) or any(result.status == "INCOMPLETE" for result in results)
    program_exit_code = _program_exit_code(failed, incomplete)
    report = {
        "schema_version": 1,
        "kind": "SOFTWARE_REGRESSION_RUN_REPORT_NOT_SCIENTIFIC_VALIDATION",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "revision": _revision(REPO_ROOT),
        "working_tree_dirty": _dirty(REPO_ROOT),
        "environment": {"python": sys.version, "platform": platform.platform(), "cwd": str(Path.cwd())},
        "request": {"all": args.all, "topic": args.topic, "changed_base": args.changed},
        "program_exit_code": program_exit_code,
        "topic_inventory": inventory,
        "results": [asdict(result) for result in results],
        "uncovered_or_missing": missing,
        "registered_research_results": registered_research_results(),
        "legacy_topic_results": legacy_readouts,
        "scientific_claim_outcomes": "registered outcomes are copied verbatim above and were not rerun or inferred from software tests",
        "exit_semantics": {"0": "all requested suites completed with no software failures or omissions",
                           "1": "one or more tests/checks failed, with no incomplete suite",
                           "2": "coverage incomplete, collection/runtime prerequisite missing, timeout, or any combination including failure"},
    }
    report_path = report_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    readable_report_path = report_dir / "report.md"
    readable_report_path.write_text(_render_markdown_report(report), encoding="utf-8", newline="\n")

    print("\nSummary")
    print(f"  revision: {_revision(REPO_ROOT)}{' (dirty)' if report['working_tree_dirty'] else ''}")
    print(f"  suites: {len(results)}; passed: {sum(r.status == 'PASS' for r in results)}; failed: {failed}; incomplete: {sum(r.status == 'INCOMPLETE' for r in results)}")
    print(f"  coverage gaps: {len(missing)}; program exit code: {program_exit_code}")
    print("  test outcomes: " + ", ".join(
        f"{key}={sum(getattr(result, key) or 0 for result in results)}"
        for key in ("passed", "failed", "errors", "skipped", "xfailed", "xpassed")
    ))
    if missing:
        print(f"  uncovered items: {len(missing)}")
        for item in missing:
            print(f"    INCOMPLETE: {item}")
    print(f"  readable report: {readable_report_path}")
    print(f"  machine-readable report and logs: {report_path}")
    research_counts = report["registered_research_results"]["counts"]
    print("  registered research outcomes (read only, not rerun): " + ", ".join(
        f"{key}={value}" for key, value in research_counts.items()))
    print("  Research PASS/FAIL/INCONCLUSIVE is not derived from test process status.")
    for item in legacy_readouts["items"]:
        print(f"  legacy result (read only, not v2 registration): {item['topic']} = {item['outcome']}; {item['path']}#{item['outcome_field']}")

    return program_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
