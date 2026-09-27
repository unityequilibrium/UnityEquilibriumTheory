"""Read-only verification of a historical dirty-worktree funding snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PLAN = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json"
RECORD = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_funding_historical_snapshot_recovery.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def inspect_source(source_root: Path) -> dict:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    rows = []
    for item in plan["baseline"]["evidence"]:
        path = item["path"]
        source_file = source_root / path
        actual = sha256(source_file) if source_file.is_file() else None
        porcelain = git_value(source_root, "status", "--porcelain=v1", "--", path)
        state = "UNTRACKED" if porcelain.startswith("?? ") else "MODIFIED" if porcelain else "TRACKED_CLEAN"
        if actual is None:
            state = "MISSING"
        rows.append({
            "path": path,
            "expected_sha256": item["sha256"],
            "observed_sha256": actual,
            "git_worktree_state": state,
        })
    return {
        "source_branch": git_value(source_root, "branch", "--show-current"),
        "source_head_at_observation": git_value(source_root, "rev-parse", "HEAD"),
        "records": rows,
    }


def verify_record(record: dict, *, source_root: Path | None = None) -> dict:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    expected = {item["path"]: item["sha256"] for item in plan["baseline"]["evidence"]}
    rows = record["records"]
    by_path = {item["path"]: item for item in rows}
    checks = {
        "plan_paths_unique_and_complete": len(by_path) == len(rows) == len(expected) and set(by_path) == set(expected),
        "recorded_hashes_match_plan": all(
            by_path[path]["expected_sha256"] == digest == by_path[path]["observed_sha256"]
            for path, digest in expected.items()
        ),
        "source_branch_matches_plan": record["source_branch"] == plan["baseline"]["branch"],
        "historical_head_not_claimed_as_current_head": record["historical_plan_head"] == plan["baseline"]["head"]
        and record["source_head_at_observation"] != record["historical_plan_head"],
        "untracked_count": sum(row["git_worktree_state"] == "UNTRACKED" for row in rows) == 4,
        "modified_count": sum(row["git_worktree_state"] == "MODIFIED" for row in rows) == 2,
        "tracked_clean_count": sum(row["git_worktree_state"] == "TRACKED_CLEAN" for row in rows) == 2,
        "no_unlock": record["g0_ready"] is False and record["full_core_unlock"] is False
        and record["admission"] == "NOT_IMPORTED_PENDING_OWNER_HANDOFF_AND_REVALIDATION",
    }
    if source_root is not None:
        live = inspect_source(source_root)
        checks["live_source_matches_record"] = live == {
            "source_branch": record["source_branch"],
            "source_head_at_observation": record["source_head_at_observation"],
            "records": rows,
        }
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Read-only source worktree to recheck")
    args = parser.parse_args()
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    checks = verify_record(record, source_root=args.source_root)
    print(json.dumps(checks, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
