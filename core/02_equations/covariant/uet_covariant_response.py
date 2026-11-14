"""Covariant conservative parent for the UET GR correspondence program.

This module implements a natural-unit tensor-formula evaluator for the
candidate action documented in ``UET_GR_NONCLOSED_RESEARCH_SPEC.md``.  It is
deliberately not a metric PDE solver and does not implement the later causal,
dissipative sector.  Its strongest current result is an exact algebraic GR
closed limit at ``epsilon_nc = 0``.

The response scalar ``phi`` is a physical candidate degree of freedom.  The
derived history trace used by the nonrelativistic prototype is not imported
here and has no feedback path into these equations.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

COVARIANT_RESPONSE_MODEL_STATUS: Final[str] = (
    "CANDIDATE_CONSERVATIVE_TENSOR_FORMULA_EVALUATOR"
)
COVARIANT_RESPONSE_CLAIM_BOUNDARY: Final[tuple[str, ...]] = (
    "not_a_metric_pde_solver",
    "not_a_bianchi_or_noether_proof",
    "not_an_open_system_implementation",
    "not_external_gr_validation",
    "natural_units_only",
)

NATURAL_UNIT_MASS_DIMENSIONS: Final[dict[str, int]] = {
    "coordinate": -1,
    "derivative": 1,
    "phi": 1,
    "epsilon_nc": 0,
    "response_kinetic": 0,
    "response_mass_sq": 2,
    "response_quartic": 0,
    "curvature_coupling": -2,
    "equilibrium_density": 4,
    "einstein_coupling": -2,
    "cosmological_constant": 2,
    "lagrangian_scalar": 4,
    "stress_tensor": 4,
    "metric_equation_residual": 2,
}


@dataclass(frozen=True)
class CovariantResponseConfig:
    """Natural-unit coefficients for the conservative scalar-response pilot.

    Defaults are deterministic research controls, not measured constants.  A
    topic-specific SI conversion contract must be added before ``unit_lane``
    can accept anything except ``"natural"``.
    """

    epsilon_nc: float = 0.0
    einstein_coupling: float = 1.0
    cosmological_constant: float = 0.0
    phi_equilibrium: float = 0.0
    response_kinetic: float = 1.0
    response_mass_sq: float = 1.0
    response_quartic: float = 1.0
    curvature_coupling: float = 0.0
    equilibrium_density: float = 0.0
    unit_lane: str = "natural"

    def __post_init__(self) -> None:
        values = {
            "epsilon_nc": self.epsilon_nc,
            "einstein_coupling": self.einstein_coupling,
            "cosmological_constant": self.cosmological_constant,
            "phi_equilibrium": self.phi_equilibrium,
            "response_kinetic": self.response_kinetic,
            "response_mass_sq": self.response_mass_sq,
            "response_quartic": self.response_quartic,
            "curvature_coupling": self.curvature_coupling,
            "equilibrium_density": self.equilibrium_density,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("covariant-response coefficients must be finite")
        if self.epsilon_nc < 0.0:
            raise ValueError("epsilon_nc must be non-negative")
        if self.einstein_coupling <= 0.0:
            raise ValueError("einstein_coupling must be positive")
        if self.response_kinetic <= 0.0:
            raise ValueError("response_kinetic must be positive")
        if self.response_mass_sq < 0.0:
            raise ValueError("response_mass_sq must be non-negative")
        if self.response_quartic <= 0.0:
            raise ValueError("response_quartic must be positive")
        if self.unit_lane != "natural":
            raise NotImplementedError(
                "the covariant response v1 supports only unit_lane='natural'"
            )


def _finite_scalar(value: float, name: str) -> float:
    scalar = float(value)
    if not isfinite(scalar):
        raise ValueError(f"{name} must be finite")
    return scalar


def _finite_array(value: Any, name: str, shape: tuple[int, ...]) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def validate_lorentz_metric(
    metric: Any,
    inverse_metric: Any | None = None,
    *,
    tolerance: float = 1e-10,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate a four-dimensional Lorentz-signature metric and its inverse."""

    g = _finite_array(metric, "metric", (4, 4))
    if not np.allclose(g, g.T, rtol=0.0, atol=tolerance):
        raise ValueError("metric must be symmetric")
    eigenvalues = np.linalg.eigvalsh(g)
    if np.count_nonzero(eigenvalues < -tolerance) != 1 or np.count_nonzero(
        eigenvalues > tolerance
    ) != 3:
        raise ValueError("metric must have Lorentz signature (-,+,+,+)")
    if inverse_metric is None:
        inverse = np.linalg.inv(g)
    else:
        inverse = _finite_array(inverse_metric, "inverse_metric", (4, 4))
        if not np.allclose(inverse, inverse.T, rtol=0.0, atol=tolerance):
            raise ValueError("inverse_metric must be symmetric")
        if not np.allclose(g @ inverse, np.eye(4), rtol=tolerance, atol=tolerance):
            raise ValueError("inverse_metric is inconsistent with metric")
    return g, inverse


def response_displacement(phi: float, config: CovariantResponseConfig) -> float:
    """Return ``phi - phi_equilibrium``."""

    return _finite_scalar(phi, "phi") - config.phi_equilibrium


def response_potential(phi: float, config: CovariantResponseConfig) -> float:
    """Return ``U(phi)`` in natural mass-dimension four units."""

    delta = response_displacement(phi, config)
    return float(
        config.equilibrium_density
        + 0.5 * config.response_mass_sq * delta**2
        + 0.25 * config.response_quartic * delta**4
    )


def response_potential_derivative(
    phi: float, config: CovariantResponseConfig
) -> float:
    """Return the exact first derivative ``dU/dphi``."""

    delta = response_displacement(phi, config)
    return float(config.response_mass_sq * delta + config.response_quartic * delta**3)


def response_potential_hessian(
    phi: float, config: CovariantResponseConfig
) -> float:
    """Return the local curvature ``d^2U/dphi^2``."""

    delta = response_displacement(phi, config)
    return float(config.response_mass_sq + 3.0 * config.response_quartic * delta**2)


def curvature_factor_base(phi: float, config: CovariantResponseConfig) -> float:
    """Return ``f(phi) = xi (phi - phi_*)^2`` before epsilon nesting."""

    delta = response_displacement(phi, config)
    return float(config.curvature_coupling * delta**2)


def curvature_factor_base_derivative(
    phi: float, config: CovariantResponseConfig
) -> float:
    """Return ``df/dphi`` before epsilon nesting."""

    delta = response_displacement(phi, config)
    return float(2.0 * config.curvature_coupling * delta)


def curvature_factor(phi: float, config: CovariantResponseConfig) -> float:
    """Return ``F_epsilon = 1 + epsilon_nc f(phi)`` and reject sign flips."""

    factor = 1.0 + config.epsilon_nc * curvature_factor_base(phi, config)
    if not isfinite(factor) or factor <= 0.0:
        raise ValueError("curvature factor must remain finite and positive")
    return float(factor)


def effective_cosmological_constant(config: CovariantResponseConfig) -> float:
    """Return the equilibrium shift ``Lambda + kappa epsilon rho_*``."""

    return float(
        config.cosmological_constant
        + config.einstein_coupling
        * config.epsilon_nc
        * config.equilibrium_density
    )


def scalar_kinetic(
    inverse_metric: Any,
    gradient_phi: Any,
) -> float:
    """Return ``g^(mu nu) grad_mu(phi) grad_nu(phi)``."""

    inverse = _finite_array(inverse_metric, "inverse_metric", (4, 4))
    gradient = _finite_array(gradient_phi, "gradient_phi", (4,))
    return float(np.einsum("mn,m,n->", inverse, gradient, gradient))


def response_stress_tensor(
    metric: Any,
    inverse_metric: Any,
    gradient_phi: Any,
    phi: float,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Evaluate the symmetric canonical response stress tensor ``T_phi``."""

    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    gradient = _finite_array(gradient_phi, "gradient_phi", (4,))
    kinetic = scalar_kinetic(inverse, gradient)
    density = 0.5 * config.response_kinetic * kinetic + response_potential(phi, config)
    stress = config.response_kinetic * np.outer(gradient, gradient) - g * density
    return np.asarray(stress, dtype=float)


def einstein_gr_residual(
    metric: Any,
    einstein_tensor: Any,
    matter_stress: Any,
    config: CovariantResponseConfig,
) -> np.ndarray:
    """Return ``G + Lambda g - kappa T_m`` for the declared GR null model."""

    g, _ = validate_lorentz_metric(metric)
    einstein = _finite_array(einstein_tensor, "einstein_tensor", (4, 4))
    matter = _finite_array(matter_stress, "matter_stress", (4, 4))
    if not np.allclose(einstein, einstein.T, rtol=0.0, atol=1e-10):
        raise ValueError("einstein_tensor must be symmetric")
    if not np.allclose(matter, matter.T, rtol=0.0, atol=1e-10):
        raise ValueError("matter_stress must be symmetric")
    return (
        einstein
        + config.cosmological_constant * g
        - config.einstein_coupling * matter
    )


def uet_metric_residual(
    metric: Any,
    einstein_tensor: Any,
    matter_stress: Any,
    phi: float,
    gradient_phi: Any,
    curvature_factor_base_hessian: Any,
    config: CovariantResponseConfig,
    *,
    inverse_metric: Any | None = None,
) -> np.ndarray:
    """Evaluate the conservative UET metric-equation residual.

    ``curvature_factor_base_hessian`` is the covariant Hessian of
    ``f(phi) = xi (phi - phi_*)^2``.  The implementation computes its box by
    metric contraction, preventing a caller from supplying an inconsistent
    trace.  At ``epsilon_nc == 0`` response inputs are algebraically decoupled
    and the exact GR residual is returned.
    """

    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    einstein = _finite_array(einstein_tensor, "einstein_tensor", (4, 4))
    matter = _finite_array(matter_stress, "matter_stress", (4, 4))
    if not np.allclose(einstein, einstein.T, rtol=0.0, atol=1e-10):
        raise ValueError("einstein_tensor must be symmetric")
    if not np.allclose(matter, matter.T, rtol=0.0, atol=1e-10):
        raise ValueError("matter_stress must be symmetric")

    if config.epsilon_nc == 0.0:
        return einstein_gr_residual(g, einstein, matter, config)

    hessian = _finite_array(
        curvature_factor_base_hessian,
        "curvature_factor_base_hessian",
        (4, 4),
    )
    if not np.allclose(hessian, hessian.T, rtol=0.0, atol=1e-10):
        raise ValueError("curvature_factor_base_hessian must be symmetric")
    factor = curvature_factor(phi, config)
    response_stress = response_stress_tensor(
        g, inverse, gradient_phi, phi, config
    )
    box_factor_base = float(np.einsum("mn,mn->", inverse, hessian))
    derivative_term = config.epsilon_nc * (g * box_factor_base - hessian)
    return (
        factor * (einstein + config.cosmological_constant * g)
        + derivative_term
        - config.einstein_coupling
        * (matter + config.epsilon_nc * response_stress)
    )


def response_scalar_equation_residual(
    curvature_scalar: float,
    box_phi: float,
    phi: float,
    config: CovariantResponseConfig,
) -> float:
    """Return the full nested scalar equation, including ``epsilon_nc``.

    The residual is identically zero at the GR null model.  No division by the
    nesting parameter is used, so the decoupling limit is regular.
    """

    if config.epsilon_nc == 0.0:
        return 0.0
    scalar_curvature = _finite_scalar(curvature_scalar, "curvature_scalar")
    box_value = _finite_scalar(box_phi, "box_phi")
    bracket = (
        config.response_kinetic * box_value
        - response_potential_derivative(phi, config)
        + curvature_factor_base_derivative(phi, config)
        * (scalar_curvature - 2.0 * config.cosmological_constant)
        / (2.0 * config.einstein_coupling)
    )
    return float(config.epsilon_nc * bracket)


def conservative_lagrangian_scalar(
    curvature_scalar: float,
    scalar_kinetic_value: float,
    phi: float,
    matter_lagrangian: float,
    config: CovariantResponseConfig,
) -> float:
    """Return the scalar integrand before multiplication by ``sqrt(-g)``."""

    curvature = _finite_scalar(curvature_scalar, "curvature_scalar")
    kinetic = _finite_scalar(scalar_kinetic_value, "scalar_kinetic_value")
    matter = _finite_scalar(matter_lagrangian, "matter_lagrangian")
    return float(
        curvature_factor(phi, config)
        * (curvature - 2.0 * config.cosmological_constant)
        / (2.0 * config.einstein_coupling)
        - 0.5 * config.epsilon_nc * config.response_kinetic * kinetic
        - config.epsilon_nc * response_potential(phi, config)
        + matter
    )


def conservative_action_density(
    metric: Any,
    inverse_metric: Any,
    curvature_scalar: float,
    gradient_phi: Any,
    phi: float,
    matter_lagrangian: float,
    config: CovariantResponseConfig,
) -> float:
    """Return ``sqrt(-g)`` times the conservative Lagrangian scalar."""

    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    determinant = float(np.linalg.det(g))
    if determinant >= 0.0:
        raise ValueError("Lorentz metric determinant must be negative")
    kinetic = scalar_kinetic(inverse, gradient_phi)
    return float(
        np.sqrt(-determinant)
        * conservative_lagrangian_scalar(
            curvature_scalar,
            kinetic,
            phi,
            matter_lagrangian,
            config,
        )
    )


def model_contract() -> dict[str, Any]:
    """Return a compact machine-readable public contract for the evaluator."""

    return {
        "status": COVARIANT_RESPONSE_MODEL_STATUS,
        "unit_lane": "natural",
        "gr_null_parameter": {"epsilon_nc": 0.0},
        "response_role": "independent_candidate_scalar",
        "derived_trace_imported": False,
        "derived_trace_backreaction": False,
        "claim_boundary": list(COVARIANT_RESPONSE_CLAIM_BOUNDARY),
        "mass_dimensions": dict(NATURAL_UNIT_MASS_DIMENSIONS),
    }
