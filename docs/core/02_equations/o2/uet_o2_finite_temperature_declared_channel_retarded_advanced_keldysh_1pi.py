"""Numerical retarded/advanced/Keldysh response for declared thermal channels.

This module lifts the audited greater/lesser and principal-value response grid
into a declared real-time component triplet.  It is an action-derived
natural-unit lane for the named 1<->3 and representative 2<->2 sunset
channels.  It is not a claim that every off-shell thermal channel or a unique
physical renormalization anchor has been supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi, tanh
from typing import Any

from docs.core.uet_o2_finite_temperature_declared_retarded_1pi_grid import (
    DeclaredRetarded1PIGridState,
    DeclaredRetardedResponsePoint,
    finite_temperature_declared_retarded_1pi_grid_state,
)


DECLARED_CHANNEL_RETA_KELDYSH_1PI_STATUS = (
    "PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE"
)
DECLARED_CHANNEL_RETA_KELDYSH_1PI_THRESHOLD = 2.0e-2
DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD = 1.0e-12


@dataclass(frozen=True)
class DeclaredChannelRetardedAdvancedKeldyshPoint:
    """Real-valued components and residuals at one invariant point."""

    invariant_s: float
    external_energy: float
    greater_measure: float
    lesser_measure: float
    spectral_measure: float
    noise_measure: float
    retarded_real_part: float
    retarded_imaginary_part: float
    advanced_real_part: float
    advanced_imaginary_part: float
    keldysh_real_part: float
    keldysh_imaginary_part: float
    retarded_advanced_conjugacy_residual: float
    retarded_discontinuity_residual: float
    keldysh_component_residual: float
    keldysh_fdt_residual: float
    one_to_three_completed: bool
    two_to_two_completed: bool
    component_triplet_completed: bool


@dataclass(frozen=True)
class DeclaredChannelRetardedAdvancedKeldysh1PIState:
    """State-matched numerical response for the declared sunset channels."""

    temperature: float
    mass_squared: float
    quartic_coupling: float
    species_count: int
    reference_euclidean_s: float
    invariant_grid: tuple[float, ...]
    points: tuple[DeclaredChannelRetardedAdvancedKeldyshPoint, ...]
    source_response_grid: DeclaredRetarded1PIGridState
    max_retarded_advanced_conjugacy_residual: float
    max_retarded_discontinuity_residual: float
    max_keldysh_component_residual: float
    max_keldysh_fdt_residual: float
    declared_channel_retarded_advanced_keldysh_1pi_completed: bool
    bphz_subtraction_interface_preserved: bool
    complete_off_shell_finite_temperature_1pi_self_energy_completed: bool = False
    all_finite_temperature_sunset_channels_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    covariant_entropy_current_completed: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_T_DECLARED_CHANNEL_RETA_KELDYSH_1PI_NO_HOLDOUT"
    )


def _relative(value: float, reference: float) -> float:
    return abs(float(value) - float(reference)) / max(abs(float(reference)), 1.0e-300)


def _point(
    source: DeclaredRetardedResponsePoint,
    temperature: float,
) -> DeclaredChannelRetardedAdvancedKeldyshPoint:
    external_energy = float(source.external_energy)
    spectral = float(source.spectral_measure)
    noise = float(source.greater_measure + source.lesser_measure)
    retarded_real = float(source.principal_value_real_part)
    retarded_imaginary = float(-pi * spectral)
    advanced_real = retarded_real
    advanced_imaginary = float(pi * spectral)
    # Convention: Sigma_K = -2 i pi (Sigma^> + Sigma^<).
    keldysh_real = 0.0
    keldysh_imaginary = float(-2.0 * pi * noise)
    fdt_target = spectral / tanh(external_energy / (2.0 * temperature))
    conjugacy_residual = abs(advanced_real - retarded_real) + abs(
        advanced_imaginary + retarded_imaginary
    )
    discontinuity_residual = abs(
        (retarded_imaginary - advanced_imaginary) + 2.0 * pi * spectral
    )
    component_residual = abs(keldysh_real) + abs(
        keldysh_imaginary + 2.0 * pi * noise
    )
    fdt_residual = _relative(noise, fdt_target)
    values = (
        source.invariant_s,
        external_energy,
        source.greater_measure,
        source.lesser_measure,
        spectral,
        noise,
        retarded_real,
        retarded_imaginary,
        advanced_real,
        advanced_imaginary,
        keldysh_real,
        keldysh_imaginary,
        conjugacy_residual,
        discontinuity_residual,
        component_residual,
        fdt_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("declared real-time 1PI component is not finite")
    return DeclaredChannelRetardedAdvancedKeldyshPoint(
        invariant_s=float(source.invariant_s),
        external_energy=external_energy,
        greater_measure=float(source.greater_measure),
        lesser_measure=float(source.lesser_measure),
        spectral_measure=spectral,
        noise_measure=noise,
        retarded_real_part=retarded_real,
        retarded_imaginary_part=retarded_imaginary,
        advanced_real_part=advanced_real,
        advanced_imaginary_part=advanced_imaginary,
        keldysh_real_part=keldysh_real,
        keldysh_imaginary_part=keldysh_imaginary,
        retarded_advanced_conjugacy_residual=float(conjugacy_residual),
        retarded_discontinuity_residual=float(discontinuity_residual),
        keldysh_component_residual=float(component_residual),
        keldysh_fdt_residual=float(fdt_residual),
        one_to_three_completed=bool(source.one_to_three_completed),
        two_to_two_completed=bool(source.two_to_two_completed),
        component_triplet_completed=bool(
            source.one_to_three_completed
            and source.two_to_two_completed
            and conjugacy_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD
            and discontinuity_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD
            and component_residual <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD
        ),
    )


def finite_temperature_declared_channel_reta_keldysh_1pi_state(
    temperature: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    reference_euclidean_s: float = 0.5,
    invariant_grid: tuple[float, ...] = (4.75, 5.0, 5.5),
) -> DeclaredChannelRetardedAdvancedKeldysh1PIState:
    """Build retarded, advanced, and Keldysh components without fitting."""

    temperature = float(temperature)
    if not isfinite(temperature) or temperature <= 0.0:
        raise ValueError("temperature must be finite and positive")
    source = finite_temperature_declared_retarded_1pi_grid_state(
        temperature,
        mass_squared,
        quartic,
        species_count=species_count,
        reference_euclidean_s=reference_euclidean_s,
        invariant_grid=invariant_grid,
    )
    points = tuple(_point(point, temperature) for point in source.points)
    max_conjugacy = max(point.retarded_advanced_conjugacy_residual for point in points)
    max_discontinuity = max(point.retarded_discontinuity_residual for point in points)
    max_component = max(point.keldysh_component_residual for point in points)
    max_fdt = max(point.keldysh_fdt_residual for point in points)
    completed = all(point.component_triplet_completed for point in points) and (
        max_fdt <= DECLARED_CHANNEL_RETA_KELDYSH_1PI_THRESHOLD
    )
    return DeclaredChannelRetardedAdvancedKeldysh1PIState(
        temperature=temperature,
        mass_squared=float(mass_squared),
        quartic_coupling=float(quartic),
        species_count=int(species_count),
        reference_euclidean_s=float(reference_euclidean_s),
        invariant_grid=tuple(float(value) for value in invariant_grid),
        points=points,
        source_response_grid=source,
        max_retarded_advanced_conjugacy_residual=float(max_conjugacy),
        max_retarded_discontinuity_residual=float(max_discontinuity),
        max_keldysh_component_residual=float(max_component),
        max_keldysh_fdt_residual=float(max_fdt),
        declared_channel_retarded_advanced_keldysh_1pi_completed=bool(completed),
        bphz_subtraction_interface_preserved=True,
    )


def finite_temperature_declared_channel_reta_keldysh_1pi_contract() -> dict[str, Any]:
    """Return equations, units, evidence class, and the claim boundary."""

    return {
        "status": DECLARED_CHANNEL_RETA_KELDYSH_1PI_STATUS,
        "equations": {
            "greater_lesser_partition": "rho_>(s)=rho_>,13(s)+rho_>,22(s); rho_<(s)=rho_<,13(s)+rho_<,22(s)",
            "spectral_and_noise": "rho(s)=rho_>(s)-rho_<(s); N(s)=rho_>(s)+rho_<(s)",
            "retarded_component": "Sigma_R^decl(s)=Re Sigma_sub^decl(s)-i*pi*rho(s)",
            "advanced_component": "Sigma_A^decl(s)=Re Sigma_sub^decl(s)+i*pi*rho(s)=Sigma_R^*(s)",
            "keldysh_component": "Sigma_K^decl(s)=-2*i*pi*N(s)",
            "retarded_discontinuity": "Sigma_R^decl(s)-Sigma_A^decl(s)=-2*i*pi*rho(s)",
            "keldysh_fdt": "N(s)/rho(s)=coth(sqrt(s)/(2*T))",
            "bphz_subtraction": "Re Sigma_sub(s)=Re Sigma(s)-Re Sigma(s_*)-(s-s_*)*dRe Sigma/ds|s_*",
        },
        "ontology": {
            "C": "collective system-behaviour coordinate; not mass or charge",
            "Phi": "effective response variable; not temperature or metric",
            "R_gen": "derived physical/history trace; no independent state or backreaction",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "temperature_and_external_energy": "energy",
            "invariant_s_and_self_energy_components": "energy squared",
            "greater_lesser_spectral_and_noise_measures": "declared energy squared measure",
            "Phi": "effective response variable; SI temperature map not supplied",
        },
        "derivation_class": (
            "action-derived numerical composition of audited finite-temperature greater/lesser "
            "and principal-value channel responses with an explicit real-time component convention"
        ),
        "observable": (
            "retarded/advanced conjugacy, retarded discontinuity, Keldysh noise component, "
            "KMS/FDT relation, and quadrature residuals on a matched invariant grid"
        ),
        "data_role": (
            "ACTION_DERIVED_FINITE_T_DECLARED_CHANNEL_RETA_KELDYSH_1PI_NO_HOLDOUT"
        ),
        "included": {
            "declared_1_to_3_channel": True,
            "declared_2_to_2_channel": True,
            "retarded_component": True,
            "advanced_component": True,
            "keldysh_component": True,
            "keldysh_fdt": True,
            "bphz_subtraction_interface": True,
        },
        "excluded": {
            "complete_off_shell_finite_temperature_1pi_self_energy": True,
            "all_finite_temperature_sunset_channels": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current_heat_flux_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes the numerical retarded/advanced/Keldysh component interface "
            "for the declared action-derived 1<->3 and representative 2<->2 thermal "
            "channels. It does not close every off-shell thermal channel, select a "
            "unique physical renormalization anchor, emit a physical Kubo coefficient, "
            "close entropy/transport, map Phi to SI, calibrate alpha_Phi_K, validate "
            "TTG, or close Full Topic 13."
        ),
    }


__all__ = [
    "DECLARED_CHANNEL_RETA_KELDYSH_1PI_I0_THRESHOLD",
    "DECLARED_CHANNEL_RETA_KELDYSH_1PI_STATUS",
    "DECLARED_CHANNEL_RETA_KELDYSH_1PI_THRESHOLD",
    "DeclaredChannelRetardedAdvancedKeldysh1PIState",
    "DeclaredChannelRetardedAdvancedKeldyshPoint",
    "finite_temperature_declared_channel_reta_keldysh_1pi_contract",
    "finite_temperature_declared_channel_reta_keldysh_1pi_state",
]
