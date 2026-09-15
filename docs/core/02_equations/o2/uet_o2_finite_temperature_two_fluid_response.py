"""Finite-temperature two-sector static response lane for Topic 13.

This module composes already-declared action-derived lanes rather than adding
new physics names to ``Phi``.  It keeps the thermodynamic condensate/normal
split, the static quasiparticle transverse response, and the normal-branch
covariant heat-flux balance in one auditable state record.

The normal response is deliberately called a static momentum susceptibility.
It is not silently promoted to a Landau normal density or to a retarded Kubo
coefficient.  The heat-flux component remains a finite-cutoff natural-unit
lane and does not provide an SI calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from docs.core.uet_o2_covariant_entropy_heat_flux_balance import (
    CovariantEntropyHeatFluxBalanceState,
    covariant_entropy_heat_flux_balance_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_formal_transverse_response import (
    FormalTransverseResponse,
    formal_transverse_quasiparticle_response,
)
from docs.core.uet_o2_formal_two_sector_thermodynamics import (
    FormalTwoSectorState,
    formal_two_sector_state,
)


FINITE_T_TWO_FLUID_STATIC_RESPONSE_STATUS = (
    "PASS_ACTION_DERIVED_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE"
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class FiniteTemperatureTwoFluidStaticState:
    """Combined state record for the declared finite-temperature sub-lanes."""

    branch: str
    temperature: float
    chemical_potential: float
    space_response: float
    total_pressure: float
    condensate_pressure: float
    normal_pressure: float
    total_charge_density: float
    condensate_charge_density: float
    normal_charge_density: float
    total_entropy_density: float
    condensate_entropy_density: float
    normal_entropy_density: float
    total_energy_density: float
    condensate_energy_density: float
    normal_energy_density: float
    total_susceptibility: float
    condensate_susceptibility: float
    normal_susceptibility: float
    normal_momentum_susceptibility: float
    condensate_phase_stiffness: float
    heat_flux_kappa_natural: float | None
    entropy_balance_residual: float | None
    charge_balance_residual: float | None
    energy_balance_residual: float | None
    momentum_balance_residual: float | None
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_phi_k_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_TWO_SECTOR_STATIC_RESPONSE_WITH_NORMAL_BRANCH_HEAT_BALANCE"
    )


def finite_temperature_two_fluid_static_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    include_normal_heat_flux_balance: bool = False,
) -> FiniteTemperatureTwoFluidStaticState:
    """Build one finite-temperature static two-sector response state.

    ``include_normal_heat_flux_balance`` is restricted to the normal branch by
    the existing covariant balance implementation.  Condensed states still
    expose their static quasiparticle response and thermodynamic sector split,
    while their dissipative two-fluid coefficient remains open.
    """

    temperature = _finite(temperature, "temperature")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    config = config or FiniteTemperatureO2QuasiparticleConfig()

    sectors: FormalTwoSectorState = formal_two_sector_state(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    static: FormalTransverseResponse = formal_transverse_quasiparticle_response(
        temperature,
        chemical_potential,
        space_response,
        config,
    )

    heat: CovariantEntropyHeatFluxBalanceState | None = None
    if include_normal_heat_flux_balance:
        if sectors.branch != "normal":
            raise NotImplementedError(
                "the current covariant heat-flux lane is restricted to the normal branch"
            )
        heat = covariant_entropy_heat_flux_balance_state(
            temperature,
            chemical_potential,
            space_response,
            config,
        )

    values = (
        sectors.total_pressure,
        sectors.condensate_pressure,
        sectors.normal_pressure,
        sectors.total_charge_density,
        sectors.condensate_charge_density,
        sectors.normal_charge_density,
        sectors.total_entropy_density,
        sectors.condensate_entropy_density,
        sectors.normal_entropy_density,
        sectors.total_energy_density,
        sectors.condensate_energy_density,
        sectors.normal_energy_density,
        sectors.total_susceptibility,
        sectors.condensate_susceptibility,
        sectors.normal_susceptibility,
        static.normal_momentum_susceptibility,
        static.condensate_phase_stiffness,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("finite-temperature two-fluid state is not finite")

    return FiniteTemperatureTwoFluidStaticState(
        branch=sectors.branch,
        temperature=sectors.temperature,
        chemical_potential=sectors.chemical_potential,
        space_response=sectors.space_response,
        total_pressure=sectors.total_pressure,
        condensate_pressure=sectors.condensate_pressure,
        normal_pressure=sectors.normal_pressure,
        total_charge_density=sectors.total_charge_density,
        condensate_charge_density=sectors.condensate_charge_density,
        normal_charge_density=sectors.normal_charge_density,
        total_entropy_density=sectors.total_entropy_density,
        condensate_entropy_density=sectors.condensate_entropy_density,
        normal_entropy_density=sectors.normal_entropy_density,
        total_energy_density=sectors.total_energy_density,
        condensate_energy_density=sectors.condensate_energy_density,
        normal_energy_density=sectors.normal_energy_density,
        total_susceptibility=sectors.total_susceptibility,
        condensate_susceptibility=sectors.condensate_susceptibility,
        normal_susceptibility=sectors.normal_susceptibility,
        normal_momentum_susceptibility=static.normal_momentum_susceptibility,
        condensate_phase_stiffness=static.condensate_phase_stiffness,
        heat_flux_kappa_natural=None if heat is None else heat.kappa_natural,
        entropy_balance_residual=None
        if heat is None
        else heat.entropy_balance_residual,
        charge_balance_residual=None
        if heat is None
        else heat.charge_balance_residual,
        energy_balance_residual=None
        if heat is None
        else heat.energy_balance_residual,
        momentum_balance_residual=None
        if heat is None
        else heat.momentum_balance_residual,
    )


def finite_temperature_two_fluid_static_contract() -> dict[str, object]:
    """Return equations, units, evidence class, and promotion boundary."""

    return {
        "status": FINITE_T_TWO_FLUID_STATIC_RESPONSE_STATUS,
        "equations": {
            "pressure_split": "p=p_condensate+p_normal",
            "charge_split": "n_i=partial_mu p_i; n=n_condensate+n_normal",
            "entropy_split": "s_i=partial_T p_i; s=s_condensate+s_normal",
            "energy_split": "epsilon_i=-p_i+T*s_i+mu*n_i; epsilon=sum_i epsilon_i",
            "static_normal_response": "chi_perp_qp=(1/3) sum_a integral[d^3k/(2*pi)^3] k^2[-partial_E n_B(E_a)]",
            "condensate_stiffness": "f_s_tree=Z*(Z*mu^2-m_eff^2)/lambda on q>0",
            "normal_heat_flux_interface": "q^mu=kappa_natural*X_T^mu; J_S^mu=s*u^mu+q^mu/T on the normal branch",
            "equilibrium_stability_boundary": (
                "s_total>=0 and chi_total>=0 on the declared reference states; "
                "sector derivative signs are not an independent density contract"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural",
            "sector_pressure_energy": "natural energy density",
            "sector_charge_entropy": "natural density",
            "normal_momentum_susceptibility": "formal natural static response; not Landau normal mass density",
            "condensate_phase_stiffness": "formal natural static stiffness",
            "heat_flux_kappa": "finite-cutoff natural moment coefficient; not SI conductivity",
            "sector_derivative_sign_policy": (
                "condensate/normal charge and energy entries are signed derivatives "
                "of residual grand-pressure sectors; positivity is checked on the "
                "total thermodynamic state, not imposed on a residual sector"
            ),
            "Phi": "effective response variable; not temperature or a metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state or feedback input",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "derivation_class": (
            "action-derived finite-temperature quasiparticle EOS composed with "
            "static Doppler response and the existing normal-branch collision balance"
        ),
        "observable": (
            "finite-temperature sector thermodynamics, static normal response, "
            "condensate stiffness, and normal-branch formal heat-flux balance"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_NATURAL_TWO_FLUID_STATIC_LANE",
        "closed_scope": [
            "finite-temperature condensate/normal thermodynamic decomposition",
            "branch-resolved static quasiparticle response",
            "condensed-branch tree stiffness boundary",
            "normal-branch finite-cutoff covariant heat-flux and entropy-balance interface",
            "total-state entropy and susceptibility stability boundary on the declared reference grid",
        ],
        "excluded_scope": [
            "retarded physical Kubo coefficient",
            "interacting finite-temperature self-energy and renormalization",
            "full dissipative condensed two-fluid tensor",
            "microscopic SK/KMS action matching beyond the declared interfaces",
            "SI heat-flux or Phi normalization",
            "numeric alpha_Phi_K",
            "TTG prediction or external validation",
        ],
        "claim_boundary": (
            "This closes a finite-temperature action-derived static two-sector lane "
            "and a normal-branch formal heat-balance interface only. It does not close "
            "the physical Kubo, condensed dissipative transport, SI, alpha_Phi_K, TTG, "
            "or Full Topic 13 gates."
        ),
    }


__all__ = [
    "FINITE_T_TWO_FLUID_STATIC_RESPONSE_STATUS",
    "FiniteTemperatureTwoFluidStaticState",
    "finite_temperature_two_fluid_static_state",
    "finite_temperature_two_fluid_static_contract",
]
