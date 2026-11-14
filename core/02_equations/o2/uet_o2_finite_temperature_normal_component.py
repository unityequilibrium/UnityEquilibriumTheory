"""Thermodynamic normal-component lane for Topic 13.

This module names and exposes the thermal quasiparticle sector already used by
the finite-temperature O(2) EOS.  It closes the thermodynamic normal
component as a natural-unit lane, while keeping the distinct physical
normal-flow and retarded-Kubo questions open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_finite_temperature_two_fluid_response import (
    finite_temperature_two_fluid_static_state,
)


THERMODYNAMIC_NORMAL_COMPONENT_STATUS = (
    "PASS_ACTION_DERIVED_THERMODYNAMIC_NORMAL_COMPONENT_LANE"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class ThermodynamicNormalComponentState:
    """Thermal-sector state with the normal component named explicitly."""

    branch: str
    temperature: float
    chemical_potential: float
    space_response: float
    normal_pressure: float
    normal_charge_density: float
    normal_entropy_density: float
    normal_energy_density: float
    normal_susceptibility: float
    normal_momentum_susceptibility: float
    total_entropy_density: float
    total_susceptibility: float
    data_role: str = (
        "ACTION_DERIVED_THERMODYNAMIC_NORMAL_COMPONENT_NOT_PHYSICAL_FLOW"
    )


def thermodynamic_normal_component_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> ThermodynamicNormalComponentState:
    """Return the declared thermal quasiparticle normal component.

    The component is defined by the thermal pressure sector and its
    thermodynamic derivatives:

    ``p_n = p_qp``, ``n_n = partial_mu p_n``,
    ``s_n = partial_T p_n``, and
    ``epsilon_n = -p_n + T*s_n + mu*n_n``.

    ``normal_momentum_susceptibility`` is retained as a separate static
    Doppler response.  It is not identified with a mass density or a physical
    retarded Kubo coefficient.
    """

    temperature = _finite(temperature, "temperature")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    state = finite_temperature_two_fluid_static_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        include_normal_heat_flux_balance=False,
    )
    values = (
        state.normal_pressure,
        state.normal_charge_density,
        state.normal_entropy_density,
        state.normal_energy_density,
        state.normal_susceptibility,
        state.normal_momentum_susceptibility,
        state.total_entropy_density,
        state.total_susceptibility,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("normal-component state is not finite")
    return ThermodynamicNormalComponentState(
        branch=state.branch,
        temperature=state.temperature,
        chemical_potential=state.chemical_potential,
        space_response=state.space_response,
        normal_pressure=state.normal_pressure,
        normal_charge_density=state.normal_charge_density,
        normal_entropy_density=state.normal_entropy_density,
        normal_energy_density=state.normal_energy_density,
        normal_susceptibility=state.normal_susceptibility,
        normal_momentum_susceptibility=state.normal_momentum_susceptibility,
        total_entropy_density=state.total_entropy_density,
        total_susceptibility=state.total_susceptibility,
    )


def thermodynamic_normal_component_contract() -> dict[str, object]:
    """Return the normal-component equations and promotion boundary."""

    return {
        "status": THERMODYNAMIC_NORMAL_COMPONENT_STATUS,
        "equations": {
            "normal_pressure": "p_n(T,mu,Phi)=p_qp(T,mu,Phi)",
            "normal_charge": "n_n=partial_mu p_n",
            "normal_entropy": "s_n=partial_T p_n",
            "normal_energy": "epsilon_n=-p_n+T*s_n+mu*n_n",
            "normal_susceptibility": "chi_n=partial_mu n_n",
            "normal_static_response": (
                "Pi_n=(1/3) sum_a integral[d^3k/(2*pi)^3] "
                "k^2[-partial_E n_B(E_a)]"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural",
            "normal_pressure_energy": "natural energy density",
            "normal_charge_entropy": "natural density",
            "normal_susceptibility": "natural static response",
            "normal_momentum_susceptibility": (
                "natural static momentum response; not Landau mass density"
            ),
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state",
            "R_obs": "observer record; not physical dynamics",
        },
        "derivation_class": (
            "action-derived tree-condensate plus thermal-quasiparticle EOS "
            "and static Doppler-response composition"
        ),
        "observable": (
            "finite-temperature thermodynamic normal component and its static "
            "momentum response"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_NATURAL_THERMODYNAMIC_LANE",
        "closed_scope": [
            "normal pressure, charge, entropy, energy, and susceptibility definitions",
            "branch-resolved finite-temperature normal component",
            "low-temperature suppression and total-state stability checks",
        ],
        "excluded_scope": [
            "physical normal-fluid mass density",
            "retarded physical Kubo coefficient",
            "condensed dissipative two-fluid transport",
            "SI Phi normalization and alpha_Phi_K",
            "Ding C_src acceptance and TTG prediction",
        ],
        "claim_boundary": (
            "This closes the thermodynamic normal component for the declared "
            "natural-unit O(2) lane.  It does not close physical normal flow, "
            "retarded transport, SI mapping, alpha_Phi_K, or Full Topic 13."
        ),
    }


__all__ = [
    "THERMODYNAMIC_NORMAL_COMPONENT_STATUS",
    "ThermodynamicNormalComponentState",
    "thermodynamic_normal_component_state",
    "thermodynamic_normal_component_contract",
]
