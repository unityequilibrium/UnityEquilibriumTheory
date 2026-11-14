"""All-positive-energy on-shell cut response for the declared O(2) sunset.

This lane combines the state-matched retarded response grid with the action-
level signed-cut multiplicity contract.  It closes the on-shell spectral-cut
response in the declared equal-mass natural-unit lane, not the complete
off-shell 1PI self-energy or a physical transport coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from docs.core.uet_o2_finite_temperature_declared_retarded_1pi_grid import (
    DeclaredRetarded1PIGridState,
    finite_temperature_declared_retarded_1pi_grid_contract,
    finite_temperature_declared_retarded_1pi_grid_state,
)
from docs.core.uet_o2_finite_temperature_signed_cut_coverage import (
    SignedCutCoverageState,
    finite_temperature_signed_cut_coverage_state,
)
from docs.core.uet_o2_finite_temperature_sunset_cut_multiplicity import (
    SunsetCutMultiplicityState,
    finite_temperature_sunset_cut_multiplicity_state,
)


ALL_ONSHELL_CUT_RESPONSE_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE"
)
ALL_ONSHELL_CUT_RESPONSE_THRESHOLD = 2.0e-2


@dataclass(frozen=True)
class AllOnshellCutResponseState:
    """State for the complete declared positive-energy on-shell cut response."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    invariant_grid: tuple[float, ...]
    response_grid: DeclaredRetarded1PIGridState
    signed_cut_taxonomy: SignedCutCoverageState
    cut_multiplicity: SunsetCutMultiplicityState
    all_positive_energy_signed_cuts_completed: bool
    all_positive_energy_on_shell_spectral_response_completed: bool
    on_shell_retarded_grid_completed: bool
    full_finite_temperature_1pi_self_energy_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_NO_HOLDOUT"
    )


def finite_temperature_all_onshell_cut_response_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    invariant_grid: tuple[float, ...] = (4.75, 5.0, 5.5),
) -> AllOnshellCutResponseState:
    """Build a response grid admitted by the signed-cut and graph contracts."""

    response_grid = finite_temperature_declared_retarded_1pi_grid_state(
        temperature,
        mass_squared,
        quartic,
        invariant_grid=invariant_grid,
    )
    signed_cut_taxonomy = finite_temperature_signed_cut_coverage_state(
        external_energy=response_grid.invariant_grid[-1] ** 0.5,
        mass_squared=mass_squared,
    )
    cut_multiplicity = finite_temperature_sunset_cut_multiplicity_state(
        mass_squared,
        quartic,
    )
    signed_cut_complete = bool(
        signed_cut_taxonomy.signed_cut_kinematic_taxonomy_completed
        and cut_multiplicity.action_level_signed_cut_multiplicity_completed
        and cut_multiplicity.current_factor_matches_two_to_two_graph_weight
    )
    response_complete = bool(
        response_grid.declared_retarded_response_grid_completed
        and response_grid.declared_1pi_pole_subtracted_response_completed
        and response_grid.matched_state_witness
        and response_grid.positive_spectral_grid_witness
        and response_grid.lower_half_plane_grid_witness
        and response_grid.max_kms_log_ratio_residual
        <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD
        and response_grid.max_fdt_residual <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD
        and response_grid.max_pv_inner_convergence_residual
        <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD
        and response_grid.max_pv_outer_convergence_residual
        <= ALL_ONSHELL_CUT_RESPONSE_THRESHOLD
        and response_grid.max_retarded_i0_consistency_residual <= 1.0e-12
    )
    return AllOnshellCutResponseState(
        temperature=float(temperature),
        mass_squared=float(mass_squared),
        quartic_coupling=float(quartic),
        invariant_grid=tuple(float(value) for value in invariant_grid),
        response_grid=response_grid,
        signed_cut_taxonomy=signed_cut_taxonomy,
        cut_multiplicity=cut_multiplicity,
        all_positive_energy_signed_cuts_completed=signed_cut_complete,
        all_positive_energy_on_shell_spectral_response_completed=bool(
            signed_cut_complete and response_complete
        ),
        on_shell_retarded_grid_completed=response_complete,
    )


def finite_temperature_all_onshell_cut_response_contract() -> dict[str, Any]:
    """Return equations, units, and the narrow on-shell claim boundary."""

    response_contract = finite_temperature_declared_retarded_1pi_grid_contract()
    return {
        "status": ALL_ONSHELL_CUT_RESPONSE_STATUS,
        "equations": {
            "signed_cut_partition": (
                "rho_T^all_onshell=rho_T^(+++)+"
                "rho_T^(-++)+rho_T^(+-+)+rho_T^(++-)"
            ),
            "equal_mass_representative_mapping": (
                "rho_T^(2<->2,all)=w_22*rho_T^(++-), w_22=3*(1/6)=1/2"
            ),
            "declared_retarded_response": (
                "Sigma_R,T^all_onshell(s+i0)="
                "Re Sigma_R,T^all_onshell,sub(s)-i*pi*rho_T^all_onshell(s)"
            ),
            "kms": "log(rho_>^all_onshell/rho_<^all_onshell)=sqrt(s)/T",
            "fdt": "N_T^all_onshell=rho_T^all_onshell*coth(sqrt(s)/(2*T))",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature or metric",
            "R_gen": "derived physical/history trace; no independent state",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "unit_contract": response_contract["unit_contract"],
        "derivation_class": (
            "action-derived equal-mass signed-cut taxonomy, graph multiplicity, "
            "and state-matched retarded spectral response grid"
        ),
        "observable": (
            "all positive-energy on-shell spectral density, retarded sign, "
            "multi-invariant KMS/FDT residuals, i0 consistency, and PV convergence"
        ),
        "data_role": (
            "ACTION_DERIVED_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_NO_HOLDOUT"
        ),
        "included": {
            "all_positive_energy_equal_mass_signed_cuts": True,
            "graph_weighted_two_to_two_representative": True,
            "state_matched_retarded_response_grid": True,
            "grid_level_kms_fdt": True,
            "retarded_i0_and_pv_convergence": True,
        },
        "excluded": {
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "unique_physical_renormalization": True,
            "physical_scattering_normalization_identity": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the all-positive-energy equal-mass on-shell thermal "
            "cut spectral response on the declared invariant grid, with the action "
            "graph multiplicity admitted. It does not close the complete off-shell "
            "finite-temperature 1PI self-energy, physical renormalization, physical "
            "scattering/Kubo normalization, entropy-current balance, SI mapping, "
            "alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "ALL_ONSHELL_CUT_RESPONSE_STATUS",
    "ALL_ONSHELL_CUT_RESPONSE_THRESHOLD",
    "AllOnshellCutResponseState",
    "finite_temperature_all_onshell_cut_response_contract",
    "finite_temperature_all_onshell_cut_response_state",
]
