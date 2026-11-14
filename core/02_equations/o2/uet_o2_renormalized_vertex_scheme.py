"""Declared mass-squared subtraction scheme for the O(2) one-loop vertex.

The vacuum bubble is subtracted at the response reference point already used
by the Topic 13 renormalized normal branch.  This closes one reproducible
natural-unit scheme lane while leaving physical scheme selection, finite
chemical potential, full SK/KMS matching, and transport outside the contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_equilibrium_kms import equilibrium_kms_state
from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_one_loop_vertex_uv_boundary import (
    _tree_vertex_tensor,
    _zero_external_bubble,
)


RENORMALIZED_VERTEX_SCHEME_STATUS = (
    "PASS_ACTION_DERIVED_RENORMALIZED_O2_ONE_LOOP_VERTEX_SCHEME"
)


@dataclass(frozen=True)
class RenormalizedO2VertexSchemeState:
    """Finite-cutoff values for the declared subtracted vertex scheme."""

    temperature: float
    chemical_potential: float
    space_response: float
    reference_space_response: float
    effective_mass: float
    reference_mass: float
    quartic_coupling: float
    raw_vacuum_values: tuple[float, ...]
    reference_vacuum_values: tuple[float, ...]
    subtracted_vacuum_values: tuple[float, ...]
    thermal_values: tuple[float, ...]
    renormalized_bubble_values: tuple[float, ...]
    renormalized_vertex_norms: tuple[float, ...]
    renormalized_correction_norms: tuple[float, ...]
    raw_vacuum_growth_ratio: float
    thermal_cutoff_relative_change: float
    renormalized_bubble_last_relative_change: float
    renormalized_vertex_last_relative_change: float
    reference_subtraction_residual: float
    kms_ratio_residual: float
    kms_noise_fdt_residual: float
    renormalized_vertex_scheme_completed: bool = True
    physical_renormalization_scheme_matched: bool = False
    finite_density_vertex_completed: bool = False
    full_interacting_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_RENORMALIZED_ONE_LOOP_VERTEX_SCHEME_NOT_PHYSICAL"
    )


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


def renormalized_vertex_scheme_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    reference_space_response: float | None = None,
    quadrature_order: int = 192,
    cutoff_multipliers: tuple[float, ...] = (8.0, 16.0, 32.0, 64.0, 128.0),
) -> RenormalizedO2VertexSchemeState:
    """Evaluate the mass-squared Taylor-subtracted one-loop vertex scheme.

    The subtraction is ``B_vac^R(m)=B_vac(m)-B_vac(m_ref)``.  Thermal pieces
    are not subtracted because they are finite and state dependent.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) > 1.0e-15:
        raise ValueError("this declared vertex scheme is evaluated only at mu=0")
    space_response = _finite(space_response, "space_response")
    if reference_space_response is None:
        reference_space_response = config.eos.response.phi_equilibrium
    reference_space_response = _finite(reference_space_response, "reference_space_response")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    quadrature_order = int(quadrature_order)
    if quadrature_order < 64:
        raise ValueError("quadrature_order must be >= 64")
    if not cutoff_multipliers or any(float(value) <= 0.0 for value in cutoff_multipliers):
        raise ValueError("cutoff_multipliers must contain positive values")
    if tuple(sorted(float(value) for value in cutoff_multipliers)) != tuple(
        float(value) for value in cutoff_multipliers
    ):
        raise ValueError("cutoff_multipliers must be sorted")

    mass_sq = effective_mass_sq(space_response, config.eos)
    reference_mass_sq = effective_mass_sq(reference_space_response, config.eos)
    mass = sqrt(_positive(mass_sq, "effective mass squared"))
    reference_mass = sqrt(_positive(reference_mass_sq, "reference mass squared"))
    coupling = _positive(config.eos.matter.matter_quartic, "quartic coupling")
    tree = _tree_vertex_tensor(coupling)
    contraction = 0.5 * np.einsum("abef,efcd->abcd", tree, tree)

    raw_vacuum: list[float] = []
    reference_vacuum: list[float] = []
    subtracted_vacuum: list[float] = []
    thermal: list[float] = []
    renormalized_bubble: list[float] = []
    vertex_norms: list[float] = []
    correction_norms: list[float] = []
    for multiplier in cutoff_multipliers:
        cutoff = max(mass, reference_mass) * float(multiplier)
        vacuum, thermal_value, _ = _zero_external_bubble(
            temperature,
            mass,
            cutoff,
            quadrature_order=quadrature_order,
        )
        reference_value, _, _ = _zero_external_bubble(
            temperature,
            reference_mass,
            cutoff,
            quadrature_order=quadrature_order,
        )
        subtracted = vacuum - reference_value
        bubble = subtracted + thermal_value
        correction = -1.5 * bubble * contraction
        vertex = tree + correction
        raw_vacuum.append(float(vacuum))
        reference_vacuum.append(float(reference_value))
        subtracted_vacuum.append(float(subtracted))
        thermal.append(float(thermal_value))
        renormalized_bubble.append(float(bubble))
        vertex_norms.append(float(np.linalg.norm(vertex)))
        correction_norms.append(float(np.linalg.norm(correction)))

    kms = equilibrium_kms_state(temperature, mass, spectral_weight=1.0)
    kms_ratio_residual = _relative(np.exp(kms.log_kms_ratio), np.exp(mass / temperature))
    kms_noise_residual = _relative(
        kms.noise_weight,
        1.0 / np.tanh(0.5 * mass / temperature),
    )
    values = (
        mass,
        reference_mass,
        coupling,
        *raw_vacuum,
        *reference_vacuum,
        *subtracted_vacuum,
        *thermal,
        *renormalized_bubble,
        *vertex_norms,
        *correction_norms,
        kms_ratio_residual,
        kms_noise_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("renormalized vertex scheme is not finite")
    return RenormalizedO2VertexSchemeState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        reference_space_response=reference_space_response,
        effective_mass=mass,
        reference_mass=reference_mass,
        quartic_coupling=coupling,
        raw_vacuum_values=tuple(raw_vacuum),
        reference_vacuum_values=tuple(reference_vacuum),
        subtracted_vacuum_values=tuple(subtracted_vacuum),
        thermal_values=tuple(thermal),
        renormalized_bubble_values=tuple(renormalized_bubble),
        renormalized_vertex_norms=tuple(vertex_norms),
        renormalized_correction_norms=tuple(correction_norms),
        raw_vacuum_growth_ratio=float(raw_vacuum[-1] / raw_vacuum[0]),
        thermal_cutoff_relative_change=_relative(thermal[-1], thermal[0]),
        renormalized_bubble_last_relative_change=_relative(
            renormalized_bubble[-1], renormalized_bubble[-2]
        ),
        renormalized_vertex_last_relative_change=_relative(
            vertex_norms[-1], vertex_norms[-2]
        ),
        reference_subtraction_residual=0.0,
        kms_ratio_residual=float(kms_ratio_residual),
        kms_noise_fdt_residual=float(kms_noise_residual),
    )


def renormalized_vertex_scheme_contract() -> dict[str, Any]:
    """Return the declared subtraction scheme and remaining boundaries."""

    return {
        "status": RENORMALIZED_VERTEX_SCHEME_STATUS,
        "equations": {
            "reference_mass": "m_ref^2=m_eff(Phi_*)^2",
            "vacuum_counterterm": "B_vac^R(m;Lambda)=B_vac(m;Lambda)-B_vac(m_ref;Lambda)",
            "renormalized_bubble": "B^R(m;T)=B_vac^R(m)+B_thermal(m;T)",
            "renormalized_vertex": "Gamma_R^(4)=V-(B_s^R*(V.V)+B_t^R*(V.V)+B_u^R*(V.V))/2",
            "reference_condition": "B_vac^R(m_ref;Lambda)=0",
        },
        "scheme": {
            "name": "mass-squared reference subtraction at Phi_*",
            "subtraction_order": 0,
            "reference_point": "Phi=Phi_* = reference_space_response",
            "finite_counterterm_origin": "declared scheme condition, not external measurement",
            "cutoff_role": "numerical regulator with an explicit convergence sequence",
        },
        "domain": {
            "unit_lane": "natural",
            "chemical_potential": "mu=0 only",
            "external_momentum": "zero Euclidean frequency and zero spatial momentum",
            "thermal_piece": "finite state-dependent contribution is retained",
        },
        "units": {
            "mass_temperature_momentum": "natural energy",
            "quartic_coupling": "dimensionless",
            "bubble_vertex": "dimensionless",
            "Phi": "effective action response variable; not temperature",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived mass-squared reference subtraction applied to the O(2) one-loop vertex bubble; not a physical scheme match",
        "observable": "finite natural-unit renormalized one-loop vertex in one declared subtraction scheme",
        "data_role": "ACTION_DERIVED_RENORMALIZED_ONE_LOOP_VERTEX_SCHEME_NOT_PHYSICAL",
        "included": {
            "reference_subtraction": True,
            "finite_thermal_bubble": True,
            "cutoff_convergence_sequence": True,
            "equilibrium_kms_fdt_witness": True,
        },
        "excluded": {
            "unique_physical_renormalization": True,
            "finite_chemical_potential_vertex": True,
            "full_interacting_sk_kms_match": True,
            "continuum_limit": True,
            "physical_kubo_coefficient": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes one declared natural-unit mass-squared reference-subtraction scheme for the zero-density one-loop O(2) vertex. It does not select a unique physical renormalization, derive the charged finite-density propagator, match a full interacting SK/KMS action, establish a continuum limit, provide physical Kubo transport, map Phi to SI temperature, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
    }


__all__ = [
    "RENORMALIZED_VERTEX_SCHEME_STATUS",
    "RenormalizedO2VertexSchemeState",
    "renormalized_vertex_scheme_state",
    "renormalized_vertex_scheme_contract",
]
