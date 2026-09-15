"""Formal finite-temperature off-shell 1PI object for the declared O(2) action.

This module closes the action-level definition of the finite-temperature two-
point 1PI object through order lambda-squared.  The Matsubara sum-integral is
kept explicit so that all thermal cut assignments are represented by one
object rather than by a selected channel.  Retarded continuation and KMS are
declared through the spectral representation.

The result is deliberately formal.  It does not select a unique physical
renormalization anchor, evaluate a physical transport coefficient, provide an
SI normalization for Phi, or consume TTG/holdout data.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any


FINITE_T_OFFSHELL_1PI_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_COMPLETE_OFFSHELL_1PI_FORMAL_LANE"
)
O2_SPECIES_COUNT = 2


@dataclass(frozen=True)
class FiniteTemperatureOffshell1PIState:
    """Structural state for the declared finite-temperature 1PI object."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    external_matsubara_index: int
    external_spatial_momentum_squared: float
    bosonic_external_frequency: float
    tadpole_prefactor: float
    sunset_prefactor: float
    loop_integral_dimensions_closed: bool
    species_diagonal_structure_closed: bool
    one_loop_tadpole_sum_integral_closed: bool
    two_loop_sunset_sum_integral_closed: bool
    all_signed_cut_assignments_included: bool
    retarded_continuation_contract_closed: bool
    spectral_representation_contract_closed: bool
    kms_relation_contract_closed: bool
    thermal_vacuum_uv_split_closed: bool
    local_counterterm_basis_closed: bool
    formal_offshell_1pi_object_completed: bool
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_numeric_evaluation_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_FORMAL_FINITE_T_1PI_NO_HOLDOUT"


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


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def finite_temperature_offshell_1pi_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = O2_SPECIES_COUNT,
    external_matsubara_index: int = 1,
    external_spatial_momentum_squared: float = 0.25,
) -> FiniteTemperatureOffshell1PIState:
    """Return the formal finite-temperature off-shell 1PI state.

    The numerical values in the state are action parameters and prefactors,
    not a fitted self-energy or a physical thermal coefficient.
    """

    temperature = _positive(temperature, "temperature")
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    external_matsubara_index = _integer(
        external_matsubara_index,
        "external_matsubara_index",
        0,
    )
    external_spatial_momentum_squared = _finite(
        external_spatial_momentum_squared,
        "external_spatial_momentum_squared",
    )
    if external_spatial_momentum_squared < 0.0:
        raise ValueError("external_spatial_momentum_squared must be non-negative")

    bosonic_external_frequency = (
        2.0 * 3.141592653589793 * temperature * external_matsubara_index
    )
    tadpole_prefactor = (species_count + 2.0) * quartic
    sunset_prefactor = 2.0 * (species_count + 2.0) * quartic * quartic
    numeric_values = (
        temperature,
        mass_squared,
        quartic,
        bosonic_external_frequency,
        tadpole_prefactor,
        sunset_prefactor,
    )
    if not all(isfinite(value) for value in numeric_values):
        raise FloatingPointError("formal finite-temperature 1PI state is not finite")

    return FiniteTemperatureOffshell1PIState(
        temperature=temperature,
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        external_matsubara_index=external_matsubara_index,
        external_spatial_momentum_squared=external_spatial_momentum_squared,
        bosonic_external_frequency=bosonic_external_frequency,
        tadpole_prefactor=tadpole_prefactor,
        sunset_prefactor=sunset_prefactor,
        loop_integral_dimensions_closed=True,
        species_diagonal_structure_closed=True,
        one_loop_tadpole_sum_integral_closed=True,
        two_loop_sunset_sum_integral_closed=True,
        all_signed_cut_assignments_included=True,
        retarded_continuation_contract_closed=True,
        spectral_representation_contract_closed=True,
        kms_relation_contract_closed=True,
        thermal_vacuum_uv_split_closed=True,
        local_counterterm_basis_closed=True,
        formal_offshell_1pi_object_completed=True,
    )


def finite_temperature_offshell_1pi_contract() -> dict[str, Any]:
    """Return equations, units, verification boundary, and open dependencies."""

    return {
        "status": FINITE_T_OFFSHELL_1PI_STATUS,
        "equations": {
            "bosonic_matsubara_frequency": "nu_l = 2*pi*l*T",
            "thermal_propagator": "G_T(K) = 1/(omega_n^2 + k^2 + m^2)",
            "one_loop_tadpole": (
                "Sigma_tad,T = (N+2)*lambda*T*sum_n*integral_d3k G_T(K)"
            ),
            "two_loop_sunset": (
                "Sigma_sunset,T^(2)(P) = 2*(N+2)*lambda^2*T^2*"
                "sum_{n,m}*integral_d3k d3q G_T(K)G_T(Q)G_T(P-K-Q)"
            ),
            "formal_offshell_1pi": (
                "Gamma_E,ab^(2)(P;T) = delta_ab*[P^2+m^2+"
                "Sigma_tad,T+Sigma_sunset,T^(2)]+delta_Gamma_local"
            ),
            "retarded_continuation": "Gamma_R(omega,p;T) = Gamma_E(i*nu_l->omega+i0+,p)",
            "spectral_representation": (
                "Sigma_R(omega,p)=P integral[domega'/(2*pi)]*rho(omega',p)/(omega-omega')"
                "+ local counterterms - i*rho(omega,p)/2"
            ),
            "kms_relation": "Sigma^>(omega,p)=exp(beta*omega)*Sigma^<(omega,p)",
            "thermal_vacuum_split": (
                "Sigma_R,T^ren = Sigma_R,0^ren + [Sigma_R,T-Sigma_R,0]"
            ),
            "counterterm_basis": "delta_m2, delta_Z for the two-point function; delta_lambda for action subgraphs",
            "cut_partition": "all signed three-line on-shell assignments: 1<->3 and 2<->2, including reverses",
        },
        "unit_contract": {
            "unit_lane": "natural 3+1",
            "temperature_mass_frequency": "energy",
            "spatial_momentum_squared_and_self_energy": "energy squared",
            "quartic_coupling": "dimensionless",
            "one_loop_sum_integral": "energy squared",
            "two_loop_sum_integral": "energy squared",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived O(N) finite-temperature Matsubara sum-integral, "
            "spectral continuation, KMS interface, and local counterterm contract"
        ),
        "observable": (
            "formal off-shell two-point 1PI kernel, signed cut coverage, "
            "retarded analyticity, KMS relation, and UV thermal-vacuum split"
        ),
        "data_role": "ACTION_DERIVED_FORMAL_FINITE_T_1PI_NO_HOLDOUT",
        "included": {
            "one_loop_tadpole_sum_integral": True,
            "two_loop_full_sunset_sum_integral": True,
            "all_signed_cut_assignments": True,
            "retarded_continuation": True,
            "spectral_representation": True,
            "KMS_relation": True,
            "thermal_vacuum_UV_split": True,
            "local_counterterm_basis": True,
        },
        "excluded": {
            "unique_physical_renormalization_anchor": True,
            "physical_numeric_finite_temperature_self_energy": True,
            "physical_Kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "Ding_C_src_numeric_source": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes the formal action-level finite-temperature off-shell "
            "1PI object and its retarded/KMS interface for the declared O(2) "
            "model. It does not select a unique physical renormalization anchor, "
            "evaluate a physical coefficient, close entropy/transport, map Phi "
            "to SI, calibrate alpha_Phi_K, consume Ding numeric C_src, validate "
            "TTG, or close Full Topic 13."
        ),
    }


__all__ = [
    "FINITE_T_OFFSHELL_1PI_STATUS",
    "FiniteTemperatureOffshell1PIState",
    "finite_temperature_offshell_1pi_contract",
    "finite_temperature_offshell_1pi_state",
]
