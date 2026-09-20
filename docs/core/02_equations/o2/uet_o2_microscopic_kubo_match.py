"""Finite-cutoff action-matched Kubo interface for Topic 13.

This module joins the declared contact SK vertex, exact transition kernel,
conservative finite-grid operator, and charged current response at one state.
It deliberately stops at a finite cutoff and natural units; the result is not
an SI transport coefficient or a continuum-limit claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_o2_contact_sk_transition_vertex_match import (
    contact_sk_transition_vertex_match_state,
)
from docs.core.uet_o2_continuum_collision_operator import (
    continuum_collision_operator_state,
)
from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


MICROSCOPIC_KUBO_MATCH_STATUS = (
    "PASS_ACTION_MATCHED_MICROSCOPIC_FINITE_CUTOFF_KUBO_LANE"
)
MATCH_TOLERANCE = 1.0e-10


@dataclass(frozen=True)
class MicroscopicKuboMatchState:
    """State and residuals for the finite-cutoff matching contract."""

    temperature: float
    chemical_potential: float
    space_response: float
    dc_response: float
    positive_mode_rate: float
    transition_rate_match_residual: float
    contact_cross_section_match_residual: float
    contact_detailed_balance_residual: float
    bethe_salpeter_match_residual: float
    kms_ratio_residual: float
    fdt_residual: float
    ward_projection_residual: float
    collision_conservation_residual: float
    entropy_production_witness: float
    positive_semidefinite_min_eigenvalue: float
    finite_cutoff: float
    finite_cutoff_boundary_declared: bool
    microscopic_bethe_salpeter_match_completed: bool
    microscopic_sk_kms_match_completed: bool
    continuum_limit_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_MATCHED_FINITE_CUTOFF_KUBO_NOT_SI"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def microscopic_kubo_match_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 8,
    collision_integration_order: int = 24,
    angular_order: int = 24,
    cutoff_factor: float = 48.0,
    transition_quadrature_order: int = 24,
    transition_channel_count: int = 64,
    transition_interpolation_order: int = 40,
) -> MicroscopicKuboMatchState:
    """Join the existing action-derived lanes at one finite-cutoff state."""

    temperature = _finite(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    config = config or FiniteTemperatureO2QuasiparticleConfig()

    continuum = continuum_collision_operator_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=radial_order,
        collision_integration_order=collision_integration_order,
        angular_order=angular_order,
        cutoff_factor=cutoff_factor,
        transition_quadrature_order=transition_quadrature_order,
        transition_channel_count=transition_channel_count,
        transition_interpolation_order=transition_interpolation_order,
    )
    contact = contact_sk_transition_vertex_match_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        channel_count=transition_channel_count,
    )
    exact = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=transition_quadrature_order,
        channel_count=transition_channel_count,
        cutoff_factor=max(float(cutoff_factor), 36.0),
    )

    exact_rates = tuple(float(value) for value in exact.channel_rates)
    matched_rates = tuple(float(value) for value in continuum.transition_channel_rates)
    if len(exact_rates) != len(matched_rates):
        raise ValueError("continuum and exact channel counts do not match")
    rate_residual = max(
        abs(left - right) / max(abs(right), 1.0e-300)
        for left, right in zip(matched_rates, exact_rates)
    )
    kms_ratio_residual = max(
        abs(left - right)
        for left, right in zip(continuum.kms_ratio, continuum.kms_target_ratio)
    )
    fdt_residual = max(
        abs(left - right)
        for left, right in zip(continuum.kms_noise, continuum.kms_noise_target)
    )
    bethe_salpeter_residual = max(abs(value) for value in continuum.bs_match_residuals)
    state_match = (
        continuum.temperature == contact.temperature == temperature
        and continuum.chemical_potential == contact.chemical_potential == chemical_potential
        and continuum.space_response == contact.space_response == space_response
    )
    if not state_match:
        raise FloatingPointError("matched lanes do not share the declared state")

    microscopic_bethe_salpeter_match = (
        rate_residual <= MATCH_TOLERANCE
        and bethe_salpeter_residual <= MATCH_TOLERANCE
        and continuum.transition_support_connected
        and continuum.collision_conservation_residual <= MATCH_TOLERANCE
    )
    microscopic_sk_kms_match = (
        contact.cross_section_match_residual <= MATCH_TOLERANCE
        and contact.max_channel_detailed_balance_residual <= MATCH_TOLERANCE
        and contact.charged_particle_kms_residual <= MATCH_TOLERANCE
        and contact.charged_antiparticle_kms_residual <= MATCH_TOLERANCE
        and kms_ratio_residual <= MATCH_TOLERANCE
        and fdt_residual <= MATCH_TOLERANCE
    )
    values = (
        continuum.dc_response,
        continuum.positive_mode_rate,
        rate_residual,
        contact.cross_section_match_residual,
        contact.max_channel_detailed_balance_residual,
        bethe_salpeter_residual,
        kms_ratio_residual,
        fdt_residual,
        continuum.projected_mapped_invariant_residual,
        continuum.collision_conservation_residual,
        continuum.entropy_production_witness,
        continuum.positive_semidefinite_min_eigenvalue,
        continuum.momentum_cutoff,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("microscopic Kubo match is not finite")

    return MicroscopicKuboMatchState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        dc_response=float(continuum.dc_response),
        positive_mode_rate=float(continuum.positive_mode_rate),
        transition_rate_match_residual=float(rate_residual),
        contact_cross_section_match_residual=float(contact.cross_section_match_residual),
        contact_detailed_balance_residual=float(contact.max_channel_detailed_balance_residual),
        bethe_salpeter_match_residual=float(bethe_salpeter_residual),
        kms_ratio_residual=float(kms_ratio_residual),
        fdt_residual=float(fdt_residual),
        ward_projection_residual=float(continuum.projected_mapped_invariant_residual),
        collision_conservation_residual=float(continuum.collision_conservation_residual),
        entropy_production_witness=float(continuum.entropy_production_witness),
        positive_semidefinite_min_eigenvalue=float(continuum.positive_semidefinite_min_eigenvalue),
        finite_cutoff=float(continuum.momentum_cutoff),
        finite_cutoff_boundary_declared=bool(continuum.finite_cutoff_boundary_declared),
        microscopic_bethe_salpeter_match_completed=bool(microscopic_bethe_salpeter_match),
        microscopic_sk_kms_match_completed=bool(microscopic_sk_kms_match),
    )


def microscopic_kubo_match_contract() -> dict[str, object]:
    """Return the finite-cutoff matching equations and claim boundary."""

    return {
        "status": MICROSCOPIC_KUBO_MATCH_STATUS,
        "equations": {
            "contact_vertex": "M_22=lambda; sigma_22=|M_22|^2/(16*pi*s)",
            "conservative_operator": "L=L_width+V_transition; L*I_(charge,E,P)=0",
            "retarded_current": "G_R^JJ(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp",
            "Kubo_response": "K_DC=Re G_R^JJ(0) on the declared finite-cutoff lane",
            "KMS": "G^>/G^<=exp(beta*omega)",
            "entropy": "sigma=b_perp^T*L*b_perp/T>=0",
        },
        "unit_contract": {
            "unit_lane": "natural finite-cutoff",
            "temperature_chemical_potential_frequency": "energy",
            "dc_response": "natural finite-cutoff response coefficient; not SI",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived physical/history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived contact-SK, exact transition, conservative Bethe-Salpeter, and retarded current matching",
        "observable": "finite-cutoff charged retarded current response and KMS/FDT/entropy residuals",
        "data_role": "ACTION_MATCHED_FINITE_CUTOFF_KUBO_NOT_SI",
        "excluded": {
            "continuum_limit": True,
            "loop_renormalized_offshell_self_energy": True,
            "physical_SI_Kubo_coefficient": True,
            "finite_temperature_two_fluid_completion": True,
            "dimensional_Phi_to_thermal_map": True,
            "alpha_Phi_K": True,
            "Ding_C_src": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": "This closes only the declared action-matched finite-cutoff natural-unit Kubo interface. It is not a continuum-limit or SI transport coefficient, not a complete two-fluid theory, and not Full Topic 13 closure.",
    }


__all__ = [
    "MICROSCOPIC_KUBO_MATCH_STATUS",
    "MicroscopicKuboMatchState",
    "microscopic_kubo_match_state",
    "microscopic_kubo_match_contract",
]
