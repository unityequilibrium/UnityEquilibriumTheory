"""Run physics tests and report physics versus bookkeeping test counts.

docs/STANDARD.md section 6: only tests marked ``@pytest.mark.physics`` count as
evidence. Status-string, hash or file-existence assertions are bookkeeping.

Usage:
  python docs/scripts/standard/check_physics_tests.py [PATH ...] [--min-physics N]

Default PATH is core/05_tests/physics. Missing paths, collection errors, an
empty collection, or fewer than --min-physics physics tests are failures.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import REPO_ROOT  # noqa: E402

DEFAULT_PATHS = ["core/05_tests/physics"]


def collected(paths: list[str], marker: str | None) -> tuple[int, int, str]:
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", *paths]
    if marker:
        cmd += ["-m", marker]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    match = re.search(r"(\d+)(?:/\d+)? tests? (?:collected|selected)", proc.stdout)
    return (int(match.group(1)) if match else 0, proc.returncode, proc.stdout + proc.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", default=DEFAULT_PATHS)
    parser.add_argument("--min-physics", type=int, default=1)
    args = parser.parse_args(argv)
    missing = [p for p in args.paths if not (REPO_ROOT / p).exists()]
    if missing:
        print(f"check_physics_tests: missing requested paths: {missing}", file=sys.stderr)
        return 2
    paths = args.paths

    total, total_status, total_output = collected(paths, None)
    physics, physics_status, physics_output = collected(paths, "physics")
    if total_status != 0 or physics_status != 0:
        print("ERROR pytest collection failed", file=sys.stderr)
        print(total_output, file=sys.stderr)
        print(physics_output, file=sys.stderr)
        return 2
    print(f"check_physics_tests: physics={physics} bookkeeping={total - physics} paths={paths}")
    if physics < args.min_physics:
        print(f"ERROR fewer than {args.min_physics} physics tests collected")
        return 1
    if total == 0 or physics == 0:
        print("ERROR requested suite collected no tests or no physics tests", file=sys.stderr)
        return 2
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "physics", *paths], cwd=REPO_ROOT)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
