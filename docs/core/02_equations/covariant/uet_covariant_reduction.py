"""Controlled response-sector reduction from the covariant parent to 1D UET.

The reduction makes the local-rest-frame, weak-curvature, near-equilibrium,
and nondimensionalization assumptions explicit.  It recovers the
``Phi, Pi`` equation used by ``matter_space_coupled_v1`` exactly after a
declared constitutive source supplies damping, matter forcing, and external
drive.

It does not itself derive the conserved ``C`` equation.  A later O(2) scalar
matter action supplies reciprocal conservative coupling, and
``uet_covariant_diffusion`` supplies a separate coarse-grained constitutive
current bridge with an exact Model-B limit.  Neither result turns this older
response-only adapter into a microscopic dissipative derivation of the full
matter-space operator.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_matter_space import MatterSpaceConfig

COVARIANT_REDUCTION_STATUS: Final[str] = "PARTIAL_RESPONSE_SECTOR_EXACT"


def _finite_positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _finite_nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be finite and non-negative")
    return result


def _array(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.ndim != 1 or result.size < 3:
        raise ValueError(f"{name} must be a one-dimensional array with at least 3 cells")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


@dataclass(frozen=True)
class WeakFieldReductionConfig:
    """Natural-to-normalized scales and target response controls."""

    length_scale: float = 1.0
    time_scale: float = 1.0
    response_field_scale: float = 1.0
    mobility_space: float = 1.0
    tau_space: float = 1.0
    coupling_g: float = 0.0
    unit_lane: str = "natural_to_normalized"

    def __post_init__(self) -> None:
        for name in (
            "length_scale",
            "time_scale",
            "response_field_scale",
            "mobility_space",
            "tau_space",
        ):
            _finite_positive(getattr(self, name), name)
        _finite_nonnegative(self.coupling_g, "coupling_g")
        if self.unit_lane != "natural_to_normalized":
            raise NotImplementedError(
                "the reduction v1 supports only unit_lane='natural_to_normalized'"
            )

    @property
    def normalized_light_speed(self) -> float:
        """Return ``c_hat = time_scale / length_scale`` for natural ``c=1``."""

        return self.time_scale / self.length_scale


@dataclass(frozen=True)
class ReducedResponseCoefficients:
    """Matter-space response coefficients implied by the declared scaling."""

    a_space: float
    b_space: float
    kappa_space: float
    mobility_space: float
    tau_space: float
    coupling_g: float
    normalized_characteristic_speed: float


def derive_response_coefficients(
    covariant: CovariantResponseConfig,
    reduction: WeakFieldReductionConfig,
) -> ReducedResponseCoefficients:
    """Map the covariant scalar coefficients to normalized response controls."""

    if covariant.epsilon_nc <= 0.0:
        raise ValueError(
            "response reduction is defined only on the epsilon_nc > 0 branch"
        )
    Z = covariant.response_kinetic
    mobility = reduction.mobility_space
    tau = reduction.tau_space
    speed_sq = reduction.normalized_light_speed**2
    mass_rate = (
        covariant.response_mass_sq * reduction.time_scale**2 / Z
    )
    quartic_rate = (
        covariant.response_quartic
        * reduction.response_field_scale**2
        * reduction.time_scale**2
        / Z
    )
    return ReducedResponseCoefficients(
        a_space=tau * mass_rate / mobility,
        b_space=tau * quartic_rate / mobility,
        kappa_space=tau * speed_sq / mobility,
        mobility_space=mobility,
        tau_space=tau,
        coupling_g=reduction.coupling_g,
        normalized_characteristic_speed=reduction.normalized_light_speed,
    )


def matter_space_config_from_reduction(
    covariant: CovariantResponseConfig,
    reduction: WeakFieldReductionConfig,
    template: MatterSpaceConfig | None = None,
) -> MatterSpaceConfig:
    """Return a normalized matter-space config with mapped response fields.

    Matter coefficients are inherited from ``template`` and are not derived by
    this bridge.
    """

    base = MatterSpaceConfig() if template is None else template
    mapped = derive_response_coefficients(covariant, reduction)
    return replace(
        base,
        a_space=mapped.a_space,
        b_space=mapped.b_space,
        kappa_space=mapped.kappa_space,
        mobility_space=mapped.mobility_space,
        tau_space=mapped.tau_space,
        coupling_g=mapped.coupling_g,
        unit_lane="normalized",
    )


def required_dimensionless_scalar_source(
    space_rate: Any,
    matter_state: Any,
    external_space_source: Any,
    coefficients: ReducedResponseCoefficients,
) -> np.ndarray:
    """Return the source needed to reproduce damping and matter forcing.

    This is ``j_hat = Pi/tau - M g C^2/(2 tau) - J_Phi/tau`` in the convention
    where the reduced covariant acceleration contains ``-j_hat``.
    """

    rate = _array(space_rate, "space_rate")
    matter = _array(matter_state, "matter_state")
    external = _array(external_space_source, "external_space_source")
    if rate.shape != matter.shape or rate.shape != external.shape:
        raise ValueError("space_rate, matter_state, and external source must share one shape")
    return (
        rate / coefficients.tau_space
        - coefficients.mobility_space
        * coefficients.coupling_g
        * np.square(matter)
        / (2.0 * coefficients.tau_space)
        - external / coefficients.tau_space
    )


def dimensional_scalar_source_minus_curvature_drive(
    dimensionless_source: Any,
    covariant: CovariantResponseConfig,
    reduction: WeakFieldReductionConfig,
) -> np.ndarray:
    """Map ``j_hat`` to ``j_phi - curvature_drive`` in natural units."""

    source = _array(dimensionless_source, "dimensionless_source")
    scale = (
        covariant.response_kinetic
        * reduction.response_field_scale
        / reduction.time_scale**2
    )
    return scale * source


def covariant_reduced_response_acceleration(
    response: Any,
    response_laplacian: Any,
    dimensionless_scalar_source: Any,
    covariant: CovariantResponseConfig,
    reduction: WeakFieldReductionConfig,
) -> np.ndarray:
    """Return the normalized local-rest-frame covariant scalar acceleration."""

    phi = _array(response, "response")
    laplacian = _array(response_laplacian, "response_laplacian")
    source = _array(dimensionless_scalar_source, "dimensionless_scalar_source")
    if phi.shape != laplacian.shape or phi.shape != source.shape:
        raise ValueError("response, Laplacian, and scalar source must share one shape")
    Z = covariant.response_kinetic
    speed_sq = reduction.normalized_light_speed**2
    mass_rate = covariant.response_mass_sq * reduction.time_scale**2 / Z
    quartic_rate = (
        covariant.response_quartic
        * reduction.response_field_scale**2
        * reduction.time_scale**2
        / Z
    )
    return (
        speed_sq * laplacian
        - mass_rate * phi
        - quartic_rate * np.power(phi, 3)
        - source
    )


def matter_space_response_acceleration(
    response: Any,
    space_rate: Any,
    response_laplacian: Any,
    matter_state: Any,
    external_space_source: Any,
    coefficients: ReducedResponseCoefficients,
) -> np.ndarray:
    """Return the ``matter_space_coupled_v1`` response acceleration."""

    phi = _array(response, "response")
    rate = _array(space_rate, "space_rate")
    laplacian = _array(response_laplacian, "response_laplacian")
    matter = _array(matter_state, "matter_state")
    external = _array(external_space_source, "external_space_source")
    if len({item.shape for item in (phi, rate, laplacian, matter, external)}) != 1:
        raise ValueError("all reduced response arrays must share one shape")
    chemical_potential = (
        coefficients.a_space * phi
        + coefficients.b_space * np.power(phi, 3)
        - coefficients.kappa_space * laplacian
        - 0.5 * coefficients.coupling_g * np.square(matter)
    )
    return (
        -rate
        - coefficients.mobility_space * chemical_potential
        + external
    ) / coefficients.tau_space


def compare_response_reduction(
    response: Any,
    space_rate: Any,
    response_laplacian: Any,
    matter_state: Any,
    external_space_source: Any,
    covariant: CovariantResponseConfig,
    reduction: WeakFieldReductionConfig,
) -> dict[str, Any]:
    """Compare both acceleration forms using the required constitutive source."""

    coefficients = derive_response_coefficients(covariant, reduction)
    source = required_dimensionless_scalar_source(
        space_rate, matter_state, external_space_source, coefficients
    )
    covariant_acceleration = covariant_reduced_response_acceleration(
        response,
        response_laplacian,
        source,
        covariant,
        reduction,
    )
    target_acceleration = matter_space_response_acceleration(
        response,
        space_rate,
        response_laplacian,
        matter_state,
        external_space_source,
        coefficients,
    )
    difference = covariant_acceleration - target_acceleration
    return {
        "coefficients": coefficients,
        "required_dimensionless_scalar_source": source,
        "covariant_acceleration": covariant_acceleration,
        "matter_space_acceleration": target_acceleration,
        "difference": difference,
        "max_abs_difference": float(np.max(np.abs(difference))),
    }


def reduction_contract() -> dict[str, Any]:
    """Return assumptions, achieved scope, and the next controlling blocker."""

    return {
        "status": COVARIANT_REDUCTION_STATUS,
        "assumptions": [
            "local_rest_frame",
            "weak_curvature_or_curvature_drive_absorbed_into_source",
            "one_spatial_dimension",
            "near_equilibrium_response_field",
            "declared_natural_to_normalized_scales",
        ],
        "response_equation_mapping": "EXACT_ALGEBRAIC",
        "matter_equation_mapping": "PARTIAL_IN_SEPARATE_CONSTITUTIVE_CURRENT_BRIDGE",
        "reciprocal_coupling_derivation": "IMPLEMENTED_ACTION_LEVEL_IN_SEPARATE_MATTER_MODULE",
        "causal_source_realization": "BLOCKED",
        "reason": "this module maps only the response equation; the separate matter action and conserved-current bridge do not yet supply microscopic CTP/KMS transport matching or a first-order hyperbolic gradient-phase-field closure",
        "derived_trace_imported": False,
        "derived_trace_backreaction": False,
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing",
    }
