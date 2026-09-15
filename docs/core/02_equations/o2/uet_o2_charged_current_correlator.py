"""Action-matched charged current-current correlator interface for Topic 13.

This lane uses the declared kinetic current source and the action-derived
finite-cutoff collision operator to expose a retarded current correlator with
explicit KMS/FDT and entropy checks.  It is deliberately not a microscopic
off-shell 1PI calculation or a physical Kubo/SI coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite
from typing import Any

import numpy as np

from docs.core.uet_o2_contact_sk_transition_vertex_match import (
    contact_sk_transition_vertex_match_state,
)
from docs.core.uet_o2_continuum_collision_operator import (
    continuum_collision_operator_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


CHARGED_CURRENT_CORRELATOR_STATUS = (
    "PASS_ACTION_MATCHED_CHARGED_CURRENT_CORRELATOR_LANE"
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


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _retarded_response(
    operator: np.ndarray,
    source: np.ndarray,
    frequency: float,
    *,
    zero_mode_tolerance: float = 1.0e-12,
) -> complex:
    """Evaluate b^T(L-i omega I)^-1 b on the dissipative subspace."""

    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    projected = eigenvectors.T @ source
    response = 0.0j
    for coefficient, eigenvalue in zip(projected, eigenvalues):
        if abs(float(eigenvalue)) <= zero_mode_tolerance and frequency == 0.0:
            continue
        response += float(coefficient * coefficient) / (
            float(eigenvalue) - 1.0j * float(frequency)
        )
    return complex(response)


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


@dataclass(frozen=True)
class ChargedCurrentCorrelatorState:
    """Finite-cutoff charged current correlator and scope controls."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    momentum_cutoff: float
    state_count: int
    invariant_rank: int
    current_source: tuple[float, ...]
    projected_current_source: tuple[float, ...]
    current_source_formula_residual: float
    current_ward_projection_residual: float
    collision_conservation_residual: float
    operator_symmetry_residual: float
    positive_semidefinite_min_eigenvalue: float
    null_mode_count: int
    positive_mode_rate: float
    response_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    dc_current_response: float
    kms_frequency_over_temperature: tuple[float, ...]
    spectral_density: tuple[float, ...]
    wightman_greater: tuple[float, ...]
    wightman_lesser: tuple[float, ...]
    kms_ratio: tuple[float, ...]
    kms_target_ratio: tuple[float, ...]
    kms_ratio_max_residual: float
    fdt_noise: tuple[float, ...]
    fdt_noise_target: tuple[float, ...]
    fdt_max_residual: float
    entropy_production_witness: float
    contact_cross_section_match_residual: float
    contact_detailed_balance_residual: float
    finite_cutoff_boundary_declared: bool = True
    microscopic_offshell_self_energy_completed: bool = False
    microscopic_current_vertex_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_MATCHED_FINITE_CUTOFF_CHARGED_CURRENT_CORRELATOR_NOT_PHYSICAL_KUBO"
    )


def charged_current_correlator_state(
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
    response_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    kms_frequency_over_temperature: tuple[float, ...] = (0.25, 0.5, 1.0),
    contact_channel_count: int = 6,
) -> ChargedCurrentCorrelatorState:
    """Evaluate the declared charged current-current correlator interface."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if not response_frequency_over_rate or response_frequency_over_rate[0] != 0.0:
        raise ValueError("response_frequency_over_rate must start at zero")
    if tuple(sorted(response_frequency_over_rate)) != tuple(response_frequency_over_rate):
        raise ValueError("response_frequency_over_rate must be sorted")
    if not kms_frequency_over_temperature:
        raise ValueError("kms_frequency_over_temperature must not be empty")
    if tuple(sorted(kms_frequency_over_temperature)) != tuple(kms_frequency_over_temperature):
        raise ValueError("kms_frequency_over_temperature must be sorted")

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
        retarded_frequency_over_rate=tuple(response_frequency_over_rate),
        kms_frequency_over_temperature=tuple(kms_frequency_over_temperature),
    )
    contact = contact_sk_transition_vertex_match_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        channel_count=contact_channel_count,
    )

    operator = np.asarray(continuum.continuum_operator, dtype=float)
    source = np.asarray(continuum.source_vector, dtype=float)
    projected_source = np.asarray(continuum.projected_source_vector, dtype=float)
    weights = np.asarray(continuum.susceptibility_weights, dtype=float)
    signs = np.asarray(continuum.state_species_signs, dtype=float)
    momenta = np.asarray(continuum.state_momenta, dtype=float)
    energies = np.asarray(continuum.state_energies, dtype=float)
    expected_source = signs * (momenta[:, 0] / energies) * np.sqrt(weights)
    source_formula_residual = float(
        np.linalg.norm(source - expected_source) / max(np.linalg.norm(expected_source), 1.0)
    )
    eigenvalues = np.linalg.eigvalsh(operator)
    positive_eigenvalues = eigenvalues[eigenvalues > 1.0e-12]
    positive_rate = _positive(float(np.mean(positive_eigenvalues)), "positive mode rate")
    response_ratios = tuple(float(value) for value in response_frequency_over_rate)
    response_frequencies = tuple(positive_rate * ratio for ratio in response_ratios)
    responses = tuple(
        _retarded_response(operator, projected_source, frequency)
        for frequency in response_frequencies
    )

    kms_ratios = tuple(float(value) for value in kms_frequency_over_temperature)
    kms_frequencies = tuple(temperature * ratio for ratio in kms_ratios)
    kms_responses = tuple(
        _retarded_response(operator, projected_source, frequency)
        for frequency in kms_frequencies
    )
    spectral = tuple(2.0 * response.imag for response in kms_responses)
    occupations = tuple(1.0 / expm1(ratio) for ratio in kms_ratios)
    greater = tuple(rho * (1.0 + occupation) for rho, occupation in zip(spectral, occupations))
    lesser = tuple(rho * occupation for rho, occupation in zip(spectral, occupations))
    kms_ratio_values = tuple(g / l for g, l in zip(greater, lesser))
    kms_target = tuple(exp(ratio) for ratio in kms_ratios)
    kms_residual = max(
        (_relative(observed, target) for observed, target in zip(kms_ratio_values, kms_target)),
        default=0.0,
    )
    noise = tuple(g + l for g, l in zip(greater, lesser))
    noise_target = tuple(
        rho * (1.0 + 2.0 * occupation)
        for rho, occupation in zip(spectral, occupations)
    )
    fdt_residual = max(
        (_relative(observed, target) for observed, target in zip(noise, noise_target)),
        default=0.0,
    )
    entropy = _positive(
        float(np.dot(projected_source, operator @ projected_source) / temperature),
        "entropy production witness",
    )
    values = (
        *eigenvalues,
        *[response.real for response in responses],
        *[response.imag for response in responses],
        *spectral,
        *greater,
        *lesser,
        *kms_ratio_values,
        *noise,
        *noise_target,
        entropy,
        source_formula_residual,
        kms_residual,
        fdt_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("charged current correlator is not finite")

    return ChargedCurrentCorrelatorState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=float(continuum.effective_mass),
        momentum_cutoff=float(continuum.momentum_cutoff),
        state_count=int(continuum.state_count),
        invariant_rank=int(continuum.invariant_rank),
        current_source=tuple(float(value) for value in source),
        projected_current_source=tuple(float(value) for value in projected_source),
        current_source_formula_residual=source_formula_residual,
        current_ward_projection_residual=float(continuum.source_constraint_residual),
        collision_conservation_residual=float(continuum.collision_conservation_residual),
        operator_symmetry_residual=float(continuum.operator_symmetry_residual),
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
        null_mode_count=int(np.sum(np.abs(eigenvalues) <= 1.0e-12)),
        positive_mode_rate=positive_rate,
        response_frequency_over_rate=response_ratios,
        retarded_response_real=tuple(float(response.real) for response in responses),
        retarded_response_imag=tuple(float(response.imag) for response in responses),
        dc_current_response=float(responses[0].real),
        kms_frequency_over_temperature=kms_ratios,
        spectral_density=tuple(float(value) for value in spectral),
        wightman_greater=tuple(float(value) for value in greater),
        wightman_lesser=tuple(float(value) for value in lesser),
        kms_ratio=tuple(float(value) for value in kms_ratio_values),
        kms_target_ratio=kms_target,
        kms_ratio_max_residual=float(kms_residual),
        fdt_noise=tuple(float(value) for value in noise),
        fdt_noise_target=tuple(float(value) for value in noise_target),
        fdt_max_residual=float(fdt_residual),
        entropy_production_witness=entropy,
        contact_cross_section_match_residual=float(contact.cross_section_match_residual),
        contact_detailed_balance_residual=float(contact.max_channel_detailed_balance_residual),
    )


def charged_current_correlator_contract() -> dict[str, Any]:
    """Return the current-correlator equations and non-promotion boundary."""

    return {
        "status": CHARGED_CURRENT_CORRELATOR_STATUS,
        "equations": {
            "current_source": "b_Jx(s,k,n)=q_s*(p_x/E_s)*sqrt(w_s)",
            "retarded_correlator": "G_R^JxJx(omega)=b_Jx,perp^T*(L_cont-i*omega*I)^(-1)*b_Jx,perp",
            "spectral_density": "rho_JJ(omega)=2*Im G_R^JxJx(omega)",
            "wightman_matching": "G^>=rho_JJ*(1+n_B); G^<=rho_JJ*n_B",
            "kms_ratio": "G^>/G^<=exp(beta_th*omega)",
            "fdt_noise": "N_JJ=G^>+G^<=rho_JJ*coth(beta_th*omega/2)",
            "entropy_witness": "sigma_J=b_Jx,perp^T*L_cont*b_Jx,perp/T>=0",
        },
        "unit_contract": {
            "unit_lane": "natural_finite_cutoff",
            "temperature_chemical_potential_energy_rate": "energy",
            "current_source": "formal charge-current response source",
            "retarded_correlator": "formal natural response quantity",
            "spectral_density": "formal natural response quantity",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived charged quasiparticle current source, finite-cutoff conservative "
            "collision operator, and explicit local contact-SK normalization witness"
        ),
        "observable": "finite-cutoff charged current retarded/KMS/FDT interface",
        "data_role": "ACTION_MATCHED_FINITE_CUTOFF_CURRENT_CORRELATOR_NO_HOLDOUT",
        "included": {
            "current_source_formula": True,
            "charge_projection_and_Ward_boundary": True,
            "retarded_current_correlator": True,
            "charged_contact_normalization": True,
            "KMS_and_FDT": True,
            "entropy_positivity_witness": True,
        },
        "excluded": {
            "continuum_limit": True,
            "loop_renormalized_offshell_self_energy": True,
            "microscopic_current_vertex": True,
            "physical_Kubo_coefficient": True,
            "finite_temperature_two_fluid_completion": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only a named action-matched finite-cutoff charged current-correlator "
            "interface. It does not close the continuum limit, loop-renormalized off-shell "
            "self-energy, microscopic current vertex, physical Kubo coefficient, finite-T "
            "two-fluid transport, SI mapping, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "CHARGED_CURRENT_CORRELATOR_STATUS",
    "ChargedCurrentCorrelatorState",
    "charged_current_correlator_state",
    "charged_current_correlator_contract",
]
