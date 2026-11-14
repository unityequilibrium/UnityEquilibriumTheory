"""Covariant balance identities for the conservative UET response parent.

The module exposes the Noether/Bianchi identity implied by the candidate
scalar-tensor formula evaluator.  It separates three statements that must not
be conflated:

* matter-number conservation, which requires its own current equation;
* matter stress-energy exchange, represented by a covector ``Q_m``; and
* total modeled balance, where matter and response exchange cancel.

No curved-spacetime derivatives are numerically approximated here.  The code
evaluates the exact local identity after the standard differential-geometric
commutator and contracted Bianchi identity have been applied.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    curvature_factor_base_derivative,
    response_potential_derivative,
    response_scalar_equation_residual,
)

COVARIANT_BALANCE_STATUS: Final[str] = "CANDIDATE_SYMBOLIC_NOETHER_BIANCHI_IDENTITY"

NATURAL_UNIT_BALANCE_DIMENSIONS: Final[dict[str, int]] = {
    "scalar_equation_residual": 3,
    "scalar_source": 3,
    "gradient_phi": 2,
    "stress_divergence": 5,
    "einstein_coupling": -2,
    "metric_residual_divergence": 3,
    "matter_number_divergence": 4,
}


def _scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _covector(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (4,):
        raise ValueError(f"{name} must have shape (4,), got {result.shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


@dataclass(frozen=True)
class CovariantExchangeLedger:
    """Exchange-completed local ledger in stress-divergence units."""

    reduced_scalar_source: float
    full_scalar_source: float
    matter_exchange: np.ndarray
    response_exchange: np.ndarray
    total_exchange: np.ndarray
    closure_max_abs: float
    unit_lane: str = "natural"

    @property
    def closed(self) -> bool:
        return self.closure_max_abs <= 1e-12


def canonical_response_stress_divergence(
    gradient_phi: Any,
    box_phi: float,
    phi: float,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Return ``div(T_phi) = (Z box(phi) - U') grad(phi)``.

    This is the divergence of the unscaled canonical response tensor.  The
    metric equation multiplies it by ``epsilon_nc``.
    """

    gradient = _covector(gradient_phi, "gradient_phi")
    box = _scalar(box_phi, "box_phi")
    bracket = (
        config.response_kinetic * box
        - response_potential_derivative(phi, config)
    )
    return bracket * gradient


def geometric_side_divergence_identity(
    gradient_phi: Any,
    curvature_scalar: float,
    phi: float,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Return the divergence of ``F(G+Lambda g)+(g box-nabla nabla)F``.

    With the ``(-,+,+,+)`` convention used by the parent, the contracted
    Bianchi identity and scalar commutator reduce this expression to
    ``-epsilon f'(R-2 Lambda) grad(phi)/2``.
    """

    gradient = _covector(gradient_phi, "gradient_phi")
    curvature = _scalar(curvature_scalar, "curvature_scalar")
    coefficient = (
        -0.5
        * config.epsilon_nc
        * curvature_factor_base_derivative(phi, config)
        * (curvature - 2.0 * config.cosmological_constant)
    )
    return coefficient * gradient


def expanded_metric_residual_divergence(
    matter_stress_divergence: Any,
    gradient_phi: Any,
    curvature_scalar: float,
    box_phi: float,
    phi: float,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Evaluate the expanded divergence of the metric residual."""

    matter_divergence = _covector(
        matter_stress_divergence, "matter_stress_divergence"
    )
    geometry = geometric_side_divergence_identity(
        gradient_phi, curvature_scalar, phi, config
    )
    response_divergence = canonical_response_stress_divergence(
        gradient_phi, box_phi, phi, config
    )
    return (
        geometry
        - config.einstein_coupling * matter_divergence
        - config.einstein_coupling
        * config.epsilon_nc
        * response_divergence
    )


def compact_metric_residual_divergence(
    matter_stress_divergence: Any,
    gradient_phi: Any,
    scalar_equation_residual: float,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Evaluate ``-kappa [div(T_m) + E_phi grad(phi)]``."""

    matter_divergence = _covector(
        matter_stress_divergence, "matter_stress_divergence"
    )
    gradient = _covector(gradient_phi, "gradient_phi")
    scalar_residual = _scalar(
        scalar_equation_residual, "scalar_equation_residual"
    )
    return -config.einstein_coupling * (
        matter_divergence + scalar_residual * gradient
    )


def evaluate_balance_identity(
    matter_stress_divergence: Any,
    gradient_phi: Any,
    curvature_scalar: float,
    box_phi: float,
    phi: float,
    config: CovariantResponseConfig,
) -> dict[str, Any]:
    """Compare expanded and compact forms of the local Noether identity."""

    scalar_residual = response_scalar_equation_residual(
        curvature_scalar, box_phi, phi, config
    )
    expanded = expanded_metric_residual_divergence(
        matter_stress_divergence,
        gradient_phi,
        curvature_scalar,
        box_phi,
        phi,
        config,
    )
    compact = compact_metric_residual_divergence(
        matter_stress_divergence,
        gradient_phi,
        scalar_residual,
        config,
    )
    difference = expanded - compact
    return {
        "scalar_equation_residual": scalar_residual,
        "expanded": expanded,
        "compact": compact,
        "difference": difference,
        "max_abs_difference": float(np.max(np.abs(difference))),
    }


def exchange_completed_ledger(
    reduced_scalar_source: float,
    gradient_phi: Any,
    config: CovariantResponseConfig,
) -> CovariantExchangeLedger:
    """Build a regular exchange ledger for ``E_phi = epsilon j_phi``.

    The full source is nested as ``J_phi = epsilon_nc * j_phi``.  Consequently
    both exchange covectors vanish exactly in the GR limit without dividing by
    ``epsilon_nc``.
    """

    reduced_source = _scalar(reduced_scalar_source, "reduced_scalar_source")
    gradient = _covector(gradient_phi, "gradient_phi")
    full_source = config.epsilon_nc * reduced_source
    matter_exchange = -full_source * gradient
    response_exchange = full_source * gradient
    total = matter_exchange + response_exchange
    return CovariantExchangeLedger(
        reduced_scalar_source=reduced_source,
        full_scalar_source=float(full_source),
        matter_exchange=matter_exchange,
        response_exchange=response_exchange,
        total_exchange=total,
        closure_max_abs=float(np.max(np.abs(total))),
    )


def sourced_on_shell_metric_divergence(
    reduced_scalar_source: float,
    gradient_phi: Any,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Return the metric-residual divergence for the exchange-completed shell."""

    ledger = exchange_completed_ledger(reduced_scalar_source, gradient_phi, config)
    return compact_metric_residual_divergence(
        ledger.matter_exchange,
        gradient_phi,
        ledger.full_scalar_source,
        config,
    )


def matter_number_balance_residual(covariant_divergence: float) -> float:
    """Validate and return ``nabla_mu N^mu`` without equating it to stress exchange."""

    return _scalar(covariant_divergence, "matter_number_current_divergence")


def balance_contract() -> dict[str, Any]:
    """Return the machine-readable scope and claim ceiling of this module."""

    return {
        "status": COVARIANT_BALANCE_STATUS,
        "identity": "div(E_metric)_nu = -kappa[div(T_m)_nu + E_phi grad_nu(phi)]",
        "exchange_source_nesting": "J_phi = epsilon_nc * j_phi",
        "matter_exchange": "Q_m_nu = -J_phi grad_nu(phi)",
        "response_exchange": "Q_response_nu = +J_phi grad_nu(phi)",
        "total_exchange": "Q_m_nu + Q_response_nu = 0",
        "matter_number_equation_independent": True,
        "derived_trace_imported": False,
        "causal_kernel_implemented": False,
        "curved_derivative_solver_implemented": False,
        "mass_dimensions": dict(NATURAL_UNIT_BALANCE_DIMENSIONS),
    }
