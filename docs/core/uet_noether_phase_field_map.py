"""Compatibility shim for the canonical Noether phase-field map."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(
    globals(),
    "docs.core.02_equations.lorentz_noether.uet_noether_phase_field_map",
)
del _forward_public_symbols
