"""Compatibility shim for the canonical legacy Lorentz diagnostics."""

from __future__ import annotations

if __package__:
    from .core_compat import (
        forward_public_symbols as _forward_public_symbols,
        run_canonical_as_script as _run_canonical_as_script,
    )
else:
    import sys as _sys
    from pathlib import Path as _Path

    _current = _Path(__file__).resolve()
    for _parent in (_current, *_current.parents):
        if (_parent / "docs" / "core").is_dir():
            _sys.path.insert(0, str(_parent))
            break
    from docs.core.core_compat import (
        forward_public_symbols as _forward_public_symbols,
        run_canonical_as_script as _run_canonical_as_script,
    )
    del _sys, _Path, _current, _parent

if __name__ == "__main__":
    _run_canonical_as_script(
        "docs.core.02_equations.lorentz_noether.uet_lorentz"
    )
else:
    _forward_public_symbols(
        globals(), "docs.core.02_equations.lorentz_noether.uet_lorentz"
    )

del _forward_public_symbols
del _run_canonical_as_script
