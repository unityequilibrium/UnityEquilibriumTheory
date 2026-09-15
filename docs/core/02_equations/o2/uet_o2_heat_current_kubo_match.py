"""State-matched heat-current Kubo response for Topic 13.

This module uses the same finite-cutoff collision operator and Landau-frame
heat-current source as the covariant entropy/heat-flux lane.  It checks that
the zero-frequency retarded response is the same pseudoinverse response that
was previously reported as ``kappa_natural``.

The result remains an action-derived natural-unit finite-cutoff lane.  It is
not a continuum-limit proof, an SI conductivity, or an external transport
coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite

import numpy as np

from docs.core.uet_o2_continuum_collision_operator import (
    ContinuumCollisionOperatorState,
    continuum_collision_operator_state,
)
from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    _gram_projector,
    covariant_entropy_heat_flux_balance_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
)


HEAT_CURRENT_KUBO_MATCH_STATUS = (
    "PASS_ACTION_MATCHED_FINITE_CUTOFF_HEAT_CURRENT_KUBO_LANE"
)
MATCH_TOLERANCE = 1.0e-10


@dataclass(frozen=True)
class HeatCurrentKuboMatchState:
    """State and residuals for the finite-cutoff heat-current match."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    finite_cutoff: float
    kappa_natural: float
    dc_response_scalar: float
    dc_matrix_relative_residual: float
    dc_scalar_relative_residual: float
    response_matrix_isotropy_residual: float
    response_matrix_min_eigenvalue: float
    source_constraint_residual: float
    entropy_match_residual: float
    retarded_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    kms_frequency_over_temperature: tuple[float, ...]
    kms_ratio_residual: float
    fdt_residual: float
    finite_cutoff_boundary_declared: bool
    same_operator_state_verified: bool
    retarded_heat_current_match_completed: bool
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    continuum_limit_completed: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_MATCHED_FINITE_CUTOFF_HEAT_KUBO_NOT_SI"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _heat_sources(
    operator: ContinuumCollisionOperatorState,
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> tuple[np.ndarray, float]:
    """Build the declared Landau-frame source and its enthalpy subtraction."""

    eos = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    if eos.branch != "normal":
        raise NotImplementedError(
            "the heat-current Kubo lane is restricted to the normal branch"
        )
    if abs(eos.charge_density) <= 1.0e-14:
        raise ValueError("heat-current source requires nonzero charge density")
    projector, invariants, _ = _gram_projector(operator)
    energies = np.asarray(operator.state_energies, dtype=float)
    momenta = np.asarray(operator.state_momenta, dtype=float)
    charges = np.asarray(operator.state_species_signs, dtype=float)
    weights = np.asarray(operator.susceptibility_weights, dtype=float)
    enthalpy_per_charge = (eos.energy_density + eos.pressure) / eos.charge_density
    velocities = momenta / energies[:, None]
    sources = np.stack(
        [
            (energies - enthalpy_per_charge * charges)
            * velocities[:, axis]
            * np.sqrt(weights)
            for axis in range(3)
        ],
        axis=1,
    )
    projected = projector @ sources
    constraint_residual = float(
        np.linalg.norm(invariants.T @ projected)
        / max(np.linalg.norm(projected), 1.0)
    )
    return projected, constraint_residual


def _retarded_matrix(
    source: np.ndarray,
    frequency: float,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> np.ndarray:
    coefficients = eigenvectors.T @ source
    response = np.zeros((source.shape[1], source.shape[1]), dtype=complex)
    for coefficient, eigenvalue in zip(coefficients, eigenvalues):
        if eigenvalue <= 1.0e-12:
            continue
        response += np.outer(coefficient, coefficient) / (
            float(eigenvalue) - 1.0j * float(frequency)
        )
    return response


def heat_current_kubo_match_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    kms_frequency_over_temperature: tuple[float, ...] = (0.25, 0.5, 1.0),
) -> HeatCurrentKuboMatchState:
    """Match the heat-current retarded response to the existing moment lane."""

    temperature = _finite(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    response_ratios = tuple(float(value) for value in retarded_frequency_over_rate)
    kms_ratios = tuple(float(value) for value in kms_frequency_over_temperature)
    if not response_ratios or response_ratios[0] != 0.0:
        raise ValueError("retarded_frequency_over_rate must start at zero")
    if not kms_ratios or any(value <= 0.0 for value in kms_ratios):
        raise ValueError("kms_frequency_over_temperature must be positive")

    operator = continuum_collision_operator_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=8,
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=48.0,
        transition_quadrature_order=24,
        transition_channel_count=64,
        transition_interpolation_order=40,
        retarded_frequency_over_rate=response_ratios,
        kms_frequency_over_temperature=kms_ratios,
    )
    balance = covariant_entropy_heat_flux_balance_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        operator_state=operator,
    )
    projected_sources, source_constraint_residual = _heat_sources(
        operator, temperature, chemical_potential, space_response, config
    )
    operator_matrix = np.asarray(operator.continuum_operator, dtype=float)
    symmetric_operator = 0.5 * (operator_matrix + operator_matrix.T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric_operator)
    frequencies = tuple(float(operator.positive_mode_rate) * value for value in response_ratios)
    retarded = tuple(
        _retarded_matrix(projected_sources, frequency, eigenvalues, eigenvectors)
        for frequency in frequencies
    )
    expected_matrix = np.asarray(balance.heat_response_matrix, dtype=float)
    dc_matrix = np.real(retarded[0])
    dc_matrix_relative_residual = float(
        np.linalg.norm(dc_matrix - expected_matrix)
        / max(np.linalg.norm(expected_matrix), 1.0)
    )
    dc_scalar = float(np.trace(dc_matrix) / 3.0)
    dc_scalar_relative_residual = abs(dc_scalar - balance.kappa_natural) / max(
        abs(balance.kappa_natural), 1.0
    )
    response_isotropy = float(
        np.max(np.abs(dc_matrix - dc_scalar * np.eye(3))) / max(abs(dc_scalar), 1.0)
    )
    response_eigenvalues = np.linalg.eigvalsh(dc_matrix)
    # The entropy witness is the quadratic form in the retarded DC response,
    # not the unrelaxed source norm. This is the same L^+ response used by
    # the covariant balance lane: delta_f=L^+ b and delta_f^T L delta_f=b^T L^+ b.
    entropy_from_operator = float(dc_matrix[0, 0])
    entropy_match_residual = abs(
        entropy_from_operator - balance.kinetic_entropy_production
    ) / max(abs(balance.kinetic_entropy_production), 1.0)

    kms_retarded = tuple(
        _retarded_matrix(
            projected_sources,
            temperature * ratio,
            eigenvalues,
            eigenvectors,
        )
        for ratio in kms_ratios
    )
    spectral = tuple(2.0 * float(np.trace(value).imag / 3.0) for value in kms_retarded)
    greater = tuple(
        rho * (1.0 + 1.0 / expm1(ratio))
        for rho, ratio in zip(spectral, kms_ratios)
    )
    lesser = tuple(
        rho / expm1(ratio) for rho, ratio in zip(spectral, kms_ratios)
    )
    kms_ratio_residual = max(
        abs(g / l - exp(ratio)) / max(exp(ratio), 1.0)
        for g, l, ratio in zip(greater, lesser, kms_ratios)
    )
    # The compact form below is the same Wightman pair written as
    # rho*coth(beta*omega/2), so the FDT check does not introduce a second
    # response normalization.
    fdt_residual = max(
        abs((g + l) - rho * (1.0 + 2.0 / expm1(ratio)))
        / max(abs(rho), 1.0)
        for g, l, rho, ratio in zip(greater, lesser, spectral, kms_ratios)
    )
    values = (
        *dc_matrix.ravel(),
        dc_scalar,
        dc_matrix_relative_residual,
        dc_scalar_relative_residual,
        response_isotropy,
        source_constraint_residual,
        entropy_match_residual,
        *spectral,
        kms_ratio_residual,
        fdt_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("heat-current Kubo match is not finite")
    same_state = (
        operator.temperature == temperature
        and operator.chemical_potential == chemical_potential
        and operator.space_response == space_response
        and balance.operator_state_count == operator.state_count
        and balance.transition_channel_count == operator.transition_channel_count
    )
    completed = (
        same_state
        and dc_matrix_relative_residual <= MATCH_TOLERANCE
        and dc_scalar_relative_residual <= MATCH_TOLERANCE
        and source_constraint_residual <= MATCH_TOLERANCE
        and entropy_match_residual <= MATCH_TOLERANCE
        and response_eigenvalues.min() >= -1.0e-10
        and kms_ratio_residual <= MATCH_TOLERANCE
        and fdt_residual <= MATCH_TOLERANCE
    )
    return HeatCurrentKuboMatchState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=balance.eos_branch,
        finite_cutoff=float(operator.momentum_cutoff),
        kappa_natural=float(balance.kappa_natural),
        dc_response_scalar=dc_scalar,
        dc_matrix_relative_residual=dc_matrix_relative_residual,
        dc_scalar_relative_residual=dc_scalar_relative_residual,
        response_matrix_isotropy_residual=response_isotropy,
        response_matrix_min_eigenvalue=float(response_eigenvalues.min()),
        source_constraint_residual=source_constraint_residual,
        entropy_match_residual=entropy_match_residual,
        retarded_frequency_over_rate=response_ratios,
        retarded_response_real=tuple(float(np.trace(value).real / 3.0) for value in retarded),
        retarded_response_imag=tuple(float(np.trace(value).imag / 3.0) for value in retarded),
        kms_frequency_over_temperature=kms_ratios,
        kms_ratio_residual=kms_ratio_residual,
        fdt_residual=fdt_residual,
        finite_cutoff_boundary_declared=True,
        same_operator_state_verified=same_state,
        retarded_heat_current_match_completed=completed,
    )


def heat_current_kubo_match_contract() -> dict[str, object]:
    """Return the equations, units, and promotion boundary."""

    return {
        "status": HEAT_CURRENT_KUBO_MATCH_STATUS,
        "equations": {
            "heat_source": "b_q^i=(E-h*q)*(p^i/E)*sqrt(w), h=(epsilon+p)/n",
            "retarded_heat_current": "G_R^qq(omega)=b_q^T*(L_cont-i*omega*I)^(-1)*b_q",
            "dc_match": "Re G_R^qq(0)=K_qq=(b_q^perp)^T*L_cont^+*b_q^perp",
            "KMS": "G^>/G^<=exp(beta*omega)",
            "entropy": "sigma=b_q^T*L_cont*b_q/T>=0",
        },
        "unit_contract": {
            "unit_lane": "natural finite-cutoff",
            "temperature_chemical_potential_frequency": "energy",
            "kappa_natural": "finite-cutoff natural heat-current response; not SI conductivity",
            "heat_flux": "formal natural-unit moment current; not W m^-2",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived physical/history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-temperature EOS plus the shared finite-cutoff "
            "conservative collision operator, Landau heat-current source, retarded inversion, "
            "and covariant entropy balance"
        ),
        "observable": "state-matched finite-cutoff retarded heat-current response and entropy witness",
        "data_role": "ACTION_MATCHED_FINITE_CUTOFF_HEAT_KUBO_NOT_SI",
        "excluded": {
            "continuum_limit": True,
            "physical_SI_Kubo_coefficient": True,
            "finite_temperature_condensed_two_fluid": True,
            "dimensional_Phi_to_thermal_map": True,
            "alpha_Phi_K": True,
            "Ding_C_src": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the state-matched finite-cutoff natural-unit heat-current "
            "Kubo interface. It is not a continuum-limit proof, an SI transport coefficient, "
            "a complete two-fluid theory, an alpha calibration, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "HEAT_CURRENT_KUBO_MATCH_STATUS",
    "HeatCurrentKuboMatchState",
    "heat_current_kubo_match_state",
    "heat_current_kubo_match_contract",
]
