"""Compatibility shim for the canonical covariant matter implementation."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(globals(), "docs.core.02_equations.covariant.uet_covariant_matter")
del _forward_public_symbols
