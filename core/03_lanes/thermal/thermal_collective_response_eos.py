"""Formal collective-response EOS for the named finite-temperature Topic 13 lane.

This is a normalized candidate effective-functional extension. ``C`` remains
a collective system-behaviour coordinate, while ``Phi`` remains an effective
response coordinate. The module does not identify either with mass, charge,
a particle, an information field, or an SI observable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.thermal_response_beta_contract import (
    ThermalResponseBetaInputs,
    a_phi_of_temperature,
    entropy_density_J_per_m3_K as beta_entropy_density_J_per_m3_K,
    validate_inputs as validate_beta_inputs,
)


@dataclass(frozen=True)
class CollectiveResponseEOSInputs:
    """Coefficient packet for the named normalized collective-response lane."""

    thermal: ThermalResponseBetaInputs
    a_c: float
    b_c: float


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def validate_eos_inputs(inputs: CollectiveResponseEOSInputs) -> None:
    """Validate a locally bounded quartic response functional."""

    validate_beta_inputs(inputs.thermal)
    _finite(inputs.a_c, "a_c")
    b_c = _finite(inputs.b_c, "b_c")
    b_phi = _finite(inputs.thermal.b_phi, "thermal.b_phi")
    if b_c <= 0.0:
        raise ValueError("b_c must be positive for quartic boundedness")
    if b_phi <= 0.0:
        raise ValueError("thermal.b_phi must be positive for quartic boundedness")


def normalized_free_energy_density(
    temperature_K: float,
    c: float,
    phi: float,
    inputs: CollectiveResponseEOSInputs,
) -> float:
    """Return the named local normalized free-energy density.

    ``f_hat = a_C C^2/2 + b_C C^4/4 + a_Phi(T) Phi^2/2
    + b_Phi Phi^4/4 - g C^2 Phi/2``.
    """

    validate_eos_inputs(inputs)
    c_value = _finite(c, "c")
    phi_value = _finite(phi, "phi")
    thermal = inputs.thermal
    return float(
        0.5 * inputs.a_c * c_value**2
        + 0.25 * inputs.b_c * c_value**4
        + 0.5 * a_phi_of_temperature(temperature_K, thermal) * phi_value**2
        + 0.25 * thermal.b_phi * phi_value**4
        - 0.5 * thermal.coupling_g * c_value**2 * phi_value
    )


def chemical_potentials(
    temperature_K: float,
    c: float,
    phi: float,
    inputs: CollectiveResponseEOSInputs,
) -> tuple[float, float]:
    """Return formal response derivatives ``(mu_C, mu_Phi)``.

    These are derivatives in normalized coordinates, not measured chemical
    potentials and not a declaration that ``C`` is a charge density.
    """

    validate_eos_inputs(inputs)
    c_value = _finite(c, "c")
    phi_value = _finite(phi, "phi")
    thermal = inputs.thermal
    mu_c = inputs.a_c * c_value + inputs.b_c * c_value**3 - thermal.coupling_g * c_value * phi_value
    mu_phi = (
        a_phi_of_temperature(temperature_K, thermal) * phi_value
        + thermal.b_phi * phi_value**3
        - 0.5 * thermal.coupling_g * c_value**2
    )
    return float(mu_c), float(mu_phi)


def hessian(
    temperature_K: float,
    c: float,
    phi: float,
    inputs: CollectiveResponseEOSInputs,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return the normalized Hessian of the declared local functional."""

    validate_eos_inputs(inputs)
    c_value = _finite(c, "c")
    phi_value = _finite(phi, "phi")
    thermal = inputs.thermal
    h_cc = inputs.a_c + 3.0 * inputs.b_c * c_value**2 - thermal.coupling_g * phi_value
    h_phi_phi = a_phi_of_temperature(temperature_K, thermal) + 3.0 * thermal.b_phi * phi_value**2
    h_c_phi = -thermal.coupling_g * c_value
    return ((float(h_cc), float(h_c_phi)), (float(h_c_phi), float(h_phi_phi)))


def local_stability(
    temperature_K: float,
    c: float,
    phi: float,
    inputs: CollectiveResponseEOSInputs,
) -> dict[str, float | bool]:
    """Evaluate local Hessian positivity and reciprocity conditions."""

    matrix = hessian(temperature_K, c, phi, inputs)
    h_cc, h_c_phi = matrix[0]
    h_phi_c, h_phi_phi = matrix[1]
    determinant = h_cc * h_phi_phi - h_c_phi * h_phi_c
    return {
        "h_cc": h_cc,
        "h_c_phi": h_c_phi,
        "h_phi_c": h_phi_c,
        "h_phi_phi": h_phi_phi,
        "determinant": determinant,
        "mixed_derivatives_equal": h_c_phi == h_phi_c,
        "positive_h_cc": h_cc > 0.0,
        "positive_h_phi_phi": h_phi_phi > 0.0,
        "positive_determinant": determinant > 0.0,
        "locally_stable": h_cc > 0.0 and h_phi_phi > 0.0 and determinant > 0.0,
    }


def entropy_density_J_per_m3_K(
    phi: float,
    inputs: CollectiveResponseEOSInputs,
    e0_J_per_m3: float,
) -> float:
    """Delegate the equilibrium entropy derivative to the beta contract."""

    validate_eos_inputs(inputs)
    return beta_entropy_density_J_per_m3_K(phi, inputs.thermal, e0_J_per_m3)


def collective_response_eos_contract() -> dict[str, str]:
    """Return explicit named-lane ontology, units, and closure limits."""

    return {
        "branch_id": "T13-THERMAL-EOS-001",
        "functional": "f_hat=a_C C^2/2+b_C C^4/4+a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2",
        "mu_C": "a_C C+b_C C^3-g C Phi",
        "mu_Phi": "a_Phi(T) Phi+b_Phi Phi^3-g C^2/2",
        "hessian": "H_CC=a_C+3b_C C^2-g Phi; H_PhiPhi=a_Phi(T)+3b_Phi Phi^2; H_CPhi=H_PhiC=-g C",
        "stability": "H_CC>0, H_PhiPhi>0, det(H)>0",
        "reciprocity": "partial_Phi(mu_C)=partial_C(mu_Phi)=-g C",
        "C": "dimensionless collective system-behaviour coordinate; not mass or charge density",
        "Phi": "dimensionless effective response coordinate; not a particle, information field, temperature, or heat flux",
        "coefficient_units": "a_C,b_C,a_Phi,b_Phi,g dimensionless in f_hat; beta_T13 dimensionless; da_Phi/dT K^-1",
        "energy_units": "f=e0*f_hat in J m^-3 only after external e0 is supplied",
        "entropy_units": "s=-partial_T f in J m^-3 K^-1 only after external e0 is supplied",
        "R_gen": "derived history trace only; absent from the functional and has no backreaction",
        "physical_status": "candidate normalized EOS/stability lane only; source coefficient provenance, SI anchor, physical EOS, transport, SK/KMS, entropy production, and dissipative balance remain open",
    }


__all__ = [
    "CollectiveResponseEOSInputs",
    "validate_eos_inputs",
    "normalized_free_energy_density",
    "chemical_potentials",
    "hessian",
    "local_stability",
    "entropy_density_J_per_m3_K",
    "collective_response_eos_contract",
]
