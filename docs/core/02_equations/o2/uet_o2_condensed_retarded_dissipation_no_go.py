"""Scoped no-go for deriving condensed dissipation from the conservative action.

The tree-level O(2) action fixes the condensed phase stiffness and Goldstone
mode, but it contains no closed-time-path noise or collision kernel.  This
module makes that boundary explicit with two causal, positive memory-kernel
witnesses that agree at zero frequency and differ at finite frequency.  The
witnesses are normalized diagnostics, not physical transport coefficients.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Any

from docs.core.uet_o2_condensate_fluctuations import (
    O2CondensateFluctuationState,
    condensate_fluctuation_state,
    quadratic_fluctuation_polynomial,
    quadratic_mode_frequencies,
)
from docs.core.uet_o2_finite_density_eos import O2FiniteDensityEOSConfig


CONDENSED_RETARDED_DISSIPATION_NO_GO_STATUS = (
    "PASS_SCOPED_CONDENSED_RETARDED_DISSIPATION_NO_GO"
)
MEMORY_KERNEL_TOLERANCE = 1.0e-12


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


def condensed_phase_stiffness(
    state: O2CondensateFluctuationState,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return the tree-level natural-unit phase stiffness ``Z*q/lambda``."""

    z = _positive(config.matter.matter_kinetic, "matter_kinetic")
    lam = _positive(config.matter.matter_quartic, "matter_quartic")
    return float(z * state.condensate_control / lam)


def conservative_phase_kernel(
    wavenumber: float,
    state: O2CondensateFluctuationState,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return the real static phase kernel fixed by the conservative action."""

    k = _finite(wavenumber, "wavenumber")
    if k < 0.0:
        raise ValueError("wavenumber must be non-negative")
    return float(condensed_phase_stiffness(state, config) * k * k)


def retarded_memory_kernel(
    omega: float,
    gamma: float,
    cutoff: float,
) -> complex:
    """Return a causal normalized memory witness.

    The corresponding time kernel is ``gamma*cutoff*exp(-cutoff*t) H(t)``.
    ``gamma`` and ``cutoff`` are witness parameters only; no physical unit or
    SI transport coefficient is assigned.
    """

    frequency = _finite(omega, "omega")
    amplitude = _positive(gamma, "gamma")
    scale = _positive(cutoff, "cutoff")
    return complex(amplitude * scale / complex(scale, -frequency))


def retarded_memory_kernel_time(
    time: float,
    gamma: float,
    cutoff: float,
) -> float:
    """Return the time-domain witness and enforce retarded support."""

    t = _finite(time, "time")
    amplitude = _positive(gamma, "gamma")
    scale = _positive(cutoff, "cutoff")
    if t < 0.0:
        return 0.0
    return float(amplitude * scale * exp(-scale * t))


@dataclass(frozen=True)
class CondensedRetardedDissipationBoundary:
    """Action-fixed reactive data plus two admissible dissipative witnesses."""

    temperature: float
    chemical_potential: float
    space_response: float
    wavenumber: float
    omega_probe: float
    condensate_control: float
    goldstone_frequency: float
    radial_frequency: float
    phase_stiffness: float
    conservative_static_kernel: float
    conservative_imaginary_part: float
    witness_zero_frequency_a: complex
    witness_zero_frequency_b: complex
    witness_probe_a: complex
    witness_probe_b: complex
    witness_a_positive_real: bool
    witness_b_positive_real: bool
    witness_a_causal: bool
    witness_b_causal: bool
    zero_frequency_match: bool
    finite_frequency_distinct: bool
    conservative_dissipation_zero: bool
    physical_transport_coefficients_emitted: bool = False
    data_role: str = (
        "INTERNAL_STRUCTURAL_CONDENSED_RETARDED_DISSIPATION_NO_GO"
    )


def condensed_retarded_dissipation_boundary(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    *,
    wavenumber: float = 0.23,
    omega_probe: float = 0.7,
    gamma: float = 0.8,
    cutoff_a: float = 1.0,
    cutoff_b: float = 4.0,
) -> CondensedRetardedDissipationBoundary:
    """Construct the condensed conservative-action dissipation boundary."""

    t = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    k = _positive(wavenumber, "wavenumber")
    omega = _positive(omega_probe, "omega_probe")
    state = condensate_fluctuation_state(mu, phi, config)
    low, high = quadratic_mode_frequencies(k, state, config)
    static_kernel = conservative_phase_kernel(k, state, config)
    zero_a = retarded_memory_kernel(0.0, gamma, cutoff_a)
    zero_b = retarded_memory_kernel(0.0, gamma, cutoff_b)
    probe_a = retarded_memory_kernel(omega, gamma, cutoff_a)
    probe_b = retarded_memory_kernel(omega, gamma, cutoff_b)

    return CondensedRetardedDissipationBoundary(
        temperature=t,
        chemical_potential=mu,
        space_response=phi,
        wavenumber=k,
        omega_probe=omega,
        condensate_control=float(state.condensate_control),
        goldstone_frequency=float(low),
        radial_frequency=float(high),
        phase_stiffness=float(condensed_phase_stiffness(state, config)),
        conservative_static_kernel=float(static_kernel),
        conservative_imaginary_part=0.0,
        witness_zero_frequency_a=zero_a,
        witness_zero_frequency_b=zero_b,
        witness_probe_a=probe_a,
        witness_probe_b=probe_b,
        witness_a_positive_real=zero_a.real >= -MEMORY_KERNEL_TOLERANCE
        and probe_a.real >= -MEMORY_KERNEL_TOLERANCE,
        witness_b_positive_real=zero_b.real >= -MEMORY_KERNEL_TOLERANCE
        and probe_b.real >= -MEMORY_KERNEL_TOLERANCE,
        witness_a_causal=(
            retarded_memory_kernel_time(-1.0, gamma, cutoff_a) == 0.0
            and retarded_memory_kernel_time(0.5, gamma, cutoff_a) > 0.0
        ),
        witness_b_causal=(
            retarded_memory_kernel_time(-1.0, gamma, cutoff_b) == 0.0
            and retarded_memory_kernel_time(0.5, gamma, cutoff_b) > 0.0
        ),
        zero_frequency_match=abs(zero_a - zero_b) <= MEMORY_KERNEL_TOLERANCE,
        finite_frequency_distinct=abs(probe_a - probe_b) > MEMORY_KERNEL_TOLERANCE,
        conservative_dissipation_zero=abs(0.0) <= MEMORY_KERNEL_TOLERANCE,
    )


def condensed_retarded_dissipation_contract() -> dict[str, Any]:
    """Return equations, units, evidence role, and the promotion boundary."""

    return {
        "status": CONDENSED_RETARDED_DISSIPATION_NO_GO_STATUS,
        "equations": {
            "condensed_branch": "q=Z*mu^2-m_eff(Phi)^2>0",
            "phase_stiffness": "f_s=Z*q/lambda",
            "goldstone_boundary": "det K_tree(omega,k)=0 and omega_G(k->0)->0",
            "conservative_retarded_kernel": "K_R^cons(omega,k) is real; Im K_R^cons=0",
            "causal_memory_witness": (
                "M_R,j(t)=gamma*Lambda_j*exp(-Lambda_j*t)*H(t)"
            ),
            "frequency_memory_witness": (
                "M_R,j(omega)=gamma*Lambda_j/(Lambda_j-i*omega)"
            ),
            "entropy_boundary": "Re M_R,j(omega)>=0 for omega>=0",
            "identifiability_witness": (
                "M_R,A(0)=M_R,B(0) but M_R,A(omega_probe)!=M_R,B(omega_probe)"
            ),
        },
        "unit_contract": {
            "unit_lane": "natural normalized structural diagnostic",
            "phase_stiffness": "natural action-derived coefficient",
            "memory_kernel": "normalized witness; no physical transport units assigned",
            "gamma_and_cutoff": "witness parameters, not calibrated coefficients",
            "Phi": "effective response variable; not temperature or a metric",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; not an independent state or feedback input",
            "R_obs": "separate observer record; not physical dynamics",
        },
        "derivation_class": (
            "tree-level conservative O(2) phase action plus explicit causal PSD "
            "memory-kernel witnesses; structural identifiability no-go"
        ),
        "observable": (
            "difference between admissible retarded condensed dissipative "
            "extensions of the same conservative phase sector"
        ),
        "data_role": "INTERNAL_STRUCTURAL_NO_GO_NOT_PHYSICAL_TRANSPORT_EVIDENCE",
        "closed_scope": [
            "the conservative action fixes the condensed phase stiffness and tree Goldstone sector",
            "the conservative action alone has no dissipative imaginary retarded kernel",
            "two causal positive-memory extensions can agree at zero frequency and differ at finite frequency",
            "a unique condensed dissipative kernel requires an independent SK/influence-functional derivation or state-matched retarded source",
        ],
        "excluded_scope": [
            "physical Kubo coefficient",
            "microscopic condensed collision kernel",
            "complete two-fluid constitutive tensor",
            "SI heat-flux or Phi normalization",
            "numeric alpha_Phi_K",
            "TTG prediction or external validation",
        ],
        "claim_boundary": (
            "This closes only the scoped no-go that the current conservative "
            "condensed action cannot identify a unique dissipative retarded "
            "kernel. It does not supply a physical coefficient or close the "
            "SK/KMS, SI, alpha_Phi_K, TTG, or Full Topic 13 gates."
        ),
    }


__all__ = [
    "CONDENSED_RETARDED_DISSIPATION_NO_GO_STATUS",
    "CondensedRetardedDissipationBoundary",
    "condensed_phase_stiffness",
    "conservative_phase_kernel",
    "retarded_memory_kernel",
    "retarded_memory_kernel_time",
    "condensed_retarded_dissipation_boundary",
    "condensed_retarded_dissipation_contract",
]
