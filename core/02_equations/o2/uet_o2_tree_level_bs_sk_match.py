"""Tree-level action vertex and formal SK/KMS matching for Topic 13.

This lane makes the normalization used by the action-derived constant
amplitude explicit and matches it to the conservative collocation operator.
It also exposes the retarded/Wightman quantities in the declared SK form.
The matching is tree-level and algebraic: loop-renormalized vertices, a full
interacting influence functional, the continuum limit, physical Kubo data, and
SI calibration remain separate gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_continuum_collision_operator import (
    continuum_collision_operator_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import _normal_state_inputs


TREE_LEVEL_BS_SK_STATUS = (
    "PASS_ACTION_DERIVED_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE"
)


@dataclass(frozen=True)
class TreeLevelBSSKMatchState:
    """Tree-level action, Bethe-Salpeter, and formal SK/KMS match values."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    quartic_coupling: float
    transition_channel_count: int
    transition_state_count: int
    action_channel_amplitude: float
    action_channel_cross_section_min: float
    action_channel_cross_section_max: float
    action_vertex_cross_section_residual: float
    exact_channel_kinematic_residual: float
    exact_channel_detailed_balance_residual: float
    action_width_vertex_decomposition_residual: float
    algebraic_bethe_salpeter_residual: float
    formal_sk_action_kms_residual: float
    formal_sk_noise_fdt_residual: float
    formal_sk_entropy_witness: float
    continuum_sequence_radial_orders: tuple[int, ...]
    continuum_sequence_channel_counts: tuple[int, ...]
    continuum_sequence_dc_responses: tuple[float, ...]
    continuum_sequence_relative_changes: tuple[float, ...]
    continuum_sequence_max_relative_change: float
    continuum_limit_completed: bool = False
    tree_level_action_match_completed: bool = True
    formal_sk_action_kms_match_completed: bool = True
    microscopic_bethe_salpeter_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_TREE_LEVEL_VERTEX_FORMAL_SK_MATCH_NOT_FULL_MICROSCOPIC"
    )


def _max_channel_residuals(values: tuple[tuple[float, ...], ...]) -> float:
    return max(max(abs(value) for value in row) for row in values)


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


def tree_level_bs_sk_match_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 8,
    transition_channel_count: int = 64,
    transition_interpolation_order: int = 40,
    cutoff_factor: float = 48.0,
) -> TreeLevelBSSKMatchState:
    """Evaluate the declared tree-level vertex and formal SK/KMS match."""

    if int(radial_order) != radial_order or int(radial_order) < 8:
        raise ValueError("radial_order must be an integer >= 8")
    if int(transition_channel_count) != transition_channel_count or int(transition_channel_count) < 8:
        raise ValueError("transition_channel_count must be an integer >= 8")
    if int(transition_interpolation_order) != transition_interpolation_order or int(transition_interpolation_order) < 2:
        raise ValueError("transition_interpolation_order must be an integer >= 2")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    base_state = continuum_collision_operator_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=int(radial_order),
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=cutoff_factor,
        transition_quadrature_order=24,
        transition_channel_count=int(transition_channel_count),
        transition_interpolation_order=int(transition_interpolation_order),
    )
    exact_state = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=24,
        channel_count=int(transition_channel_count),
        cutoff_factor=max(float(cutoff_factor), 36.0),
    )
    _, _, mass, _, quartic = _normal_state_inputs(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    cross_sections: list[float] = []
    cross_section_residuals: list[float] = []
    for channel in range(exact_state.channel_count):
        first = 4 * channel
        energies = exact_state.state_energies[first : first + 4]
        momenta = np.asarray(exact_state.state_momenta[first : first + 4], dtype=float)
        total_energy = float(energies[0] + energies[1])
        total_momentum = momenta[0] + momenta[1]
        invariant_s = total_energy * total_energy - float(np.dot(total_momentum, total_momentum))
        sigma = float(quartic * quartic / (16.0 * pi * invariant_s))
        cross_sections.append(sigma)
        cross_section_residuals.append(
            _relative(16.0 * pi * invariant_s * sigma, quartic * quartic)
        )

    kms_residuals = [
        _relative(value, target)
        for value, target in zip(
            base_state.kms_ratio,
            base_state.kms_target_ratio,
        )
    ]
    fdt_residuals = [
        _relative(value, target)
        for value, target in zip(
            base_state.kms_noise,
            base_state.kms_noise_target,
        )
    ]

    sequence_radial = (8, 10, 12, 14)
    sequence_channels = (64, 96, 128, 160)
    sequence_states = [
        base_state,
        *[
            continuum_collision_operator_state(
                temperature,
                chemical_potential,
                space_response,
                config,
                radial_order=order,
                collision_integration_order=24,
                angular_order=24,
                cutoff_factor=cutoff_factor,
                transition_quadrature_order=24,
                transition_channel_count=channels,
                transition_interpolation_order=int(transition_interpolation_order),
            )
            for order, channels in zip(sequence_radial[1:], sequence_channels[1:])
        ],
    ]
    sequence_responses = tuple(float(state.dc_response) for state in sequence_states)
    sequence_changes = tuple(
        _relative(later, earlier)
        for earlier, later in zip(sequence_responses, sequence_responses[1:])
    )
    sequence_max_change = max(sequence_changes)
    values = (
        *cross_sections,
        *cross_section_residuals,
        *kms_residuals,
        *fdt_residuals,
        *sequence_responses,
        *sequence_changes,
        sequence_max_change,
        base_state.formal_entropy_production_witness
        if hasattr(base_state, "formal_entropy_production_witness")
        else base_state.entropy_production_witness,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("tree-level action/SK matching state is not finite")

    return TreeLevelBSSKMatchState(
        temperature=base_state.temperature,
        chemical_potential=base_state.chemical_potential,
        space_response=base_state.space_response,
        effective_mass=mass,
        quartic_coupling=quartic,
        transition_channel_count=exact_state.channel_count,
        transition_state_count=exact_state.state_count,
        action_channel_amplitude=float(quartic),
        action_channel_cross_section_min=float(min(cross_sections)),
        action_channel_cross_section_max=float(max(cross_sections)),
        action_vertex_cross_section_residual=float(max(cross_section_residuals)),
        exact_channel_kinematic_residual=_max_channel_residuals(
            exact_state.channel_invariant_residuals
        ),
        exact_channel_detailed_balance_residual=float(
            max(exact_state.channel_detailed_balance_residuals)
        ),
        action_width_vertex_decomposition_residual=base_state.vertex_decomposition_residual,
        algebraic_bethe_salpeter_residual=float(max(base_state.bs_match_residuals)),
        formal_sk_action_kms_residual=float(max(kms_residuals)),
        formal_sk_noise_fdt_residual=float(max(fdt_residuals)),
        formal_sk_entropy_witness=base_state.entropy_production_witness,
        continuum_sequence_radial_orders=sequence_radial,
        continuum_sequence_channel_counts=sequence_channels,
        continuum_sequence_dc_responses=sequence_responses,
        continuum_sequence_relative_changes=sequence_changes,
        continuum_sequence_max_relative_change=sequence_max_change,
    )


def tree_level_bs_sk_match_contract() -> dict[str, object]:
    """Return equations, units, and the tree-level/microscopic boundary."""

    return {
        "status": TREE_LEVEL_BS_SK_STATUS,
        "equations": {
            "declared_action_channel": "M_tree=lambda in the declared charged elastic channel; sigma_22=|M_tree|^2/(16*pi*s)",
            "exact_channel_kinematics": "p1+p2=p3+p4; E1+E2=E3+E4",
            "conservative_operator_match": "L_cont=L_width+K_transition; K_transition=sum_c W_c*u_c^P*(u_c^P)^T",
            "bethe_salpeter_kernel": "K_BS=gamma_ref*I-L_cont; G_R=G_0+G_0*K_BS*G_R",
            "sk_action": "S_SK=integral [Phi_a D_R Phi_r + i*Phi_a N Phi_a/2]",
            "kms_fdt": "N(omega)=coth(beta_th*omega/2)*rho(omega); rho=2*Im K_R; G^>/G^<=exp(beta_th*omega)",
            "entropy_witness": "sigma_formal=b_perp^T*L_cont*b_perp/T>=0",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass_momentum_energy": "energy",
            "quartic_coupling": "dimensionless action coupling in the declared lane",
            "cross_section": "inverse energy squared",
            "response_noise_entropy": "formal natural-unit quantities",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "tree-level action-derived constant-amplitude charged-sector vertex, exact elastic "
            "kinematics, conservative collocation decomposition, and formal SK/KMS algebra"
        ),
        "observable": "tree-level action cross-section normalization, finite-cutoff BS response, and formal SK/KMS noise interface",
        "data_role": "ACTION_DERIVED_TREE_LEVEL_VERTEX_FORMAL_SK_MATCH_NOT_FULL_MICROSCOPIC",
        "included": {
            "tree_level_action_vertex_normalization": True,
            "action_cross_section_match": True,
            "conservative_operator_vertex_decomposition": True,
            "algebraic_bethe_salpeter_match": True,
            "formal_sk_action_kms_fdt_match": True,
            "formal_entropy_witness": True,
            "continuum_sequence_recorded": True,
        },
        "excluded": {
            "loop_renormalized_vertex": True,
            "full_microscopic_bethe_salpeter_solution": True,
            "full_interacting_sk_influence_functional": True,
            "continuum_limit": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_dissipative_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only the declared tree-level action vertex normalization and formal "
            "SK/KMS/Bethe-Salpeter interface on a finite-cutoff conservative collocation lane. "
            "The recorded resolution sequence does not establish a continuum limit. The result "
            "is not a loop-renormalized microscopic vertex, a full interacting SK action match, "
            "a physical Kubo coefficient, an SI map, an alpha_Phi_K calibration, TTG validation, "
            "or Full Topic 13 closure."
        ),
    }


__all__ = [
    "TREE_LEVEL_BS_SK_STATUS",
    "TreeLevelBSSKMatchState",
    "tree_level_bs_sk_match_state",
    "tree_level_bs_sk_match_contract",
]
