"""Compatibility shim for the migrated core tooling path."""

from __future__ import annotations

import runpy
from pathlib import Path

_CANONICAL_RELATIVE = "docs/scripts/core/maintenance/log/validate_logging_compliance.py"


def _run() -> None:
    current = Path(__file__).resolve()
    for ancestor in (current.parent, *current.parents):
        candidate = ancestor / _CANONICAL_RELATIVE
        if candidate.exists():
            runpy.run_path(str(candidate), run_name="__main__")
            return
    raise FileNotFoundError(f"canonical tooling script not found: {_CANONICAL_RELATIVE}")


if __name__ == "__main__":
    _run()
