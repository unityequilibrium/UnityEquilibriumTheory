"""Compatibility shim for the canonical non-closed covariant implementation."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(globals(), "docs.core.02_equations.covariant.uet_covariant_nonclosed")
del _forward_public_symbols
