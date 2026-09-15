"""Action-derived natural-unit Phi-to-thermal observable bridge for Topic 13.

This lane derives a local response map from the finite-temperature action/EOS
to an energy-density response and then to a natural-unit quasi-temperature
response.  It deliberately uses the fixed-(mu, Phi) energy derivative
C_epsilon_T = (partial_T epsilon)_(mu,Phi) instead of relabeling it as a
source-backed volumetric c_v.  The result is therefore an internal
natural-unit bridge, not a Kelvin calibration of the base normalized Phi.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Callable

from docs.core.uet_o2_action_thermal_stiffness_beta import (
    action_thermal_stiffness_config,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
)


ACTION_NATURAL_PHI_THERMAL_BRIDGE_STATUS = (
    "PASS_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE"
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


def _central_difference(
    function: Callable[[float], float],
    value: float,
    step: float,
) -> float:
    h = _positive(step, "difference step")
    return (float(function(value + h)) - float(function(value - h))) / (2.0 * h)


def _energy_density(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    return float(
        finite_temperature_o2_state(
            temperature,
            chemical_potential,
            space_response,
            config,
        ).energy_density
    )


def natural_bridge_config() -> FiniteTemperatureO2QuasiparticleConfig:
    """Return the same action-coupled configuration used by the beta lane."""

    return action_thermal_stiffness_config()


def energy_response_derivative(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    phi_step: float,
) -> float:
    """Return (partial_Phi epsilon)_(T,mu) in the natural action lane."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    return _central_difference(
        lambda candidate: _energy_density(
            temperature,
            chemical_potential,
            candidate,
            config,
        ),
        space_response,
        phi_step,
    )


def energy_temperature_susceptibility(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    temperature_step: float,
) -> float:
    """Return C_epsilon_T=(partial_T epsilon)_(mu,Phi).

    This name is intentional.  A fixed-chemical-potential derivative is not
    silently relabeled as the source-backed fixed-density volumetric c_v.
    """

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    _positive(temperature_step, "temperature_step")
    if temperature <= temperature_step:
        raise ValueError("temperature must exceed temperature_step")
    return _central_difference(
        lambda candidate: _energy_density(
            candidate,
            chemical_potential,
            space_response,
            config,
        ),
        temperature,
        temperature_step,
    )


def natural_phi_to_temperature_coefficient(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    phi_step: float,
    temperature_step: float,
) -> float:
    """Return alpha_Phi_T^nat for the local natural-unit bridge."""

    response = energy_response_derivative(
        temperature,
        chemical_potential,
        space_response,
        config,
        phi_step,
    )
    capacity = energy_temperature_susceptibility(
        temperature,
        chemical_potential,
        space_response,
        config,
        temperature_step,
    )
    if not isfinite(capacity) or capacity <= 0.0:
        raise FloatingPointError(
            "the natural thermal susceptibility must be finite and positive"
        )
    return response / capacity


@dataclass(frozen=True)
class ActionNaturalPhiThermalBridgeState:
    """Machine-readable state for the action-derived local bridge."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    pressure: float
    entropy_density: float
    charge_density: float
    energy_density: float
    thermodynamic_identity_residual: float
    energy_response_derivative: float
    refined_energy_response_derivative: float
    energy_temperature_susceptibility: float
    refined_energy_temperature_susceptibility: float
    alpha_phi_temperature_natural: float
    refined_alpha_phi_temperature_natural: float
    response_probe_phi: float
    linear_energy_response: float
    linear_temperature_response_natural: float
    exact_energy_response: float
    linearization_relative_residual: float
    response_refinement_relative_change: float
    susceptibility_refinement_relative_change: float
    coefficient_refinement_relative_change: float
    phi_ontology_preserved: bool
    normalized_beta_t13_emitted: bool
    numeric_alpha_phi_k_emitted: bool
    numeric_e0_emitted: bool
    physical_cv_emitted: bool
    landauer_identity_used: bool
    parameter_fitting_performed: bool
    target_data_used: bool
    xie_2026_accessed: bool
    data_role: str


def action_natural_phi_thermal_bridge_state(
    temperature: float = 0.22,
    chemical_potential: float = 0.35,
    space_response: float = 0.15,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    phi_step: float = 2.0e-3,
    temperature_step: float = 1.0e-3,
    refined_phi_step: float = 1.0e-3,
    refined_temperature_step: float = 5.0e-4,
    response_probe_phi: float = 1.0e-3,
) -> ActionNaturalPhiThermalBridgeState:
    """Evaluate the local action/EOS-to-natural-temperature response map."""

    config = config or natural_bridge_config()
    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    phi_step = _positive(phi_step, "phi_step")
    temperature_step = _positive(temperature_step, "temperature_step")
    refined_phi_step = _positive(refined_phi_step, "refined_phi_step")
    refined_temperature_step = _positive(
        refined_temperature_step,
        "refined_temperature_step",
    )
    response_probe_phi = _positive(response_probe_phi, "response_probe_phi")
    if temperature <= max(temperature_step, refined_temperature_step):
        raise ValueError("temperature must exceed all temperature steps")

    base = finite_temperature_o2_state(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    stencil_states = [
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
            temperature - refined_temperature_step,
            temperature + refined_temperature_step,
        )
        for point_phi in (
            space_response - phi_step,
            space_response,
            space_response + phi_step,
            space_response - refined_phi_step,
            space_response + refined_phi_step,
        )
    ]
    if any(state.branch != base.branch for state in stencil_states):
        raise NotImplementedError(
            "the natural bridge requires one declared thermodynamic branch across its stencil"
        )

    response = energy_response_derivative(
        temperature,
        chemical_potential,
        space_response,
        config,
        phi_step,
    )
    refined_response = energy_response_derivative(
        temperature,
        chemical_potential,
        space_response,
        config,
        refined_phi_step,
    )
    susceptibility = energy_temperature_susceptibility(
        temperature,
        chemical_potential,
        space_response,
        config,
        temperature_step,
    )
    refined_susceptibility = energy_temperature_susceptibility(
        temperature,
        chemical_potential,
        space_response,
        config,
        refined_temperature_step,
    )
    coefficient = response / susceptibility
    refined_coefficient = refined_response / refined_susceptibility
    exact_energy_response = _energy_density(
        temperature,
        chemical_potential,
        space_response + response_probe_phi,
        config,
    ) - base.energy_density
    linear_energy_response = response * response_probe_phi
    linear_temperature_response = coefficient * response_probe_phi
    linearization_residual = abs(exact_energy_response - linear_energy_response) / max(
        abs(exact_energy_response),
        1.0e-30,
    )
    identity_residual = base.energy_density - (
        -base.pressure
        + temperature * base.entropy_density
        + chemical_potential * base.charge_density
    )
    values = (
        base.pressure,
        base.entropy_density,
        base.charge_density,
        base.energy_density,
        identity_residual,
        response,
        refined_response,
        susceptibility,
        refined_susceptibility,
        coefficient,
        refined_coefficient,
        exact_energy_response,
        linear_energy_response,
        linear_temperature_response,
        linearization_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("natural Phi-to-thermal bridge produced a non-finite value")
    if susceptibility <= 0.0 or refined_susceptibility <= 0.0:
        raise FloatingPointError("natural thermal susceptibility must be positive")

    return ActionNaturalPhiThermalBridgeState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=base.branch,
        pressure=base.pressure,
        entropy_density=base.entropy_density,
        charge_density=base.charge_density,
        energy_density=base.energy_density,
        thermodynamic_identity_residual=float(identity_residual),
        energy_response_derivative=float(response),
        refined_energy_response_derivative=float(refined_response),
        energy_temperature_susceptibility=float(susceptibility),
        refined_energy_temperature_susceptibility=float(refined_susceptibility),
        alpha_phi_temperature_natural=float(coefficient),
        refined_alpha_phi_temperature_natural=float(refined_coefficient),
        response_probe_phi=response_probe_phi,
        linear_energy_response=float(linear_energy_response),
        linear_temperature_response_natural=float(linear_temperature_response),
        exact_energy_response=float(exact_energy_response),
        linearization_relative_residual=float(linearization_residual),
        response_refinement_relative_change=abs(refined_response - response)
        / max(abs(refined_response), 1.0e-30),
        susceptibility_refinement_relative_change=abs(
            refined_susceptibility - susceptibility
        )
        / max(abs(refined_susceptibility), 1.0e-30),
        coefficient_refinement_relative_change=abs(
            refined_coefficient - coefficient
        )
        / max(abs(refined_coefficient), 1.0e-30),
        phi_ontology_preserved=True,
        normalized_beta_t13_emitted=False,
        numeric_alpha_phi_k_emitted=False,
        numeric_e0_emitted=False,
        physical_cv_emitted=False,
        landauer_identity_used=False,
        parameter_fitting_performed=False,
        target_data_used=False,
        xie_2026_accessed=False,
        data_role="ACTION_DERIVED_NATURAL_UNIT_LOCAL_BRIDGE_NO_SI_CALIBRATION",
    )


def action_natural_phi_thermal_bridge_contract() -> dict[str, Any]:
    """Return the equations and boundaries for the natural bridge lane."""

    return {
        "status": ACTION_NATURAL_PHI_THERMAL_BRIDGE_STATUS,
        "equations": {
            "action_eos": "p=p_qp(T,mu,Phi); epsilon=-p+T*partial_T p+mu*partial_mu p",
            "energy_response": "Delta_epsilon^nat=(partial_Phi epsilon)_(T,mu)*Delta_Phi",
            "thermal_susceptibility": "C_epsilon_T^nat=(partial_T epsilon)_(mu,Phi)",
            "natural_temperature_response": "Delta_T_q^nat=Delta_epsilon^nat/C_epsilon_T^nat",
            "natural_bridge_coefficient": "alpha_Phi_T^nat=(partial_Phi epsilon)_(T,mu)/(partial_T epsilon)_(mu,Phi)",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature": "natural energy",
            "energy_density": "natural energy density",
            "energy_response_derivative": "natural energy density per Phi",
            "C_epsilon_T": "natural energy density per natural energy at fixed (mu,Phi); not source c_v",
            "alpha_Phi_T_natural": "natural energy per Phi; not K per normalized Phi",
            "Phi": "existing effective response variable; normalization-dependent and not temperature",
            "Delta_Tq_natural": "natural energy response; not SI Kelvin",
            "alpha_Phi_K": "not emitted; requires independent Phi/e0/SI calibration",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-temperature quasiparticle EOS, thermodynamic identity, "
            "and local finite-difference response derivatives"
        ),
        "observable": (
            "natural-unit local Phi-induced energy-density response and quasi-temperature response"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_NATURAL_BRIDGE_NO_SOURCE_ROWS_NO_HOLDOUT",
        "included": {
            "non_circular_action_to_energy_map": True,
            "thermodynamic_identity": True,
            "local_energy_to_temperature_response": True,
            "branch_lock": True,
            "finite_difference_refinement": True,
        },
        "excluded": {
            "physical_cv": True,
            "SI_kelvin_map": True,
            "numeric_alpha_Phi_K": True,
            "base_Phi_to_Phi_E_scale": True,
            "normalized_beta_T13": True,
            "physical_Kubo": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only the action-derived natural-unit local bridge. It does not "
            "calibrate base Phi in SI, identify C_epsilon_T with source c_v, emit "
            "alpha_Phi_K, predict TTG temperature, or close Full Topic 13."
        ),
    }


__all__ = [
    "ACTION_NATURAL_PHI_THERMAL_BRIDGE_STATUS",
    "ActionNaturalPhiThermalBridgeState",
    "natural_bridge_config",
    "energy_response_derivative",
    "energy_temperature_susceptibility",
    "natural_phi_to_temperature_coefficient",
    "action_natural_phi_thermal_bridge_state",
    "action_natural_phi_thermal_bridge_contract",
]
