"""Covariant O(2) matter pilot coupled to the UET response scalar.

The module supplies the missing conservative matter-action layer for the UET
GR correspondence program.  Two real scalar components form an O(2) doublet,
equivalent to one complex scalar.  Their amplitude couples to the response
displacement through one action term, so the matter and response forces are
reciprocal variational derivatives of the same interaction.

The global O(2) symmetry gives an on-shell Noether-current identity.  This is
not yet a derivation of the conserved diffusive ``C`` equation used by
``matter_space_coupled_v1``: the relativistic amplitude is not automatically a
particle-number density, and Cahn-Hilliard dynamics requires a separate
constitutive or closed-time-path reduction.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    conservative_action_density,
    response_displacement,
    response_potential,
    response_scalar_equation_residual,
    uet_metric_residual,
    validate_lorentz_metric,
)

COVARIANT_MATTER_STATUS: Final[str] = (
    "CANDIDATE_O2_SCALAR_ACTION_WITH_RECIPROCAL_RESPONSE_COUPLING"
)

NATURAL_UNIT_MATTER_DIMENSIONS: Final[dict[str, int]] = {
    "matter_doublet": 1,
    "matter_gradient": 2,
    "matter_box": 3,
    "matter_kinetic": 0,
    "matter_mass_sq": 2,
    "matter_quartic": 0,
    "response_coupling": 1,
    "matter_potential": 4,
    "interaction_energy_density": 4,
    "matter_eom_residual": 3,
    "noether_current": 3,
    "current_divergence": 4,
    "stress_tensor": 4,
}


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _doublet(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (2,):
        raise ValueError(f"{name} must have shape (2,), got {result.shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


def _doublet_gradients(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (2, 4):
        raise ValueError(f"{name} must have shape (2, 4), got {result.shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


@dataclass(frozen=True)
class CovariantMatterConfig:
    """Natural-unit controls for the O(2) scalar matter pilot."""

    matter_kinetic: float = 1.0
    matter_mass_sq: float = 1.0
    matter_quartic: float = 1.0
    response_coupling: float = 0.0
    unit_lane: str = "natural"

    def __post_init__(self) -> None:
        values = {
            "matter_kinetic": self.matter_kinetic,
            "matter_mass_sq": self.matter_mass_sq,
            "matter_quartic": self.matter_quartic,
            "response_coupling": self.response_coupling,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("covariant-matter coefficients must be finite")
        if self.matter_kinetic <= 0.0:
            raise ValueError("matter_kinetic must be positive")
        if self.matter_quartic <= 0.0:
            raise ValueError("matter_quartic must be positive")
        if self.response_coupling < 0.0:
            raise ValueError("response_coupling must be non-negative")
        if self.unit_lane != "natural":
            raise NotImplementedError(
                "the covariant matter v1 supports only unit_lane='natural'"
            )


def matter_amplitude_sq(matter_doublet: Any) -> float:
    """Return ``C^2 = chi_1^2 + chi_2^2``."""

    fields = _doublet(matter_doublet, "matter_doublet")
    return float(np.dot(fields, fields))


def matter_potential(
    matter_doublet: Any,
    config: CovariantMatterConfig,
) -> float:
    """Return the O(2)-invariant quartic matter potential ``W(C)``."""

    amplitude_sq = matter_amplitude_sq(matter_doublet)
    return float(
        0.5 * config.matter_mass_sq * amplitude_sq
        + 0.25 * config.matter_quartic * amplitude_sq**2
    )


def interaction_energy_density(
    phi: float,
    matter_doublet: Any,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> float:
    """Return ``V_int = -epsilon h delta_phi C^2 / 2``."""

    delta = response_displacement(phi, response_config)
    amplitude_sq = matter_amplitude_sq(matter_doublet)
    return float(
        -0.5
        * response_config.epsilon_nc
        * matter_config.response_coupling
        * delta
        * amplitude_sq
    )


def reciprocal_interaction_derivatives(
    phi: float,
    matter_doublet: Any,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> tuple[float, np.ndarray]:
    """Return exact energy derivatives ``(dV_int/dphi, dV_int/dchi_A)``."""

    fields = _doublet(matter_doublet, "matter_doublet")
    epsilon_h = response_config.epsilon_nc * matter_config.response_coupling
    response_derivative = -0.5 * epsilon_h * float(np.dot(fields, fields))
    matter_derivative = -epsilon_h * response_displacement(
        phi, response_config
    ) * fields
    return float(response_derivative), np.asarray(matter_derivative, dtype=float)


def joint_potential_energy(
    phi: float,
    matter_doublet: Any,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> float:
    """Return the nested response-plus-matter potential energy density."""

    return float(
        matter_potential(matter_doublet, matter_config)
        + response_config.epsilon_nc * response_potential(phi, response_config)
        + interaction_energy_density(
            phi, matter_doublet, response_config, matter_config
        )
    )


def matter_kinetic_scalar(
    inverse_metric: Any,
    matter_gradients: Any,
) -> float:
    """Return ``sum_A g^(mu nu) grad_mu chi_A grad_nu chi_A``."""

    inverse = np.asarray(inverse_metric, dtype=float)
    if inverse.shape != (4, 4) or not np.all(np.isfinite(inverse)):
        raise ValueError("inverse_metric must be a finite array with shape (4, 4)")
    gradients = _doublet_gradients(matter_gradients, "matter_gradients")
    return float(np.einsum("mn,am,an->", inverse, gradients, gradients))


def coupled_matter_lagrangian_scalar(
    inverse_metric: Any,
    matter_gradients: Any,
    matter_doublet: Any,
    phi: float,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> float:
    """Return ``L_m = -Z_C (grad chi)^2/2 - W - V_int``."""

    kinetic = matter_kinetic_scalar(inverse_metric, matter_gradients)
    return float(
        -0.5 * matter_config.matter_kinetic * kinetic
        - matter_potential(matter_doublet, matter_config)
        - interaction_energy_density(
            phi, matter_doublet, response_config, matter_config
        )
    )


def coupled_conservative_action_density(
    metric: Any,
    inverse_metric: Any,
    curvature_scalar: float,
    gradient_phi: Any,
    phi: float,
    matter_doublet: Any,
    matter_gradients: Any,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> float:
    """Return the complete conservative pilot density ``sqrt(-g) L``."""

    matter_lagrangian = coupled_matter_lagrangian_scalar(
        inverse_metric,
        matter_gradients,
        matter_doublet,
        phi,
        response_config,
        matter_config,
    )
    return conservative_action_density(
        metric,
        inverse_metric,
        curvature_scalar,
        gradient_phi,
        phi,
        matter_lagrangian,
        response_config,
    )


def matter_eom_residual(
    matter_box: Any,
    matter_doublet: Any,
    phi: float,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> np.ndarray:
    """Return the two covariant Euler-Lagrange residuals for the doublet."""

    box = _doublet(matter_box, "matter_box")
    fields = _doublet(matter_doublet, "matter_doublet")
    common = (
        matter_config.matter_mass_sq
        + matter_config.matter_quartic * float(np.dot(fields, fields))
        - response_config.epsilon_nc
        * matter_config.response_coupling
        * response_displacement(phi, response_config)
    )
    return matter_config.matter_kinetic * box - common * fields


def matter_on_shell_box(
    matter_doublet: Any,
    phi: float,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> np.ndarray:
    """Return ``box chi_A`` implied by the conservative matter equation."""

    fields = _doublet(matter_doublet, "matter_doublet")
    common = (
        matter_config.matter_mass_sq
        + matter_config.matter_quartic * float(np.dot(fields, fields))
        - response_config.epsilon_nc
        * matter_config.response_coupling
        * response_displacement(phi, response_config)
    )
    return common * fields / matter_config.matter_kinetic


def coupled_response_scalar_equation_residual(
    curvature_scalar: float,
    box_phi: float,
    phi: float,
    matter_doublet: Any,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> float:
    """Return the full nested response equation including matter forcing."""

    uncoupled = response_scalar_equation_residual(
        curvature_scalar, box_phi, phi, response_config
    )
    forcing = (
        0.5
        * response_config.epsilon_nc
        * matter_config.response_coupling
        * matter_amplitude_sq(matter_doublet)
    )
    return float(uncoupled + forcing)


def matter_noether_current(
    inverse_metric: Any,
    matter_doublet: Any,
    matter_gradients: Any,
    matter_config: CovariantMatterConfig,
) -> np.ndarray:
    """Return the contravariant global-O(2) Noether current ``N^mu``."""

    inverse = np.asarray(inverse_metric, dtype=float)
    if inverse.shape != (4, 4) or not np.all(np.isfinite(inverse)):
        raise ValueError("inverse_metric must be a finite array with shape (4, 4)")
    fields = _doublet(matter_doublet, "matter_doublet")
    gradients = _doublet_gradients(matter_gradients, "matter_gradients")
    raised = np.einsum("mn,an->am", inverse, gradients)
    return matter_config.matter_kinetic * (
        fields[0] * raised[1] - fields[1] * raised[0]
    )


def matter_current_divergence(
    matter_box: Any,
    matter_doublet: Any,
    matter_config: CovariantMatterConfig,
) -> float:
    """Return ``nabla_mu N^mu`` before imposing the matter equations."""

    box = _doublet(matter_box, "matter_box")
    fields = _doublet(matter_doublet, "matter_doublet")
    return float(
        matter_config.matter_kinetic
        * (fields[0] * box[1] - fields[1] * box[0])
    )


def matter_current_divergence_from_eom(
    matter_eom: Any,
    matter_doublet: Any,
) -> float:
    """Return the exact Noether identity ``chi_1 E_2 - chi_2 E_1``."""

    residual = _doublet(matter_eom, "matter_eom")
    fields = _doublet(matter_doublet, "matter_doublet")
    return float(fields[0] * residual[1] - fields[1] * residual[0])


def coupled_matter_stress_tensor(
    metric: Any,
    inverse_metric: Any,
    matter_doublet: Any,
    matter_gradients: Any,
    phi: float,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
) -> np.ndarray:
    """Return the symmetric stress tensor of matter plus interaction."""

    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    gradients = _doublet_gradients(matter_gradients, "matter_gradients")
    kinetic = matter_kinetic_scalar(inverse, gradients)
    potential = matter_potential(matter_doublet, matter_config) + interaction_energy_density(
        phi, matter_doublet, response_config, matter_config
    )
    gradient_outer = np.einsum("am,an->mn", gradients, gradients)
    return np.asarray(
        matter_config.matter_kinetic * gradient_outer
        - g * (0.5 * matter_config.matter_kinetic * kinetic + potential),
        dtype=float,
    )


def coupled_metric_residual(
    metric: Any,
    einstein_tensor: Any,
    phi: float,
    gradient_phi: Any,
    curvature_factor_base_hessian: Any,
    matter_doublet: Any,
    matter_gradients: Any,
    response_config: CovariantResponseConfig,
    matter_config: CovariantMatterConfig,
    *,
    inverse_metric: Any | None = None,
) -> np.ndarray:
    """Return the parent metric residual with the scalar-matter stress."""

    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    matter_stress = coupled_matter_stress_tensor(
        g,
        inverse,
        matter_doublet,
        matter_gradients,
        phi,
        response_config,
        matter_config,
    )
    return uet_metric_residual(
        g,
        einstein_tensor,
        matter_stress,
        phi,
        gradient_phi,
        curvature_factor_base_hessian,
        response_config,
        inverse_metric=inverse,
    )


def matter_action_contract() -> dict[str, Any]:
    """Return the achieved action scope and unresolved reduction boundary."""

    return {
        "status": COVARIANT_MATTER_STATUS,
        "representation": "two_real_scalars_global_O2_equivalent_to_complex_scalar",
        "matter_amplitude_role": "lorentz_scalar_amplitude_not_yet_density_C",
        "interaction": "epsilon_nc*h*(phi-phi_equilibrium)*(chi_1^2+chi_2^2)/2",
        "reciprocal_variation": "IMPLEMENTED_ACTION_LEVEL",
        "matter_current": "ON_SHELL_GLOBAL_O2_NOETHER_CURRENT",
        "gr_limit": "epsilon_nc=0 removes response interaction and retains Einstein GR with scalar matter",
        "normalized_matter_space_map": "PARTIAL_RESPONSE_ONLY",
        "diffusive_matter_dynamics": "NOT_DERIVED",
        "regular_normalized_epsilon_limit": "NOT_IMPLEMENTED",
        "derived_trace_imported": False,
        "derived_trace_backreaction": False,
        "particle_identity": "NOT_ESTABLISHED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": "regular_covariant_to_diffusive_matter_reduction_missing",
        "mass_dimensions": dict(NATURAL_UNIT_MATTER_DIMENSIONS),
    }
