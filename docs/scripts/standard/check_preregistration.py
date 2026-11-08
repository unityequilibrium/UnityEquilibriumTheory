"""Enforce Test Card preregistration from git history (docs/STANDARD.md section 4).

Rules:
- the first commit in which a Test Card has status APPROVED (or CLOSED) is its
  approval commit; frozen fields may not change after it, in later commits or
  in the working tree
- every result that cites a Test Card must first appear in a commit that is a
  strict descendant of that approval commit (an uncommitted result is allowed
  only when the approval is already committed)

Frozen fields: hypothesis, observable, test_kind, theory_card, data_sources,
free_parameters, fixed_parameters, pass_criterion, fail_criterion.

Needs full git history (CI: actions/checkout with fetch-depth: 0).
Usage: python docs/scripts/standard/check_preregistration.py [--root PATH]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO_ROOT, RESULTS_DIR, TESTS_DIR, load_json, record_files  # noqa: E402

FROZEN_FIELDS = (
    "hypothesis",
    "observable",
    "test_kind",
    "theory_card",
    "data_sources",
    "free_parameters",
    "fixed_parameters",
    "pass_criterion",
    "fail_criterion",
)
APPROVED_STATES = {"APPROVED", "CLOSED"}


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
    )


def commits_touching(root: Path, rel: str) -> list[str]:
    out = git(root, "log", "--format=%H", "--reverse", "--", rel).stdout
    return [line for line in out.splitlines() if line.strip()]


def first_added_commit(root: Path, rel: str) -> str | None:
    out = git(root, "log", "--diff-filter=A", "--format=%H", "--reverse", "--", rel).stdout
    lines = [line for line in out.splitlines() if line.strip()]
    return lines[0] if lines else None


def show_json(root: Path, commit: str, rel: str) -> dict | None:
    proc = git(root, "show", f"{commit}:{rel}", check=False)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return None


def frozen(card: dict) -> dict:
    return {key: card.get(key) for key in FROZEN_FIELDS}


def is_strict_ancestor(root: Path, older: str, newer: str) -> bool:
    if older == newer:
        return False
    return git(root, "merge-base", "--is-ancestor", older, newer, check=False).returncode == 0


def run(root: Path) -> list[str]:
    errors: list[str] = []
    approvals: dict[str, str] = {}

    for path in record_files(root, TESTS_DIR):
        rel = path.relative_to(root).as_posix()
        try:
            current = load_json(path)
        except ValueError as exc:
            errors.append(f"{rel}: cannot read JSON: {exc}")
            continue
        test_id = current.get("test_id", path.stem)
        snapshot: dict | None = None
        for commit in commits_touching(root, rel):
            version = show_json(root, commit, rel)
            if version is None:
                continue
            if snapshot is None:
                if version.get("status") in APPROVED_STATES:
                    approvals[test_id] = commit
                    snapshot = frozen(version)
                continue
            if frozen(version) != snapshot:
                errors.append(f"test {test_id}: frozen fields changed after approval in commit {commit[:10]}")
        if snapshot is not None and frozen(current) != snapshot:
            errors.append(f"test {test_id}: working tree changes frozen fields after approval")
        if snapshot is None and current.get("status") in APPROVED_STATES:
            approvals.setdefault(test_id, "")  # approved only in the working tree

    for path in record_files(root, RESULTS_DIR):
        rel = path.relative_to(root).as_posix()
        try:
            result = load_json(path)
        except ValueError as exc:
            errors.append(f"{rel}: cannot read JSON: {exc}")
            continue
        test_id = result.get("test_card_id")
        if not test_id:
            continue
        approval = approvals.get(test_id)
        if approval is None:
            errors.append(f"result {result.get('result_id', path.stem)}: Test Card {test_id} was never approved")
            continue
        if approval == "":
            errors.append(f"result {result.get('result_id', path.stem)}: approval of Test Card {test_id} is not committed yet")
            continue
        added = first_added_commit(root, rel)
        if added is None:
            continue  # uncommitted result after a committed approval: allowed
        if not is_strict_ancestor(root, approval, added):
            errors.append(
                f"result {result.get('result_id', path.stem)}: first committed in {added[:10]}, "
                f"which does not come after Test Card {test_id} approval {approval[:10]}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    errors = run(args.root.resolve())
    for error in errors:
        print(f"ERROR {error}")
    print(f"check_preregistration: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
