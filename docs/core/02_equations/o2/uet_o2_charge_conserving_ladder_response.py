"""Conserving two-channel retarded response lane for Topic 13.

This module adds a bounded response construction on top of the corrected
quantum collision width.  The collision operator has an explicit conserved
zero mode and one dissipative relative mode.  Its matrix inverse is a small
ladder-like resummation, not a microscopic Bethe-Salpeter or SK/KMS match.
The lane remains in natural units and does not emit a physical Kubo
coefficient, an SI observable, or an ``alpha_Phi_K`` calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

import numpy as np

from docs.core.uet_o2_kinetic_collision_kubo import kinetic_collision_state
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


CHARGE_CONSERVING_LADDER_RESPONSE_STATUS = (
    "PASS_ACTION_DERIVED_CONSERVING_LADDER_RESPONSE_LANE"
)


@dataclass(frozen=True)
class ChargeConservingLadderResponseState:
    """Finite-dimensional conserving response quantities."""

    temperature: float
    chemical_potential: float
    space_response: float
    conserved_vector: tuple[float, float]
    charge_vector: tuple[float, float]
    projector: tuple[tuple[float, float], tuple[float, float]]
    collision_operator: tuple[tuple[float, float], tuple[float, float]]
    collision_operator_eigenvalues: tuple[float, float]
    relative_collision_rate: float
    drude_weight_by_species: tuple[float, float]
    quantum_collision_width_by_species: tuple[float, float]
    source_vector: tuple[float, float]
    projected_source_vector: tuple[float, float]
    source_norm_squared: float
    conservation_residual: float
    symmetry_residual: float
    positive_semidefinite_min_eigenvalue: float
    frequency_over_gamma: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    dc_response: float
    dc_closed_form: float
    quadrature_order: int
    angular_order: int
    final_state_bose_enhancement_included: bool = True
    ladder_vertex_resummation_included: bool = True
    physical_kubo_coefficient_emitted: bool = False
    data_role: str = (
        "ACTION_DERIVED_CONSERVING_LADDER_RESPONSE_LANE_NOT_PHYSICAL_KUBO"
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


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, float], tuple[float, float]]:
    return tuple(tuple(float(value) for value in row) for row in matrix)  # type: ignore[return-value]


def _response(
    collision_operator: np.ndarray,
    source: np.ndarray,
    omega: float,
    relative_collision_rate: float,
) -> complex:
    """Evaluate b^T (L - i omega I)^-1 b on the relative subspace."""

    source_norm_squared = float(np.dot(source, source))
    if omega == 0.0:
        return complex(source_norm_squared / relative_collision_rate, 0.0)
    identity = np.eye(2, dtype=float)
    solved = np.linalg.solve(collision_operator - 1j * omega * identity, source)
    return complex(np.dot(source, solved))


def charge_conserving_ladder_response_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 64,
    angular_order: int = 48,
    cutoff_factor: float = 24.0,
    frequency_over_gamma: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    include_final_state_bose_enhancement: bool = True,
) -> ChargeConservingLadderResponseState:
    """Build the declared two-channel conserving retarded response lane."""

    if not include_final_state_bose_enhancement:
        raise ValueError("this lane requires the corrected quantum collision width")
    if not frequency_over_gamma:
        raise ValueError("frequency_over_gamma must not be empty")
    ratios = tuple(_finite(value, "frequency_over_gamma") for value in frequency_over_gamma)
    if any(value < 0.0 for value in ratios):
        raise ValueError("frequency_over_gamma must be non-negative")
    if tuple(sorted(ratios)) != ratios:
        raise ValueError("frequency_over_gamma must be sorted")
    if ratios[0] != 0.0:
        raise ValueError("frequency_over_gamma must include zero frequency first")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    quantum_state = kinetic_collision_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        angular_order=angular_order,
        cutoff_factor=cutoff_factor,
        include_final_state_bose_enhancement=True,
    )
    widths = np.asarray(quantum_state.collision_width_by_species, dtype=float)
    drude = np.asarray(quantum_state.drude_weight_by_species, dtype=float)
    if not np.all(np.isfinite(widths)) or not np.all(widths > 0.0):
        raise FloatingPointError("quantum collision widths must be finite and positive")
    if not np.all(np.isfinite(drude)) or not np.all(drude > 0.0):
        raise FloatingPointError("drude weights must be finite and positive")

    # The sum mode is conserved; the difference mode is the only dissipative
    # mode in this deliberately bounded two-channel construction.
    conserved = np.asarray((1.0, 1.0), dtype=float)
    charge = np.asarray((-1.0, 1.0), dtype=float)
    projector = np.eye(2, dtype=float) - np.outer(conserved, conserved) / np.dot(
        conserved, conserved
    )
    relative_rate = _positive(float(np.mean(widths)), "relative collision rate")
    collision_operator = relative_rate * projector
    source = charge * np.sqrt(drude)
    projected_source = projector @ source
    source_norm_squared = _positive(float(np.dot(projected_source, projected_source)), "source norm")
    frequencies = tuple(relative_rate * ratio for ratio in ratios)
    responses = tuple(
        _response(collision_operator, projected_source, omega, relative_rate)
        for omega in frequencies
    )
    eigenvalues = tuple(float(value) for value in np.linalg.eigvalsh(collision_operator))
    conservation_residual = float(np.linalg.norm(collision_operator @ conserved))
    symmetry_residual = float(np.linalg.norm(collision_operator - collision_operator.T))
    minimum_eigenvalue = float(min(eigenvalues))
    dc_closed_form = source_norm_squared / relative_rate
    if not all(isfinite(value.real) and isfinite(value.imag) for value in responses):
        raise FloatingPointError("retarded response is not finite")

    return ChargeConservingLadderResponseState(
        temperature=float(quantum_state.temperature),
        chemical_potential=float(quantum_state.chemical_potential),
        space_response=float(quantum_state.space_response),
        conserved_vector=tuple(float(value) for value in conserved),
        charge_vector=tuple(float(value) for value in charge),
        projector=_matrix_tuple(projector),
        collision_operator=_matrix_tuple(collision_operator),
        collision_operator_eigenvalues=eigenvalues,
        relative_collision_rate=relative_rate,
        drude_weight_by_species=tuple(float(value) for value in drude),
        quantum_collision_width_by_species=tuple(float(value) for value in widths),
        source_vector=tuple(float(value) for value in source),
        projected_source_vector=tuple(float(value) for value in projected_source),
        source_norm_squared=source_norm_squared,
        conservation_residual=conservation_residual,
        symmetry_residual=symmetry_residual,
        positive_semidefinite_min_eigenvalue=minimum_eigenvalue,
        frequency_over_gamma=ratios,
        retarded_response_real=tuple(float(value.real) for value in responses),
        retarded_response_imag=tuple(float(value.imag) for value in responses),
        dc_response=float(responses[0].real),
        dc_closed_form=float(dc_closed_form),
        quadrature_order=int(quantum_state.quadrature_order),
        angular_order=int(quantum_state.angular_order),
    )


def charge_conserving_ladder_response_contract() -> dict[str, object]:
    """Return the lane equations, units, and claim boundary."""

    return {
        "status": CHARGE_CONSERVING_LADDER_RESPONSE_STATUS,
        "equations": {
            "conserved_projector": "P_perp=I-n*n^T/(n^T*n), n=(1,1)",
            "relative_collision_rate": "Gamma_rel=(Gamma_+ + Gamma_-)/2",
            "collision_operator": "L=Gamma_rel*P_perp, L*n=0, L>=0",
            "projected_source": "b_perp=P_perp*q*sqrt(D), q=(-1,+1)",
            "retarded_response": "K_R(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp",
            "dc_response": "K_R(0)=b_perp^T*b_perp/Gamma_rel",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_rate": "energy",
            "omega": "energy/inverse time",
            "response": "formal finite-dimensional response quantity",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived quantum collision width plus explicit conserving "
            "two-channel matrix-resolvent ladder comparator"
        ),
        "observable": "retarded relative-channel response in the declared normal O(2) lane",
        "data_role": "ACTION_DERIVED_CONSERVING_LADDER_RESPONSE_LANE_NOT_PHYSICAL_KUBO",
        "included": {
            "quantum_final_state_bose_enhancement": True,
            "conserved_zero_mode": True,
            "positive_dissipative_relative_mode": True,
            "finite_frequency_retarded_response": True,
            "deterministic_quadrature_refinement": True,
        },
        "excluded": {
            "microscopic_bethe_salpeter_ladder": True,
            "condensed_scattering": True,
            "microscopic_SK_KMS_match": True,
            "physical_Kubo_coefficient": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only a named action-derived conserving two-channel "
            "response lane. It does not close microscopic ladder vertices, "
            "SK/KMS matching, physical transport, SI calibration, alpha_Phi_K, "
            "TTG prediction, or Full Topic 13."
        ),
    }


__all__ = [
    "CHARGE_CONSERVING_LADDER_RESPONSE_STATUS",
    "ChargeConservingLadderResponseState",
    "charge_conserving_ladder_response_state",
    "charge_conserving_ladder_response_contract",
]
