"""Finite-temperature beta contract for a named Topic 13 response lane.

The module provides a formal, normalized effective-functional lane only. It
does not identify the legacy core ``beta`` coupling, the hyperbolic comparator
``beta_wave``, a covariant field coefficient, or an externally measured
thermal transport coefficient. Its purpose is to state one non-Landauer
meaning for ``beta_T13`` with an explicit action term and unit contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ThermalResponseBetaInputs:
    """Inputs for the declared normalized finite-temperature response lane.

    ``beta_t13_dimensionless`` is the logarithmic-temperature slope
    ``T0 * da_phi/dT`` of the response stiffness. It is an input coefficient
    pending source-backed provenance, not a value inferred from Landauer or a
    replacement for a legacy beta.
    """

    reference_temperature_K: float
    a_phi_T0: float
    beta_t13_dimensionless: float
    b_phi: float
    coupling_g: float


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def validate_inputs(inputs: ThermalResponseBetaInputs) -> None:
    """Validate the formal normalized coefficient domain."""

    temperature = _finite(inputs.reference_temperature_K, "reference_temperature_K")
    if temperature <= 0.0:
        raise ValueError("reference_temperature_K must be positive")
    for name in ("a_phi_T0", "beta_t13_dimensionless", "b_phi", "coupling_g"):
        _finite(getattr(inputs, name), name)


def a_phi_of_temperature(
    temperature_K: float,
    inputs: ThermalResponseBetaInputs,
) -> float:
    """Return ``a_Phi(T)=a_Phi(T0)+beta_T13*(T-T0)/T0``."""

    validate_inputs(inputs)
    temperature = _finite(temperature_K, "temperature_K")
    if temperature <= 0.0:
        raise ValueError("temperature_K must be positive")
    return float(
        inputs.a_phi_T0
        + inputs.beta_t13_dimensionless
        * (temperature - inputs.reference_temperature_K)
        / inputs.reference_temperature_K
    )


def da_phi_dT_per_K(inputs: ThermalResponseBetaInputs) -> float:
    """Return ``da_Phi/dT = beta_T13/T0`` in K^-1."""

    validate_inputs(inputs)
    return float(inputs.beta_t13_dimensionless / inputs.reference_temperature_K)


def beta_t13_from_stiffness_slope(
    reference_temperature_K: float,
    da_phi_dT_value_per_K: float,
) -> float:
    """Return ``beta_T13 = T0 * da_Phi/dT``."""

    temperature = _finite(reference_temperature_K, "reference_temperature_K")
    slope = _finite(da_phi_dT_value_per_K, "da_phi_dT_value_per_K")
    if temperature <= 0.0:
        raise ValueError("reference_temperature_K must be positive")
    return float(temperature * slope)


def normalized_free_energy_density(
    temperature_K: float,
    c: float,
    phi: float,
    inputs: ThermalResponseBetaInputs,
) -> float:
    """Evaluate the declared local normalized density ``f_hat_T13``.

    ``f_hat = a_Phi(T) Phi^2/2 + b_Phi Phi^4/4 - g C^2 Phi/2``. ``C`` is a
    collective coordinate and ``Phi`` a response coordinate; neither is a
    mass, charge, or information field in this contract.
    """

    c_value = _finite(c, "c")
    phi_value = _finite(phi, "phi")
    a_phi = a_phi_of_temperature(temperature_K, inputs)
    return float(
        0.5 * a_phi * phi_value**2
        + 0.25 * inputs.b_phi * phi_value**4
        - 0.5 * inputs.coupling_g * c_value**2 * phi_value
    )


def free_energy_density_J_per_m3(
    temperature_K: float,
    c: float,
    phi: float,
    inputs: ThermalResponseBetaInputs,
    e0_J_per_m3: float,
) -> float:
    """Apply an explicit externally supplied density scale ``e0``."""

    e0 = _finite(e0_J_per_m3, "e0_J_per_m3")
    if e0 <= 0.0:
        raise ValueError("e0_J_per_m3 must be positive")
    return e0 * normalized_free_energy_density(temperature_K, c, phi, inputs)


def entropy_density_J_per_m3_K(
    phi: float,
    inputs: ThermalResponseBetaInputs,
    e0_J_per_m3: float,
) -> float:
    """Return ``s=-partial_T f`` for the declared first-order path.

    This is an equilibrium derivative identity only. It is not an entropy
    production law and does not establish positivity, SK/KMS matching,
    Onsager reciprocity, or dissipative closure.
    """

    phi_value = _finite(phi, "phi")
    e0 = _finite(e0_J_per_m3, "e0_J_per_m3")
    if e0 <= 0.0:
        raise ValueError("e0_J_per_m3 must be positive")
    return float(-0.5 * e0 * phi_value**2 * da_phi_dT_per_K(inputs))


def thermal_response_beta_contract() -> dict[str, str]:
    """Expose ontology, formula, and explicit non-identification boundaries."""

    return {
        "branch_id": "T13-THERMAL-BETA-001",
        "functional": "f_hat_T13(C,Phi,T)=a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2",
        "beta_definition": "beta_T13=T0*(da_Phi/dT)|T0",
        "stiffness_path": "a_Phi(T)=a_Phi(T0)+beta_T13*(T-T0)/T0",
        "entropy_identity": "s=-partial_T(e0*f_hat_T13)=-e0*Phi^2*beta_T13/(2*T0)",
        "C": "dimensionless collective system-behaviour coordinate",
        "Phi": "dimensionless effective response coordinate",
        "T": "K",
        "beta_T13": "dimensionless local stiffness-temperature slope",
        "da_Phi_dT": "K^-1",
        "e0": "J m^-3 external input",
        "f": "J m^-3 after e0 is supplied",
        "s": "J m^-3 K^-1 after e0 is supplied",
        "beta_th_identity": "not used",
        "beta_core_identity": "not asserted; legacy beta_core couples a legacy I state and is not Phi",
        "beta_wave_identity": "not asserted; beta_wave is a hyperbolic comparator coefficient",
        "R_gen_identity": "derived history trace only; absent from this functional and has no backreaction",
        "physical_status": "candidate finite-temperature lane; source coefficient provenance, SI anchor, physical calibration, EOS, transport, KMS, and entropy-production closure remain open",
    }


__all__ = [
    "ThermalResponseBetaInputs",
    "validate_inputs",
    "a_phi_of_temperature",
    "da_phi_dT_per_K",
    "beta_t13_from_stiffness_slope",
    "normalized_free_energy_density",
    "free_energy_density_J_per_m3",
    "entropy_density_J_per_m3_K",
    "thermal_response_beta_contract",
]
