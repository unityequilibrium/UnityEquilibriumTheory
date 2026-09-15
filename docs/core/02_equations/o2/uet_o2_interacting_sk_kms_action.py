"""Exact local interacting SK contour and charged KMS interface.

The local O(2) action is evaluated on the two contour branches and rewritten
in ``r/a`` variables.  This closes the algebraic interacting contour
identity and attaches the charged KMS/detailed-balance witnesses already
defined for the normal branch.  It deliberately does not claim a nonlocal
influence functional, a physical retarded self-energy, or a Kubo coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_density_charged_vertex import (
    finite_density_charged_vertex_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


INTERACTING_SK_KMS_ACTION_STATUS = (
    "PASS_ACTION_DERIVED_INTERACTING_SK_KMS_LOCAL_ACTION_INTERFACE"
)


@dataclass(frozen=True)
class InteractingSKKMSActionState:
    """Local contour identities and charged equilibrium witnesses."""

    temperature: float
    chemical_potential: float
    effective_chemical_potential: float
    space_response: float
    effective_mass: float
    quartic_coupling: float
    contour_action_difference: float
    contour_ra_expansion_residual: float
    contour_unitarity_residual: float
    contour_reality_residual: float
    no_pure_r_interaction_residual: float
    ra_interaction_r3a_weight: float
    ra_interaction_ra3_weight: float
    charged_particle_kms_residual: float
    charged_antiparticle_kms_residual: float
    charged_collision_detailed_balance_residual: float
    charged_collision_kms_residual: float
    charged_collision_fdt_residual: float
    formal_entropy_witness: float
    local_interacting_sk_action_completed: bool = True
    formal_charged_kms_match_completed: bool = True
    nonlocal_influence_functional_completed: bool = False
    microscopic_retarded_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_LOCAL_INTERACTING_SK_KMS_INTERFACE_NOT_PHYSICAL_TRANSPORT"
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


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


def _rotation_generator() -> np.ndarray:
    return np.asarray(((0.0, -1.0), (1.0, 0.0)), dtype=float)


def _quartic_potential(field: np.ndarray, coupling: float) -> float:
    norm_sq = float(np.dot(field, field))
    return float(coupling * norm_sq * norm_sq / 4.0)


def _local_euclidean_action_density(
    field: np.ndarray,
    temporal_derivative: np.ndarray,
    spatial_gradient: np.ndarray,
    mass_sq: float,
    coupling: float,
    effective_chemical_potential: float,
) -> float:
    generator = _rotation_generator()
    covariant_time = temporal_derivative + effective_chemical_potential * generator @ field
    return float(
        0.5 * np.dot(covariant_time, covariant_time)
        + 0.5 * np.sum(np.asarray(spatial_gradient, dtype=float) ** 2)
        + 0.5 * mass_sq * np.dot(field, field)
        + _quartic_potential(field, coupling)
    )


def _contour_witnesses(
    mass_sq: float,
    coupling: float,
    effective_chemical_potential: float,
) -> tuple[float, float, float, float, float, float, float]:
    response = np.asarray((0.37, -0.22), dtype=float)
    difference = np.asarray((0.13, 0.19), dtype=float)
    response_time = np.asarray((0.17, -0.08), dtype=float)
    difference_time = np.asarray((-0.11, 0.07), dtype=float)
    response_gradient = np.asarray(((0.09, -0.04, 0.03), (-0.06, 0.05, 0.02)))
    difference_gradient = np.asarray(((0.02, 0.03, -0.05), (0.04, -0.01, 0.06)))
    plus = response + 0.5 * difference
    minus = response - 0.5 * difference
    plus_time = response_time + 0.5 * difference_time
    minus_time = response_time - 0.5 * difference_time
    plus_gradient = response_gradient + 0.5 * difference_gradient
    minus_gradient = response_gradient - 0.5 * difference_gradient
    direct = _local_euclidean_action_density(
        plus,
        plus_time,
        plus_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    ) - _local_euclidean_action_density(
        minus,
        minus_time,
        minus_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    )
    generator = _rotation_generator()
    covariant_response_time = response_time + effective_chemical_potential * generator @ response
    covariant_difference_time = difference_time + effective_chemical_potential * generator @ difference
    quadratic_difference = float(
        np.dot(covariant_response_time, covariant_difference_time)
        + np.sum(response_gradient * difference_gradient)
        + mass_sq * np.dot(response, difference)
    )
    response_norm_sq = float(np.dot(response, response))
    difference_norm_sq = float(np.dot(difference, difference))
    quartic_difference = float(
        coupling * response_norm_sq * np.dot(response, difference)
        + coupling * difference_norm_sq * np.dot(response, difference) / 4.0
    )
    expansion = quadratic_difference + quartic_difference
    expansion_residual = _relative(direct, expansion)
    unitary = _local_euclidean_action_density(
        response,
        response_time,
        response_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    ) - _local_euclidean_action_density(
        response,
        response_time,
        response_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    )
    negative_difference = _local_euclidean_action_density(
        response - 0.5 * difference,
        response_time - 0.5 * difference_time,
        response_gradient - 0.5 * difference_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    ) - _local_euclidean_action_density(
        response + 0.5 * difference,
        response_time + 0.5 * difference_time,
        response_gradient + 0.5 * difference_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    )
    reality = _relative(direct, -negative_difference)
    no_a = _local_euclidean_action_density(
        response,
        response_time,
        response_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    ) - _local_euclidean_action_density(
        response,
        response_time,
        response_gradient,
        mass_sq,
        coupling,
        effective_chemical_potential,
    )
    quartic_r3a = coupling * response_norm_sq * np.dot(response, difference)
    quartic_ra3 = coupling * difference_norm_sq * np.dot(response, difference) / 4.0
    return (
        float(direct),
        float(expansion_residual),
        float(abs(unitary)),
        float(reality),
        float(abs(no_a)),
        float(quartic_r3a),
        float(quartic_ra3),
    )


def interacting_sk_kms_action_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    channel_count: int = 12,
) -> InteractingSKKMSActionState:
    """Evaluate the exact local contour and charged KMS interface."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if int(channel_count) != channel_count or int(channel_count) < 4:
        raise ValueError("channel_count must be an integer >= 4")
    charged = finite_density_charged_vertex_state(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    contour = _contour_witnesses(
        charged.effective_mass**2,
        charged.quartic_coupling,
        charged.effective_chemical_potential,
    )
    transition = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        channel_count=int(channel_count),
    )
    collision_kms_residual = max(
        _relative(value, target)
        for value, target in zip(transition.kms_ratio, transition.kms_target_ratio)
    )
    collision_fdt_residual = max(
        _relative(value, target)
        for value, target in zip(transition.kms_noise, transition.kms_noise_target)
    )
    values = (
        *contour,
        charged.particle_kms_residual,
        charged.antiparticle_kms_residual,
        max(transition.channel_detailed_balance_residuals),
        collision_kms_residual,
        collision_fdt_residual,
        transition.entropy_production_witness,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("interacting local SK/KMS state is not finite")
    return InteractingSKKMSActionState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        effective_chemical_potential=charged.effective_chemical_potential,
        space_response=space_response,
        effective_mass=charged.effective_mass,
        quartic_coupling=charged.quartic_coupling,
        contour_action_difference=contour[0],
        contour_ra_expansion_residual=contour[1],
        contour_unitarity_residual=contour[2],
        contour_reality_residual=contour[3],
        no_pure_r_interaction_residual=contour[4],
        ra_interaction_r3a_weight=contour[5],
        ra_interaction_ra3_weight=contour[6],
        charged_particle_kms_residual=charged.particle_kms_residual,
        charged_antiparticle_kms_residual=charged.antiparticle_kms_residual,
        charged_collision_detailed_balance_residual=float(
            max(transition.channel_detailed_balance_residuals)
        ),
        charged_collision_kms_residual=float(collision_kms_residual),
        charged_collision_fdt_residual=float(collision_fdt_residual),
        formal_entropy_witness=float(transition.entropy_production_witness),
    )


def interacting_sk_kms_action_contract() -> dict[str, Any]:
    """Return the local action-level SK/KMS contract and boundaries."""

    return {
        "status": INTERACTING_SK_KMS_ACTION_STATUS,
        "equations": {
            "contour_action": "S_SK=S_E[Phi_r+Phi_a/2]-S_E[Phi_r-Phi_a/2]",
            "covariant_time_derivative": "D_tau Phi=partial_tau Phi+mu_eff*J*Phi; J^2=-I",
            "quartic_ra_expansion": "V(r+a/2)-V(r-a/2)=lambda*(r.r)*(r.a)+(lambda/4)*(a.a)*(r.a)",
            "interaction_vertices": "S_int,SK contains r^3*a and r*a^3 only; no pure-r interaction",
            "charged_kms": "G_particle^>/G_particle^<=exp(beta*(E-mu_eff)); G_antiparticle^>/G_antiparticle^<=exp(beta*(E+mu_eff))",
            "collision_detailed_balance": "W_forward/W_reverse=exp[-beta*(Delta E-mu_eff*Delta Q)] = 1 on conserved channels",
            "fluctuation_dissipation": "N(omega)=coth(beta*omega/2)*rho(omega) for the declared equilibrium mode interface",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_mass_momentum_chemical_potential": "natural energy",
            "action_density": "natural energy density",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "exact local O(2) contour action difference plus action-derived charged detailed-balance and equilibrium KMS/FDT identities",
        "observable": "local interacting contour algebra and charged equilibrium KMS/detailed-balance interface",
        "data_role": "ACTION_DERIVED_LOCAL_INTERACTING_SK_KMS_INTERFACE_NOT_PHYSICAL_TRANSPORT",
        "included": {
            "local_interacting_contour_action": True,
            "unitarity_contour_identity": True,
            "ra_vertex_content": True,
            "charged_kms_fdt": True,
            "charged_collision_detailed_balance": True,
            "formal_entropy_witness": True,
        },
        "excluded": {
            "nonlocal_influence_functional": True,
            "microscopic_retarded_self_energy": True,
            "unique_physical_renormalization": True,
            "condensed_two_fluid_completion": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_dissipative_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes the local action-level interacting SK contour and charged equilibrium KMS/detailed-balance interface. It does not derive a nonlocal influence functional or microscopic retarded self-energy, select a unique physical renormalization, close the condensed/two-fluid sector, provide physical Kubo transport or entropy-current balance, map Phi to SI temperature, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
    }


__all__ = [
    "INTERACTING_SK_KMS_ACTION_STATUS",
    "InteractingSKKMSActionState",
    "interacting_sk_kms_action_state",
    "interacting_sk_kms_action_contract",
]
