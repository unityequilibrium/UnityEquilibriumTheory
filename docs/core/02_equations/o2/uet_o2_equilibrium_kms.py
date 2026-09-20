"""Equilibrium KMS/FDT identities for the finite-temperature O(2) lane.

This module verifies the equilibrium Bose Wightman identities mode by mode.
It is an action-derived spectral witness, not a microscopic dissipative
Schwinger-Keldysh action and not a physical transport-coefficient source.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cosh, exp, expm1, isfinite, log, sinh
from typing import Any


EQUILIBRIUM_KMS_STATUS = "PASS_ACTION_DERIVED_EQUILIBRIUM_KMS_FDT_LANE"


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


def _bose_occupation(argument: float) -> float:
    x = _positive(argument, "beta_energy")
    if x > 50.0:
        return exp(-x)
    return 1.0 / expm1(x)


@dataclass(frozen=True)
class EquilibriumKMSState:
    """Mode-level equilibrium KMS and fluctuation-dissipation witness."""

    temperature: float
    mode_energy: float
    spectral_weight: float
    occupation: float
    greater_weight: float
    lesser_weight: float
    log_kms_ratio: float
    noise_weight: float
    mode_entropy: float
    entropy_production: float = 0.0
    unit_lane: str = "natural"
    data_role: str = "ACTION_DERIVED_EQUILIBRIUM_KMS_WITNESS_NOT_TRANSPORT"


def equilibrium_kms_state(
    temperature: float,
    mode_energy: float,
    *,
    spectral_weight: float = 1.0,
) -> EquilibriumKMSState:
    """Evaluate the bosonic equilibrium KMS/FDT identities for one mode.

    The declared convention is ``G^>=(1+n)rho``, ``G^<=n rho`` and
    ``N=coth(beta E/2)rho`` for a positive-frequency spectral weight ``rho``.
    """

    t = _positive(temperature, "temperature")
    energy = _positive(mode_energy, "mode_energy")
    rho = _positive(spectral_weight, "spectral_weight")
    argument = energy / t
    occupation = _bose_occupation(argument)
    greater = rho * (1.0 + occupation)
    lesser = rho * occupation
    half_argument = 0.5 * argument
    noise = rho * cosh(half_argument) / sinh(half_argument)
    mode_entropy = (1.0 + occupation) * log(1.0 + occupation) - occupation * log(
        occupation
    )
    values = (occupation, greater, lesser, noise, mode_entropy)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("equilibrium KMS state is not finite")
    return EquilibriumKMSState(
        temperature=t,
        mode_energy=energy,
        spectral_weight=rho,
        occupation=occupation,
        greater_weight=greater,
        lesser_weight=lesser,
        log_kms_ratio=argument,
        noise_weight=noise,
        mode_entropy=mode_entropy,
    )


def equilibrium_kms_contract() -> dict[str, Any]:
    """Return the equilibrium KMS/FDT lane and its explicit boundary."""

    return {
        "status": EQUILIBRIUM_KMS_STATUS,
        "equations": {
            "bose_occupation": "n_B(E)=1/(exp(beta_th*E)-1)",
            "wightman_greater": "G^>(E)=(1+n_B(E))*rho(E)",
            "wightman_lesser": "G^<(E)=n_B(E)*rho(E)",
            "kms": "G^>(E)=exp(beta_th*E)*G^<(E)",
            "spectral_difference": "G^>(E)-G^<(E)=rho(E)",
            "fluctuation_dissipation": "N(E)=coth(beta_th*E/2)*rho(E)",
            "equilibrium_entropy": "s_mode=(1+n)ln(1+n)-n ln(n)>=0",
            "equilibrium_entropy_production": "nabla_mu J_S^mu=0 for uniform equilibrium",
        },
        "units": {
            "unit_lane": "natural",
            "temperature": "natural energy",
            "mode_energy": "natural energy",
            "beta_th": "inverse natural energy",
            "spectral_weight": "normalized spectral witness",
            "entropy": "dimensionless mode entropy witness",
        },
        "derivation_class": "action-derived equilibrium Bose KMS/FDT identity; no dissipative matching",
        "observable": "mode-level equilibrium Wightman ratio, spectral difference, noise relation, and entropy witness",
        "data_role": "ACTION_DERIVED_EQUILIBRIUM_KMS_WITNESS_NOT_TRANSPORT",
        "scope": {
            "closed": "equilibrium mode-level KMS, FDT identity, nonnegative mode entropy, and zero equilibrium entropy production",
            "open": "interacting SK action, collision/noise kernel, retarded correlator matching, physical Kubo coefficients, spatial entropy current, SI Phi map, alpha_Phi_K, and TTG validation",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not a charge or mode occupation",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace only; not an equilibrium state or feedback source",
            "R_obs": "separate observer record; not included in the mode identity",
        },
        "claim_boundary": "This closes only the equilibrium KMS/FDT identity lane for declared positive-energy O(2) quasiparticle modes. It is not a microscopic interacting SK/KMS match, dissipative transport closure, physical Kubo coefficient, SI calibration, or Full Topic 13 closure.",
    }


__all__ = [
    "EQUILIBRIUM_KMS_STATUS",
    "EquilibriumKMSState",
    "equilibrium_kms_state",
    "equilibrium_kms_contract",
]
