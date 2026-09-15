"""Vacuum retarded discontinuity interface for the O(2) sunset.

This lane derives the equal-mass three-body cut of the action-normalized
sunset at zero temperature and uses it in a twice-subtracted dispersion
relation.  The spacelike dispersion is compared with the regulated Euclidean
loop, and the above-threshold real part is evaluated with an analytic pole
subtraction.  The finite-temperature SK/KMS completion remains open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_action_1pi_sunset_tensor import (
    expected_sunset_tensor_prefactor,
)


RETARDED_1PI_SUNSET_STATUS = (
    "PASS_ACTION_DERIVED_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE"
)
RETARDED_1PI_SUNSET_CONVERGENCE_THRESHOLD = 2.0e-2
DEFAULT_RETARDED_PROBES = (0.25, 0.36, 0.64, 0.81, 1.00)


@dataclass(frozen=True)
class RetardedOnePISunsetState:
    """Vacuum sunset phase-space and dispersive continuation quantities."""

    mass_squared: float
    quartic_coupling: float
    species_count: int
    sunset_tensor_prefactor: float
    reference_euclidean_s: float
    spacelike_probe_euclidean_s: tuple[float, ...]
    three_body_threshold_s: float
    below_threshold_s: float
    timelike_probe_s: float
    spacelike_dispersion_response: tuple[float, ...]
    euclidean_reference_response: tuple[float, ...]
    euclidean_dispersion_match_residual: float
    phase_space_below_threshold: float
    phase_space_at_timelike_probe: float
    spectral_measure_at_timelike_probe: float
    retarded_spectral_density_at_timelike_probe: float
    retarded_imaginary_part_at_timelike_probe: float
    above_threshold_principal_value_real_part: float
    inner_phase_space_convergence_residual: float
    outer_dispersion_convergence_residual: float
    above_threshold_pv_inner_convergence_residual: float
    above_threshold_pv_outer_convergence_residual: float
    below_threshold_zero_witness: bool
    above_threshold_nonzero_witness: bool
    retarded_imaginary_sign_witness: bool
    vacuum_three_body_cut_completed: bool = True
    spacelike_dispersion_completed: bool = True
    retarded_i0_discontinuity_completed: bool = True
    above_threshold_principal_value_real_part_completed: bool = True
    full_1pi_retarded_self_energy_completed: bool = False
    finite_temperature_completion_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "ACTION_DERIVED_VACUUM_RETARDED_SUNSET_NO_HOLDOUT"


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _integer(value: int, name: str, minimum: int) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _ordered_positive(values: tuple[float, ...], name: str) -> tuple[float, ...]:
    if not values:
        raise ValueError(f"{name} must not be empty")
    result = tuple(_positive(value, f"{name} value") for value in values)
    if tuple(sorted(result)) != result:
        raise ValueError(f"{name} must be sorted")
    return result


def _relative(first: float, second: float) -> float:
    return abs(float(first) - float(second)) / max(abs(float(second)), 1.0e-300)


def three_body_phase_space(
    invariant_s: float,
    mass_squared: float,
    *,
    inner_order: int = 64,
) -> float:
    """Return integrated three-body phase space for three equal masses."""

    invariant_s = _positive(invariant_s, "invariant_s")
    mass_squared = _positive(mass_squared, "mass_squared")
    inner_order = _integer(inner_order, "inner_order", 16)
    threshold = 9.0 * mass_squared
    if invariant_s <= threshold:
        return 0.0
    mass = sqrt(mass_squared)
    lower = 4.0 * mass_squared
    upper = (sqrt(invariant_s) - mass) ** 2
    if upper <= lower:
        return 0.0
    nodes, weights = np.polynomial.legendre.leggauss(inner_order)
    pair_invariant = 0.5 * (upper - lower) * (nodes + 1.0) + lower
    scaled_weights = 0.5 * (upper - lower) * weights
    kallen_one = (
        invariant_s - pair_invariant - mass_squared
    ) ** 2 - 4.0 * pair_invariant * mass_squared
    kallen_two = pair_invariant * (pair_invariant - 4.0 * mass_squared)
    integrand = (
        np.sqrt(np.maximum(kallen_one, 0.0))
        * np.sqrt(np.maximum(kallen_two, 0.0))
        / (invariant_s * pair_invariant)
    )
    result = float(np.sum(scaled_weights * integrand) / (128.0 * pi**3))
    if not isfinite(result) or result < 0.0:
        raise FloatingPointError("three-body phase space is not finite and positive")
    return result


def vacuum_sunset_spectral_measure(
    invariant_s: float,
    mass_squared: float,
    quartic: float,
    *,
    species_count: int = 2,
    inner_order: int = 64,
) -> float:
    """Return the dispersive spectral measure used by the declared convention."""

    prefactor = expected_sunset_tensor_prefactor(
        quartic,
        species_count=species_count,
    )
    return prefactor * three_body_phase_space(
        invariant_s,
        mass_squared,
        inner_order=inner_order,
    ) / (2.0 * pi)


def _spacelike_dispersion(
    spacelike_s: float,
    reference_s: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    *,
    outer_order: int,
    inner_order: int,
    transform_scale: float,
) -> float:
    spacelike_s = _positive(spacelike_s, "spacelike_s")
    reference_s = _positive(reference_s, "reference_s")
    threshold = 9.0 * mass_squared
    nodes, weights = np.polynomial.legendre.leggauss(outer_order)
    unit_x = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    spectral_s = threshold + transform_scale * unit_x / (1.0 - unit_x)
    jacobian = transform_scale / (1.0 - unit_x) ** 2
    measures = np.array(
        [
            vacuum_sunset_spectral_measure(
                float(value),
                mass_squared,
                quartic,
                species_count=species_count,
                inner_order=inner_order,
            )
            for value in spectral_s
        ]
    )
    kernel = (spacelike_s - reference_s) ** 2 / (
        (spectral_s + spacelike_s) * (spectral_s + reference_s) ** 2
    )
    result = float(np.sum(scaled_weights * jacobian * measures * kernel))
    if not isfinite(result):
        raise FloatingPointError("spacelike sunset dispersion is not finite")
    return result


def _above_threshold_principal_value(
    timelike_s: float,
    reference_euclidean_s: float,
    mass_squared: float,
    quartic: float,
    species_count: int,
    *,
    outer_order: int,
    inner_order: int,
    transform_scale: float,
) -> float:
    """Evaluate the twice-subtracted retarded real part above threshold.

    The pole at ``sprime=timelike_s`` is removed analytically.  The remaining
    quadrature integrates ``rho(sprime)-rho(timelike_s)`` against the same
    twice-subtracted kernel used by the declared dispersion convention.
    """

    timelike_s = _positive(timelike_s, "timelike_s")
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    outer_order = _integer(outer_order, "outer_order", 32)
    inner_order = _integer(inner_order, "inner_order", 16)
    transform_scale = _positive(transform_scale, "transform_scale")
    threshold = 9.0 * mass_squared
    if timelike_s <= threshold:
        raise ValueError("timelike_s must be above the three-body threshold")

    reference_minkowski_s = -reference_euclidean_s
    nodes, weights = np.polynomial.legendre.leggauss(outer_order)
    unit_x = 0.5 * (nodes + 1.0)
    scaled_weights = 0.5 * weights
    spectral_s = threshold + transform_scale * unit_x / (1.0 - unit_x)
    jacobian = transform_scale / (1.0 - unit_x) ** 2
    measures = np.array(
        [
            vacuum_sunset_spectral_measure(
                float(value),
                mass_squared,
                quartic,
                species_count=species_count,
                inner_order=inner_order,
            )
            for value in spectral_s
        ]
    )
    probe_measure = vacuum_sunset_spectral_measure(
        timelike_s,
        mass_squared,
        quartic,
        species_count=species_count,
        inner_order=inner_order,
    )
    subtraction_kernel = (
        1.0 / (spectral_s - timelike_s)
        - 1.0 / (spectral_s - reference_minkowski_s)
        - (timelike_s - reference_minkowski_s)
        / (spectral_s - reference_minkowski_s) ** 2
    )
    regularized_integral = float(
        np.sum(
            scaled_weights
            * jacobian
            * (measures - probe_measure)
            * subtraction_kernel
        )
    )
    analytic_pole_integral = log(
        (threshold - reference_minkowski_s)
        / abs(threshold - timelike_s)
    ) - (timelike_s - reference_minkowski_s) / (
        threshold - reference_minkowski_s
    )
    result = regularized_integral + probe_measure * analytic_pole_integral
    if not isfinite(result):
        raise FloatingPointError(
            "above-threshold principal-value sunset is not finite"
        )
    return result


def retarded_vacuum_sunset_state(
    mass_squared: float,
    quartic: float,
    euclidean_reference_response: tuple[float, ...],
    *,
    species_count: int = 2,
    reference_euclidean_s: float = 0.5,
    spacelike_probe_euclidean_s: tuple[float, ...] = DEFAULT_RETARDED_PROBES,
    below_threshold_s: float | None = None,
    timelike_probe_s: float | None = None,
    inner_order: int = 64,
    refined_inner_order: int | None = None,
    outer_order: int = 96,
    refined_outer_order: int | None = None,
    transform_scale: float | None = None,
) -> RetardedOnePISunsetState:
    """Build the vacuum retarded discontinuity and spacelike dispersion lane."""

    mass_squared = _positive(mass_squared, "mass_squared")
    quartic = _positive(quartic, "quartic")
    species_count = _integer(species_count, "species_count", 1)
    reference_euclidean_s = _positive(
        reference_euclidean_s,
        "reference_euclidean_s",
    )
    probes = _ordered_positive(
        spacelike_probe_euclidean_s,
        "spacelike_probe_euclidean_s",
    )
    if len(euclidean_reference_response) != len(probes):
        raise ValueError("euclidean_reference_response length must match probes")
    inner_order = _integer(inner_order, "inner_order", 16)
    if refined_inner_order is None:
        refined_inner_order = inner_order + 16
    refined_inner_order = _integer(
        refined_inner_order,
        "refined_inner_order",
        inner_order + 1,
    )
    outer_order = _integer(outer_order, "outer_order", 32)
    if refined_outer_order is None:
        refined_outer_order = outer_order + 32
    refined_outer_order = _integer(
        refined_outer_order,
        "refined_outer_order",
        outer_order + 1,
    )
    threshold = 9.0 * mass_squared
    if below_threshold_s is None:
        below_threshold_s = 8.0 * mass_squared
    below_threshold_s = _positive(below_threshold_s, "below_threshold_s")
    if below_threshold_s >= threshold:
        raise ValueError("below_threshold_s must be below the three-body threshold")
    if timelike_probe_s is None:
        timelike_probe_s = 10.0 * mass_squared
    timelike_probe_s = _positive(timelike_probe_s, "timelike_probe_s")
    if timelike_probe_s <= threshold:
        raise ValueError("timelike_probe_s must be above the three-body threshold")
    if transform_scale is None:
        transform_scale = threshold / 3.0
    transform_scale = _positive(transform_scale, "transform_scale")

    spacelike_response = tuple(
        _spacelike_dispersion(
            probe,
            reference_euclidean_s,
            mass_squared,
            quartic,
            species_count,
            outer_order=outer_order,
            inner_order=inner_order,
            transform_scale=transform_scale,
        )
        for probe in probes
    )
    refined_response = tuple(
        _spacelike_dispersion(
            probe,
            reference_euclidean_s,
            mass_squared,
            quartic,
            species_count,
            outer_order=refined_outer_order,
            inner_order=refined_inner_order,
            transform_scale=transform_scale,
        )
        for probe in probes
    )
    inner_phase = three_body_phase_space(
        timelike_probe_s,
        mass_squared,
        inner_order=inner_order,
    )
    refined_inner_phase = three_body_phase_space(
        timelike_probe_s,
        mass_squared,
        inner_order=refined_inner_order,
    )
    measure = vacuum_sunset_spectral_measure(
        timelike_probe_s,
        mass_squared,
        quartic,
        species_count=species_count,
        inner_order=refined_inner_order,
    )
    physical_spectral_density = pi * measure
    imaginary_part = -physical_spectral_density
    euclidean_match = max(
        _relative(current, expected)
        for current, expected in zip(spacelike_response, euclidean_reference_response)
    )
    outer_convergence = max(
        _relative(current, refined)
        for current, refined in zip(spacelike_response, refined_response)
    )
    inner_convergence = _relative(inner_phase, refined_inner_phase)
    pv_real = _above_threshold_principal_value(
        timelike_probe_s,
        reference_euclidean_s,
        mass_squared,
        quartic,
        species_count,
        outer_order=outer_order,
        inner_order=inner_order,
        transform_scale=transform_scale,
    )
    pv_refined = _above_threshold_principal_value(
        timelike_probe_s,
        reference_euclidean_s,
        mass_squared,
        quartic,
        species_count,
        outer_order=refined_outer_order,
        inner_order=refined_inner_order,
        transform_scale=transform_scale,
    )
    pv_inner_refined_outer = _above_threshold_principal_value(
        timelike_probe_s,
        reference_euclidean_s,
        mass_squared,
        quartic,
        species_count,
        outer_order=refined_outer_order,
        inner_order=inner_order,
        transform_scale=transform_scale,
    )
    pv_outer_refined_inner = _above_threshold_principal_value(
        timelike_probe_s,
        reference_euclidean_s,
        mass_squared,
        quartic,
        species_count,
        outer_order=outer_order,
        inner_order=refined_inner_order,
        transform_scale=transform_scale,
    )
    pv_inner_convergence = _relative(pv_inner_refined_outer, pv_refined)
    pv_outer_convergence = _relative(pv_outer_refined_inner, pv_refined)
    values = (
        mass_squared,
        quartic,
        threshold,
        below_threshold_s,
        timelike_probe_s,
        *spacelike_response,
        *euclidean_reference_response,
        euclidean_match,
        inner_phase,
        refined_inner_phase,
        measure,
        physical_spectral_density,
        imaginary_part,
        pv_real,
        pv_refined,
        inner_convergence,
        outer_convergence,
        pv_inner_convergence,
        pv_outer_convergence,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("retarded sunset state is not finite")
    below_phase = three_body_phase_space(
        below_threshold_s,
        mass_squared,
        inner_order=refined_inner_order,
    )
    return RetardedOnePISunsetState(
        mass_squared=mass_squared,
        quartic_coupling=quartic,
        species_count=species_count,
        sunset_tensor_prefactor=expected_sunset_tensor_prefactor(
            quartic,
            species_count=species_count,
        ),
        reference_euclidean_s=reference_euclidean_s,
        spacelike_probe_euclidean_s=probes,
        three_body_threshold_s=threshold,
        below_threshold_s=below_threshold_s,
        timelike_probe_s=timelike_probe_s,
        spacelike_dispersion_response=spacelike_response,
        euclidean_reference_response=tuple(
            float(value) for value in euclidean_reference_response
        ),
        euclidean_dispersion_match_residual=float(euclidean_match),
        phase_space_below_threshold=float(below_phase),
        phase_space_at_timelike_probe=float(refined_inner_phase),
        spectral_measure_at_timelike_probe=float(measure),
        retarded_spectral_density_at_timelike_probe=float(
            physical_spectral_density
        ),
        retarded_imaginary_part_at_timelike_probe=float(imaginary_part),
        above_threshold_principal_value_real_part=float(pv_real),
        inner_phase_space_convergence_residual=float(inner_convergence),
        outer_dispersion_convergence_residual=float(outer_convergence),
        above_threshold_pv_inner_convergence_residual=float(pv_inner_convergence),
        above_threshold_pv_outer_convergence_residual=float(pv_outer_convergence),
        below_threshold_zero_witness=below_phase <= 1.0e-30,
        above_threshold_nonzero_witness=refined_inner_phase > 0.0,
        retarded_imaginary_sign_witness=imaginary_part < 0.0,
    )


def retarded_vacuum_sunset_contract() -> dict[str, Any]:
    """Return the vacuum cut, dispersion convention, and open boundaries."""

    return {
        "status": RETARDED_1PI_SUNSET_STATUS,
        "equations": {
            "three_body_threshold": "s_th=9*m^2",
            "three_body_phase_space": (
                "Phi_3(s)=1/(128*pi^3*s)*integral_{4m^2}^{(sqrt(s)-m)^2} "
                "ds12*sqrt(lambda(s,s12,m^2))*sqrt(lambda(s12,m^2,m^2))/s12"
            ),
            "dispersive_measure": "rho_disp(s)=2*(N+2)*lambda^2*Phi_3(s)/(2*pi)",
            "retarded_dispersion": "Sigma_R(s)=integral_{s_th}^infty dsprime*rho_disp(sprime)/(sprime-s+i0)",
            "spacelike_subtraction": (
                "Sigma_E,R(sE)=integral dsprime*rho_disp(sprime)*"
                "(sE-s_*)^2/[(sprime+sE)*(sprime+s_*)^2]"
            ),
            "retarded_imaginary_part": "Im Sigma_R(s)=-pi*rho_disp(s)=-rho_ret(s)",
            "retarded_spectral_density": "rho_ret(s)=pi*rho_disp(s)",
            "above_threshold_pv_subtraction": (
                "PV Sigma_R^sub(s)=integral_{s_th}^infty dsprime*"
                "[rho_disp(dsprime)-rho_disp(s)]*K_sub(dsprime) + "
                "rho_disp(s)*A(s;s_th,r)"
            ),
            "above_threshold_pole_subtraction_kernel": (
                "K_sub(dsprime)=1/(dsprime-s)-1/(dsprime-r)-"
                "(s-r)/(dsprime-r)^2, r=-s_*"
            ),
            "analytic_pole_integral": (
                "A=ln((s_th-r)/abs(s_th-s))-(s-r)/(s_th-r)"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural vacuum 3+1",
            "mass_squared_and_invariant_s": "energy squared",
            "three_body_phase_space": "energy squared",
            "rho_disp_and_rho_ret": "energy squared",
            "retarded_self_energy": "energy squared",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived O(2) sunset tensor prefactor, equal-mass three-body "
            "phase-space cut, declared retarded i0 discontinuity, twice-subtracted "
            "dispersion, and analytic above-threshold pole subtraction"
        ),
        "observable": (
            "three-body threshold, below/above-threshold spectral support, negative retarded "
            "imaginary sign, spacelike dispersion, Euclidean-loop matching, and "
            "above-threshold principal-value real part"
        ),
        "data_role": "ACTION_DERIVED_VACUUM_RETARDED_SUNSET_NO_HOLDOUT",
        "included": {
            "vacuum_three_body_cut": True,
            "retarded_i0_discontinuity": True,
            "spacelike_subtracted_dispersion": True,
            "euclidean_dispersion_match": True,
            "above_threshold_principal_value_real_part": True,
        },
        "excluded": {
            "full_above_threshold_retarded_1pi_completion": True,
            "full_retarded_1pi_self_energy": True,
            "finite_temperature_self_energy": True,
            "microscopic_sk_kms_match": True,
            "unique_physical_renormalization": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the vacuum three-body cut, retarded imaginary/discontinuity "
            "interface, above-threshold principal-value real-part interface, and spacelike "
            "dispersion match for the action-derived O(2) sunset. It does not close the full "
            "finite-temperature retarded 1PI self-energy, finite-temperature SK/KMS, unique physical renormalization, "
            "transport, entropy, SI Phi mapping, alpha_Phi_K, TTG, external validation, or Full Topic 13."
        ),
    }


__all__ = [
    "DEFAULT_RETARDED_PROBES",
    "RETARDED_1PI_SUNSET_CONVERGENCE_THRESHOLD",
    "RETARDED_1PI_SUNSET_STATUS",
    "RetardedOnePISunsetState",
    "retarded_vacuum_sunset_contract",
    "retarded_vacuum_sunset_state",
    "three_body_phase_space",
    "vacuum_sunset_spectral_measure",
]
