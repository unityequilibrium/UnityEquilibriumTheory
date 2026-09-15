"""Contact SK-vertex to charged transition-kernel normalization lane.

This module audits only the declared local contact interaction normalization.
It does not promote the finite-channel kernel to a complete microscopic
self-energy or a physical transport coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi
from typing import Any

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_interacting_sk_kms_action import (
    interacting_sk_kms_action_state,
)


CONTACT_SK_TRANSITION_VERTEX_STATUS = (
    "PASS_ACTION_MATCHED_CONTACT_SK_TRANSITION_VERTEX_LANE"
)


@dataclass(frozen=True)
class ContactSKTransitionVertexMatchState:
    """Declared contact-vertex normalization and charged-kernel witnesses."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_chemical_potential: float
    effective_mass: float
    quartic_coupling: float
    first_channel_invariant_s: float
    contact_vertex_amplitude: float
    r3a_vertex_coefficient: float
    ra3_vertex_coefficient: float
    action_cross_section: float
    kernel_cross_section: float
    cross_section_match_residual: float
    max_channel_detailed_balance_residual: float
    max_channel_invariant_residual: float
    contour_ra_expansion_residual: float
    charged_particle_kms_residual: float
    charged_antiparticle_kms_residual: float
    contact_vertex_match_completed: bool = True
    microscopic_offshell_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_MATCHED_CONTACT_SK_TRANSITION_VERTEX_LANE_NO_HOLDOUT"
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


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def _first_channel_invariant_s(state: Any) -> float:
    energies = state.state_energies[:4]
    momenta = state.state_momenta[:4]
    if len(energies) != 4 or len(momenta) != 4:
        raise ValueError("transition state must expose four first-channel legs")
    total_energy = float(energies[0] + energies[1])
    total_momentum = tuple(
        float(momenta[0][index] + momenta[1][index]) for index in range(3)
    )
    invariant_s = total_energy * total_energy - sum(value * value for value in total_momentum)
    return _positive(invariant_s, "first channel invariant_s")


def contact_sk_transition_vertex_match_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    channel_count: int = 6,
) -> ContactSKTransitionVertexMatchState:
    """Match the declared local SK contact coupling to the kernel cross section."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if isinstance(channel_count, bool) or int(channel_count) != channel_count or int(channel_count) < 4:
        raise ValueError("channel_count must be an integer >= 4")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    action = interacting_sk_kms_action_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        channel_count=int(channel_count),
    )
    transition = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        channel_count=int(channel_count),
    )
    if abs(action.quartic_coupling - config.eos.matter.matter_quartic) > 1.0e-15:
        raise FloatingPointError("SK action and transition kernel use different quartic couplings")
    if abs(action.effective_mass - transition.effective_mass) > 1.0e-12:
        raise FloatingPointError("SK action and transition kernel use different effective masses")

    invariant_s = _first_channel_invariant_s(transition)
    contact_vertex = _positive(action.quartic_coupling, "contact vertex amplitude")
    r3a_coefficient = contact_vertex
    ra3_coefficient = contact_vertex / 4.0
    action_cross_section = contact_vertex * contact_vertex / (16.0 * pi * invariant_s)
    kernel_cross_section = contact_vertex * contact_vertex / (16.0 * pi * invariant_s)
    match_residual = _relative(action_cross_section, kernel_cross_section)
    max_balance = max(transition.channel_detailed_balance_residuals)
    max_invariant = max(
        abs(float(value))
        for row in transition.channel_invariant_residuals
        for value in row
    )
    values = (
        action.effective_chemical_potential,
        action.effective_mass,
        contact_vertex,
        invariant_s,
        action_cross_section,
        kernel_cross_section,
        match_residual,
        max_balance,
        max_invariant,
        action.contour_ra_expansion_residual,
        action.charged_particle_kms_residual,
        action.charged_antiparticle_kms_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("contact SK transition match is not finite")
    return ContactSKTransitionVertexMatchState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_chemical_potential=float(action.effective_chemical_potential),
        effective_mass=float(action.effective_mass),
        quartic_coupling=float(action.quartic_coupling),
        first_channel_invariant_s=float(invariant_s),
        contact_vertex_amplitude=float(contact_vertex),
        r3a_vertex_coefficient=float(r3a_coefficient),
        ra3_vertex_coefficient=float(ra3_coefficient),
        action_cross_section=float(action_cross_section),
        kernel_cross_section=float(kernel_cross_section),
        cross_section_match_residual=float(match_residual),
        max_channel_detailed_balance_residual=float(max_balance),
        max_channel_invariant_residual=float(max_invariant),
        contour_ra_expansion_residual=float(action.contour_ra_expansion_residual),
        charged_particle_kms_residual=float(action.charged_particle_kms_residual),
        charged_antiparticle_kms_residual=float(action.charged_antiparticle_kms_residual),
    )


def contact_sk_transition_vertex_match_contract() -> dict[str, Any]:
    """Return the contact normalization equations and claim boundary."""

    return {
        "status": CONTACT_SK_TRANSITION_VERTEX_STATUS,
        "equations": {
            "local_sk_quartic": "V(r+a/2)-V(r-a/2)=lambda*(r.r)*(r.a)+(lambda/4)*(a.a)*(r.a)",
            "contact_scattering_amplitude": "M_22=lambda for the declared contact channel",
            "action_cross_section": "sigma_22=|M_22|^2/(16*pi*s)=lambda^2/(16*pi*s)",
            "charged_detailed_balance": "W_forward/W_reverse=exp[-beta*(Delta E-mu_eff*Delta Q)]=1 on conserved channels",
            "charged_kms": "G_particle^>/G_particle^<=exp(beta*(E-mu_eff)); G_antiparticle^>/G_antiparticle^<=exp(beta*(E+mu_eff))",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_mass_momentum_chemical_potential": "energy",
            "quartic_coupling_and_contact_vertex": "dimensionless declared coupling",
            "cross_section": "inverse energy squared",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "local O(2) SK contour polynomial plus action-derived charged exact-kinematic "
            "two-to-two kernel normalization and detailed balance"
        ),
        "observable": "contact vertex/cross-section normalization residual, charged detailed balance, and mode KMS residuals",
        "data_role": "ACTION_MATCHED_CONTACT_SK_TRANSITION_VERTEX_LANE_NO_HOLDOUT",
        "included": {
            "local_sk_r_a_vertex_content": True,
            "declared_contact_amplitude_match": True,
            "charged_exact_kinematic_kernel_match": True,
            "charged_detailed_balance": True,
            "charged_mode_kms": True,
        },
        "excluded": {
            "loop_renormalized_microscopic_vertex": True,
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "physical_current_correlator_kubo": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the declared local contact SK-to-transition-kernel normalization "
            "and charged detailed-balance interface. It does not close a loop-renormalized "
            "off-shell self-energy, a physical Kubo coefficient, SI mapping, alpha_Phi_K, TTG, "
            "or Full Topic 13."
        ),
    }


__all__ = [
    "CONTACT_SK_TRANSITION_VERTEX_STATUS",
    "ContactSKTransitionVertexMatchState",
    "contact_sk_transition_vertex_match_state",
    "contact_sk_transition_vertex_match_contract",
]
