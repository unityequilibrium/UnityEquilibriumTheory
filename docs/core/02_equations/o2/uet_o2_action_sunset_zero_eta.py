"""Distributional zero-eta sunset self-energy interface for Topic 13.

This branch keeps the action-normalized O(2) sunset cut from
``uet_o2_action_sunset_1pi_spectral`` and replaces the finite ``eta`` pole
smearing with the declared retarded distribution
``1/(x+i0)=PV(1/x)-i*pi*delta(x)``.  The real part uses an analytic
principal-value pole subtraction.  A BPHZ-like condition at invariant
``s_* = 0`` removes the constant and linear-in-s counterterms:
``Sigma_R(0)=0`` and ``d Sigma_R/ds(0)=0``.

The result is a physical-limit and subtraction interface for the declared
action cut.  It is not a proof of a unique microscopic renormalization, a
complete off-shell 1PI action calculation, a physical Kubo coefficient, or
an SI Phi-to-temperature calibration.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_action_sunset_1pi_spectral import (
    action_matrix_element_squared,
    _cut_rates,
)
from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


ZERO_ETA_SUNSET_STATUS = (
    "PASS_ACTION_MATCHED_O2_SUNSET_ZERO_ETA_SUBTRACTION_INTERFACE_LANE"
)
ZERO_ETA_CONVERGENCE_THRESHOLD = 2.0e-2
DEFAULT_ZERO_ETA_PROBES = (0.60, 0.76, 0.90, 1.05)


@dataclass(frozen=True)
class ZeroEtaSunsetState:
    """Distributional zero-eta and subtraction-interface quantities."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    external_species: int
    quartic_coupling: float
    action_matrix_element_squared: float
    reference_invariant_s: float
    frequency_lower: float
    frequency_upper: float
    radial_cutoff: float
    radial_order: int
    center_of_mass_order: int
    frequency_order: int
    probe_energies: tuple[float, ...]
    greater_cut: tuple[float, ...]
    lesser_cut: tuple[float, ...]
    spectral_density: tuple[float, ...]
    noise_density: tuple[float, ...]
    kms_ratios: tuple[float, ...]
    kms_target_ratios: tuple[float, ...]
    kms_max_residual: float
    physical_real_response: tuple[float, ...]
    physical_imaginary_response: tuple[float, ...]
    imaginary_distribution_match_residual: float
    subtraction_at_reference_residual: float
    subtraction_derivative_at_reference_residual: float
    principal_value_convergence_residual: float
    convergence_threshold: float
    convergence_passed: bool
    action_vertex_normalization_completed: bool = True
    continuum_cut_completed: bool = True
    zero_eta_distributional_interface_completed: bool = True
    declared_bphz_subtraction_interface_completed: bool = True
    full_1pi_retarded_self_energy_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_MATCHED_INTERNAL_O2_SUNSET_ZERO_ETA_SUBTRACTION_NO_HOLDOUT"
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


def _order(value: int, name: str, minimum: int = 16) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _bose(energy: float, temperature: float) -> float:
    argument = _positive(energy / temperature, "beta energy")
    return exp(-argument) if argument > 50.0 else 1.0 / expm1(argument)


def _scaled_change(first: complex, second: complex, scale: float = 1.0e-12) -> float:
    return abs(first - second) / max(abs(second), scale)


def _quadrature(order: int, lower: float, upper: float) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return (
        0.5 * (upper - lower) * (nodes + 1.0) + lower,
        0.5 * (upper - lower) * weights,
    )


def _spectral_density(
    frequency: float,
    temperature: float,
    mass: float,
    quartic: float,
    external_species: int,
    radial_order: int,
    center_of_mass_order: int,
    cutoff_factor: float,
) -> tuple[float, float, float, float]:
    greater, lesser = _cut_rates(
        frequency,
        temperature,
        mass,
        quartic,
        external_species,
        radial_order,
        center_of_mass_order,
        cutoff_factor,
    )
    spectral = 2.0 * frequency * (greater - lesser)
    noise = 2.0 * frequency * (greater + lesser)
    return float(greater), float(lesser), float(spectral), float(noise)


def _pv_real_subtracted_response(
    frequency: float,
    temperature: float,
    mass: float,
    quartic: float,
    external_species: int,
    radial_order: int,
    center_of_mass_order: int,
    frequency_order: int,
    cutoff_factor: float,
    frequency_lower: float,
    frequency_upper: float,
) -> float:
    """Evaluate the real twice-subtracted response with an analytic PV."""

    omega = _positive(frequency, "frequency")
    invariant_s = omega * omega
    nodes, weights = np.polynomial.legendre.leggauss(frequency_order)

    def integrate_regular(lower: float, upper: float, pole_term: bool) -> float:
        if upper - lower <= 1.0e-14:
            return 0.0
        value = 0.0
        for node, weight in zip(nodes, weights):
            nu = 0.5 * (upper - lower) * (float(node) + 1.0) + lower
            rho = _spectral_density(
                nu,
                temperature,
                mass,
                quartic,
                external_species,
                radial_order,
                center_of_mass_order,
                cutoff_factor,
            )[2]
            if pole_term:
                regular = (rho - pole_density) / (omega - nu)
            else:
                regular = rho / (omega - nu)
            regular += rho * (
                -1.0 / (omega + nu) + 2.0 / nu + 2.0 * invariant_s / (nu**3)
            )
            value += 0.5 * (upper - lower) * float(weight) * regular
        return value

    if frequency_lower < omega < frequency_upper:
        pole_density = _spectral_density(
            omega,
            temperature,
            mass,
            quartic,
            external_species,
            radial_order,
            center_of_mass_order,
            cutoff_factor,
        )[2]
        pole_log = pole_density * log(
            (omega - frequency_lower) / (frequency_upper - omega)
        )
        regular_integral = integrate_regular(frequency_lower, omega, True)
        regular_integral += integrate_regular(omega, frequency_upper, True)
        return float((pole_log + regular_integral) / pi)

    return float(integrate_regular(frequency_lower, frequency_upper, False) / pi)


def _physical_response(
    frequency: float,
    temperature: float,
    mass: float,
    quartic: float,
    external_species: int,
    radial_order: int,
    center_of_mass_order: int,
    frequency_order: int,
    cutoff_factor: float,
    frequency_lower: float,
    frequency_upper: float,
) -> tuple[float, float, float]:
    _, _, spectral, _ = _spectral_density(
        frequency,
        temperature,
        mass,
        quartic,
        external_species,
        radial_order,
        center_of_mass_order,
        cutoff_factor,
    )
    real = _pv_real_subtracted_response(
        frequency,
        temperature,
        mass,
        quartic,
        external_species,
        radial_order,
        center_of_mass_order,
        frequency_order,
        cutoff_factor,
        frequency_lower,
        frequency_upper,
    )
    return float(real), float(-spectral), float(spectral)


def zero_eta_sunset_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    external_species: int = 0,
    radial_order: int = 24,
    center_of_mass_order: int = 24,
    frequency_order: int = 16,
    cutoff_factor: float = 24.0,
    frequency_cutoff_factor: float = 6.0,
    probe_energies: tuple[float, ...] = DEFAULT_ZERO_ETA_PROBES,
) -> ZeroEtaSunsetState:
    """Build the action-matched distributional zero-eta sunset interface."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) > 1.0e-14:
        raise ValueError("zero-eta sunset lane locks chemical_potential=0")
    space_response = _finite(space_response, "space_response")
    if external_species not in (0, 1):
        raise ValueError("external_species must be 0 or 1")
    radial_order = _order(radial_order, "radial_order")
    center_of_mass_order = _order(center_of_mass_order, "center_of_mass_order")
    frequency_order = _order(frequency_order, "frequency_order", minimum=8)
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    frequency_cutoff_factor = _positive(
        frequency_cutoff_factor, "frequency_cutoff_factor"
    )
    if not probe_energies:
        raise ValueError("probe_energies must not be empty")
    probes = tuple(_positive(value, "probe_energy") for value in probe_energies)
    if tuple(sorted(probes)) != probes:
        raise ValueError("probe_energies must be sorted")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    mass_sq = effective_mass_sq(space_response, config.eos)
    if mass_sq <= 0.0:
        raise ValueError("zero-eta sunset lane requires positive mass squared")
    mass = sqrt(mass_sq)
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    frequency_lower = max(0.25 * mass, 1.0e-6)
    frequency_upper = max(
        frequency_cutoff_factor * temperature,
        frequency_cutoff_factor * mass,
        1.0,
    )
    cuts = tuple(
        _spectral_density(
            omega,
            temperature,
            mass,
            quartic,
            external_species,
            radial_order,
            center_of_mass_order,
            cutoff_factor,
        )
        for omega in probes
    )
    greater = tuple(item[0] for item in cuts)
    lesser = tuple(item[1] for item in cuts)
    spectral = tuple(item[2] for item in cuts)
    noise = tuple(item[3] for item in cuts)
    kms_ratios = tuple(g / l for g, l in zip(greater, lesser))
    kms_targets = tuple(exp(omega / temperature) for omega in probes)
    kms_residual = max(
        abs(value - target) / max(abs(target), 1.0e-300)
        for value, target in zip(kms_ratios, kms_targets)
    )
    responses = tuple(
        _physical_response(
            omega,
            temperature,
            mass,
            quartic,
            external_species,
            radial_order,
            center_of_mass_order,
            frequency_order,
            cutoff_factor,
            frequency_lower,
            frequency_upper,
        )
        for omega in probes
    )
    refined_responses = tuple(
        _physical_response(
            omega,
            temperature,
            mass,
            quartic,
            external_species,
            radial_order + 8,
            center_of_mass_order + 8,
            frequency_order + 8,
            cutoff_factor + 4.0,
            frequency_lower,
            frequency_upper,
        )
        for omega in probes
    )
    convergence = max(
        _scaled_change(
            complex(real, imaginary),
            complex(refined_real, refined_imaginary),
            scale=max(abs(spectral_value), 1.0e-12),
        )
        for (real, imaginary, _), (refined_real, refined_imaginary, _), spectral_value in zip(
            responses, refined_responses, spectral
        )
    )
    imaginary_residual = max(
        abs(imaginary + spectral_value)
        for (_, imaginary, _), spectral_value in zip(responses, spectral)
    )
    values = (
        *greater,
        *lesser,
        *spectral,
        *noise,
        *kms_ratios,
        *kms_targets,
        *(value for response in responses for value in response),
        convergence,
        imaginary_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("zero-eta sunset state is not finite")
    return ZeroEtaSunsetState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=mass,
        external_species=external_species,
        quartic_coupling=quartic,
        action_matrix_element_squared=action_matrix_element_squared(
            quartic, external_species
        ),
        reference_invariant_s=0.0,
        frequency_lower=frequency_lower,
        frequency_upper=frequency_upper,
        radial_cutoff=max(cutoff_factor * temperature, cutoff_factor * mass, 1.0),
        radial_order=radial_order,
        center_of_mass_order=center_of_mass_order,
        frequency_order=frequency_order,
        probe_energies=probes,
        greater_cut=greater,
        lesser_cut=lesser,
        spectral_density=spectral,
        noise_density=noise,
        kms_ratios=kms_ratios,
        kms_target_ratios=kms_targets,
        kms_max_residual=float(kms_residual),
        physical_real_response=tuple(value[0] for value in responses),
        physical_imaginary_response=tuple(value[1] for value in responses),
        imaginary_distribution_match_residual=float(imaginary_residual),
        subtraction_at_reference_residual=0.0,
        subtraction_derivative_at_reference_residual=0.0,
        principal_value_convergence_residual=float(convergence),
        convergence_threshold=ZERO_ETA_CONVERGENCE_THRESHOLD,
        convergence_passed=convergence <= ZERO_ETA_CONVERGENCE_THRESHOLD,
    )


def zero_eta_sunset_contract() -> dict[str, Any]:
    """Return equations, units, and the zero-eta claim boundary."""

    return {
        "status": ZERO_ETA_SUNSET_STATUS,
        "equations": {
            "interaction_potential": "W_int=lambda*(chi_a chi_a)^2/4",
            "action_vertex": "V_abcd=2*lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)",
            "action_cut": "rho_Sigma(omega)=2*omega*(Gamma_>(omega)-Gamma_<(omega))",
            "retarded_distribution": "1/(x+i0)=PV(1/x)-i*pi*delta(x)",
            "dispersion_kernel": "K(s,nu)=1/(sqrt(s)-nu+i0)-1/(sqrt(s)+nu+i0)",
            "bphz_subtraction": "Sigma_R,sub2(s)=integral dnu/pi*rho(nu)*[K(s,nu)-K(0,nu)-s*dK/ds(0,nu)]",
            "reference_conditions": "Sigma_R,sub2(0)=0; dSigma_R,sub2/ds(0)=0",
            "reference_kernel": "K(0,nu)=-2/nu; dK/ds(0,nu)=-2/nu^3",
            "imaginary_part": "Im Sigma_R,sub2(omega)=-rho_Sigma(omega)",
            "kms": "Gamma_>(omega)/Gamma_<(omega)=exp(beta*omega)",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_mass_momentum_energy": "energy",
            "quartic_coupling": "dimensionless",
            "cut_rate": "energy",
            "spectral_density": "energy squared in declared cut normalization",
            "real_imaginary_self_energy": "energy squared in declared normalized lane",
            "reference_invariant_s": "energy squared",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-matched O(2) contact vertex, continuum thermal sunset cut, "
            "distributional retarded prescription, analytic principal-value pole "
            "subtraction, and declared BPHZ-like invariant subtraction"
        ),
        "observable": (
            "action-normalized greater/lesser cut, KMS ratio, spectral density, "
            "distributional imaginary part, principal-value real response, and "
            "quadrature convergence"
        ),
        "data_role": "ACTION_MATCHED_INTERNAL_ZERO_ETA_SUBTRACTION_NO_HOLDOUT",
        "included": {
            "action_vertex_normalization": True,
            "continuum_sunset_cut": True,
            "zero_eta_distributional_retarded_interface": True,
            "analytic_principal_value": True,
            "declared_bphz_subtraction": True,
            "kms_and_spectral_sign": True,
        },
        "excluded": {
            "full_microscopic_1PI_action_derivation": True,
            "unique_physical_renormalization": True,
            "microscopic_SK_KMS_match": True,
            "physical_Kubo_coefficient": True,
            "covariant_entropy_current": True,
            "heat_flux_dissipative_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only the distributional zero-eta and declared subtraction "
            "interface for the action-normalized O(2) sunset cut. It does not close "
            "a unique microscopic renormalization, a complete off-shell 1PI action "
            "calculation, microscopic SK/KMS matching, physical transport, entropy "
            "current, SI Phi mapping, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "DEFAULT_ZERO_ETA_PROBES",
    "ZERO_ETA_CONVERGENCE_THRESHOLD",
    "ZERO_ETA_SUNSET_STATUS",
    "ZeroEtaSunsetState",
    "zero_eta_sunset_contract",
    "zero_eta_sunset_state",
]
