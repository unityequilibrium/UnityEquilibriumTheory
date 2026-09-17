"""Finite-channel entropy balance and H-theorem witness for Topic 13.

This module turns the separately evaluated forward and reverse elastic channel
weights into a formal discrete entropy-production identity.  The affinity
witness is an explicitly declared internal perturbation; it is not external
data and does not select a physical thermal gradient or an SI heat flux.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log
from typing import Any

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


FINITE_CHANNEL_ENTROPY_BALANCE_STATUS = (
    "PASS_ACTION_DERIVED_FINITE_CHANNEL_ENTROPY_BALANCE_LANE"
)


@dataclass(frozen=True)
class FiniteChannelEntropyBalanceState:
    """Formal finite-channel entropy balance witnesses."""

    temperature: float
    chemical_potential: float
    space_response: float
    channel_count: int
    affinity_scale: float
    channel_affinities: tuple[float, ...]
    channel_entropy_production: tuple[float, ...]
    channel_entropy_flux: tuple[float, ...]
    equilibrium_entropy_production: float
    perturbed_entropy_production: float
    entropy_balance_divergence: float
    entropy_balance_residual: float
    minimum_channel_entropy_production: float
    positive_affinity_witness: bool
    detailed_balance_max_residual: float
    collision_conservation_residual: float
    response_kms_max_residual: float
    response_fdt_max_residual: float
    physical_entropy_current_completed: bool = False
    physical_heat_flux_balance_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_CHANNEL_FORMAL_ENTROPY_BALANCE_NO_SI_FLUX"
    )


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


def finite_channel_entropy_balance_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 24,
    channel_count: int = 12,
    cutoff_factor: float = 36.0,
    affinity_scale: float = 0.05,
) -> FiniteChannelEntropyBalanceState:
    """Evaluate the finite-channel entropy-production identity."""

    temperature = _positive(temperature, "temperature")
    affinity_scale = _positive(affinity_scale, "affinity_scale")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    transition = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        channel_count=channel_count,
        cutoff_factor=cutoff_factor,
    )
    forward = np.asarray(transition.channel_rates, dtype=float)
    reverse = np.asarray(transition.channel_reverse_rates, dtype=float)
    if forward.shape != reverse.shape or not forward.size:
        raise ValueError("forward and reverse channel rates must have equal nonzero shape")
    # This is a declared internal affinity witness, not a fitted gradient.
    imposed_affinity = affinity_scale * np.arange(1.0, float(forward.size) + 1.0) / float(forward.size)
    forward_perturbed = forward * np.exp(0.5 * imposed_affinity)
    reverse_perturbed = reverse * np.exp(-0.5 * imposed_affinity)
    affinities = np.log(forward_perturbed / reverse_perturbed)
    entropy_terms = (forward_perturbed - reverse_perturbed) * affinities / temperature
    entropy_flux = (forward_perturbed - reverse_perturbed) / temperature
    equilibrium_terms = (forward - reverse) * np.log(forward / reverse) / temperature
    total = float(np.sum(entropy_terms))
    divergence = float(np.sum(entropy_flux * affinities))
    values = (
        *affinities,
        *entropy_terms,
        *entropy_flux,
        float(np.sum(equilibrium_terms)),
        total,
        divergence,
        float(np.max(np.abs(entropy_terms - entropy_flux * affinities))),
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("finite-channel entropy balance is not finite")
    return FiniteChannelEntropyBalanceState(
        temperature=transition.temperature,
        chemical_potential=transition.chemical_potential,
        space_response=transition.space_response,
        channel_count=transition.channel_count,
        affinity_scale=affinity_scale,
        channel_affinities=tuple(float(value) for value in affinities),
        channel_entropy_production=tuple(float(value) for value in entropy_terms),
        channel_entropy_flux=tuple(float(value) for value in entropy_flux),
        equilibrium_entropy_production=float(np.sum(equilibrium_terms)),
        perturbed_entropy_production=total,
        entropy_balance_divergence=divergence,
        entropy_balance_residual=abs(total - divergence),
        minimum_channel_entropy_production=float(np.min(entropy_terms)),
        positive_affinity_witness=bool(np.all(affinities > 0.0)),
        detailed_balance_max_residual=max(transition.channel_detailed_balance_residuals),
        collision_conservation_residual=transition.collision_conservation_residual,
        response_kms_max_residual=max(
            abs(value - target) / max(abs(target), 1.0e-300)
            for value, target in zip(transition.kms_ratio, transition.kms_target_ratio)
        ),
        response_fdt_max_residual=max(
            abs(value - target) / max(abs(target), 1.0e-300)
            for value, target in zip(transition.kms_noise, transition.kms_noise_target)
        ),
    )


def finite_channel_entropy_balance_contract() -> dict[str, Any]:
    """Return the formal entropy equations and claim boundary."""

    return {
        "status": FINITE_CHANNEL_ENTROPY_BALANCE_STATUS,
        "equations": {
            "channel_affinity": "A_c=log(W_f,c/W_r,c)",
            "channel_entropy_production": "sigma_c=(W_f,c-W_r,c)*A_c/T>=0",
            "formal_entropy_balance": "partial_mu S^mu_discrete=sum_c sigma_c",
            "equilibrium_boundary": "W_f,c=W_r,c implies A_c=0 and sigma_c=0",
            "declared_internal_witness": "W_f->W_f*exp(+a_c/2); W_r->W_r*exp(-a_c/2), a_c>0",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature": "energy",
            "channel_rate": "formal natural-unit rate",
            "entropy_production": "formal natural-unit channel quantity",
            "entropy_current": "not a covariant SI current in this lane",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-channel H-theorem identity with a declared internal affinity witness"
        ),
        "observable": "formal discrete entropy production and balance residual",
        "data_role": "ACTION_DERIVED_INTERNAL_FORMAL_ENTROPY_NO_SOURCE_ROWS_NO_HOLDOUT",
        "excluded": {
            "covariant_entropy_current": True,
            "physical_heat_flux": True,
            "physical_kubo_coefficient": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only the finite-channel formal entropy-production identity. It does not "
            "close a covariant entropy current, heat-flux balance, physical Kubo coefficient, "
            "SI Phi map, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "FINITE_CHANNEL_ENTROPY_BALANCE_STATUS",
    "FiniteChannelEntropyBalanceState",
    "finite_channel_entropy_balance_state",
    "finite_channel_entropy_balance_contract",
]
