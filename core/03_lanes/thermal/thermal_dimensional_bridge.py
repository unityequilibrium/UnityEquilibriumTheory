"""Conditional dimensional thermal bridge for the Topic 13 response lane.

The normalized matter-space functional does not contain a temperature law or an
absolute energy scale. This module therefore exposes the smallest conditional
extension explicitly, so the algebra and unit contract can be tested without
silently turning missing inputs into a calibration or prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ConditionalThermalInputs:
    """Inputs for the local-equilibrium response map.

    The polynomial coefficients belong to a dimensionless normalized free
    energy ``f_hat``. ``da_phi_dT_per_K`` is the only input carrying an
    inverse-temperature unit in this local map.
    """

    a_phi_T0: float
    b_phi: float
    phi0: float
    da_phi_dT_per_K: float
    e0_J_per_m3: float | None = None


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def effective_phi_curvature(inputs: ConditionalThermalInputs) -> float:
    """Return ``a_phi(T0) + 3*b_phi*Phi0^2`` in normalized units."""

    a_phi = _finite(inputs.a_phi_T0, "a_phi_T0")
    b_phi = _finite(inputs.b_phi, "b_phi")
    phi0 = _finite(inputs.phi0, "phi0")
    return a_phi + 3.0 * b_phi * phi0 * phi0


def alpha_phi_k_from_local_equilibrium(
    inputs: ConditionalThermalInputs,
) -> float:
    """Derive the conditional local-equilibrium slope in K per normalized Phi.

    This is an implicit-function result, not a source-free UET prediction. The
    caller must provide the temperature-dependent coefficient derivative and a
    regular stable equilibrium branch.
    """

    phi0 = _finite(inputs.phi0, "phi0")
    derivative = _finite(inputs.da_phi_dT_per_K, "da_phi_dT_per_K")
    if abs(phi0) <= 1.0e-15:
        raise ValueError("phi0 must be nonzero for the local-equilibrium map")
    if abs(derivative) <= 1.0e-15:
        raise ValueError("da_phi_dT_per_K must be nonzero for the local-equilibrium map")
    curvature = effective_phi_curvature(inputs)
    if curvature <= 0.0:
        raise ValueError("the local equilibrium branch must have positive curvature")
    return -curvature / (derivative * phi0)


def joint_delta_temperature_K(
    inputs: ConditionalThermalInputs,
    delta_phi: float,
    delta_c: float = 0.0,
    coupling_g: float = 0.0,
    c0: float = 0.0,
) -> float:
    """Return the conditional first-order temperature response in kelvin."""

    delta_phi = _finite(delta_phi, "delta_phi")
    delta_c = _finite(delta_c, "delta_c")
    coupling_g = _finite(coupling_g, "coupling_g")
    c0 = _finite(c0, "c0")
    phi0 = _finite(inputs.phi0, "phi0")
    derivative = _finite(inputs.da_phi_dT_per_K, "da_phi_dT_per_K")
    if abs(phi0) <= 1.0e-15 or abs(derivative) <= 1.0e-15:
        raise ValueError("regular local-equilibrium inputs are required")
    curvature = effective_phi_curvature(inputs)
    if curvature <= 0.0:
        raise ValueError("the local equilibrium branch must have positive curvature")
    return -(curvature * delta_phi - coupling_g * c0 * delta_c) / (derivative * phi0)


def free_energy_density_J_per_m3(normalized_density: float, e0_J_per_m3: float) -> float:
    """Apply an explicit free-energy-density scale to a normalized density."""

    normalized_density = _finite(normalized_density, "normalized_density")
    e0 = _finite(e0_J_per_m3, "e0_J_per_m3")
    if e0 <= 0.0:
        raise ValueError("e0_J_per_m3 must be positive")
    return e0 * normalized_density


def entropy_density_J_per_m3_K(
    e0_J_per_m3: float,
    d_fhat_d_theta: float,
    d_theta_dT_per_K: float,
) -> float:
    """Return the conditional entropy density from a declared parameter path."""

    e0 = _finite(e0_J_per_m3, "e0_J_per_m3")
    d_fhat = _finite(d_fhat_d_theta, "d_fhat_d_theta")
    d_theta = _finite(d_theta_dT_per_K, "d_theta_dT_per_K")
    if e0 <= 0.0:
        raise ValueError("e0_J_per_m3 must be positive")
    return -e0 * d_fhat * d_theta


def dimensional_bridge_unit_contract() -> dict[str, str]:
    """Return the explicit unit contract for the conditional bridge."""

    return {
        "C": "dimensionless normalized coordinate",
        "Phi": "dimensionless normalized response coordinate",
        "a_phi_T0": "dimensionless coefficient in f_hat",
        "b_phi": "dimensionless coefficient in f_hat",
        "da_phi_dT_per_K": "K^-1",
        "e0_J_per_m3": "J m^-3",
        "free_energy_density": "J m^-3",
        "entropy_density": "J m^-3 K^-1",
        "alpha_Phi_K": "K per normalized Phi",
        "Delta_Tq": "K",
    }


__all__ = [
    "ConditionalThermalInputs",
    "effective_phi_curvature",
    "alpha_phi_k_from_local_equilibrium",
    "joint_delta_temperature_K",
    "free_energy_density_J_per_m3",
    "entropy_density_J_per_m3_K",
    "dimensional_bridge_unit_contract",
]
