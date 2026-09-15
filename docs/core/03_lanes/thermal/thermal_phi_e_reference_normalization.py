"""Source-backed reference normalization for a named Topic 13 ``Phi_E`` lane.

This module defines an operational energy-response coordinate only. It leaves
the base UET ``Phi`` response coordinate unmapped and does not provide a
calibration for ``alpha_Phi_K`` of the base lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class PhiEReferenceInputs:
    reference_temperature_K: float
    reference_cv_J_per_m3_K: float


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def reference_energy_density_J_per_m3(inputs: PhiEReferenceInputs) -> float:
    """Define the named-coordinate convention ``e0_ref = c_v(T_ref)*T_ref``."""

    return _positive(inputs.reference_temperature_K, "reference_temperature_K") * _positive(
        inputs.reference_cv_J_per_m3_K, "reference_cv_J_per_m3_K"
    )


def phi_e_from_delta_u(delta_u_J_per_m3: float, inputs: PhiEReferenceInputs) -> float:
    """Return the named energy-response coordinate ``Phi_E=Delta_u/e0_ref``."""

    delta_u = float(delta_u_J_per_m3)
    if not isfinite(delta_u):
        raise ValueError("delta_u_J_per_m3 must be finite")
    return delta_u / reference_energy_density_J_per_m3(inputs)


def alpha_phi_e_K(cv_J_per_m3_K: float, inputs: PhiEReferenceInputs) -> float:
    """Return the standard energy-response map ``Delta_Tq=alpha*Phi_E``."""

    return reference_energy_density_J_per_m3(inputs) / _positive(cv_J_per_m3_K, "cv_J_per_m3_K")


def phi_e_reference_contract() -> dict[str, str]:
    return {
        "branch_id": "T13-PHI-E-CVREF-001",
        "definition": "e0_ref=c_v(T_ref)*T_ref; Phi_E=Delta_u/e0_ref",
        "temperature_map": "Delta_Tq=(e0_ref/c_v(T))*Phi_E",
        "reference_identity": "alpha_Phi_E_K(T_ref)=T_ref by coordinate convention",
        "e0_ref": "J m^-3",
        "c_v": "J m^-3 K^-1",
        "T_ref": "K",
        "Phi_E": "dimensionless named energy-response coordinate",
        "alpha_Phi_E_K": "K per normalized Phi_E",
        "uncertainty": "source c_v uncertainty cancels only in alpha(T_ref)=T_ref because e0_ref and denominator use the same row; this is not a physical calibration uncertainty",
        "base_Phi_identity": "not asserted; base Phi-to-Phi_E remains open",
        "C_identity": "c_v is not UET C and Phi_E is not UET C",
        "R_gen_identity": "derived history trace only; absent and non-backreacting",
    }


__all__ = [
    "PhiEReferenceInputs",
    "reference_energy_density_J_per_m3",
    "phi_e_from_delta_u",
    "alpha_phi_e_K",
    "phi_e_reference_contract",
]
