"""Compatibility entry point for the single repository regression runner."""

from __future__ import annotations

from run_all_tests import main


if __name__ == "__main__":
    raise SystemExit(main(["--all", *(__import__("sys").argv[1:])]))
