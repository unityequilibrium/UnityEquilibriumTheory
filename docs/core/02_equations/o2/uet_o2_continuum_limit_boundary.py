"""Scoped continuum-limit acceptance boundary for the Topic 13 collocation lane.

The existing tree-level/finite-cutoff artifact records a resolution sequence
whose response changes remain above the repository's declared ``1e-2``
continuum-controller threshold.  This module turns that observation into a
machine-readable boundary: the current discretization cannot be promoted to a
continuum result, while the finite-cutoff algebraic lane remains intact.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


CONTINUUM_LIMIT_BOUNDARY_STATUS = (
    "PASS_SCOPED_CONTINUUM_LIMIT_CURRENT_SCHEME_NO_GO"
)
CONTINUUM_ACCEPTANCE_THRESHOLD = 1.0e-2


@dataclass(frozen=True)
class ContinuumLimitBoundary:
    """A no-go assessment for one declared resolution sequence."""

    radial_orders: tuple[int, ...]
    channel_counts: tuple[int, ...]
    dc_responses: tuple[float, ...]
    relative_changes: tuple[float, ...]
    acceptance_threshold: float
    maximum_relative_change: float
    current_scheme_continuum_no_go: bool
    extrapolated_response_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False


def assess_continuum_limit(
    radial_orders: tuple[int, ...],
    channel_counts: tuple[int, ...],
    dc_responses: tuple[float, ...],
    relative_changes: tuple[float, ...],
    *,
    acceptance_threshold: float = CONTINUUM_ACCEPTANCE_THRESHOLD,
) -> ContinuumLimitBoundary:
    """Assess the declared sequence without extrapolating a limit."""

    if len(radial_orders) != len(channel_counts) or len(radial_orders) != len(dc_responses):
        raise ValueError("resolution arrays must have equal length")
    if len(relative_changes) != max(len(dc_responses) - 1, 0):
        raise ValueError("relative_changes must contain one adjacent change per pair")
    if len(dc_responses) < 2:
        raise ValueError("at least two resolution points are required")
    threshold = float(acceptance_threshold)
    if not isfinite(threshold) or threshold <= 0.0:
        raise ValueError("acceptance_threshold must be positive and finite")
    if any(int(order) != order or int(order) < 1 for order in radial_orders):
        raise ValueError("radial_orders must be positive integers")
    if any(int(count) != count or int(count) < 1 for count in channel_counts):
        raise ValueError("channel_counts must be positive integers")
    if not all(isfinite(float(value)) for value in (*dc_responses, *relative_changes)):
        raise ValueError("resolution values must be finite")
    maximum = max(float(value) for value in relative_changes)
    return ContinuumLimitBoundary(
        radial_orders=tuple(int(value) for value in radial_orders),
        channel_counts=tuple(int(value) for value in channel_counts),
        dc_responses=tuple(float(value) for value in dc_responses),
        relative_changes=tuple(float(value) for value in relative_changes),
        acceptance_threshold=threshold,
        maximum_relative_change=maximum,
        current_scheme_continuum_no_go=maximum > threshold,
    )


def continuum_limit_boundary_contract() -> dict[str, object]:
    """Return the scope and claim boundary for the no-go assessment."""

    return {
        "status": CONTINUUM_LIMIT_BOUNDARY_STATUS,
        "equations": {
            "adjacent_change": "r_i=abs(D_i-D_(i-1))/max(abs(D_(i-1)),1e-300)",
            "acceptance_controller": "max_i(r_i)<=1e-2 is required before continuum promotion",
            "current_result": "max_i(r_i)>1e-2 => no-go for the declared current discretization scheme",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "dc_response": "finite-cutoff formal natural-unit response",
            "threshold": "dimensionless relative change",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "acceptance-boundary audit over the existing action-derived resolution sequence",
        "observable": "finite-cutoff DC response stability under declared radial/channel refinement",
        "data_role": "ACTION_DERIVED_INTERNAL_CONVERGENCE_BOUNDARY_NO_SOURCE_ROWS",
        "closed_scope": [
            "the current resolution sequence is machine-readable",
            "the existing 1e-2 continuum-controller threshold is applied without adjustment",
            "the current discretization is rejected for continuum promotion when the sequence is nonconverged",
            "no extrapolated continuum response is emitted",
        ],
        "excluded_scope": [
            "mathematical no-go for every future discretization",
            "microscopic Bethe-Salpeter or SK/KMS matching",
            "physical Kubo coefficient",
            "SI map or alpha_Phi_K",
            "TTG validation",
        ],
        "claim_boundary": (
            "This closes only a scoped no-go for continuum promotion of the declared "
            "current finite-cutoff discretization. It does not prove that every future "
            "continuum formulation is impossible and does not close physical transport."
        ),
    }


__all__ = [
    "CONTINUUM_LIMIT_BOUNDARY_STATUS",
    "CONTINUUM_ACCEPTANCE_THRESHOLD",
    "ContinuumLimitBoundary",
    "assess_continuum_limit",
    "continuum_limit_boundary_contract",
]
