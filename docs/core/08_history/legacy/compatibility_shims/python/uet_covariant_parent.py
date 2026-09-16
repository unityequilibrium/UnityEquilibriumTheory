"""Compatibility shim for the canonical covariant parent implementation."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(globals(), "docs.core.02_equations.covariant.uet_covariant_parent")
del _forward_public_symbols
