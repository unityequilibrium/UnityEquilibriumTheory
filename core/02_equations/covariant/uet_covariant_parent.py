"""Integrated conservative parent contract for the UET covariant pilot.

The module composes the existing response, O(2) matter, and exchange-balance
formula evaluators. It adds no dissipative dynamics, trace feedback, metric PDE
solver, or empirical interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_balance import (
    CovariantExchangeLedger,
    exchange_completed_ledger,
)
from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    coupled_conservative_action_density,
    coupled_matter_stress_tensor,
    coupled_metric_residual,
    coupled_response_scalar_equation_residual,
    matter_amplitude_sq,
    matter_current_divergence,
    matter_eom_residual,
    matter_noether_current,
    reciprocal_interaction_derivatives,
)
from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    einstein_gr_residual,
    response_stress_tensor,
    validate_lorentz_metric,
)


COVARIANT_PARENT_STATUS: Final[str] = (
    "CANDIDATE_INTEGRATED_CONSERVATIVE_PARENT_FORMULA_EVALUATOR"
)


@dataclass(frozen=True)
class CovariantParentConfig:
    """Configuration pair for the natural-unit parent contract."""

    response: CovariantResponseConfig
    matter: CovariantMatterConfig
    unit_lane: str = "natural"

    def __post_init__(self) -> None:
        if self.unit_lane != "natural":
            raise NotImplementedError(
                "the covariant parent v1 supports only unit_lane='natural'"
            )
        if self.response.unit_lane != self.unit_lane:
            raise ValueError("response config unit lane must match parent unit lane")
        if self.matter.unit_lane != self.unit_lane:
            raise ValueError("matter config unit lane must match parent unit lane")


@dataclass(frozen=True)
class CovariantParentState:
    """One local covariant state at which the parent formulas are evaluated."""

    metric: Any
    inverse_metric: Any
    einstein_tensor: Any
    curvature_scalar: float
    phi: float
    gradient_phi: Any
    box_phi: float
    curvature_factor_base_hessian: Any
    matter_doublet: Any
    matter_gradients: Any
    matter_box: Any


@dataclass(frozen=True)
class CovariantParentResult:
    """Integrated conservative formula result.

    All tensor quantities use the declared (-,+,+,+) convention and natural
    units. The result intentionally contains no generated trace or observer
    record.
    """

    action_density: float
    metric_equation_residual: np.ndarray
    response_equation_residual: float
    matter_equation_residual: np.ndarray
    noether_current: np.ndarray
    noether_current_divergence: float
    matter_stress_energy: np.ndarray
    response_stress_energy: np.ndarray
    reciprocal_response_source: float
    reciprocal_matter_source: np.ndarray
    exchange_ledger: CovariantExchangeLedger
    gr_null_residual: np.ndarray
    gr_null_difference: np.ndarray | None
    unit_lane: str = "natural"

    @property
    def exact_gr_null_nesting(self) -> bool:
        return self.gr_null_difference is not None and bool(
            np.max(np.abs(self.gr_null_difference)) <= 1e-12
        )


def evaluate_conservative_parent(
    state: CovariantParentState,
    config: CovariantParentConfig,
) -> CovariantParentResult:
    """Evaluate the complete conservative scalar/O(2) parent contract."""

    metric, inverse = validate_lorentz_metric(
        state.metric,
        state.inverse_metric,
    )
    action_density = coupled_conservative_action_density(
        metric,
        inverse,
        state.curvature_scalar,
        state.gradient_phi,
        state.phi,
        state.matter_doublet,
        state.matter_gradients,
        config.response,
        config.matter,
    )
    matter_eom = matter_eom_residual(
        state.matter_box,
        state.matter_doublet,
        state.phi,
        config.response,
        config.matter,
    )
    response_eom = coupled_response_scalar_equation_residual(
        state.curvature_scalar,
        state.box_phi,
        state.phi,
        state.matter_doublet,
        config.response,
        config.matter,
    )
    noether_current = matter_noether_current(
        inverse,
        state.matter_doublet,
        state.matter_gradients,
        config.matter,
    )
    noether_divergence = matter_current_divergence(
        state.matter_box,
        state.matter_doublet,
        config.matter,
    )
    matter_stress = coupled_matter_stress_tensor(
        metric,
        inverse,
        state.matter_doublet,
        state.matter_gradients,
        state.phi,
        config.response,
        config.matter,
    )
    response_stress = response_stress_tensor(
        metric,
        inverse,
        state.gradient_phi,
        state.phi,
        config.response,
    )
    metric_residual = coupled_metric_residual(
        metric,
        state.einstein_tensor,
        state.phi,
        state.gradient_phi,
        state.curvature_factor_base_hessian,
        state.matter_doublet,
        state.matter_gradients,
        config.response,
        config.matter,
        inverse_metric=inverse,
    )
    response_source, matter_source = reciprocal_interaction_derivatives(
        state.phi,
        state.matter_doublet,
        config.response,
        config.matter,
    )

    reduced_scalar_source = (
        0.5
        * config.matter.response_coupling
        * matter_amplitude_sq(state.matter_doublet)
    )
    exchange_ledger = exchange_completed_ledger(
        reduced_scalar_source,
        state.gradient_phi,
        config.response,
    )
    gr_residual = einstein_gr_residual(
        metric,
        state.einstein_tensor,
        matter_stress,
        config.response,
    )
    gr_difference = None
    if config.response.epsilon_nc == 0.0:
        gr_difference = np.asarray(metric_residual - gr_residual, dtype=float)

    return CovariantParentResult(
        action_density=float(action_density),
        metric_equation_residual=np.asarray(metric_residual, dtype=float),
        response_equation_residual=float(response_eom),
        matter_equation_residual=np.asarray(matter_eom, dtype=float),
        noether_current=np.asarray(noether_current, dtype=float),
        noether_current_divergence=float(noether_divergence),
        matter_stress_energy=np.asarray(matter_stress, dtype=float),
        response_stress_energy=np.asarray(response_stress, dtype=float),
        reciprocal_response_source=float(response_source),
        reciprocal_matter_source=np.asarray(matter_source, dtype=float),
        exchange_ledger=exchange_ledger,
        gr_null_residual=np.asarray(gr_residual, dtype=float),
        gr_null_difference=gr_difference,
    )


def covariant_parent_contract() -> dict[str, Any]:
    """Return the public scope and claim boundary of the integrated parent."""

    return {
        "status": COVARIANT_PARENT_STATUS,
        "unit_lane": "natural",
        "field_content": {
            "metric": "standard Lorentz metric",
            "matter": "global O(2) scalar doublet",
            "response": "candidate scalar Phi",
        },
        "generator": "one conservative scalar-tensor-plus-O2 action density",
        "derived_relations": [
            "metric equation",
            "response equation",
            "matter equation",
            "O2 Noether current",
            "matter and response stress tensors",
            "reciprocal interaction sources",
            "local exchange-completed ledger",
        ],
        "gr_null_limit": "epsilon_nc=0 and Phi=Phi_* removes response corrections",
        "generated_trace_present": False,
        "observer_state_present": False,
        "dissipative_sector_present": False,
        "metric_pde_solver_present": False,
        "claim_boundary": (
            "integrated natural-unit conservative formula evaluator; "
            "not curved numerical GR, open-system closure, or physical validation"
        ),
        "next_controller": "lane_specific_covariant_coarse_graining_not_closed",
    }
