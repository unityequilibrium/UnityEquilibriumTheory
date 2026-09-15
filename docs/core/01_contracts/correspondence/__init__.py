"""Canonical standard-physics correspondence contract surface."""

from .uet_gr_correspondence import (
    GR_CORRESPONDENCE_STATUS,
    GRBenchmarkRecord,
    flat_flrw_control,
    gr_correspondence_contract,
    minkowski_null_control,
    newtonian_poisson_residual,
    schwarzschild_exterior_null_control,
)

__all__ = [
    "GR_CORRESPONDENCE_STATUS",
    "GRBenchmarkRecord",
    "minkowski_null_control",
    "flat_flrw_control",
    "schwarzschild_exterior_null_control",
    "newtonian_poisson_residual",
    "gr_correspondence_contract",
]
