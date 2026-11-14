"""Verified wrapper for the Topic 13 sunset dispersion interface.

The exploratory dispersion module contains the shared phase-space and
composite-quadrature helpers.  This wrapper owns the evidence-facing state
builder and validates real and imaginary response components separately before
emitting the lane state.
"""

from __future__ import annotations

from math import exp, isfinite, sqrt

from docs.core.uet_o2_finite_density_eos import effective_mass_sq
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_sunset_dispersion_interface import (
    DEFAULT_PROBE_ENERGIES,
    DISPERSION_CONVERGENCE_THRESHOLD,
    SUNSET_DISPERSION_STATUS,
    SunsetDispersionInterfaceState,
    _cut_rates,
    _finite,
    _order,
    _positive,
    _relative_change,
    _retarded_pair,
    sunset_dispersion_interface_contract,
)


def sunset_dispersion_interface_verified_state(
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
    """Return a finite-checked formal neutral dispersion interface state."""

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

    refined_subtracted: list[complex] = []
    for energy in probes:
        _, subtracted = _retarded_pair(
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
        refined_subtracted.append(subtracted)
    dispersion_residual = max(
        _relative_change(value, refined)
        for value, refined in zip(subtracted_responses, refined_subtracted)
    )
    real_values = (
        *greater,
        *lesser,
        *spectral,
        *noise,
        *kms_ratios,
        *kms_targets,
        dispersion_residual,
        abs(reference_subtracted),
    )
    if not all(isfinite(float(value)) for value in real_values):
        raise FloatingPointError("sunset dispersion scalar state is not finite")
    complex_values = (*raw_responses, *subtracted_responses, reference_raw)
    if not all(
        isfinite(value.real) and isfinite(value.imag) for value in complex_values
    ):
        raise FloatingPointError("sunset dispersion response is not finite")

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


__all__ = [
    "SUNSET_DISPERSION_STATUS",
    "SunsetDispersionInterfaceState",
    "sunset_dispersion_interface_contract",
    "sunset_dispersion_interface_verified_state",
]
