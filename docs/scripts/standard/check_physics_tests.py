"""Run physics tests and report physics versus bookkeeping test counts.

docs/STANDARD.md section 6: only tests marked ``@pytest.mark.physics`` count as
evidence. Status-string, hash or file-existence assertions are bookkeeping.

Usage:
  python docs/scripts/standard/check_physics_tests.py [PATH ...] [--min-physics N]

Default PATH is docs/core/05_tests/physics. Exit status is non-zero when a
physics test fails or fewer than --min-physics physics tests are collected.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO_ROOT  # noqa: E402

DEFAULT_PATHS = ["docs/core/05_tests/physics"]
NO_TESTS_COLLECTED = 5


def collected(paths: list[str], marker: str | None) -> int:
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", *paths]
    if marker:
        cmd += ["-m", marker]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    match = re.search(r"(\d+)(?:/\d+)? tests? (?:collected|selected)", proc.stdout)
    if match:
        return int(match.group(1))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", default=DEFAULT_PATHS)
    parser.add_argument("--min-physics", type=int, default=0)
    args = parser.parse_args(argv)
    paths = [p for p in args.paths if (REPO_ROOT / p).exists()]
    if not paths:
        print("check_physics_tests: no test paths exist; physics=0")
        return 1 if args.min_physics > 0 else 0

    total = collected(paths, None)
    physics = collected(paths, "physics")
    print(f"check_physics_tests: physics={physics} bookkeeping={total - physics} paths={paths}")
    if physics < args.min_physics:
        print(f"ERROR fewer than {args.min_physics} physics tests collected")
        return 1
    if physics == 0:
        return 0
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-m", "physics", *paths], cwd=REPO_ROOT
    )
    if proc.returncode == NO_TESTS_COLLECTED:
        return 0
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
