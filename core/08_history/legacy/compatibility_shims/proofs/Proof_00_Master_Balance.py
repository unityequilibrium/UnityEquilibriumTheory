"""Compatibility shim for the migrated proof path."""

from __future__ import annotations

import runpy
from pathlib import Path

_CANONICAL_RELATIVE = "docs/core/04_proofs/Proof_00_Master_Balance.py"


def _run() -> None:
    current = Path(__file__).resolve()
    for ancestor in (current.parent, *current.parents):
        candidate = ancestor / _CANONICAL_RELATIVE
        if candidate.exists():
            runpy.run_path(str(candidate), run_name="__main__")
            return
    raise FileNotFoundError(_CANONICAL_RELATIVE)


if __name__ == "__main__":
    _run()
