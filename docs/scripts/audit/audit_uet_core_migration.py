"""Run the organization/path/import/link controls for the UET core migration."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs" / "core"
AUDIT = CORE / "00_governance" / "uet_core_migration_enforcement_audit.json"
REPORT = CORE / "00_governance" / "UET_CORE_MIGRATION_ENFORCEMENT_REPORT.md"

AUDITS = {
    "paths": (ROOT / "docs/scripts/audit/audit_uet_core_paths.py", CORE / "00_governance/uet_core_paths_audit.json"),
    "imports": (ROOT / "docs/scripts/audit/audit_uet_core_imports.py", CORE / "00_governance/uet_core_imports_audit.json"),
    "links": (ROOT / "docs/scripts/audit/audit_uet_core_links.py", CORE / "00_governance/uet_core_links_audit.json"),
}


def run_audit(script: Path) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "script": script.relative_to(ROOT).as_posix(),
        "returncode": result.returncode,
        "stdout": result.stdout.strip()[-2000:],
        "stderr": result.stderr.strip()[-2000:],
    }


def build() -> dict[str, object]:
    executions = {name: run_audit(script) for name, (script, _) in AUDITS.items()}
    reports: dict[str, object] = {}
    for name, (_, path) in AUDITS.items():
        reports[name] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    structural_failures = [
        name for name, report in reports.items()
        if not isinstance(report, dict) or report.get("status") != "PASS"
    ]
    status = "PASS" if not structural_failures else "BLOCKED"
    return {
        "schema_version": "1.0",
        "artifact": "uet_core_migration_enforcement_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "docs/scripts/audit/audit_uet_core_migration.py",
        "status": status,
        "controlling_blocker": None if status == "PASS" else "core_migration_enforcement_subaudit_failed",
        "subaudits": reports,
        "executions": executions,
        "failed_subaudits": structural_failures,
        "claim_boundary": "organization/path/import/link controls only; no physics-status promotion",
    }


def render_report(result: dict[str, object]) -> str:
    lines = [
        "# UET Core Migration Enforcement Report",
        "",
        "> Organization controls only. A passing organization audit does not pass the physics foundation gate.",
        "",
        f"Generated at: {result['generated_at']}",
        f"Status: **{result['status']}**",
        "",
        "## Subaudits",
        "",
    ]
    for name, report in result["subaudits"].items():
        status = report.get("status", "MISSING") if isinstance(report, dict) else "MISSING"
        lines.append(f"- `{name}`: **{status}**")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The physical migration may improve discovery and compatibility, but it does not change equation meaning, evidence class, foundation status, or claim ceiling.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    result = build()
    AUDIT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(result), encoding="utf-8")
    print(json.dumps({"status": result["status"], "failed_subaudits": result["failed_subaudits"]}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
