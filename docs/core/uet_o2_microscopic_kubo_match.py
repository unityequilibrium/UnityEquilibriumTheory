"""Compatibility shim for `docs/core/02_equations/o2/uet_o2_microscopic_kubo_match.py`."""

from __future__ import annotations

if __package__:
    from .core_compat import forward_public_symbols as _forward_public_symbols
else:
    import sys as _sys
    from pathlib import Path as _Path

    _current = _Path(__file__).resolve()
    for _parent in (_current, *_current.parents):
        if (_parent / "docs" / "core").is_dir():
            _sys.path.insert(0, str(_parent))
            break
    from docs.core.core_compat import forward_public_symbols as _forward_public_symbols
    del _sys, _Path, _current, _parent

_forward_public_symbols(globals(), "docs.core.02_equations.o2.uet_o2_microscopic_kubo_match")
del _forward_public_symbols
