"""Named energy-response bridge for the Topic 13 thermal lane.

This module keeps the base UET ``Phi`` ontology separate from an explicitly
named response branch.  The branch defines ``Phi_E`` from an energy-density
response and therefore exposes the standard heat-capacity map without silently
asserting that ``Phi_E`` is the base ``Phi``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class EnergyResponseInputs:
    """External dimensional inputs for the named ``Phi_E`` branch.

    ``e0`` and ``c_v`` are deliberately required inputs.  No material value is
    supplied by this module, and uncertainty propagation is unavailable until
    both source uncertainties are present.
    """

    e0_J_per_m3: float
    cv_J_per_m3_K: float
    sigma_e0_J_per_m3: float | None = None
    sigma_cv_J_per_m3_K: float | None = None


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


def validate_energy_response_inputs(inputs: EnergyResponseInputs) -> None:
    """Validate the dimensional domain without choosing any material values."""

    _positive(inputs.e0_J_per_m3, "e0_J_per_m3")
    _positive(inputs.cv_J_per_m3_K, "cv_J_per_m3_K")
    _optional_nonnegative(inputs.sigma_e0_J_per_m3, "sigma_e0_J_per_m3")
    _optional_nonnegative(inputs.sigma_cv_J_per_m3_K, "sigma_cv_J_per_m3_K")


def phi_e_from_delta_u(delta_u_J_per_m3: float, e0_J_per_m3: float) -> float:
    """Define the named energy-normalized response ``Phi_E := Delta_u/e0``."""

    delta_u = _finite(delta_u_J_per_m3, "delta_u_J_per_m3")
    e0 = _positive(e0_J_per_m3, "e0_J_per_m3")
    return delta_u / e0


def delta_tq_from_delta_u(
    delta_u_J_per_m3: float,
    cv_J_per_m3_K: float,
) -> float:
    """Map energy-density response to quasi-temperature response in kelvin."""

    delta_u = _finite(delta_u_J_per_m3, "delta_u_J_per_m3")
    cv = _positive(cv_J_per_m3_K, "cv_J_per_m3_K")
    return delta_u / cv


def alpha_phi_e_k(inputs: EnergyResponseInputs) -> float:
    """Return ``alpha_(Phi_E,K) = e0/c_v`` in K per normalized ``Phi_E``."""

    validate_energy_response_inputs(inputs)
    return inputs.e0_J_per_m3 / inputs.cv_J_per_m3_K


def alpha_phi_e_uncertainty_K(inputs: EnergyResponseInputs) -> float:
    """Propagate independent ``e0`` and ``c_v`` standard uncertainties.

    The result is intentionally unavailable when either source uncertainty is
    absent.  This prevents a source value without an uncertainty contract from
    becoming a numeric calibration.
    """

    validate_energy_response_inputs(inputs)
    sigma_e0 = _optional_nonnegative(inputs.sigma_e0_J_per_m3, "sigma_e0_J_per_m3")
    sigma_cv = _optional_nonnegative(inputs.sigma_cv_J_per_m3_K, "sigma_cv_J_per_m3_K")
    if sigma_e0 is None or sigma_cv is None:
        raise ValueError("both e0 and c_v uncertainties are required")
    alpha = alpha_phi_e_k(inputs)
    relative = sqrt(
        (sigma_e0 / inputs.e0_J_per_m3) ** 2
        + (sigma_cv / inputs.cv_J_per_m3_K) ** 2
    )
    return abs(alpha) * relative


def named_energy_response_branch_contract() -> dict[str, str]:
    """Return the explicit ontology and unit boundary for the named branch."""

    return {
        "branch_id": "T13-PHI-E-001",
        "definition": "Phi_E := Delta_u / e0",
        "standard_map": "Delta_Tq = Delta_u / c_v = (e0 / c_v) * Phi_E",
        "alpha": "alpha_Phi_E_K = e0 / c_v",
        "Delta_u": "J m^-3",
        "e0": "J m^-3",
        "c_v": "J m^-3 K^-1",
        "Phi_E": "dimensionless named energy-response coordinate",
        "Delta_Tq": "K",
        "alpha_Phi_E_K": "K per normalized Phi_E",
        "base_Phi_identity": "not asserted",
        "base_Phi_to_Phi_E_map": "OPEN_DERIVATION_OR_CALIBRATION",
        "C_identity": "Phi_E is not UET C and c_v is not UET C",
        "R_gen_identity": "Phi_E does not introduce or promote R_gen",
    }


__all__ = [
    "EnergyResponseInputs",
    "validate_energy_response_inputs",
    "phi_e_from_delta_u",
    "delta_tq_from_delta_u",
    "alpha_phi_e_k",
    "alpha_phi_e_uncertainty_K",
    "named_energy_response_branch_contract",
]
