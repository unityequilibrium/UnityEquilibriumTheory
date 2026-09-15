"""Declare the physical renormalization-condition contract for the O(2) sunset.

The contract separates an on-shell condition from the declared internal
subtraction references.  It verifies the algebraic pole and residue conditions
on a below-threshold formal witness, but it does not claim that an external
mass, residue, or microscopic finite-temperature self-energy has been
supplied.  The physical anchor therefore remains an explicit open input.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any


PHYSICAL_RENORMALIZATION_CONTRACT_STATUS = (
    "PASS_ON_SHELL_PHYSICAL_RENORMALIZATION_CONDITION_CONTRACT_OPEN_EXTERNAL_ANCHOR"
)
ON_SHELL_CONDITION_THRESHOLD = 1.0e-12


@dataclass(frozen=True)
class PhysicalRenormalizationConditionState:
    """Formal below-threshold on-shell condition witness."""

    internal_mass_squared: float
    pole_mass_squared: float
    three_body_threshold_s: float
    self_energy_at_pole: float
    self_energy_derivative_at_pole: float
    mass_counterterm: float
    wavefunction_counterterm: float
    subtracted_self_energy_at_pole: float
    subtracted_self_energy_derivative_at_pole: float
    inverse_propagator_pole_residual: float
    inverse_propagator_residue_residual: float
    below_threshold_domain: bool
    physical_anchor_supplied: bool = False
    physical_renormalization_scheme_match_completed: bool = False
    full_finite_temperature_1pi_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "FORMULA_CONTRACT_INTERNAL_WITNESS_NO_EXTERNAL_ANCHOR"


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


def physical_renormalization_condition_state(
    internal_mass_squared: float,
    pole_mass_squared: float,
    self_energy_at_pole: float,
    self_energy_derivative_at_pole: float,
    *,
    physical_anchor_supplied: bool = False,
) -> PhysicalRenormalizationConditionState:
    """Evaluate the below-threshold pole and unit-residue conditions.

    The formal inverse propagator uses the twice-subtracted self-energy
    ``Sigma_sub(s)=Sigma(s)-Sigma(s*)-(s-s*) Sigma'(s*)``.  The witness is
    deliberately local and action-agnostic: a physical anchor is required to
    identify ``s*`` and the self-energy values in an actual UET match.
    """

    internal_mass_squared = _positive(internal_mass_squared, "internal_mass_squared")
    pole_mass_squared = _positive(pole_mass_squared, "pole_mass_squared")
    self_energy_at_pole = _finite(self_energy_at_pole, "self_energy_at_pole")
    self_energy_derivative_at_pole = _finite(
        self_energy_derivative_at_pole,
        "self_energy_derivative_at_pole",
    )
    threshold = 9.0 * internal_mass_squared
    below_threshold = pole_mass_squared < threshold
    if not below_threshold:
        raise ValueError(
            "the real below-threshold contract requires pole_mass_squared < 9*internal_mass_squared"
        )

    mass_counterterm = self_energy_at_pole
    wavefunction_counterterm = -self_energy_derivative_at_pole
    subtracted_self_energy_at_pole = (
        self_energy_at_pole - mass_counterterm
    )
    subtracted_self_energy_derivative_at_pole = (
        self_energy_derivative_at_pole + wavefunction_counterterm
    )
    inverse_propagator_pole_residual = abs(subtracted_self_energy_at_pole)
    inverse_propagator_residue_residual = abs(
        subtracted_self_energy_derivative_at_pole
    )
    return PhysicalRenormalizationConditionState(
        internal_mass_squared=internal_mass_squared,
        pole_mass_squared=pole_mass_squared,
        three_body_threshold_s=threshold,
        self_energy_at_pole=self_energy_at_pole,
        self_energy_derivative_at_pole=self_energy_derivative_at_pole,
        mass_counterterm=float(mass_counterterm),
        wavefunction_counterterm=float(wavefunction_counterterm),
        subtracted_self_energy_at_pole=float(subtracted_self_energy_at_pole),
        subtracted_self_energy_derivative_at_pole=float(
            subtracted_self_energy_derivative_at_pole
        ),
        inverse_propagator_pole_residual=float(inverse_propagator_pole_residual),
        inverse_propagator_residue_residual=float(
            inverse_propagator_residue_residual
        ),
        below_threshold_domain=below_threshold,
        physical_anchor_supplied=bool(physical_anchor_supplied),
    )


def physical_renormalization_condition_contract() -> dict[str, Any]:
    """Return the equations and acceptance fields for a future physical match."""

    return {
        "status": PHYSICAL_RENORMALIZATION_CONTRACT_STATUS,
        "equations": {
            "inverse_propagator": "Gamma_R^(2)(s)=s-s_* - Sigma_R,sub(s;s_*)",
            "subtracted_self_energy": "Sigma_R,sub(s;s_*)=Sigma_R(s)-Sigma_R(s_*)-(s-s_*) dSigma_R/ds|s_*",
            "pole_condition": "Re Gamma_R^(2)(s_*)=0",
            "residue_condition": "d Re Gamma_R^(2)/ds|s_* = 1",
            "counterterms": "delta_m^2=Re Sigma_R(s_*); delta_Z=-d Re Sigma_R/ds|s_*",
            "real_domain": "0 < s_* < 9 m_internal^2; above-threshold matching requires a complex-pole contract",
        },
        "unit_contract": {
            "internal_mass_squared": "natural energy squared",
            "pole_mass_squared": "physical pole energy squared; external input required",
            "self_energy_at_pole": "natural energy squared",
            "self_energy_derivative_at_pole": "dimensionless",
            "mass_counterterm": "natural energy squared",
            "wavefunction_counterterm": "dimensionless",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "on-shell Taylor-condition contract with an action-derived self-energy interface; "
            "formal witness only until external physical anchor is source-locked"
        ),
        "observable": "pole location and unit-residue inverse-propagator conditions",
        "data_role": "FORMULA_CONTRACT_INTERNAL_WITNESS_NO_EXTERNAL_ANCHOR",
        "required_external_anchor_fields": [
            "source_identity",
            "locator",
            "physical_pole_mass_squared",
            "pole_or_residue_definition",
            "units",
            "uncertainty",
            "state_matching",
            "independence_statement",
            "source_hash",
        ],
        "forbidden_inputs": [
            "TTG target residuals",
            "Xie 2026 numeric holdout",
            "post-inspection parameter tuning",
            "synthetic replacement data",
        ],
        "included": {
            "below_threshold_real_domain": True,
            "pole_condition": True,
            "unit_residue_condition": True,
            "external_anchor_acceptance_schema": True,
        },
        "excluded": {
            "physical_anchor_match": True,
            "complete_finite_temperature_1pi_self_energy": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes the acceptance contract for an on-shell physical renormalization "
            "condition and verifies its below-threshold algebraic witness. It does not claim "
            "that a physical mass/residue or microscopic finite-temperature self-energy has "
            "been supplied, and it does not close Topic 13."
        ),
    }


__all__ = [
    "ON_SHELL_CONDITION_THRESHOLD",
    "PHYSICAL_RENORMALIZATION_CONTRACT_STATUS",
    "PhysicalRenormalizationConditionState",
    "physical_renormalization_condition_contract",
    "physical_renormalization_condition_state",
]
