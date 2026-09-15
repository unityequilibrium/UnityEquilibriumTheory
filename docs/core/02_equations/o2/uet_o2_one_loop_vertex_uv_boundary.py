"""Action-derived O(2) four-point vertex and one-loop UV boundary.

This lane derives the O(2) tensor vertex from the declared quartic action,
checks its Keldysh contour expansion, and evaluates the zero-external-momentum
Euclidean bubble at finite cutoff.  The thermal bubble is finite while the
vacuum part grows logarithmically with the cutoff.  The result is therefore a
renormalization boundary, not a renormalized microscopic transport claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_equilibrium_kms import equilibrium_kms_state
from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


ONE_LOOP_VERTEX_UV_STATUS = "PASS_ACTION_DERIVED_O2_ONE_LOOP_VERTEX_UV_BOUNDARY"


@dataclass(frozen=True)
class O2OneLoopVertexUVState:
    """Bare O(2) vertex, contour identity, and cutoff boundary values."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    quartic_coupling: float
    tree_vertex_tensor_norm: float
    tree_vertex_symmetry_residual: float
    tree_vertex_o2_rotation_residual: float
    contour_action_identity_residual: float
    contour_classical_vertex_weight: float
    contour_quantum_vertex_weight: float
    cutoff_multipliers: tuple[float, ...]
    bubble_cutoffs: tuple[float, ...]
    bubble_vacuum_values: tuple[float, ...]
    bubble_thermal_values: tuple[float, ...]
    bubble_total_values: tuple[float, ...]
    one_loop_vertex_norms: tuple[float, ...]
    one_loop_correction_norms: tuple[float, ...]
    thermal_cutoff_relative_change: float
    vacuum_growth_ratio: float
    one_loop_correction_growth_ratio: float
    kms_ratio_residual: float
    kms_noise_fdt_residual: float
    one_loop_renormalized_vertex_completed: bool = False
    full_interacting_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_ONE_LOOP_VERTEX_UV_BOUNDARY_NOT_RENORMALIZED"


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


def _tree_vertex_tensor(coupling: float) -> np.ndarray:
    delta = np.eye(2, dtype=float)
    return float(coupling) * (
        np.einsum("ab,cd->abcd", delta, delta)
        + np.einsum("ac,bd->abcd", delta, delta)
        + np.einsum("ad,bc->abcd", delta, delta)
    )


def _zero_external_bubble(
    temperature: float,
    mass: float,
    cutoff: float,
    *,
    quadrature_order: int,
) -> tuple[float, float, float]:
    nodes, weights = np.polynomial.legendre.leggauss(int(quadrature_order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    weights = 0.5 * cutoff * weights
    energy = np.sqrt(momenta * momenta + mass * mass)
    occupation = 1.0 / np.expm1(energy / temperature)
    measure = momenta * momenta / (2.0 * pi**2)
    vacuum = float(np.sum(weights * measure / (4.0 * energy**3)))
    thermal = float(
        np.sum(
            weights
            * measure
            * (
                occupation / (2.0 * energy**3)
                + occupation * (1.0 + occupation) / (2.0 * temperature * energy**2)
            )
        )
    )
    total = vacuum + thermal
    values = (vacuum, thermal, total)
    if not all(isfinite(value) and value > 0.0 for value in values):
        raise FloatingPointError("one-loop bubble returned a non-positive value")
    return values


def _contour_identity(coupling: float) -> tuple[float, float, float]:
    response = np.asarray((0.37, -0.22), dtype=float)
    difference = np.asarray((0.13, 0.19), dtype=float)
    plus = response + 0.5 * difference
    minus = response - 0.5 * difference

    def potential(field: np.ndarray) -> float:
        return float(coupling * np.dot(field, field) ** 2 / 4.0)

    direct = potential(plus) - potential(minus)
    expanded = float(
        coupling * np.dot(response, response) * np.dot(response, difference)
        + coupling
        * np.dot(difference, difference)
        * np.dot(response, difference)
        / 4.0
    )
    residual = abs(direct - expanded) / max(abs(direct), 1.0e-300)
    return float(residual), float(coupling), float(coupling / 4.0)


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


def one_loop_vertex_uv_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 192,
    cutoff_multipliers: tuple[float, ...] = (8.0, 16.0, 32.0, 64.0),
) -> O2OneLoopVertexUVState:
    """Evaluate the bare tensor and finite-cutoff one-loop bubble boundary.

    The present derivation is restricted to the homogeneous normal action at
    zero chemical potential.  This avoids silently replacing the charged
    finite-density propagator by a neutral scalar propagator.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) > 1.0e-15:
        raise ValueError("the one-loop vertex boundary is declared only at mu=0")
    space_response = _finite(space_response, "space_response")
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

    config = config or FiniteTemperatureO2QuasiparticleConfig(
        quadrature_order=quadrature_order
    )
    mass_sq = effective_mass_sq(space_response, config.eos)
    mass = sqrt(_positive(mass_sq, "effective mass squared"))
    coupling = _positive(config.eos.matter.matter_quartic, "quartic coupling")
    tree = _tree_vertex_tensor(coupling)
    symmetry_residual = max(
        float(np.linalg.norm(tree - tree.transpose(permutation)))
        for permutation in (
            (1, 0, 2, 3),
            (0, 1, 3, 2),
            (2, 3, 0, 1),
        )
    ) / max(float(np.linalg.norm(tree)), 1.0e-300)
    angle = 0.37
    rotation = np.asarray(
        ((np.cos(angle), -np.sin(angle)), (np.sin(angle), np.cos(angle))),
        dtype=float,
    )
    rotated = np.einsum("aA,bB,cC,dD,ABCD->abcd", rotation, rotation, rotation, rotation, tree)
    rotation_residual = float(np.max(np.abs(rotated - tree)))
    contour_residual, classical_weight, quantum_weight = _contour_identity(coupling)

    cutoffs: list[float] = []
    vacuum_values: list[float] = []
    thermal_values: list[float] = []
    total_values: list[float] = []
    vertex_norms: list[float] = []
    correction_norms: list[float] = []
    channel_contraction = 0.5 * np.einsum("abef,efcd->abcd", tree, tree)
    for multiplier in cutoff_multipliers:
        cutoff = mass * float(multiplier)
        vacuum, thermal, total = _zero_external_bubble(
            temperature,
            mass,
            cutoff,
            quadrature_order=quadrature_order,
        )
        correction = -1.5 * total * channel_contraction
        vertex = tree + correction
        cutoffs.append(float(cutoff))
        vacuum_values.append(vacuum)
        thermal_values.append(thermal)
        total_values.append(total)
        vertex_norms.append(float(np.linalg.norm(vertex)))
        correction_norms.append(float(np.linalg.norm(correction)))

    kms = equilibrium_kms_state(temperature, mass, spectral_weight=1.0)
    kms_target_ratio = exp(mass / temperature)
    kms_ratio_residual = _relative(exp(kms.log_kms_ratio), kms_target_ratio)
    kms_noise_target = 1.0 / tanh(0.5 * mass / temperature)
    kms_noise_residual = _relative(kms.noise_weight, kms_noise_target)
    values = (
        mass,
        coupling,
        symmetry_residual,
        rotation_residual,
        contour_residual,
        *cutoffs,
        *vacuum_values,
        *thermal_values,
        *total_values,
        *vertex_norms,
        *correction_norms,
        kms_ratio_residual,
        kms_noise_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("one-loop vertex boundary is not finite")
    return O2OneLoopVertexUVState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=mass,
        quartic_coupling=coupling,
        tree_vertex_tensor_norm=float(np.linalg.norm(tree)),
        tree_vertex_symmetry_residual=float(symmetry_residual),
        tree_vertex_o2_rotation_residual=rotation_residual,
        contour_action_identity_residual=float(contour_residual),
        contour_classical_vertex_weight=classical_weight,
        contour_quantum_vertex_weight=quantum_weight,
        cutoff_multipliers=tuple(float(value) for value in cutoff_multipliers),
        bubble_cutoffs=tuple(cutoffs),
        bubble_vacuum_values=tuple(vacuum_values),
        bubble_thermal_values=tuple(thermal_values),
        bubble_total_values=tuple(total_values),
        one_loop_vertex_norms=tuple(vertex_norms),
        one_loop_correction_norms=tuple(correction_norms),
        thermal_cutoff_relative_change=_relative(thermal_values[-1], thermal_values[0]),
        vacuum_growth_ratio=float(vacuum_values[-1] / vacuum_values[0]),
        one_loop_correction_growth_ratio=float(correction_norms[-1] / correction_norms[0]),
        kms_ratio_residual=float(kms_ratio_residual),
        kms_noise_fdt_residual=float(kms_noise_residual),
    )


def one_loop_vertex_uv_contract() -> dict[str, Any]:
    """Return equations, units, and the renormalization boundary."""

    return {
        "status": ONE_LOOP_VERTEX_UV_STATUS,
        "equations": {
            "bare_o2_vertex": "V_abcd=lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)",
            "zero_external_bubble": "B_E^Lambda(0)=integral_0^Lambda d^3k/(2*pi)^3*[(1+2*n_B(E))/(4*E^3)+n_B(E)*(1+n_B(E))/(2*T*E^2)]",
            "one_loop_vertex": "Gamma_1PI^(4)=V-(1/2)*[B_s*(V.V)+B_t*(V.V)+B_u*(V.V)]",
            "sk_contour_interaction": "V(phi_r+phi_a/2)-V(phi_r-phi_a/2)=lambda*(phi_r^2)*(phi_r.phi_a)+(lambda/4)*(phi_a^2)*(phi_r.phi_a)",
            "equilibrium_kms": "G^>/G^<=exp(beta_th*E); N=coth(beta_th*E/2)*rho",
        },
        "domain": {
            "unit_lane": "natural",
            "chemical_potential": "mu=0 only; charged finite-density propagator is not silently substituted",
            "background": "homogeneous normal O(2) mass eigenstate",
            "external_momentum": "zero Euclidean frequency and zero spatial momentum",
            "cutoff": "finite Lambda sequence; vacuum bubble is not renormalized",
        },
        "units": {
            "field": "natural mass dimension one",
            "mass_temperature_momentum": "natural energy",
            "quartic_coupling": "dimensionless",
            "bubble_and_vertex": "dimensionless in 3+1 natural units",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable in the action; not temperature",
            "R_gen": "derived history trace; no backreaction in this lane",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived O(2) tensor vertex, Keldysh contour expansion, zero-external-momentum one-loop Euclidean bubble, and equilibrium KMS witness",
        "observable": "bare O(2) four-point tensor, contour vertex weights, and finite-cutoff one-loop UV boundary",
        "data_role": "ACTION_DERIVED_ONE_LOOP_VERTEX_UV_BOUNDARY_NOT_RENORMALIZED",
        "included": {
            "o2_tensor_vertex": True,
            "o2_rotation_and_permutation_checks": True,
            "tree_level_sk_contour_identity": True,
            "finite_cutoff_one_loop_bubble": True,
            "vacuum_thermal_bubble_separation": True,
            "equilibrium_kms_witness": True,
        },
        "excluded": {
            "vacuum_counterterm": True,
            "renormalized_one_loop_vertex": True,
            "finite_chemical_potential_vertex": True,
            "full_interacting_sk_influence_functional": True,
            "physical_kubo_coefficient": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes only the O(2) bare tensor/contour identity and the finite-cutoff one-loop UV boundary at mu=0. The logarithmically growing vacuum bubble is an explicit renormalization blocker. This is not a renormalized microscopic vertex, a finite-density charged SK action, a full interacting KMS match, a physical Kubo coefficient, an SI map, an alpha_Phi_K calibration, or Full Topic 13 closure.",
    }


__all__ = [
    "ONE_LOOP_VERTEX_UV_STATUS",
    "O2OneLoopVertexUVState",
    "one_loop_vertex_uv_state",
    "one_loop_vertex_uv_contract",
]
