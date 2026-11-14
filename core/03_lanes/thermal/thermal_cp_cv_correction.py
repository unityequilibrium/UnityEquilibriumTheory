"""Thermodynamic correction contract for the Topic 13 heat-capacity lane.

The Georgia Tech source provides a mass-specific ``c_p`` row.  This module
keeps the standard ``c_p`` to ``c_v`` correction explicit and refuses to
pretend that the correction inputs are available until their provenance and
uncertainties are source-locked.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class CpCvCorrectionInputs:
    """State inputs for the solid thermodynamic heat-capacity correction."""

    temperature_K: float
    cp_mass_J_per_kg_K: float
    density_kg_per_m3: float
    alpha_volume_per_K: float
    bulk_modulus_Pa: float
    sigma_temperature_K: float | None = None
    sigma_cp_mass_J_per_kg_K: float | None = None
    sigma_density_kg_per_m3: float | None = None
    sigma_alpha_volume_per_K: float | None = None
    sigma_bulk_modulus_Pa: float | None = None


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def _optional_nonnegative(value: float | None, name: str) -> float | None:
    if value is None:
        return None
    result = _finite(value, name)
    if result < 0.0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def validate_cp_cv_inputs(inputs: CpCvCorrectionInputs) -> None:
    """Validate the thermodynamic domain without selecting material values."""

    _positive(inputs.temperature_K, "temperature_K")
    _positive(inputs.cp_mass_J_per_kg_K, "cp_mass_J_per_kg_K")
    _positive(inputs.density_kg_per_m3, "density_kg_per_m3")
    _finite(inputs.alpha_volume_per_K, "alpha_volume_per_K")
    _positive(inputs.bulk_modulus_Pa, "bulk_modulus_Pa")
    for value, name in (
        (inputs.sigma_temperature_K, "sigma_temperature_K"),
        (inputs.sigma_cp_mass_J_per_kg_K, "sigma_cp_mass_J_per_kg_K"),
        (inputs.sigma_density_kg_per_m3, "sigma_density_kg_per_m3"),
        (inputs.sigma_alpha_volume_per_K, "sigma_alpha_volume_per_K"),
        (inputs.sigma_bulk_modulus_Pa, "sigma_bulk_modulus_Pa"),
    ):
        _optional_nonnegative(value, name)


def cp_minus_cv_mass_J_per_kg_K(inputs: CpCvCorrectionInputs) -> float:
    """Return ``c_p-c_v = T alpha_V^2 K_T / rho`` for mass-specific heat."""

    validate_cp_cv_inputs(inputs)
    return (
        inputs.temperature_K
        * inputs.alpha_volume_per_K**2
        * inputs.bulk_modulus_Pa
        / inputs.density_kg_per_m3
    )


def cp_minus_cv_volumetric_J_per_m3_K(inputs: CpCvCorrectionInputs) -> float:
    """Return ``c_p-c_v = T alpha_V^2 K_T`` per unit volume."""

    validate_cp_cv_inputs(inputs)
    return (
        inputs.temperature_K
        * inputs.alpha_volume_per_K**2
        * inputs.bulk_modulus_Pa
    )


def cv_mass_from_cp_J_per_kg_K(inputs: CpCvCorrectionInputs) -> float:
    """Convert a mass-specific ``c_p`` into ``c_v`` at the same state."""

    validate_cp_cv_inputs(inputs)
    result = inputs.cp_mass_J_per_kg_K - cp_minus_cv_mass_J_per_kg_K(inputs)
    if result <= 0.0:
        raise ValueError("corrected c_v must remain positive")
    return result


def cv_volumetric_from_cp_J_per_m3_K(inputs: CpCvCorrectionInputs) -> float:
    """Convert mass-specific ``c_p`` into volumetric ``c_v``."""

    validate_cp_cv_inputs(inputs)
    result = (
        inputs.density_kg_per_m3 * inputs.cp_mass_J_per_kg_K
        - cp_minus_cv_volumetric_J_per_m3_K(inputs)
    )
    if result <= 0.0:
        raise ValueError("corrected volumetric c_v must remain positive")
    return result


def _require_uncertainties(inputs: CpCvCorrectionInputs) -> tuple[float, ...]:
    values = (
        inputs.sigma_temperature_K,
        inputs.sigma_cp_mass_J_per_kg_K,
        inputs.sigma_density_kg_per_m3,
        inputs.sigma_alpha_volume_per_K,
        inputs.sigma_bulk_modulus_Pa,
    )
    if any(value is None for value in values):
        raise ValueError("all independent input uncertainties are required")
    return tuple(float(value) for value in values)


def cv_volumetric_uncertainty_J_per_m3_K(inputs: CpCvCorrectionInputs) -> float:
    """Propagate independent first-order uncertainties into volumetric ``c_v``."""

    validate_cp_cv_inputs(inputs)
    sigma_T, sigma_cp, sigma_rho, sigma_alpha, sigma_bulk = _require_uncertainties(inputs)
    T = inputs.temperature_K
    cp = inputs.cp_mass_J_per_kg_K
    rho = inputs.density_kg_per_m3
    alpha = inputs.alpha_volume_per_K
    bulk = inputs.bulk_modulus_Pa
    derivatives = (
        -alpha**2 * bulk,
        rho,
        cp,
        -2.0 * T * alpha * bulk,
        -T * alpha**2,
    )
    sigmas = (sigma_T, sigma_cp, sigma_rho, sigma_alpha, sigma_bulk)
    return sqrt(sum((derivative * sigma) ** 2 for derivative, sigma in zip(derivatives, sigmas)))


def cp_cv_correction_contract() -> dict[str, object]:
    """Return the explicit formula and ontology boundary for this lane."""

    return {
        "formula_mass_specific": "c_p - c_v = T * alpha_V^2 * K_T / rho",
        "formula_volumetric": "c_p^V - c_v^V = T * alpha_V^2 * K_T",
        "volumetric_cp_map": "c_p^V = rho * c_p",
        "volumetric_cv_map": "c_v^V = rho * c_p - T * alpha_V^2 * K_T",
        "alpha_V": "volumetric thermal expansion coefficient [K^-1]",
        "K_T": "isothermal bulk modulus [Pa = J m^-3]",
        "rho": "mass density [kg m^-3]",
        "c_p_mass": "mass-specific constant-pressure heat capacity [J kg^-1 K^-1]",
        "c_v_volumetric": "constant-volume heat capacity density [J m^-3 K^-1]",
        "uncertainty_method": "independent first-order propagation; no covariance supplied",
        "source_role": "standard thermodynamic identity; numeric material inputs remain open",
        "base_Phi_identity": "not asserted",
        "R_gen_identity": "unchanged derived history trace; no new physical state",
    }


__all__ = [
    "CpCvCorrectionInputs",
    "validate_cp_cv_inputs",
    "cp_minus_cv_mass_J_per_kg_K",
    "cp_minus_cv_volumetric_J_per_m3_K",
    "cv_mass_from_cp_J_per_kg_K",
    "cv_volumetric_from_cp_J_per_m3_K",
    "cv_volumetric_uncertainty_J_per_m3_K",
    "cp_cv_correction_contract",
]
