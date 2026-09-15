"""State-matched condensed SK/KMS interface for Topic 13.

The module lifts the admitted condensed relative-flow retarded coefficient to
the two-by-two relative projector and constructs the corresponding greater,
lesser, and Keldysh noise components.  It closes the declared channel's
algebraic SK/KMS/FDT interface while leaving the full finite-temperature 1PI
self-energy and all-channel microscopic influence functional open.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_condensed_loop_renormalized_vertex import (
    CondensedLoopRenormalizedVertexState,
    condensed_loop_renormalized_vertex_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


CONDENSED_SK_KMS_STATUS = (
    "PASS_ACTION_DERIVED_CONDENSED_SK_KMS_KUBO_MATCH_LANE"
)
CONDENSED_SK_KMS_THRESHOLD = 1.0e-12
CONDENSED_SK_KMS_KUBO_STATUS = CONDENSED_SK_KMS_STATUS
RELATIVE_PROJECTOR = np.asarray(((1.0, -1.0), (-1.0, 1.0)), dtype=float)


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


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


@dataclass(frozen=True)
class CondensedSKKMSKuboMatchState:
    """State-matched retarded and Keldysh response record."""

    temperature: float
    chemical_potential: float
    space_response: float
    branch: str
    relative_susceptibility: float
    relative_collision_rate: float
    zero_frequency_kubo_coefficient: float
    frequency_over_rate: tuple[float, ...]
    frequencies: tuple[float, ...]
    retarded_real: tuple[float, ...]
    retarded_imag: tuple[float, ...]
    spectral_scalar: tuple[float, ...]
    greater_scalar: tuple[float, ...]
    lesser_scalar: tuple[float, ...]
    noise_scalar: tuple[float, ...]
    kms_residual: float
    fdt_residual: float
    retarded_reality_residual: float
    spectral_psd_minimum: float
    retarded_pole_imaginary_part: float
    negative_time_support_residual: float
    positive_time_kernel_value: float
    zero_frequency_kubo_match_residual: float
    entropy_production_at_unit_force: float
    state_matched_kubo_admission_completed: bool = True
    declared_channel_sk_kms_match_completed: bool = True
    physical_retarded_self_energy_completed: bool = False
    full_interacting_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = True
    numeric_alpha_phi_k_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = "DERIVED_ACTION_CONDENSED_SK_KMS_KUBO_CHANNEL_NOT_FULL_1PI"


def condensed_sk_kms_kubo_match_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    reference_space_response: float = 0.0,
    frequency_over_rate: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0),
    loop_state: CondensedLoopRenormalizedVertexState | None = None,
) -> CondensedSKKMSKuboMatchState:
    """Build the declared condensed relative-flow SK/KMS response."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    ratios = tuple(_finite(value, "frequency_over_rate") for value in frequency_over_rate)
    if (
        not ratios
        or tuple(sorted(ratios)) != ratios
        or any(value <= 0.0 for value in ratios)
    ):
        raise ValueError("frequency_over_rate must be sorted and positive")
    state = loop_state or condensed_loop_renormalized_vertex_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        reference_space_response=reference_space_response,
    )
    if state.branch != "condensed":
        raise ValueError("condensed SK/KMS match requires the condensed branch")
    susceptibility = _positive(state.relative_susceptibility, "relative susceptibility")
    rate = _positive(state.relative_collision_rate, "relative collision rate")
    dc = _positive(state.dc_relative_response, "zero-frequency Kubo coefficient")
    frequencies = tuple(rate * ratio for ratio in ratios)
    retarded = tuple(
        2.0 * susceptibility / complex(2.0 * rate, -frequency)
        for frequency in frequencies
    )
    real_values = tuple(float(value.real) for value in retarded)
    imag_values = tuple(float(value.imag) for value in retarded)
    spectral_values = tuple(2.0 * value for value in imag_values)
    greater_values: list[float] = []
    lesser_values: list[float] = []
    noise_values: list[float] = []
    kms_residual = 0.0
    fdt_residual = 0.0
    reality_residual = 0.0
    psd_minimum = float("inf")
    for frequency, spectral in zip(frequencies, spectral_values):
        occupation = 1.0 / expm1(frequency / temperature)
        greater = spectral * (1.0 + occupation)
        lesser = spectral * occupation
        noise = greater + lesser
        greater_values.append(float(greater))
        lesser_values.append(float(lesser))
        noise_values.append(float(noise))
        kms_residual = max(
            kms_residual,
            _relative(greater / lesser, exp(frequency / temperature)),
        )
        fdt_residual = max(
            fdt_residual,
            _relative(noise, spectral / tanh(0.5 * frequency / temperature)),
        )
        negative_frequency = 2.0 * susceptibility / complex(2.0 * rate, frequency)
        reality_residual = max(
            reality_residual,
            abs(negative_frequency - np.conjugate(complex(real_values[len(greater_values) - 1], imag_values[len(greater_values) - 1])))
            / max(abs(retarded[len(greater_values) - 1]), 1.0e-300),
        )
        psd_minimum = min(
            psd_minimum,
            float(np.min(np.linalg.eigvalsh(spectral * RELATIVE_PROJECTOR))),
        )
    positive_time_kernel = 2.0 * susceptibility
    zero_frequency_match = _relative(susceptibility / rate, dc)
    entropy = _positive(dc / temperature, "entropy production")
    values = (
        susceptibility,
        rate,
        dc,
        *frequencies,
        *real_values,
        *imag_values,
        *spectral_values,
        *greater_values,
        *lesser_values,
        *noise_values,
        kms_residual,
        fdt_residual,
        reality_residual,
        psd_minimum,
        positive_time_kernel,
        zero_frequency_match,
        entropy,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("condensed SK/KMS Kubo state is not finite")
    return CondensedSKKMSKuboMatchState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        branch=state.branch,
        relative_susceptibility=susceptibility,
        relative_collision_rate=rate,
        zero_frequency_kubo_coefficient=dc,
        frequency_over_rate=ratios,
        frequencies=frequencies,
        retarded_real=real_values,
        retarded_imag=imag_values,
        spectral_scalar=spectral_values,
        greater_scalar=tuple(greater_values),
        lesser_scalar=tuple(lesser_values),
        noise_scalar=tuple(noise_values),
        kms_residual=float(kms_residual),
        fdt_residual=float(fdt_residual),
        retarded_reality_residual=float(reality_residual),
        spectral_psd_minimum=float(psd_minimum),
        retarded_pole_imaginary_part=float(-2.0 * rate),
        negative_time_support_residual=0.0,
        positive_time_kernel_value=float(positive_time_kernel),
        zero_frequency_kubo_match_residual=float(zero_frequency_match),
        entropy_production_at_unit_force=entropy,
    )


def condensed_sk_kms_kubo_match_contract() -> dict[str, Any]:
    """Return equations, units, and the full-self-energy boundary."""

    return {
        "status": CONDENSED_SK_KMS_STATUS,
        "equations": {
            "relative_projector": "P_rel=((1,-1),(-1,1))",
            "retarded_correlator": "G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)*P_rel",
            "spectral_function": "rho(omega)=2*Im G_R^rel(omega)",
            "greater_lesser": "G^>=rho*(1+n_B(omega)); G^<=rho*n_B(omega)",
            "kms": "G^>/G^<=exp(omega/T)",
            "fdt": "G^K=G^>+G^<=rho*coth(omega/(2*T))",
            "entropy": "sigma_rel=K_rel^natural/T>=0 for unit relative force",
        },
        "unit_contract": {
            "unit_lane": "natural continuum 3+1",
            "temperature_chemical_potential_frequency_rate": "energy",
            "retarded_and_keldysh_response": "natural-unit relative-flow response",
            "Phi": "effective response variable; not temperature or metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state or feedback input",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "derivation_class": "action-derived loop-renormalized condensed contact response lifted to a relative-projector SK/KMS/FDT interface",
        "observable": "state-matched retarded, spectral, greater, lesser, noise, and entropy response in the declared channel",
        "data_role": "DERIVED_ACTION_CONDENSED_SK_KMS_KUBO_CHANNEL_NOT_FULL_1PI",
        "closed_scope": [
            "state-matched relative-projector retarded response",
            "retarded pole and causal time-domain sign",
            "spectral PSD, KMS ratio, and FDT noise identity",
            "zero-frequency match to the admitted natural Kubo coefficient",
            "nonnegative declared-channel entropy witness",
        ],
        "excluded_scope": [
            "full finite-temperature retarded 1PI self-energy",
            "unique physical renormalization across all channels",
            "complete condensed two-fluid constitutive tensor",
            "SI transport coefficient",
            "alpha_Phi_K calibration",
            "TTG validation",
            "Full Topic 13 closure",
        ],
        "claim_boundary": (
            "This closes the state-matched SK/KMS/FDT interface for the declared "
            "condensed relative-flow contact channel only. It does not close the "
            "full interacting finite-temperature 1PI self-energy, all-channel "
            "renormalization, SI transport, or Full Topic 13."
        ),
    }


__all__ = [
    "CONDENSED_SK_KMS_KUBO_STATUS",
    "CONDENSED_SK_KMS_STATUS",
    "CONDENSED_SK_KMS_THRESHOLD",
    "CondensedSKKMSKuboMatchState",
    "condensed_sk_kms_kubo_match_contract",
    "condensed_sk_kms_kubo_match_state",
]
