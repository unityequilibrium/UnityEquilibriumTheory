"""Action-derived one-loop thermal normal branch for the O(2) pilot.

The branch is evaluated around the homogeneous normal background A=0.  The
thermal determinant uses the effective mass already fixed by the conservative
UET action.  Vacuum counterterms, the condensed branch, and a finite-T
two-fluid completion are intentionally outside this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np

from docs.core.standard_o2_finite_temperature_comparator import (
    StandardO2ThermalNormalState,
    _bose_occupation,
    standard_o2_normal_state,
)
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)


@dataclass(frozen=True)
class UETO2OneLoopNormalState:
    """Thermal one-loop normal-branch state in natural units."""

    thermal_state: StandardO2ThermalNormalState
    effective_mass_sq: float
    dm_eff_sq_dphi: float
    thermal_scalar_density: float
    pressure_phi_derivative: float
    matter_grand_potential: float
    one_loop_thermal_grand_potential: float
    vacuum_counterterm_included: bool = False
    condensate_contribution_included: bool = False
    normal_two_fluid_completion: bool = False
    data_role: str = "ACTION_DERIVED_ONE_LOOP_NORMAL_LANE_NOT_FULL_UET_THERMAL_CLOSURE"

    @property
    def temperature(self) -> float:
        return self.thermal_state.temperature

    @property
    def chemical_potential(self) -> float:
        return self.thermal_state.chemical_potential

    @property
    def space_response(self) -> float:
        return self.thermal_state.space_response

    @property
    def pressure(self) -> float:
        return self.thermal_state.pressure

    @property
    def charge_density(self) -> float:
        return self.thermal_state.charge_density

    @property
    def entropy_density(self) -> float:
        return self.thermal_state.entropy_density

    @property
    def energy_density(self) -> float:
        return self.thermal_state.energy_density

    @property
    def charge_susceptibility(self) -> float:
        return self.thermal_state.charge_susceptibility


def _thermal_scalar_density(state: StandardO2ThermalNormalState) -> float:
    """Return 1/2 integral (n_- + n_+)/E in the thermal normal state."""

    nodes, weights = np.polynomial.legendre.leggauss(state.quadrature_order)
    momenta = 0.5 * state.momentum_cutoff * (nodes + 1.0)
    weights = 0.5 * state.momentum_cutoff * weights
    energy = np.sqrt(momenta * momenta + state.effective_mass**2)
    measure = momenta * momenta / (2.0 * np.pi**2)
    arguments_minus = (energy - state.chemical_potential) / state.temperature
    arguments_plus = (energy + state.chemical_potential) / state.temperature
    occupations_minus = np.array(
        [_bose_occupation(float(value)) for value in arguments_minus]
    )
    occupations_plus = np.array(
        [_bose_occupation(float(value)) for value in arguments_plus]
    )
    result = 0.5 * float(
        np.sum(weights * measure * (occupations_minus + occupations_plus) / energy)
    )
    if not isfinite(result) or result <= 0.0:
        raise FloatingPointError("thermal scalar density must be finite and positive")
    return result


def uet_o2_one_loop_normal_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 50.0,
) -> UETO2OneLoopNormalState:
    """Evaluate the action-derived thermal determinant on the normal branch.

    The matter background is fixed at ``A=0`` and the thermal fluctuation
    determinant is the standard complex-scalar contribution.  The only UET
    input to the determinant is ``m_eff(Phi)`` from the conservative action.
    """

    state = standard_o2_normal_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        cutoff_factor=cutoff_factor,
    )
    mass_sq = float(effective_mass_sq(space_response, config))
    dm_eff_sq_dphi = float(
        -config.response.epsilon_nc * config.matter.response_coupling
    )
    scalar_density = _thermal_scalar_density(state)
    pressure_phi_derivative = -dm_eff_sq_dphi * scalar_density
    matter_grand_potential = 0.0
    one_loop_thermal_grand_potential = -state.pressure
    values = (
        mass_sq,
        dm_eff_sq_dphi,
        scalar_density,
        pressure_phi_derivative,
        one_loop_thermal_grand_potential,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("one-loop normal branch produced a non-finite value")
    return UETO2OneLoopNormalState(
        thermal_state=state,
        effective_mass_sq=mass_sq,
        dm_eff_sq_dphi=dm_eff_sq_dphi,
        thermal_scalar_density=scalar_density,
        pressure_phi_derivative=pressure_phi_derivative,
        matter_grand_potential=matter_grand_potential,
        one_loop_thermal_grand_potential=one_loop_thermal_grand_potential,
    )


def uet_o2_one_loop_normal_branch_contract() -> dict[str, Any]:
    """Return the derived branch boundary and excluded physics."""

    return {
        "status": "ACTION_DERIVED_ONE_LOOP_THERMAL_NORMAL_BRANCH",
        "equations": {
            "normal_condition": "Z*mu^2 < m_eff(Phi)^2",
            "dispersion": "E_k = sqrt(k^2 + m_eff(Phi)^2)",
            "grand_potential": "Omega_N^(1,T) = T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))] d^3k/(2 pi)^3",
            "pressure": "p_N^(1,T) = -Omega_N^(1,T)",
            "charge_density": "n_N = partial p_N/partial mu",
            "entropy_density": "s_N = partial p_N/partial T",
            "energy_density": "epsilon_N = -p_N + T*s_N + mu*n_N",
            "response_derivative": "partial p_N/partial Phi = -(partial m_eff^2/partial Phi) * 1/2 integral[(n_-+n_+)/E_k] d^3k/(2 pi)^3",
            "action_mass_map": "partial m_eff^2/partial Phi = -epsilon_nc * response_coupling",
        },
        "approximation": {
            "background": "homogeneous normal branch A=0",
            "loop_content": "thermal one-loop determinant only",
            "vacuum_counterterm": "NOT_INCLUDED",
            "condensate_branch": "NOT_INCLUDED",
            "normal_two_fluid_completion": "NOT_INCLUDED",
        },
        "units": {
            "unit_lane": "natural",
            "T_mu_m_eff": "natural energy",
            "Omega_pressure_energy": "natural energy density",
            "n": "natural charge density",
            "s": "natural entropy density",
            "dpressure_dPhi": "natural energy density per natural Phi field unit",
        },
        "ontology": {
            "C": "not identified with charge density",
            "Phi": "action response input; not temperature",
            "R_gen": "not used as state or feedback",
            "R_obs": "not included in the branch",
        },
        "data_role": "ACTION_DERIVED_ONE_LOOP_NORMAL_LANE_NOT_FULL_UET_THERMAL_CLOSURE",
        "claim_boundary": "The branch derives a thermal normal-background determinant from the declared natural-unit action mass map. It does not close the renormalized finite-temperature UET action, condensate/two-fluid sector, physical Kubo transport, SK/KMS matching, SI Phi calibration, or external validation.",
    }


__all__ = [
    "UETO2OneLoopNormalState",
    "uet_o2_one_loop_normal_state",
    "uet_o2_one_loop_normal_branch_contract",
]
