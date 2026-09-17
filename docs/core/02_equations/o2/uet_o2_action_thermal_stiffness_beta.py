"""Non-Landauer action-origin stiffness slope for the Topic 13 beta lane.

The finite-temperature quasiparticle EOS already supplies an action-derived
pressure with the declared response coupling.  This module differentiates its
free-energy density at fixed ``(T, mu)`` with respect to the existing effective
response variable and then differentiates that curvature with respect to the
natural temperature:

    f_qp(T, mu, Phi) = -p_qp(T, mu, Phi)
    a_Phi^nat(T) = d^2 f_qp / dPhi^2
    beta_Phi^nat = T * d a_Phi^nat / dT.

This is a local normal-branch natural-unit action lane.  It is not silently
identified with the normalized beta contract, a Kelvin coefficient, a physical
Phi scale, Landauer's identity, or alpha_Phi_K.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
    quasiparticle_pressure,
)


ACTION_THERMAL_STIFFNESS_BETA_STATUS = (
    "PASS_ACTION_DERIVED_THERMAL_STIFFNESS_BETA_LANE"
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


def action_thermal_stiffness_config() -> FiniteTemperatureO2QuasiparticleConfig:
    """Return the fixed action-coupled natural-unit control configuration."""

    response = CovariantResponseConfig(
        epsilon_nc=0.05,
        phi_equilibrium=0.0,
        response_kinetic=1.0,
        response_mass_sq=1.0,
        response_quartic=1.0,
    )
    matter = CovariantMatterConfig(
        matter_kinetic=1.0,
        matter_mass_sq=1.0,
        matter_quartic=1.0,
        response_coupling=0.8,
    )
    return FiniteTemperatureO2QuasiparticleConfig(
        eos=O2FiniteDensityEOSConfig(matter=matter, response=response),
        quadrature_order=128,
        cutoff_factor=60.0,
        derivative_step=1.0e-4,
    )


def _free_energy_density(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    return float(
        -quasiparticle_pressure(
            temperature, chemical_potential, space_response, config
        )
    )


def response_free_energy_curvature(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    phi_step: float,
) -> float:
    """Return ``d^2 f_qp/dPhi^2`` by a symmetric fixed-state difference."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    step = _positive(phi_step, "phi_step")
    return float(
        (
            _free_energy_density(
                temperature,
                chemical_potential,
                space_response + step,
                config,
            )
            - 2.0
            * _free_energy_density(
                temperature, chemical_potential, space_response, config
            )
            + _free_energy_density(
                temperature,
                chemical_potential,
                space_response - step,
                config,
            )
        )
        / (step * step)
    )


def action_thermal_stiffness_beta_state(
    temperature: float = 0.22,
    chemical_potential: float = 0.35,
    space_response: float = 0.15,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    phi_step: float = 5.0e-3,
    temperature_step: float = 2.0e-3,
    refined_phi_step: float = 2.0e-3,
    refined_temperature_step: float = 1.0e-3,
) -> "ActionThermalStiffnessBetaState":
    """Evaluate the action-derived natural-unit stiffness-temperature slope."""

    config = config or action_thermal_stiffness_config()
    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    phi_step = _positive(phi_step, "phi_step")
    temperature_step = _positive(temperature_step, "temperature_step")
    refined_phi_step = _positive(refined_phi_step, "refined_phi_step")
    refined_temperature_step = _positive(
        refined_temperature_step, "refined_temperature_step"
    )

    base_state = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    branch_points = [
        finite_temperature_o2_state(
            point_temperature,
            chemical_potential,
            point_phi,
            config,
        )
        for point_temperature in (
            temperature - temperature_step,
            temperature,
            temperature + temperature_step,
        )
        for point_phi in (
            space_response - phi_step,
            space_response,
            space_response + phi_step,
        )
    ]
    if any(state.branch != "normal" for state in branch_points):
        raise NotImplementedError(
            "the action thermal stiffness lane requires one declared normal branch across its stencil"
        )

    curvature = response_free_energy_curvature(
        temperature,
        chemical_potential,
        space_response,
        config,
        phi_step,
    )
    curvature_plus = response_free_energy_curvature(
        temperature + temperature_step,
        chemical_potential,
        space_response,
        config,
        phi_step,
    )
    curvature_minus = response_free_energy_curvature(
        temperature - temperature_step,
        chemical_potential,
        space_response,
        config,
        phi_step,
    )
    beta_natural = temperature * (curvature_plus - curvature_minus) / (
        2.0 * temperature_step
    )

    refined_curvature = response_free_energy_curvature(
        temperature,
        chemical_potential,
        space_response,
        config,
        refined_phi_step,
    )
    refined_curvature_plus = response_free_energy_curvature(
        temperature + refined_temperature_step,
        chemical_potential,
        space_response,
        config,
        refined_phi_step,
    )
    refined_curvature_minus = response_free_energy_curvature(
        temperature - refined_temperature_step,
        chemical_potential,
        space_response,
        config,
        refined_phi_step,
    )
    refined_beta_natural = temperature * (
        refined_curvature_plus - refined_curvature_minus
    ) / (2.0 * refined_temperature_step)
    values = (
        base_state.pressure,
        base_state.entropy_density,
        curvature,
        beta_natural,
        refined_curvature,
        refined_beta_natural,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("action-derived thermal stiffness is not finite")
    return ActionThermalStiffnessBetaState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=base_state.branch,
        effective_mass=base_state.effective_mass,
        pressure=base_state.pressure,
        entropy_density=base_state.entropy_density,
        response_epsilon_nc=config.eos.response.epsilon_nc,
        response_coupling=config.eos.matter.response_coupling,
        phi_step=phi_step,
        temperature_step=temperature_step,
        refined_phi_step=refined_phi_step,
        refined_temperature_step=refined_temperature_step,
        a_phi_natural=curvature,
        beta_phi_natural=float(beta_natural),
        refined_a_phi_natural=refined_curvature,
        refined_beta_phi_natural=float(refined_beta_natural),
        curvature_relative_change=abs(refined_curvature - curvature)
        / max(abs(refined_curvature), 1.0e-30),
        beta_relative_change=abs(refined_beta_natural - beta_natural)
        / max(abs(refined_beta_natural), 1.0e-30),
        normalized_beta_T13_emitted=False,
        numeric_e0_emitted=False,
        numeric_alpha_Phi_K_emitted=False,
        landauer_identity_used=False,
        parameter_fitting_performed=False,
        target_data_used=False,
        xie_2026_accessed=False,
        data_role="ACTION_DERIVED_NATURAL_RESPONSE_STIFFNESS_NOT_NORMALIZED_BETA",
    )


@dataclass(frozen=True)
class ActionThermalStiffnessBetaState:
    """Action-derived natural-unit beta/stiffness state and convergence fields."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    effective_mass: float
    pressure: float
    entropy_density: float
    response_epsilon_nc: float
    response_coupling: float
    phi_step: float
    temperature_step: float
    refined_phi_step: float
    refined_temperature_step: float
    a_phi_natural: float
    beta_phi_natural: float
    refined_a_phi_natural: float
    refined_beta_phi_natural: float
    curvature_relative_change: float
    beta_relative_change: float
    normalized_beta_T13_emitted: bool
    numeric_e0_emitted: bool
    numeric_alpha_Phi_K_emitted: bool
    landauer_identity_used: bool
    parameter_fitting_performed: bool
    target_data_used: bool
    xie_2026_accessed: bool
    data_role: str


def action_thermal_stiffness_beta_contract() -> dict[str, Any]:
    """Return the natural-unit action derivation and non-identification rules."""

    return {
        "status": ACTION_THERMAL_STIFFNESS_BETA_STATUS,
        "equations": {
            "finite_temperature_free_energy": "f_qp(T,mu,Phi)=-p_qp(T,mu,Phi)",
            "response_stiffness": "a_Phi^nat(T)=partial_Phi^2 f_qp(T,mu,Phi)|_(T,mu,Phi_ref)",
            "action_beta": "beta_Phi^nat=T*partial_T a_Phi^nat",
            "temperature_difference": "partial_T a_Phi^nat=(a_Phi^nat(T+h_T)-a_Phi^nat(T-h_T))/(2*h_T)",
            "response_difference": "partial_Phi^2 f_qp=(f_qp(Phi+h_Phi)-2*f_qp(Phi)+f_qp(Phi-h_Phi))/h_Phi^2",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "T_mu_effective_mass": "natural energy",
            "Phi": "existing effective response variable with natural action dimension; not temperature",
            "a_Phi_natural": "natural response free-energy curvature; normalization-dependent",
            "beta_Phi_natural": "natural stiffness-temperature product T*partial_T a_Phi^nat",
            "normalized_beta_T13": "not emitted; requires an independent Phi/e0 normalization map",
            "e0": "not supplied",
            "alpha_Phi_K": "not emitted",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-temperature quasiparticle pressure, fixed-state response curvature, "
            "and symmetric temperature differentiation with a refined stencil"
        ),
        "observable": "natural-unit local response stiffness slope on a declared normal branch",
        "data_role": "ACTION_DERIVED_INTERNAL_NO_SOURCE_ROWS_NO_HOLDOUT",
        "included": {
            "non_circular_action_origin": True,
            "finite_temperature_quasiparticle_determinant": True,
            "fixed_mu_and_phi_stencil": True,
            "temperature_stencil_refinement": True,
            "landauer_identity": False,
        },
        "excluded": {
            "normalized_beta_T13": True,
            "physical_beta_source": True,
            "SI_Phi_normalization": True,
            "e0": True,
            "alpha_Phi_K": True,
            "physical_Kubo": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only the non-Landauer action-origin of a local natural-unit response stiffness slope "
            "on the declared normal quasiparticle branch. It does not identify the normalized beta_T13, "
            "a physical SI coefficient, alpha_Phi_K, a TTG prediction, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "ACTION_THERMAL_STIFFNESS_BETA_STATUS",
    "ActionThermalStiffnessBetaState",
    "action_thermal_stiffness_beta_contract",
    "action_thermal_stiffness_beta_state",
    "action_thermal_stiffness_config",
    "response_free_energy_curvature",
]
