"""Action-normalized O(2) sunset spectral interface for Topic 13.

This lane derives the contact four-point tensor from the declared matter
potential ``W_int=lambda*(chi^2)^2/4`` before constructing the equal-mass
thermal sunset cut.  The species sum and identical-final-state symmetry
factor are explicit, so this branch is not silently identified with the
constant-amplitude comparator used by the earlier continuum lane.

The retarded response is a finite-regulator, twice-subtracted dispersion
interface.  It is an evidence-producing internal lane, not a claim that the
zero-regulator 1PI self-energy, microscopic renormalization, Kubo transport,
or the Phi-to-temperature map is complete.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


ACTION_SUNSET_STATUS = (
    "PASS_ACTION_DERIVED_O2_SUNSET_1PI_SPECTRAL_INTERFACE_LANE"
)
ACTION_SUNSET_CONVERGENCE_THRESHOLD = 2.0e-2
DEFAULT_ACTION_SUNSET_PROBES = (0.60, 0.76, 0.90, 1.05)
O2_SPECIES_COUNT = 2


@dataclass(frozen=True)
class ActionSunsetSpectralState:
    """Action-normalized neutral sunset and dispersion quantities."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    external_species: int
    quartic_coupling: float
    action_vertex_factor: float
    action_matrix_element_squared: float
    comparator_matrix_element_squared: float
    action_to_comparator_matrix_element_ratio: float
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
    on_shell_greater_cut: float
    on_shell_lesser_cut: float
    on_shell_spectral_cut: float
    raw_real_response: tuple[float, ...]
    raw_imaginary_response: tuple[float, ...]
    twice_subtracted_real_response: tuple[float, ...]
    twice_subtracted_imaginary_response: tuple[float, ...]
    reference_subtraction_residual: float
    reference_first_s_derivative_residual: float
    retarded_imaginary_sign_witness: bool
    spectral_positivity_witness: bool
    dispersion_convergence_residual: float
    convergence_threshold: float
    convergence_passed: bool
    action_vertex_normalization_completed: bool = True
    action_continuum_cut_completed: bool = True
    twice_subtracted_dispersion_interface_completed: bool = True
    full_1pi_retarded_self_energy_completed: bool = False
    zero_eta_physical_limit_completed: bool = False
    unique_physical_renormalization_scheme_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_INTERNAL_O2_SUNSET_SPECTRAL_INTERFACE_NO_HOLDOUT"
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


def _relative_change(first: complex, second: complex) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def _delta(first: int, second: int) -> float:
    return 1.0 if first == second else 0.0


def action_vertex_component(
    external_species: int,
    bath_species: int,
    final_species_one: int,
    final_species_two: int,
    quartic: float,
) -> float:
    """Return the magnitude of the O(2) contact four-point vertex.

    The declared action convention is ``W_int=lambda*(chi^2)^2/4``.  The
    overall sign is irrelevant for the cut, while the factor of two and all
    Kronecker structures are retained in the squared matrix element.
    """

    indices = (
        external_species,
        bath_species,
        final_species_one,
        final_species_two,
    )
    if any(index not in range(O2_SPECIES_COUNT) for index in indices):
        raise ValueError("O(2) species indices must be 0 or 1")
    quartic = _positive(quartic, "quartic")
    tensor = (
        _delta(external_species, bath_species)
        * _delta(final_species_one, final_species_two)
        + _delta(external_species, final_species_one)
        * _delta(bath_species, final_species_two)
        + _delta(external_species, final_species_two)
        * _delta(bath_species, final_species_one)
    )
    return 2.0 * quartic * tensor


def action_matrix_element_squared(
    quartic: float,
    external_species: int = 0,
) -> float:
    """Sum ``|V_abcd|^2`` over bath and final species.

    The final-state factor ``1/(1+delta_cd)`` prevents double counting of
    identical final particles.  For either external O(2) species this gives
    ``28*lambda^2`` under the declared action convention.
    """

    quartic = _positive(quartic, "quartic")
    if external_species not in range(O2_SPECIES_COUNT):
        raise ValueError("external_species must be 0 or 1")
    result = 0.0
    for bath_species in range(O2_SPECIES_COUNT):
        for final_species_one in range(O2_SPECIES_COUNT):
            for final_species_two in range(O2_SPECIES_COUNT):
                vertex = action_vertex_component(
                    external_species,
                    bath_species,
                    final_species_one,
                    final_species_two,
                    quartic,
                )
                result += vertex * vertex / (
                    1.0 + _delta(final_species_one, final_species_two)
                )
    return float(result)


def _action_cross_section(
    invariant_s: float,
    quartic: float,
    external_species: int,
) -> float:
    invariant_s = _positive(invariant_s, "invariant_s")
    matrix_element_sq = action_matrix_element_squared(
        quartic, external_species
    )
    return matrix_element_sq / (16.0 * pi * invariant_s)


def _quadrature(order: int, lower: float, upper: float) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return (
        0.5 * (upper - lower) * (nodes + 1.0) + lower,
        0.5 * (upper - lower) * weights,
    )


def _cm_bose_averages(
    momentum: float,
    external_energy: float,
    mass: float,
    temperature: float,
    angular_order: int,
) -> tuple[float, float]:
    invariant_s = external_energy * external_energy + mass * mass + 2.0 * external_energy * sqrt(
        momentum * momentum + mass * mass
    )
    root_s = sqrt(invariant_s)
    energy_star = 0.5 * root_s
    momentum_star = sqrt(max(0.25 * invariant_s - mass * mass, 0.0))
    bath_energy = sqrt(momentum * momentum + mass * mass)
    beta_cm = momentum / (external_energy + bath_energy)
    gamma_cm = (external_energy + bath_energy) / root_s
    nodes, weights = np.polynomial.legendre.leggauss(angular_order)
    greater = 0.0
    lesser = 0.0
    for cosine, weight in zip(nodes, weights):
        energy_three = gamma_cm * (
            energy_star + beta_cm * momentum_star * float(cosine)
        )
        energy_four = gamma_cm * (
            energy_star - beta_cm * momentum_star * float(cosine)
        )
        occupation_three = _bose(energy_three, temperature)
        occupation_four = _bose(energy_four, temperature)
        greater += 0.5 * float(weight) * (1.0 + occupation_three) * (
            1.0 + occupation_four
        )
        lesser += 0.5 * float(weight) * occupation_three * occupation_four
    return float(greater), float(lesser)


def _cut_rates(
    external_energy: float,
    temperature: float,
    mass: float,
    quartic: float,
    external_species: int,
    radial_order: int,
    center_of_mass_order: int,
    cutoff_factor: float,
) -> tuple[float, float]:
    """Evaluate the action-normalized neutral elastic cut."""

    omega = _positive(external_energy, "external_energy")
    cutoff = max(cutoff_factor * temperature, cutoff_factor * mass, 1.0)
    required_bath_energy = (3.0 * mass * mass - omega * omega) / (2.0 * omega)
    minimum_momentum = (
        sqrt(max(required_bath_energy * required_bath_energy - mass * mass, 0.0))
        if required_bath_energy > mass
        else 0.0
    )
    if minimum_momentum >= cutoff:
        return 0.0, 0.0

    momenta, radial_weights = _quadrature(
        radial_order, minimum_momentum, cutoff
    )
    greater = 0.0
    lesser = 0.0
    for momentum, radial_weight in zip(momenta, radial_weights):
        k = float(momentum)
        bath_energy = sqrt(k * k + mass * mass)
        invariant_s = omega * omega + mass * mass + 2.0 * omega * bath_energy
        if invariant_s < 4.0 * mass * mass:
            continue
        final_greater, final_lesser = _cm_bose_averages(
            k, omega, mass, temperature, center_of_mass_order
        )
        measure = float(radial_weight) * k * k / (2.0 * pi * pi)
        relative_velocity = k / bath_energy
        cross_section = _action_cross_section(
            invariant_s, quartic, external_species
        )
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


def _dispersion_pair(
    omega: float,
    reference: float,
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
    regulator_eta: float,
) -> tuple[complex, complex, complex]:
    """Return raw, twice-subtracted, and reference ``d/d(omega^2)`` terms."""

    raw = 0.0j
    reference_raw = 0.0j
    reference_s_derivative = 0.0j
    breakpoints = _frequency_breakpoints(
        frequency_lower, frequency_upper, omega, reference
    )
    for left, right in zip(breakpoints[:-1], breakpoints[1:]):
        if right - left <= 1.0e-14:
            continue
        frequencies, frequency_weights = _quadrature(
            frequency_order, left, right
        )
        for frequency, frequency_weight in zip(frequencies, frequency_weights):
            nu = float(frequency)
            greater, lesser = _cut_rates(
                nu,
                temperature,
                mass,
                quartic,
                external_species,
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
            derivative_kernel = (
                -1.0 / (reference - nu + 1.0j * regulator_eta) ** 2
                + 1.0 / (reference + nu + 1.0j * regulator_eta) ** 2
            ) / (2.0 * reference)
            weight = float(frequency_weight) * spectral / pi
            raw += weight * kernel
            reference_raw += weight * reference_kernel
            reference_s_derivative += weight * derivative_kernel
    twice_subtracted = raw - reference_raw - (
        omega * omega - reference * reference
    ) * reference_s_derivative
    return complex(raw), complex(twice_subtracted), complex(reference_s_derivative)


def action_sunset_spectral_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    external_species: int = 0,
    radial_order: int = 32,
    center_of_mass_order: int = 24,
    frequency_order: int = 10,
    cutoff_factor: float = 24.0,
    frequency_cutoff_factor: float = 6.0,
    regulator_eta: float = 0.025,
    probe_energies: tuple[float, ...] = DEFAULT_ACTION_SUNSET_PROBES,
) -> ActionSunsetSpectralState:
    """Build the action-normalized neutral sunset spectral interface."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    if abs(chemical_potential) > 1.0e-14:
        raise ValueError("action sunset spectral lane locks chemical_potential=0")
    space_response = _finite(space_response, "space_response")
    if external_species not in range(O2_SPECIES_COUNT):
        raise ValueError("external_species must be 0 or 1")
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
        raise ValueError("action sunset spectral lane requires positive mass squared")
    mass = sqrt(mass_sq)
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    action_matrix_sq = action_matrix_element_squared(quartic, external_species)
    comparator_matrix_sq = quartic * quartic
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
            external_species,
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
        _relative_change(value, target)
        for value, target in zip(kms_ratios, kms_targets)
    )

    raw_responses: list[complex] = []
    subtracted_responses: list[complex] = []
    for energy in probes:
        raw, subtracted, _ = _dispersion_pair(
            energy,
            mass,
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
            regulator_eta,
        )
        raw_responses.append(raw)
        subtracted_responses.append(subtracted)
    reference_raw, reference_subtracted, reference_s_derivative = _dispersion_pair(
        mass,
        mass,
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
        regulator_eta,
    )
    raw_responses.append(reference_raw)
    subtracted_responses.append(reference_subtracted)

    refined_subtracted: list[complex] = []
    for energy in probes:
        _, subtracted, _ = _dispersion_pair(
            energy,
            mass,
            temperature,
            mass,
            quartic,
            external_species,
            radial_order + 8,
            center_of_mass_order + 8,
            frequency_order + 4,
            cutoff_factor + 4.0,
            frequency_lower,
            frequency_upper,
            regulator_eta,
        )
        refined_subtracted.append(subtracted)
    dispersion_residual = max(
        _relative_change(value, refined)
        for value, refined in zip(subtracted_responses[:-1], refined_subtracted)
    )

    derivative_step = 1.0e-4 * max(mass * mass, 1.0)
    derivative_step = min(derivative_step, 0.25 * mass * mass)
    plus_energy = sqrt(mass * mass + derivative_step)
    minus_energy = sqrt(max(mass * mass - derivative_step, 1.0e-12))
    plus_raw, _, _ = _dispersion_pair(
        plus_energy,
        mass,
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
        regulator_eta,
    )
    minus_raw, _, _ = _dispersion_pair(
        minus_energy,
        mass,
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
        regulator_eta,
    )
    finite_difference_derivative = (plus_raw - minus_raw) / (2.0 * derivative_step)
    derivative_residual = _relative_change(
        finite_difference_derivative, reference_s_derivative
    )

    on_shell_greater, on_shell_lesser = _cut_rates(
        mass,
        temperature,
        mass,
        quartic,
        external_species,
        radial_order,
        center_of_mass_order,
        cutoff_factor,
    )
    on_shell_spectral = 2.0 * mass * (on_shell_greater - on_shell_lesser)
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
        derivative_residual,
        on_shell_greater,
        on_shell_lesser,
        on_shell_spectral,
    )
    if not all(
        isfinite(float(value.real)) and isfinite(float(value.imag))
        if isinstance(value, complex)
        else isfinite(float(value))
        for value in all_values
    ):
        raise FloatingPointError("action sunset spectral state is not finite")

    return ActionSunsetSpectralState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=mass,
        external_species=external_species,
        quartic_coupling=quartic,
        action_vertex_factor=2.0,
        action_matrix_element_squared=float(action_matrix_sq),
        comparator_matrix_element_squared=float(comparator_matrix_sq),
        action_to_comparator_matrix_element_ratio=float(
            action_matrix_sq / comparator_matrix_sq
        ),
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
        on_shell_greater_cut=float(on_shell_greater),
        on_shell_lesser_cut=float(on_shell_lesser),
        on_shell_spectral_cut=float(on_shell_spectral),
        raw_real_response=tuple(value.real for value in raw_responses),
        raw_imaginary_response=tuple(value.imag for value in raw_responses),
        twice_subtracted_real_response=tuple(
            value.real for value in subtracted_responses
        ),
        twice_subtracted_imaginary_response=tuple(
            value.imag for value in subtracted_responses
        ),
        reference_subtraction_residual=float(abs(reference_subtracted)),
        reference_first_s_derivative_residual=float(derivative_residual),
        retarded_imaginary_sign_witness=all(
            value <= 1.0e-18 for value in (value.imag for value in raw_responses)
        ),
        spectral_positivity_witness=all(value >= -1.0e-30 for value in spectral),
        dispersion_convergence_residual=float(dispersion_residual),
        convergence_threshold=ACTION_SUNSET_CONVERGENCE_THRESHOLD,
        convergence_passed=dispersion_residual <= ACTION_SUNSET_CONVERGENCE_THRESHOLD,
    )


def action_sunset_spectral_contract() -> dict[str, Any]:
    """Return the action-normalization equations and claim boundary."""

    return {
        "status": ACTION_SUNSET_STATUS,
        "equations": {
            "interaction_potential": "W_int=lambda*(chi_a chi_a)^2/4",
            "action_four_point_vertex": (
                "V_abcd=2*lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)"
            ),
            "action_matrix_element_squared": (
                "M2_action=sum_{b,c,d}|V_abcd|^2/(1+delta_cd)=28*lambda^2 for O(2)"
            ),
            "action_cross_section": "sigma_action=M2_action/(16*pi*s)",
            "greater_cut": (
                "Gamma_>=integral n_k*v_rel*sigma_action*<(1+n_3)(1+n_4)>_CM"
            ),
            "lesser_cut": (
                "Gamma_<=integral (1+n_k)*v_rel*sigma_action*<n_3*n_4>_CM"
            ),
            "spectral_density": "rho_cut(omega)=2*omega*(Gamma_>-Gamma_<)",
            "noise_density": "N_cut(omega)=2*omega*(Gamma_>+Gamma_<)",
            "kms": "Gamma_>(omega)/Gamma_<(omega)=exp(beta*omega)",
            "retarded_dispersion": (
                "Sigma_R^eta(omega)=integral_0^Omega dnu/pi*rho_cut(nu)*"
                "[1/(omega-nu+i*eta)-1/(omega+nu+i*eta)]"
            ),
            "twice_subtraction": (
                "Sigma_R,sub2(omega;omega_*)=Sigma_R^eta(omega)-Sigma_R^eta(omega_*)-"
                "(omega^2-omega_*^2)*dSigma_R^eta/d(omega^2)|_{omega_*}"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass_momentum_energy": "energy",
            "quartic_coupling": "dimensionless",
            "matrix_element_squared": "dimensionless",
            "cross_section": "inverse energy squared",
            "cut_rate": "energy",
            "spectral_density": "energy squared in declared cut normalization",
            "regulator_eta": "energy; numerical retarded smearing",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived O(2) contact vertex, explicit species/symmetry-factor sum, "
            "neutral thermal phase-space cut, and finite-regulator twice-subtracted "
            "dispersion interface"
        ),
        "observable": (
            "action vertex normalization, on-shell cut, KMS ratio, positive spectral/noise "
            "density, retarded sign, subtraction residual, and quadrature convergence"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_O2_SUNSET_SPECTRAL_INTERFACE_NO_HOLDOUT",
        "included": {
            "action_vertex_tensor": True,
            "final_state_symmetry_factor": True,
            "action_normalized_continuum_cut": True,
            "kms_ratio": True,
            "twice_subtracted_formal_dispersion": True,
        },
        "excluded": {
            "full_1PI_retarded_self_energy": True,
            "zero_eta_physical_limit": True,
            "unique_physical_renormalization": True,
            "microscopic_SK_KMS_match": True,
            "physical_kubo_coefficient": True,
            "covariant_entropy_current": True,
            "heat_flux_dissipative_balance": True,
            "dimensional_Phi_to_thermal_observable_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
            "Xie_2026_holdout": True,
        },
        "claim_boundary": (
            "This closes only an internal action-normalized O(2) sunset spectral "
            "interface with a finite regulator and twice-subtracted dispersion. It "
            "does not close the zero-regulator physical 1PI self-energy, unique "
            "renormalization, microscopic SK/KMS matching, physical transport, "
            "entropy-current balance, dimensional Phi mapping, alpha_Phi_K, TTG "
            "validation, or Full Topic 13."
        ),
    }


__all__ = [
    "ACTION_SUNSET_CONVERGENCE_THRESHOLD",
    "ACTION_SUNSET_STATUS",
    "ActionSunsetSpectralState",
    "action_matrix_element_squared",
    "action_sunset_spectral_contract",
    "action_sunset_spectral_state",
    "action_vertex_component",
]
