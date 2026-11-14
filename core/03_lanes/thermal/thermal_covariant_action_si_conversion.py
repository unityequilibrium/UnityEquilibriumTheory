"""Symbolic natural-unit to SI conversion for the covariant response lane.

The covariant parent is currently specified in natural units.  This module
derives the unit conversion factors after an energy reference is declared,
without choosing that reference or identifying the covariant field with the
normalized Topic 13 Phi variable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi


@dataclass(frozen=True)
class ExactSIConstants:
    """SI constants needed by the symbolic conversion contract."""

    h_J_s: float
    c_m_per_s: float
    k_B_J_per_K: float

    @property
    def hbar_J_s(self) -> float:
        return self.h_J_s / (2.0 * pi)


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


@dataclass(frozen=True)
class NaturalUnitScale:
    """Conversion scale after an energy reference is explicitly supplied.

    Natural-unit numeric densities are interpreted as coefficients of
    ``E_ref**4`` and natural-unit heat capacities as coefficients of
    ``E_ref**3``.  The reference is an open physical input, not a fitted
    value and not a default hidden in this module.
    """

    energy_reference_J: float
    constants: ExactSIConstants

    def __post_init__(self) -> None:
        _positive(self.energy_reference_J, "energy_reference_J")
        _positive(self.constants.h_J_s, "h_J_s")
        _positive(self.constants.c_m_per_s, "c_m_per_s")
        _positive(self.constants.k_B_J_per_K, "k_B_J_per_K")

    @property
    def hbar_c_J_m(self) -> float:
        return self.constants.hbar_J_s * self.constants.c_m_per_s

    @property
    def length_reference_m(self) -> float:
        return self.hbar_c_J_m / self.energy_reference_J

    @property
    def time_reference_s(self) -> float:
        return self.constants.hbar_J_s / self.energy_reference_J

    @property
    def temperature_reference_K(self) -> float:
        return self.energy_reference_J / self.constants.k_B_J_per_K

    @property
    def energy_density_scale_J_per_m3(self) -> float:
        return self.energy_reference_J**4 / self.hbar_c_J_m**3

    @property
    def heat_capacity_density_scale_J_per_m3_K(self) -> float:
        return (
            self.constants.k_B_J_per_K
            * self.energy_reference_J**3
            / self.hbar_c_J_m**3
        )

    def density_to_si(self, natural_density: float) -> float:
        return float(natural_density) * self.energy_density_scale_J_per_m3

    def heat_capacity_to_si(self, natural_heat_capacity: float) -> float:
        return float(natural_heat_capacity) * self.heat_capacity_density_scale_J_per_m3_K

    def temperature_energy_to_si(self, natural_temperature_energy: float) -> float:
        return float(natural_temperature_energy) * self.temperature_reference_K

    def alpha_energy_to_si(self, natural_alpha_energy: float) -> float:
        """Convert d(theta)/d(Phi) from E_ref to kelvin per Phi."""

        return self.temperature_energy_to_si(natural_alpha_energy)

    def normalized_phi_from_covariant(self, covariant_phi: float, phi_scale: float) -> float:
        """Return a dimensionless normalized coordinate for a declared field scale."""

        scale = _positive(phi_scale, "phi_scale")
        return float(covariant_phi) / scale

    def covariant_phi_scale_to_si_energy(self, phi_scale: float) -> float:
        """Convert a natural canonical-field scale to joules."""

        return _positive(phi_scale, "phi_scale") * self.energy_reference_J


def symbolic_si_conversion_contract() -> dict[str, object]:
    """Return the declared equations and open inputs for the SI route."""

    return {
        "energy_reference": "E_ref [J] is an explicit external/provenance input",
        "length_reference": "ell_ref = hbar*c/E_ref [m]",
        "time_reference": "t_ref = hbar/E_ref [s]",
        "temperature_reference": "T_ref = E_ref/k_B [K]",
        "energy_density": "u_SI = u_nat * E_ref^4/(hbar*c)^3 [J m^-3]",
        "heat_capacity_density": "C_SI = C_nat * k_B*E_ref^3/(hbar*c)^3 [J m^-3 K^-1]",
        "thermal_response": "Delta_Tq = (E_ref/k_B) * Delta_theta",
        "alpha_response": "alpha_Phi_K = (E_ref/k_B) * alpha_Phi_theta",
        "field_normalization": "Phi_normalized = Phi_covariant/Phi_scale",
        "base_phi_to_phi_e": "OPEN_DERIVATION_OR_INDEPENDENT_CALIBRATION",
        "e0": "OPEN; no physical energy-density scale is emitted",
        "calibration": "FORBIDDEN_FROM_TTG_RESIDUALS_AND_XIE_2026_HOLDOUT",
    }


__all__ = [
    "ExactSIConstants",
    "NaturalUnitScale",
    "symbolic_si_conversion_contract",
]
