"""Once-subtracted retarded dispersion interface for Topic 13.

The continuum sunset-cut lane supplies an on-shell, action-derived positive
cut.  This module extends that same declared elastic branch to a positive
external rest energy and builds a finite-regulator retarded dispersion
interface.  Composite frequency quadrature resolves the near-pole regions
around the target and subtraction energies.

The extension is deliberately not called a full 1PI self-energy.  Its
off-shell flux normalization is inherited from the declared elastic branch;
the unique microscopic regulator, real-part renormalization, and analytic
continuation of the full action remain open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


SUNSET_DISPERSION_STATUS = (
    "PASS_ACTION_DERIVED_SUBTRACTED_SUNSET_DISPERSION_INTERFACE_LANE"
)
DISPERSION_CONVERGENCE_THRESHOLD = 1.0e-2
DEFAULT_PROBE_ENERGIES = (0.60, 0.76, 0.90, 1.05)


@dataclass(frozen=True)
class SunsetDispersionInterfaceState:
    """Formal neutral retarded dispersion quantities at p=(omega,0)."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    reference_energy: float
    regulator_eta: float
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
    retarded_raw_real: tuple[float, ...]
    retarded_raw_imaginary: tuple[float, ...]
    subtracted_real_response: tuple[float, ...]
    subtracted_imaginary_response: tuple[float, ...]
    reference_subtraction_residual: float
    retarded_imaginary_sign_witness: bool
    spectral_positivity_witness: bool
    dispersion_convergence_residual: float
    convergence_threshold: float
    convergence_passed: bool
    continuum_dispersion_interface_completed: bool = True
    real_part_subtraction_interface_completed: bool = True
    off_shell_matching_interface_completed: bool = True
    continuum_sunset_self_energy_completed: bool = False
    full_1pi_retarded_self_energy_completed: bool = False
    real_part_subtraction_completed: bool = False
    off_shell_matching_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    physical_retarded_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_INTERNAL_FORMAL_SUBTRACTED_DISPERSION_NO_HOLDOUT"
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


def _order(value: int, name: str, minimum: int = 24) -> int:
    if isinstance(value, bool) or int(value) != value or int(value) < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _bose(energy: float, temperature: float) -> float:
    argument = _positive(energy / temperature, "beta energy")
    return exp(-argument) if argument > 50.0 else 1.0 / expm1(argument)


def _relative_change(first: complex, second: complex) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def _cut_rates(
    external_energy: float,
    temperature: float,
    mass: float,
    quartic: float,
    radial_order: int,
    center_of_mass_order: int,
    cutoff_factor: float,
) -> tuple[float, float]:
    """Evaluate the declared off-shell extension of the elastic cut."""

    omega = _positive(external_energy, "external_energy")
    cutoff = max(cutoff_factor * temperature, cutoff_factor * mass, 1.0)
    required_bath_energy = (3.0 * mass * mass - omega * omega) / (2.0 * omega)
    if required_bath_energy > mass:
        minimum_momentum = sqrt(
            max(required_bath_energy * required_bath_energy - mass * mass, 0.0)
        )
    else:
        minimum_momentum = 0.0
    if minimum_momentum >= cutoff:
        return 0.0, 0.0

    nodes, weights = np.polynomial.legendre.leggauss(radial_order)
    momenta = 0.5 * (cutoff - minimum_momentum) * (nodes + 1.0) + minimum_momentum
    radial_weights = 0.5 * (cutoff - minimum_momentum) * weights
    angle_nodes, angle_weights = np.polynomial.legendre.leggauss(
        center_of_mass_order
    )
    greater = 0.0
    lesser = 0.0
    for momentum, radial_weight in zip(momenta, radial_weights):
        k = float(momentum)
        bath_energy = sqrt(k * k + mass * mass)
        invariant_s = (
            omega * omega + mass * mass + 2.0 * omega * bath_energy
        )
        if invariant_s < 4.0 * mass * mass:
            continue
        root_s = sqrt(invariant_s)
        energy_star = 0.5 * root_s
        momentum_star = sqrt(max(0.25 * invariant_s - mass * mass, 0.0))
        beta_cm = k / (omega + bath_energy)
        gamma_cm = (omega + bath_energy) / root_s
        final_greater = 0.0
        final_lesser = 0.0
        for cosine, angle_weight in zip(angle_nodes, angle_weights):
            energy_three = gamma_cm * (
                energy_star + beta_cm * momentum_star * float(cosine)
            )
            energy_four = gamma_cm * (
                energy_star - beta_cm * momentum_star * float(cosine)
            )
            occupation_three = _bose(energy_three, temperature)
            occupation_four = _bose(energy_four, temperature)
            final_greater += (
                0.5
                * float(angle_weight)
                * (1.0 + occupation_three)
                * (1.0 + occupation_four)
            )
            final_lesser += (
                0.5
                * float(angle_weight)
                * occupation_three
                * occupation_four
            )
        measure = float(radial_weight) * k * k / (2.0 * pi * pi)
        relative_velocity = k / bath_energy
        cross_section = quartic * quartic / (16.0 * pi * invariant_s)
        bath_occupation = _bose(bath_energy, temperature)
        greater += (
            measure
            * bath_occupation
            * relative_velocity
            * cross_section
            * final_greater
        )
        lesser += (
            measure
            * (1.0 + bath_occupation)
            * relative_velocity
            * cross_section
            * final_lesser
        )
    return float(greater), float(lesser)


def _frequency_breakpoints(
    lower: float,
    upper: float,
    omega: float,
    reference: float,
) -> tuple[float, ...]:
    points = [lower, upper, omega, reference]
    for center in (omega, reference):
        points.extend(
            (
                center - 0.25,
                center + 0.25,
                center - 0.06,
                center + 0.06,
            )
        )
    return tuple(sorted({max(lower, min(upper, point)) for point in points}))


def _retarded_pair(
    omega: float,
    reference: float,
    temperature: float,
    mass: float,
    quartic: float,
    radial_order: int,
    center_of_mass_order: int,
    frequency_order: int,
    cutoff_factor: float,
    frequency_lower: float,
    frequency_upper: float,
    regulator_eta: float,
) -> tuple[complex, complex]:
    """Return raw and reference-subtracted retarded dispersion responses."""

    raw = 0.0j
    reference_raw = 0.0j
    breakpoints = _frequency_breakpoints(
        frequency_lower, frequency_upper, omega, reference
    )
    for left, right in zip(breakpoints[:-1], breakpoints[1:]):
        if right - left <= 1.0e-14:
            continue
        nodes, weights = np.polynomial.legendre.leggauss(frequency_order)
        frequencies = 0.5 * (right - left) * (nodes + 1.0) + left
        frequency_weights = 0.5 * (right - left) * weights
        for frequency, frequency_weight in zip(frequencies, frequency_weights):
            nu = float(frequency)
            greater, lesser = _cut_rates(
                nu,
                temperature,
                mass,
                quartic,
                radial_order,
                center_of_mass_order,
                cutoff_factor,
            )
            spectral = 2.0 * nu * (greater - lesser)
            kernel = 1.0 / (omega - nu + 1.0j * regulator_eta) - 1.0 / (
                omega + nu + 1.0j * regulator_eta
            )
            reference_kernel = 1.0 / (
                reference - nu + 1.0j * regulator_eta
            ) - 1.0 / (reference + nu + 1.0j * regulator_eta)
            weight = float(frequency_weight) * spectral / pi
            raw += weight * kernel
            reference_raw += weight * reference_kernel
    return complex(raw), complex(raw - reference_raw)


def sunset_dispersion_interface_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 48,
    center_of_mass_order: int = 40,
    frequency_order: int = 12,
    cutoff_factor: float = 24.0,
    frequency_cutoff_factor: float = 6.0,
    regulator_eta: float = 0.025,
    probe_energies: tuple[float, ...] = DEFAULT_PROBE_ENERGIES,
) -> SunsetDispersionInterfaceState:
    """Build a neutral, once-subtracted formal retarded dispersion interface."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) > 1.0e-14:
        raise ValueError("sunset dispersion interface locks chemical_potential=0")
    space_response = _finite(space_response, "space_response")
    radial_order = _order(radial_order, "radial_order")
    center_of_mass_order = _order(center_of_mass_order, "center_of_mass_order")
    frequency_order = _order(frequency_order, "frequency_order", minimum=8)
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    frequency_cutoff_factor = _positive(
        frequency_cutoff_factor, "frequency_cutoff_factor"
    )
    regulator_eta = _positive(regulator_eta, "regulator_eta")
    if not probe_energies:
        raise ValueError("probe_energies must not be empty")
    probes = tuple(_positive(value, "probe_energy") for value in probe_energies)
    if tuple(sorted(probes)) != probes:
        raise ValueError("probe_energies must be sorted")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    mass_sq = effective_mass_sq(space_response, config.eos)
    if mass_sq <= 0.0:
        raise ValueError("sunset dispersion interface requires positive mass squared")
    mass = sqrt(mass_sq)
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    frequency_lower = max(0.25 * mass, 1.0e-6)
    frequency_upper = max(
        frequency_cutoff_factor * temperature,
        frequency_cutoff_factor * mass,
        1.0,
    )

    cuts = tuple(
        _cut_rates(
            energy,
            temperature,
            mass,
            quartic,
            radial_order,
            center_of_mass_order,
            cutoff_factor,
        )
        for energy in probes
    )
    greater = tuple(pair[0] for pair in cuts)
    lesser = tuple(pair[1] for pair in cuts)
    spectral = tuple(
        2.0 * energy * (g_value - l_value)
        for energy, g_value, l_value in zip(probes, greater, lesser)
    )
    noise = tuple(
        2.0 * energy * (g_value + l_value)
        for energy, g_value, l_value in zip(probes, greater, lesser)
    )
    kms_ratios = tuple(g_value / l_value for g_value, l_value in zip(greater, lesser))
    kms_targets = tuple(exp(energy / temperature) for energy in probes)
    kms_residual = max(
        abs(value - target) / max(abs(target), 1.0e-300)
        for value, target in zip(kms_ratios, kms_targets)
    )

    raw_responses: list[complex] = []
    subtracted_responses: list[complex] = []
    for energy in probes:
        raw, subtracted = _retarded_pair(
            energy,
            mass,
            temperature,
            mass,
            quartic,
            radial_order,
            center_of_mass_order,
            frequency_order,
            cutoff_factor,
            frequency_lower,
            frequency_upper,
            regulator_eta,
        )
        raw_responses.append(raw)
        subtracted_responses.append(subtracted)
    reference_raw, reference_subtracted = _retarded_pair(
        mass,
        mass,
        temperature,
        mass,
        quartic,
        radial_order,
        center_of_mass_order,
        frequency_order,
        cutoff_factor,
        frequency_lower,
        frequency_upper,
        regulator_eta,
    )
    raw_responses.append(reference_raw)

    refined_raw: list[complex] = []
    refined_subtracted: list[complex] = []
    for energy in probes:
        raw, subtracted = _retarded_pair(
            energy,
            mass,
            temperature,
            mass,
            quartic,
            radial_order + 8,
            center_of_mass_order + 8,
            frequency_order + 4,
            cutoff_factor + 4.0,
            frequency_lower,
            frequency_upper,
            regulator_eta,
        )
        refined_raw.append(raw)
        refined_subtracted.append(subtracted)
    dispersion_residual = max(
        _relative_change(value, refined)
        for value, refined in zip(subtracted_responses, refined_subtracted)
    )
    all_values = (
        *greater,
        *lesser,
        *spectral,
        *noise,
        *kms_ratios,
        *kms_targets,
        *raw_responses,
        *subtracted_responses,
        dispersion_residual,
        abs(reference_subtracted),
    )
    if not all(isfinite(float(value)) for value in all_values):
        raise FloatingPointError("sunset dispersion interface is not finite")
    return SunsetDispersionInterfaceState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=mass,
        reference_energy=mass,
        regulator_eta=regulator_eta,
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
        retarded_raw_real=tuple(value.real for value in raw_responses),
        retarded_raw_imaginary=tuple(value.imag for value in raw_responses),
        subtracted_real_response=tuple(value.real for value in subtracted_responses),
        subtracted_imaginary_response=tuple(
            value.imag for value in subtracted_responses
        ),
        reference_subtraction_residual=float(abs(reference_subtracted)),
        retarded_imaginary_sign_witness=all(
            value <= 1.0e-18 for value in (value.imag for value in raw_responses)
        ),
        spectral_positivity_witness=all(value >= -1.0e-30 for value in spectral),
        dispersion_convergence_residual=float(dispersion_residual),
        convergence_threshold=DISPERSION_CONVERGENCE_THRESHOLD,
        convergence_passed=dispersion_residual <= DISPERSION_CONVERGENCE_THRESHOLD,
    )


def sunset_dispersion_interface_contract() -> dict[str, Any]:
    """Return equations and the formal dispersion claim boundary."""

    return {
        "status": SUNSET_DISPERSION_STATUS,
        "equations": {
            "off_shell_cut_extension": (
                "s(omega,k)=omega^2+m_eff^2+2*omega*E_k; "
                "Gamma_>^cut(omega)=integral n_k*v_rel*sigma_22 "
                "<(1+n_3)(1+n_4)>_CM"
            ),
            "spectral_density": "rho_cut(omega)=2*omega*(Gamma_>^cut(omega)-Gamma_<^cut(omega))",
            "noise_density": "N_cut(omega)=2*omega*(Gamma_>^cut(omega)+Gamma_<^cut(omega))",
            "kms": "Gamma_>^cut(omega)/Gamma_<^cut(omega)=exp(beta*omega)",
            "retarded_dispersion": (
                "Sigma_R^eta(omega)=integral_0^Omega dnu/pi*rho_cut(nu)*"
                "[1/(omega-nu+i*eta)-1/(omega+nu+i*eta)]"
            ),
            "once_subtraction": "Sigma_R,sub(omega;omega_*)=Sigma_R^eta(omega)-Sigma_R^eta(omega_*)",
            "matching_interface": "rho_cut(omega_*=m_eff) matches the continuum on-shell cut artifact under identical controls",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass_momentum_energy": "energy",
            "regulator_eta": "energy; declared numerical retarded smearing",
            "spectral_density": "formal natural-unit cut normalization",
            "retarded_response": "formal natural-unit response normalization",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived neutral elastic cut with a declared off-shell rest-energy "
            "extension and once-subtracted finite-regulator dispersion interface"
        ),
        "observable": (
            "greater/lesser KMS ratio, positive cut spectral/noise density, retarded "
            "sign witness, subtraction residual, on-shell matching residual, and "
            "composite-quadrature convergence"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_FORMAL_DISPERSION_NO_SOURCE_ROWS_NO_HOLDOUT",
        "excluded": {
            "full_1PI_retarded_self_energy": True,
            "zero_eta_physical_limit": True,
            "unique_physical_renormalization": True,
            "off_shell_microscopic_action_match": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only a formal once-subtracted retarded dispersion interface "
            "built from the declared neutral continuum cut and its finite regulator. "
            "It does not close the full 1PI retarded self-energy, the zero-regulator "
            "physical limit, unique renormalization, microscopic off-shell action "
            "matching, physical Kubo/transport, covariant entropy-current balance, "
            "SI Phi mapping, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "DEFAULT_PROBE_ENERGIES",
    "DISPERSION_CONVERGENCE_THRESHOLD",
    "SUNSET_DISPERSION_STATUS",
    "SunsetDispersionInterfaceState",
    "sunset_dispersion_interface_contract",
    "sunset_dispersion_interface_state",
]
