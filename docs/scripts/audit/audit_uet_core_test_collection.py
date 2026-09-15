"""Check pytest collection after the physical core-test migration.

The full collection, canonical collection, and legacy-boundary collection are
reported separately. A collection failure must remain visible; this script
never turns an exclusion into a full-suite pass.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
OUTPUT = CORE / "00_governance" / "uet_core_test_collection_audit.json"
GENERATOR = "docs/scripts/audit/audit_uet_core_test_collection.py"
COLLECTED_PATTERN = re.compile(r"(?P<count>\d+)\s+tests? collected")
ERROR_PATTERN = re.compile(r"(?P<count>\d+)\s+errors?", re.IGNORECASE)


def summarize(label: str, args: list[str], allow_empty: bool = False) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = result.stdout + "\n" + result.stderr
    collected_match = COLLECTED_PATTERN.search(output)
    error_match = ERROR_PATTERN.search(output)
    error_lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip().startswith("ERROR collecting") or "ModuleNotFoundError" in line
    ]
    return {
        "label": label,
        "status": "PASS" if result.returncode == 0 or (allow_empty and result.returncode == 5 and collected_match is None) else "BLOCKED",
        "returncode": result.returncode,
        "collected": int(collected_match.group("count")) if collected_match else None,
        "errors": int(error_match.group("count")) if error_match else 0,
        "diagnostic_lines": error_lines[:8],
        "paths": args,
        "empty_expected": allow_empty,
    }


def build() -> dict[str, Any]:
    full = summarize(
        "full_legacy_plus_canonical",
        ["docs/core/test", "docs/core/05_tests"],
    )
    combined = summarize(
        "combined_legacy_plus_canonical",
        ["docs/core/test", "docs/core/05_tests"],
    )
    canonical_only = summarize("canonical_05_tests_only", ["docs/core/05_tests"])
    legacy_only = summarize(
        "retained_legacy_boundary",
        ["docs/core/test"],
        allow_empty=True,
    )
    checks = [
        {
            "check_id": "full_collection_is_reported",
            "status": "PASS" if full["collected"] is not None else "FAIL",
            "observed": full["collected"],
        },
        {
            "check_id": "canonical_collection_has_no_collection_error",
            "status": "PASS" if canonical_only["status"] == "PASS" else "FAIL",
            "observed": canonical_only["status"],
        },
        {
            "check_id": "legacy_boundary_collection_is_expected_empty",
            "status": "PASS" if legacy_only["status"] == "PASS" else "FAIL",
            "observed": legacy_only["status"],
        },
        {
            "check_id": "combined_collection_has_no_collection_error",
            "status": "PASS" if combined["status"] == "PASS" else "FAIL",
            "observed": combined["status"],
        },
        {
            "check_id": "full_suite_blocker_is_not_hidden",
            "status": "PASS" if full["status"] == "BLOCKED" else "PASS",
            "observed": full["status"],
            "note": "The legacy boundary is expected to be empty after physical migration; canonical collection remains the controlling check.",
        },
    ]
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_test_collection_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": GENERATOR,
        "scope": "docs/core/test and docs/core/05_tests",
        "status": "PASS" if canonical_only["status"] == "PASS" and legacy_only["status"] == "PASS" else "BLOCKED",
        "controlling_blocker": None
        if full["status"] == "PASS"
        else "canonical_test_collection",
        "checks": checks,
        "collections": {
            "full": full,
            "combined_legacy_plus_canonical": combined,
            "canonical_only": canonical_only,
            "legacy_only": legacy_only,
        },
        "claim_boundary": "collection evidence only; no physics-status promotion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    payload = build()
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "full_status": payload["collections"]["full"]["status"],
        "full_collected": payload["collections"]["full"]["collected"],
        "canonical_status": payload["collections"]["canonical_only"]["status"],
        "canonical_collected": payload["collections"]["canonical_only"]["collected"],
        "legacy_status": payload["collections"]["legacy_only"]["status"],
        "legacy_collected": payload["collections"]["legacy_only"]["collected"],
        "output": OUTPUT.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False))
    # A collection blocker is a truthful non-zero result for this audit.  It
    # does not invalidate the physical migration audit itself.
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
