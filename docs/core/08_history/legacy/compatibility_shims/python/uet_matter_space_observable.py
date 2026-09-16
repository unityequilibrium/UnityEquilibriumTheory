"""Compatibility shim for the canonical matter-space observable adapter."""

from .core_compat import forward_public_symbols as _forward_public_symbols

_forward_public_symbols(globals(), "docs.core.03_lanes.review.uet_matter_space_observable")
del _forward_public_symbols
