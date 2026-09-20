"""Compatibility shim for the canonical conserved matter-space flux branch."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(globals(), "docs.core.02_equations.matter_space.uet_matter_space_flux_telegraph")
del _forward_public_symbols
