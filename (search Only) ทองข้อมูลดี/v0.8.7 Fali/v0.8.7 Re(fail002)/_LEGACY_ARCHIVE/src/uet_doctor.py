#!/usr/bin/env python3
"""
UET Harness Doctor

Quick sanity checks for the most common "it worked yesterday" issues:
- Wrong Python (conda base vs .venv)
- Running from the wrong working directory (uet_core) causing stdlib shadowing
- PYTHONPATH pointing at uet_core instead of repo root
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    here = Path.cwd().resolve()
    print("=== UET Doctor ===")
    print("cwd:", here)
    print("python:", sys.executable)
    print("sys.path[0]:", sys.path[0])

    # 1) Working directory check
    if here.name == "uet_core" and (here / "logging.py").exists():
        print("\n[FAIL] You are running from the `uet_core/` folder.")
        print("       That folder contains `logging.py` which can SHADOW Python stdlib `logging`.")
        print("       Fix: `cd` to the repo root (the folder that contains `scripts/` and `uet_core/`) and run again.\n")
        return 2

    # 2) sys.path shadowing check (PYTHONPATH)
    for p in sys.path[:5]:
        try:
            pp = Path(p).resolve()
        except Exception:
            continue
        if pp.name == "uet_core" and (pp / "logging.py").exists():
            print("\n[WARN] Your sys.path includes the `uet_core/` directory directly.")
            print("       That can cause stdlib shadowing (logging.py, etc.).")
            print("       Fix: remove uet_core from PYTHONPATH; add the repo ROOT instead.\n")
            break

    # 3) venv check
    venv = os.environ.get("VIRTUAL_ENV", "")
    if not venv:
        print("\n[WARN] VIRTUAL_ENV is not set (you may be using conda 'base' or system python).")
        print("       Recommended (PowerShell):")
        print("         cd <repo-root>")
        print("         .\\.venv\\Scripts\\Activate.ps1")
        print("         python -V")
    else:
        print("\n[OK] VIRTUAL_ENV:", venv)

    # 4) quick import smoke test
    try:
        import pandas  # noqa
        import matplotlib  # noqa
    except Exception as e:
        print("\n[FAIL] Import test failed:", repr(e))
        print("       Fix: activate .venv then `python -m pip install -r requirements.txt` (or install pandas/matplotlib).")
        return 3

    print("\n[OK] Basic environment looks sane.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
