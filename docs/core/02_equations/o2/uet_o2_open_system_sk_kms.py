"""Formal open-system SK/KMS lane for the Topic 13 response variable.

This module declares a local dissipative ansatz and verifies algebraic KMS,
FDT, retardedness, and entropy-positivity identities. The coefficients are
formal lane parameters, not physical Kubo measurements or SI calibrations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class OpenSystemParameters:
    """Formal natural-unit parameters for one scalar response mode."""

    beta_th: float
    kappa: float
    chi: float
    gamma: float

    def validate(self) -> None:
        if self.beta_th <= 0.0:
            raise ValueError("beta_th must be positive")
        if self.kappa <= 0.0 or self.chi <= 0.0 or self.gamma <= 0.0:
            raise ValueError("kappa, chi, and gamma must be positive")


def _coth(value: float) -> float:
    if value <= 0.0:
        raise ValueError("coth witness requires a positive argument")
    return float(1.0 / np.tanh(value))


def retarded_kernel(omega: float, parameters: OpenSystemParameters) -> complex:
    """Return K_R for the Fourier convention exp(-i omega t)."""

    parameters.validate()
    if omega <= 0.0:
        raise ValueError("the lane records positive frequencies")
    return complex(
        parameters.kappa - parameters.chi * omega**2,
        -parameters.gamma * omega,
    )


def spectral_density(omega: float, parameters: OpenSystemParameters) -> float:
    """Return rho_R=-2 Im(K_R) in the declared retarded convention."""

    kernel = retarded_kernel(omega, parameters)
    return float(-2.0 * kernel.imag)


def bose_occupancy(omega: float, parameters: OpenSystemParameters) -> float:
    parameters.validate()
    if omega <= 0.0:
        raise ValueError("the lane records positive frequencies")
    return float(1.0 / np.expm1(parameters.beta_th * omega))


def kms_correlators(omega: float, parameters: OpenSystemParameters) -> dict[str, float]:
    """Return synthetic greater/lesser correlators with a KMS ratio."""

    rho = spectral_density(omega, parameters)
    occupation = bose_occupancy(omega, parameters)
    greater = rho * (1.0 + occupation)
    lesser = rho * occupation
    return {
        "rho": rho,
        "n_B": occupation,
        "greater": float(greater),
        "lesser": float(lesser),
        "noise": float(greater + lesser),
        "kms_ratio": float(greater / lesser),
        "kms_target": float(np.exp(parameters.beta_th * omega)),
    }


def noise_kernel(omega: float, parameters: OpenSystemParameters) -> float:
    """Return N=rho*coth(beta_th*omega/2), the formal FDT noise kernel."""

    return float(
        spectral_density(omega, parameters)
        * _coth(0.5 * parameters.beta_th * omega)
    )


def formal_entropy_production(
    velocity: float,
    temperature: float,
    parameters: OpenSystemParameters,
) -> float:
    """Return the nonnegative entropy-production witness for the local bath."""

    parameters.validate()
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    return float(parameters.gamma * velocity**2 / temperature)


def retarded_poles(parameters: OpenSystemParameters) -> np.ndarray:
    """Return the poles of K_R=0 for the local damped oscillator ansatz."""

    parameters.validate()
    return np.roots([parameters.chi, 1j * parameters.gamma, -parameters.kappa])


def open_system_sk_contract() -> dict[str, Any]:
    """Return equations, units, ontology, and the lane claim boundary."""

    return {
        "contract_id": "T13-O2-OPEN-SYSTEM-SK-KMS-001",
        "fourier_convention": "exp(-i omega t)",
        "sk_action": "S_SK = integral dt [Phi_a (K_R Phi_r) + i Phi_a N Phi_a / 2]",
        "retarded_kernel": "K_R(omega) = kappa - chi omega^2 - i gamma omega",
        "local_operator": "K_R <- kappa + chi d_t^2 + gamma d_t",
        "spectral_density": "rho_R(omega) = -2 Im K_R(omega) = 2 gamma omega",
        "kms_correlators": "G^>(omega)=rho(1+n_B), G^<(omega)=rho n_B, G^>/G^<=exp(beta_th omega)",
        "fdt_noise": "N(omega)=G^>(omega)+G^<(omega)=rho coth(beta_th omega/2)",
        "entropy_production": "sigma_formal = gamma (d_t Phi_r)^2 / T >= 0",
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; contour copies Phi_r and Phi_a are not new physical fields",
            "R_gen": "derived history trace; no backreaction in this lane",
            "R_obs": "observer record kept separate from the formal dynamics",
        },
        "unit_contract": {
            "hbar": "1 (formal lane convention)",
            "k_B": "1 (formal lane convention)",
            "omega": "formal inverse-time/energy unit",
            "beta_th": "inverse formal energy unit",
            "kappa_chi_gamma": "formal action-kernel units",
            "Phi_r_Phi_a": "normalized effective-response copies",
            "sigma_formal": "formal entropy-production witness; not an SI observable",
        },
        "coefficient_policy": "kappa, chi, and gamma are verifier parameters only; physical Kubo records require microscopic or source-backed matching",
        "scope": {
            "closed": "local formal open-system KMS/FDT and entropy-positivity identities",
            "open": "interacting microscopic SK matching, physical Kubo provenance, finite-temperature transport, SI Phi anchor, alpha_Phi_K, and TTG material mapping",
        },
    }
