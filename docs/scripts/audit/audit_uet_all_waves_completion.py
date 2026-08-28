"""Strict completion audit for the planned UET research waves.

This audit closes project-control status only.  It refuses to call the program
physically closed when any evidence file is missing/drifted, a wave lacks its
claim/controller boundary, or the foundation gate permits physical promotion.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CLOSURE = ROOT / "docs/core/artifacts/uet_all_waves_closure.json"
FOUNDATION = ROOT / "docs/core/artifacts/uet_foundation_dependency_gate.json"
CLOSURE_LOG = ROOT / "docs/core/UET_ALL_WAVES_CLOSURE_UPDATE_LOG.md"
REPORT = ROOT / "docs/core/UET_FOUNDATION_RESEARCH_PROGRAM_REPORT.md"
WAVE_LOG = ROOT / "docs/core/UET_WAVE3_WAVE10_UPDATE_LOG.md"
WORK_LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-08.md"
OUTPUT = ROOT / "docs/core/artifacts/uet_all_waves_completion_audit.json"
CORE_REGRESSION_TIMEOUT_SECONDS = 300


def load(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [str(item) for item in value.values() if isinstance(item, str)]
    return []


def evidence_audit(waves: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool, bool, list[str]]:
    rows: list[dict[str, Any]] = []
    all_present = True
    all_current = True
    failed: list[str] = []
    for wave in waves:
        wave_present = True
        wave_current = True
        wave_failed: list[str] = []
        evidence_rows: list[dict[str, Any]] = []
        for entry in wave.get("evidence", []):
            rel = entry.get("path")
            path = ROOT / rel if rel else ROOT / "__missing__"
            exists = bool(rel and path.exists())
            current_hash = sha256(path) if exists else None
            current = bool(exists and entry.get("sha256") == current_hash)
            parse_ok = True
            top_statuses: list[str] = []
            if exists and path.suffix.lower() == ".json":
                try:
                    payload = load(path)
                    if not isinstance(payload, (dict, list)):
                        parse_ok = False
                    if isinstance(payload, dict):
                        top_statuses = status_strings(payload.get("audit_status")) + status_strings(payload.get("status"))
                        if any(value.upper() == "FAIL" or value.upper().startswith("FAIL_") for value in top_statuses):
                            wave_failed.append(rel)
                except (OSError, ValueError, json.JSONDecodeError):
                    parse_ok = False
            if not exists or not parse_ok:
                wave_present = False
            if not current:
                wave_current = False
            evidence_rows.append({
                "path": rel,
                "exists": exists,
                "hash_matches_closure": current,
                "json_parse_ok": parse_ok,
                "top_level_statuses": top_statuses,
            })
        all_present = all_present and wave_present
        all_current = all_current and wave_current
        failed.extend(wave_failed)
        rows.append({
            "wave": wave.get("wave"),
            "name": wave.get("name"),
            "status": wave.get("status"),
            "physics_status": wave.get("physics_status"),
            "closure_status": wave.get("closure_status"),
            "controller": wave.get("controlling_blocker"),
            "claim_ceiling": wave.get("claim_ceiling"),
            "evidence": evidence_rows,
            "evidence_present": wave_present,
            "evidence_hashes_current": wave_current,
            "failed_evidence_paths": wave_failed,
            "boundary_complete": bool(
                wave.get("status")
                and wave.get("closure_status")
                and wave.get("controlling_blocker")
                and wave.get("claim_ceiling")
            ),
        })
    return rows, all_present, all_current, failed


def run_core_regression() -> dict[str, Any]:
    command = [sys.executable, "-m", "pytest", "-q", "docs/core/test"]
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=CORE_REGRESSION_TIMEOUT_SECONDS,
            check=False,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        normalized_output = re.sub(r" in \d+(?:\.\d+)?s", " in <elapsed>", output)
        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        return {
            "command": " ".join(command),
            "exit_code": result.returncode,
            "passed_count": int(passed_match.group(1)) if passed_match else None,
            "failed_count": int(failed_match.group(1)) if failed_match else 0,
            "status": "PASS" if result.returncode == 0 and failed_match is None else "FAIL",
            "tail": "\n".join(normalized_output.splitlines()[-12:]),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(command),
            "exit_code": None,
            "passed_count": None,
            "failed_count": None,
            "status": "FAIL_TIMEOUT",
            "tail": str(exc),
        }


def build(*, run_tests: bool = False) -> dict[str, Any]:
    closure = load(CLOSURE)
    foundation = load(FOUNDATION)
    waves = closure.get("waves", [])
    evidence_rows, evidence_present, hashes_current, failed_paths = evidence_audit(waves)
    wave_numbers = [wave.get("wave") for wave in waves]
    expected_numbers = list(range(12))
    log_text = CLOSURE_LOG.read_text(encoding="utf-8") if CLOSURE_LOG.exists() else ""
    required_docs = {
        "closure_log": CLOSURE_LOG.exists(),
        "foundation_report": REPORT.exists(),
        "wave_update_log": WAVE_LOG.exists(),
        "work_ledger": WORK_LEDGER.exists(),
    }
    log_wave_coverage = {str(number): f"| {number} |" in log_text for number in expected_numbers}
    foundation_snapshot = foundation.get("source_and_calibration_snapshot", {})
    downstream_policy = foundation.get("downstream_policy", {})
    checks = {
        "closure_artifact_passes": closure.get("audit_status") == "PASS",
        "exactly_twelve_planned_waves": wave_numbers == expected_numbers,
        "all_waves_have_closure_status": all(row.get("closure_status") in {"CLOSED_AS_BLOCKED", "CLOSED_WITH_CONDITIONS"} for row in evidence_rows),
        "all_waves_have_boundary": all(row.get("boundary_complete") for row in evidence_rows),
        "all_evidence_present_and_parseable": evidence_present,
        "all_evidence_hashes_current": hashes_current,
        "no_failed_evidence_artifact": not failed_paths,
        "closure_log_covers_all_waves": all(log_wave_coverage.values()),
        "required_report_and_ledger_exist": all(required_docs.values()),
        "foundation_gate_remains_blocked": foundation.get("status") == "BLOCKED",
        "physical_promotion_remains_disabled": foundation_snapshot.get("physical_promotion_allowed") is False,
        "physical_data_claims_remain_blocked": downstream_policy.get("physical_data_claims") == "BLOCKED",
        "closure_checks_pass": all(bool(value) for value in closure.get("checks", {}).values()),
    }
    regression = run_core_regression() if run_tests else {
        "command": "not_run_in_build(run_tests=False)",
        "exit_code": None,
        "passed_count": None,
        "failed_count": None,
        "status": "NOT_RUN",
        "tail": "",
    }
    checks["core_regression_passes"] = regression["status"] == "PASS" if run_tests else True
    audit_status = "PASS_WITH_FOUNDATION_PHYSICS_BLOCKED" if all(checks.values()) else "FAIL"
    return {
        "schema_version": "1.0",
        "artifact": "uet_all_waves_completion_audit",
        "generated_at": date.today().isoformat(),
        "audit_status": audit_status,
        "status": "PROGRAM_CONTROL_CLOSED_FOUNDATION_PHYSICS_NOT_CLOSED" if audit_status != "FAIL" else "BLOCKED_INCOMPLETE_CLOSURE_PACKET",
        "objective": "close every planned research wave as a bounded project-control lane without promoting blocked physics",
        "wave_count": len(waves),
        "waves": evidence_rows,
        "log_wave_coverage": log_wave_coverage,
        "required_documents": required_docs,
        "failed_evidence_paths": failed_paths,
        "core_regression": regression,
        "checks": checks,
        "foundation_boundary": {
            "status": foundation.get("status"),
            "claim_ceiling": foundation.get("claim_ceiling"),
            "physical_promotion_allowed": foundation_snapshot.get("physical_promotion_allowed"),
            "next_controller": foundation.get("next_controller"),
        },
        "claim_boundary": "This closes wave accounting, evidence integrity, logs, and claim boundaries; it does not claim that UET physics, SI mappings, GR, particles, galaxy dynamics, or global cosmology are established.",
        "next_controller": foundation.get("next_controller"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-core-test", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    report = build(run_tests=not args.skip_core_test)
    if not args.no_write:
        OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"audit_status={report['audit_status']}")
        print(f"status={report['status']}")
        print(f"wave_count={report['wave_count']}")
        print(f"core_regression={report['core_regression']['status']}")
        print(f"failed_evidence_paths={report['failed_evidence_paths']}")
        for key, value in report["checks"].items():
            print(f"{key}={value}")
    return 0 if report["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
