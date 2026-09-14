"""Compatibility shim for the canonical covariant balance implementation."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(globals(), "docs.core.02_equations.covariant.uet_covariant_balance")
del _forward_public_symbols
