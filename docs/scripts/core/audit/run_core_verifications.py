"""
Run core-topic verification commands and write transparent artifacts.

This runner does not certify scientific correctness. It records what actually happened when
the repository's current VERIFICATION_SPEC.md command is executed: exit code, timeout, output,
input hashes, input-path resolution, and environment details.
"""

from __future__ import annotations

# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


DOCS_ROOT = _UET_REPO_ROOT / "docs"
REPO_ROOT = DOCS_ROOT.parent
TOPICS_ROOT = DOCS_ROOT / "topics"
READINESS_FILE = DOCS_ROOT / "meta" / "topic_readiness.json"
SPEC_FILE = "VERIFICATION_SPEC.md"
OUTPUT_LIMIT = 20000
RUNNER_ARTIFACT_ROOT = DOCS_ROOT / "meta" / "core_verification_artifacts"


def load_core_topics() -> list[str]:
    data = json.loads(READINESS_FILE.read_text(encoding="utf-8"))
    names = [
        entry["name"]
        for entry in data["topics"]
        if entry.get("scope_class") == "core_research"
    ]
    return sorted(names, key=topic_key)


def topic_key(name: str) -> tuple[int, int, str]:
    match = re.match(r"^0\.(\d+)_", name)
    if not match:
        return (99, 99, name)
    return (0, int(match.group(1)), name)


def extract_next_backtick_value(lines: list[str], marker: str) -> str | None:
    for index, line in enumerate(lines):
        if marker in line:
            for candidate in lines[index + 1 : index + 6]:
                match = re.search(r"\x60([^\x60]+)\x60", candidate)
                if match:
                    return match.group(1).strip()
                stripped = candidate.strip().lstrip("-").strip()
                if stripped and not stripped.startswith("#"):
                    return stripped
    return None


def extract_input_paths(lines: list[str]) -> list[str]:
    input_paths: list[str] = []
    in_inputs = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- Inputs:"):
            in_inputs = True
            continue
        if in_inputs and (
            stripped.startswith("- Baseline:")
            or stripped.startswith("- Reported metrics:")
            or stripped.startswith("- Fixed threshold:")
            or stripped.startswith("- Current threshold:")
            or stripped.startswith("- Artifact target:")
            or stripped.startswith("- Interpretation:")
        ):
            break
        if in_inputs:
            for match in re.finditer(r"\x60([^\x60]+)\x60", line):
                value = match.group(1).strip()
                if value and value not in input_paths:
                    input_paths.append(value)
    return input_paths


def parse_spec(topic_dir: Path) -> tuple[str | None, str, list[str]]:
    spec_path = topic_dir / SPEC_FILE
    if not spec_path.exists():
        return None, "Result/artifacts/missing_verification_spec.json", []
    lines = spec_path.read_text(encoding="utf-8").splitlines()
    command = extract_next_backtick_value(lines, "Primary command")
    artifact = extract_next_backtick_value(lines, "Artifact target")
    if not artifact:
        artifact = f"Result/artifacts/{topic_dir.name.lower()}_verification.json"
    return command, artifact, extract_input_paths(lines)


def resolve_command(command: str) -> list[str]:
    parts = shlex.split(command, posix=False)
    if not parts:
        return []
    if parts[0].lower() in {"python", "python.exe", "py"}:
        parts[0] = sys.executable
    return parts


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def resolve_input_path(
    topic_dir: Path, input_path: str, repo_root: Path = REPO_ROOT
) -> dict[str, object]:
    """Resolve an input from topic_dir first, then repo_root.

    If both candidates exist as different files, return ambiguous instead of
    choosing silently. This keeps path drift visible in the run contract.
    """

    declared = Path(input_path)
    if declared.is_absolute():
        candidates = [(declared, "absolute")]
    else:
        candidates = [
            (topic_dir / declared, "topic_dir"),
            (repo_root / declared, "repo_root"),
        ]

    existing: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    for candidate, base in candidates:
        resolved = candidate.resolve()
        if resolved.is_file() and resolved not in seen:
            existing.append((resolved, base))
            seen.add(resolved)

    if len(existing) > 1:
        return {
            "path": input_path,
            "status": "ambiguous",
            "resolution_status": "ambiguous",
            "candidates": [
                {
                    "path": _display_path(path, repo_root),
                    "resolution_base": base,
                }
                for path, base in existing
            ],
        }

    if not existing:
        return {
            "path": input_path,
            "status": "missing",
            "resolution_status": "missing",
            "candidates": [
                {
                    "path": _display_path(path, repo_root),
                    "resolution_base": base,
                }
                for path, base in candidates
            ],
        }

    path, base = existing[0]
    return {
        "path": input_path,
        "status": "present",
        "resolution_status": "resolved",
        "resolution_base": base,
        "resolved_path": _display_path(path, repo_root),
        "sha256": sha256_file(path),
        "bytes": str(path.stat().st_size),
    }


def collect_input_hashes(
    topic_dir: Path, input_paths: list[str], repo_root: Path = REPO_ROOT
) -> list[dict[str, object]]:
    return [resolve_input_path(topic_dir, path, repo_root) for path in input_paths]


def trim_output(value: str) -> str:
    if len(value) <= OUTPUT_LIMIT:
        return value
    return value[-OUTPUT_LIMIT:]


def runner_artifact_path(topic_name: str) -> Path:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", topic_name).strip("_").lower()
    return RUNNER_ARTIFACT_ROOT / f"{slug}_run_contract.json"


def run_topic(topic_name: str, timeout: int) -> dict[str, object]:
    topic_dir = TOPICS_ROOT / topic_name
    command, declared_artifact_rel, input_paths = parse_spec(topic_dir)
    declared_artifact_path = topic_dir / declared_artifact_rel
    declared_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    run_artifact_path = runner_artifact_path(topic_name)
    run_artifact_path.parent.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    input_hashes = collect_input_hashes(topic_dir, input_paths)
    input_statuses = {record["status"] for record in input_hashes}
    input_resolution_status = (
        "BLOCKED"
        if "ambiguous" in input_statuses
        else "WARN"
        if "missing" in input_statuses
        else "PASS"
    )
    result: dict[str, object] = {
        "schema_version": "1.1",
        "topic": topic_name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "python_executable": sys.executable,
        "verification_spec": str(topic_dir / SPEC_FILE),
        "declared_scientific_artifact_path": str(declared_artifact_path),
        "runner_artifact_path": str(run_artifact_path),
        "command": command,
        "input_hashes": input_hashes,
        "input_resolution_status": input_resolution_status,
        "timeout_seconds": timeout,
    }

    if not command:
        result.update(
            {
                "status": "blocked",
                "reason": "No primary command found in VERIFICATION_SPEC.md",
                "passed_run_contract": False,
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        )
        run_artifact_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    if "ambiguous" in input_statuses:
        result.update(
            {
                "status": "blocked",
                "reason": "One or more declared inputs resolve to multiple different files.",
                "passed_run_contract": False,
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        )
        run_artifact_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    resolved = resolve_command(command)
    result["resolved_command"] = resolved
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = (
        str(REPO_ROOT)
        if not env.get("PYTHONPATH")
        else str(REPO_ROOT) + os.pathsep + env["PYTHONPATH"]
    )
    result["environment_overrides"] = {
        "PYTHONIOENCODING": env["PYTHONIOENCODING"],
        "PYTHONUTF8": env["PYTHONUTF8"],
        "PYTHONPATH_PREFIX": str(REPO_ROOT),
    }

    try:
        completed = subprocess.run(
            resolved,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=timeout,
            check=False,
        )
        result.update(
            {
                "status": "ran",
                "exit_code": completed.returncode,
                "passed_run_contract": completed.returncode == 0,
                "duration_seconds": round(time.monotonic() - started, 3),
                "stdout_tail": trim_output(completed.stdout),
                "stderr_tail": trim_output(completed.stderr),
            }
        )
    except subprocess.TimeoutExpired as exc:
        result.update(
            {
                "status": "timeout",
                "exit_code": None,
                "passed_run_contract": False,
                "duration_seconds": round(time.monotonic() - started, 3),
                "stdout_tail": trim_output(exc.stdout or ""),
                "stderr_tail": trim_output(exc.stderr or ""),
            }
        )
    except OSError as exc:
        result.update(
            {
                "status": "blocked",
                "reason": f"{type(exc).__name__}: {exc}",
                "exit_code": None,
                "passed_run_contract": False,
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        )

    result["declared_scientific_artifact_exists"] = declared_artifact_path.exists()
    if declared_artifact_path.exists() and declared_artifact_path.is_file():
        result["declared_scientific_artifact_sha256"] = sha256_file(declared_artifact_path)
        result["declared_scientific_artifact_bytes"] = declared_artifact_path.stat().st_size
    run_artifact_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--topic", action="append", default=[])
    args = parser.parse_args()

    topics = args.topic or load_core_topics()
    summary = []
    for topic in topics:
        result = run_topic(topic, args.timeout)
        summary.append(
            {
                "topic": topic,
                "status": result.get("status"),
                "exit_code": result.get("exit_code"),
                "passed_run_contract": result.get("passed_run_contract", False),
                "input_resolution_status": result.get("input_resolution_status"),
                "runner_artifact_path": result.get("runner_artifact_path"),
                "declared_scientific_artifact_path": result.get(
                    "declared_scientific_artifact_path"
                ),
            }
        )
        print(
            f"{topic}: status={result.get('status')} "
            f"exit={result.get('exit_code')} "
            f"inputs={result.get('input_resolution_status')} "
            f"pass={result.get('passed_run_contract', False)}"
        )

    summary_path = DOCS_ROOT / "meta" / "core_verification_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    failed = [item for item in summary if not item["passed_run_contract"]]
    print(f"Wrote summary: {summary_path}")
    print(f"Passed run contract: {len(summary) - len(failed)}/{len(summary)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
