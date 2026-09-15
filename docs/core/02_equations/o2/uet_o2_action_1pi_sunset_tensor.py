"""Action-derived O(2) two-loop 1PI sunset tensor interface.

This module derives the species contraction and local counterterm basis of the
two-loop sunset topology from the declared O(2) quartic action.  It then
matches the invariant subtraction variables used by the zero-eta spectral
interface.  The loop integral itself, its physical regulator, and a unique
microscopic renormalization scheme remain explicit open boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np

from docs.core.uet_o2_action_sunset_1pi_spectral import (
    action_matrix_element_squared,
)


ACTION_1PI_SUNSET_TENSOR_STATUS = (
    "PASS_ACTION_DERIVED_O2_1PI_SUNSET_TENSOR_INTERFACE_LANE"
)
SUNSET_SYMMETRY_FACTOR = 1.0 / 6.0
SUNSET_TENSOR_CONVERGENCE_THRESHOLD = 1.0e-12
O2_SPECIES_COUNT = 2


@dataclass(frozen=True)
class ActionOnePISunsetTensorState:
    """Species and renormalization-contract quantities for the sunset graph."""

    species_count: int
    external_species: int
    quartic_coupling: float
    vertex_tensor_norm: float
    vertex_contraction_matrix: tuple[tuple[float, ...], ...]
    vertex_contraction_diagonal: float
    vertex_contraction_off_diagonal_maximum: float
    sunset_symmetry_factor: float
    sunset_tensor_prefactor: float
    expected_sunset_tensor_prefactor: float
    tensor_contraction_residual: float
    reference_invariant_s: float
    probe_invariants_s: tuple[float, ...]
    invariant_subtraction_conditions: tuple[str, ...]
    two_point_counterterm_basis: tuple[str, ...]
    action_subdivergence_counterterm_basis: tuple[str, ...]
    action_scattering_matrix_element_squared: float
    sunset_to_scattering_prefactor_ratio: float
    action_scattering_comparison_available: bool
    action_vertex_tensor_completed: bool = True
    one_pi_sunset_tensor_completed: bool = True
    local_counterterm_basis_completed: bool = True
    invariant_subtraction_interface_matched: bool = True
    full_1pi_retarded_self_energy_completed: bool = False
    loop_integral_evaluated: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_O2_1PI_SUNSET_TENSOR_INTERFACE_NO_HOLDOUT"
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


def _species_count(value: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < 1:
        raise ValueError("species_count must be a positive integer")
    return int(value)


def _ordered_positive(values: tuple[float, ...], name: str) -> tuple[float, ...]:
    if not values:
        raise ValueError(f"{name} must not be empty")
    result = tuple(_positive(value, f"{name} value") for value in values)
    if tuple(sorted(result)) != result:
        raise ValueError(f"{name} must be sorted")
    return result


def _delta(first: int, second: int) -> float:
    return 1.0 if first == second else 0.0


def action_vertex_tensor(
    quartic: float,
    *,
    species_count: int = O2_SPECIES_COUNT,
) -> np.ndarray:
    """Return ``V_abcd`` for ``W_int=lambda*(chi^2)^2/4``."""

    quartic = _positive(quartic, "quartic")
    species_count = _species_count(species_count)
    tensor = np.zeros(
        (species_count, species_count, species_count, species_count),
        dtype=float,
    )
    for a in range(species_count):
        for b in range(species_count):
            for c in range(species_count):
                for d in range(species_count):
                    tensor[a, b, c, d] = 2.0 * quartic * (
                        _delta(a, b) * _delta(c, d)
                        + _delta(a, c) * _delta(b, d)
                        + _delta(a, d) * _delta(b, c)
                    )
    return tensor


def sunset_vertex_contraction(
    quartic: float,
    *,
    species_count: int = O2_SPECIES_COUNT,
) -> np.ndarray:
    """Contract the three internal lines of the two sunset vertices."""

    vertex = action_vertex_tensor(quartic, species_count=species_count)
    return np.einsum("aijk,bijk->ab", vertex, vertex)


def expected_sunset_tensor_prefactor(
    quartic: float,
    *,
    species_count: int = O2_SPECIES_COUNT,
) -> float:
    """Return the diagonal coefficient after the sunset symmetry factor."""

    quartic = _positive(quartic, "quartic")
    species_count = _species_count(species_count)
    return 2.0 * (species_count + 2.0) * quartic * quartic


def action_1pi_sunset_tensor_state(
    quartic: float,
    *,
    species_count: int = O2_SPECIES_COUNT,
    external_species: int = 0,
    reference_invariant_s: float = 0.5,
    probe_invariants_s: tuple[float, ...] = (0.36, 0.64, 0.81, 1.21),
) -> ActionOnePISunsetTensorState:
    """Build the action-derived tensor and declared subtraction interface."""

    quartic = _positive(quartic, "quartic")
    species_count = _species_count(species_count)
    if external_species not in range(species_count):
        raise ValueError("external_species is outside species_count")
    reference_invariant_s = _positive(
        reference_invariant_s, "reference_invariant_s"
    )
    probe_invariants_s = _ordered_positive(probe_invariants_s, "probe_invariants_s")
    if reference_invariant_s in probe_invariants_s:
        raise ValueError("reference_invariant_s must be separate from probes")

    vertex = action_vertex_tensor(quartic, species_count=species_count)
    contraction = sunset_vertex_contraction(
        quartic,
        species_count=species_count,
    )
    expected = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    normalized = SUNSET_SYMMETRY_FACTOR * contraction
    target = expected * np.eye(species_count)
    residual = float(
        np.linalg.norm(normalized - target) / max(np.linalg.norm(target), 1.0e-300)
    )
    diagonal = float(normalized[external_species, external_species])
    off_diagonal = float(
        max(
            abs(normalized[row, column])
            for row in range(species_count)
            for column in range(species_count)
            if row != column
        )
        if species_count > 1
        else 0.0
    )
    action_scattering = 0.0
    comparison_available = species_count == O2_SPECIES_COUNT
    if comparison_available:
        action_scattering = action_matrix_element_squared(
            quartic,
            external_species,
        )
    ratio = (
        diagonal / action_scattering
        if comparison_available and action_scattering > 0.0
        else 0.0
    )
    values = (
        quartic,
        float(np.linalg.norm(vertex)),
        diagonal,
        off_diagonal,
        expected,
        residual,
        reference_invariant_s,
        *probe_invariants_s,
        action_scattering,
        ratio,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("action 1PI sunset tensor state is not finite")
    return ActionOnePISunsetTensorState(
        species_count=species_count,
        external_species=external_species,
        quartic_coupling=quartic,
        vertex_tensor_norm=float(np.linalg.norm(vertex)),
        vertex_contraction_matrix=tuple(
            tuple(float(value) for value in row) for row in contraction
        ),
        vertex_contraction_diagonal=float(contraction[external_species, external_species]),
        vertex_contraction_off_diagonal_maximum=float(
            max(
                abs(contraction[row, column])
                for row in range(species_count)
                for column in range(species_count)
                if row != column
            )
            if species_count > 1
            else 0.0
        ),
        sunset_symmetry_factor=SUNSET_SYMMETRY_FACTOR,
        sunset_tensor_prefactor=diagonal,
        expected_sunset_tensor_prefactor=expected,
        tensor_contraction_residual=residual,
        reference_invariant_s=reference_invariant_s,
        probe_invariants_s=probe_invariants_s,
        invariant_subtraction_conditions=(
            "Sigma_R,ab(s_*)=0",
            "dSigma_R,ab/ds|s_* = 0",
        ),
        two_point_counterterm_basis=("delta_m2", "delta_Z"),
        action_subdivergence_counterterm_basis=(
            "delta_m2",
            "delta_Z",
            "delta_lambda",
        ),
        action_scattering_matrix_element_squared=float(action_scattering),
        sunset_to_scattering_prefactor_ratio=float(ratio),
        action_scattering_comparison_available=comparison_available,
    )


def action_1pi_sunset_tensor_contract() -> dict[str, Any]:
    """Return equations, units, and the deliberately narrow claim boundary."""

    return {
        "status": ACTION_1PI_SUNSET_TENSOR_STATUS,
        "equations": {
            "interaction_potential": "W_int=lambda*(chi_a chi_a)^2/4",
            "action_four_point_vertex": (
                "V_abcd=2*lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)"
            ),
            "sunset_vertex_contraction": (
                "S_ab=sum_{i,j,k} V_aijk*V_bijk=12*(N+2)*lambda^2*delta_ab"
            ),
            "sunset_1pi_prefactor": (
                "Sigma_sunset,ab^(2)(p)=S_ab/6*I_3(p)="
                "2*(N+2)*lambda^2*delta_ab*I_3(p)"
            ),
            "sunset_loop_integral": (
                "I_3(p)=integral d^4k/(2*pi)^4 d^4q/(2*pi)^4 "
                "D(k)D(q)D(p-k-q)"
            ),
            "invariant_subtraction": (
                "Sigma_R,ab(s)=Sigma_ab(s)-Sigma_ab(s_*)-"
                "(s-s_*)*dSigma_ab/ds|s_*"
            ),
            "rest_energy_match": "p=(omega,0), s=p^2=omega^2",
            "counterterm_basis": (
                "two-point sunset: delta_m2 and delta_Z; "
                "full action subdivergence also requires delta_lambda"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural 3+1",
            "temperature_mass_momentum_frequency": "energy",
            "invariant_s": "energy squared",
            "quartic_coupling": "dimensionless",
            "vertex_tensor": "dimensionless",
            "sunset_loop_integral_I3": "energy squared",
            "self_energy_and_delta_m2": "energy squared",
            "delta_Z_and_delta_lambda": "dimensionless",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived O(N) species contraction, explicit sunset symmetry factor, "
            "local counterterm power-counting interface, and invariant subtraction match"
        ),
        "observable": (
            "vertex contraction matrix, diagonal 1PI sunset prefactor, species symmetry, "
            "counterterm basis, and rest-energy subtraction-variable match"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_1PI_TENSOR_INTERFACE_NO_HOLDOUT",
        "included": {
            "action_vertex_tensor": True,
            "sunset_internal_species_contraction": True,
            "sunset_symmetry_factor": True,
            "two_point_counterterm_basis": True,
            "invariant_subtraction_variable_match": True,
        },
        "excluded": {
            "full_off_shell_loop_integral": True,
            "physical_retarded_1PI_self_energy": True,
            "unique_physical_renormalization": True,
            "microscopic_SK_KMS_match": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current": True,
            "heat_flux_dissipative_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the action-derived O(2) sunset 1PI tensor and local "
            "counterterm interface. It does not evaluate the full off-shell loop, "
            "select a unique physical renormalization, match microscopic SK/KMS, "
            "emit transport or entropy production, map Phi to SI, calibrate alpha_Phi_K, "
            "validate TTG, or close Full Topic 13."
        ),
    }


__all__ = [
    "ACTION_1PI_SUNSET_TENSOR_STATUS",
    "ActionOnePISunsetTensorState",
    "SUNSET_SYMMETRY_FACTOR",
    "action_1pi_sunset_tensor_contract",
    "action_1pi_sunset_tensor_state",
    "action_vertex_tensor",
    "expected_sunset_tensor_prefactor",
    "sunset_vertex_contraction",
]
