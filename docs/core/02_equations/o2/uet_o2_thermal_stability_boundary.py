"""Thermal-only stability boundary for the homogeneous condensed O(2) lane.

The tree-level phase-curvature condition identifies the lower boundary of the
quadratic stable domain.  This module deliberately does not reinterpret that
boundary as a finite-temperature stationary point: thermal backreaction and a
renormalized self-energy are separate, still-open inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_gaussian_offshell_background import (
    off_shell_curvatures,
    off_shell_mode_omega_sq,
)


@dataclass(frozen=True)
class O2ThermalStabilityBoundary:
    """Analytic lower boundary of the quadratic condensed stable domain."""

    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    condensate_control: float
    quartic_coupling: float
    amplitude_boundary: float
    amplitude_squared_boundary: float
    radial_curvature_at_boundary: float
    phase_curvature_at_boundary: float
    unit_lane: str = "natural"
    thermal_only: bool = True
    self_consistent_finite_temperature_boundary: bool = False
    interacting_self_energy_included: bool = False
    data_role: str = "ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def thermal_stability_boundary(
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> O2ThermalStabilityBoundary:
    """Return ``A_boundary^2=q/lambda`` in the condensed tree-level lane."""

    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(phi, config))
    z = float(config.matter.matter_kinetic)
    quartic = float(config.matter.matter_quartic)
    q = z * mu * mu - mass_sq
    if q <= 0.0:
        raise ValueError("thermal stability boundary requires q > 0 condensed control")
    if quartic <= 0.0 or not isfinite(quartic):
        raise ValueError("thermal stability boundary requires positive quartic coupling")
    amplitude_squared = q / quartic
    amplitude = sqrt(amplitude_squared)
    _, radial, phase = off_shell_curvatures(amplitude, mu, phi, config)
    values = (mass_sq, q, amplitude_squared, amplitude, radial, phase)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("thermal stability boundary is not finite")
    return O2ThermalStabilityBoundary(
        chemical_potential=mu,
        space_response=phi,
        effective_mass_sq=mass_sq,
        condensate_control=q,
        quartic_coupling=quartic,
        amplitude_boundary=amplitude,
        amplitude_squared_boundary=amplitude_squared,
        radial_curvature_at_boundary=radial,
        phase_curvature_at_boundary=phase,
    )


def phase_curvature_at_amplitude(
    amplitude: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return the phase Hessian entry controlling the lower stable boundary."""

    return float(
        off_shell_curvatures(
            amplitude,
            chemical_potential,
            space_response,
            config,
        )[2]
    )


def mode_stability_witness(
    amplitude: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
    wavenumbers: tuple[float, ...],
) -> dict[str, Any]:
    """Return unmodified mode-root signs over a declared wavenumber witness."""

    records = []
    for wavenumber in wavenumbers:
        low, high = off_shell_mode_omega_sq(
            wavenumber,
            amplitude,
            chemical_potential,
            space_response,
            config,
        )
        records.append(
            {
                "wavenumber": float(wavenumber),
                "low_omega_sq": float(low),
                "high_omega_sq": float(high),
            }
        )
    return {
        "amplitude": float(amplitude),
        "records": records,
        "minimum_low_omega_sq": min(item["low_omega_sq"] for item in records),
        "minimum_high_omega_sq": min(item["high_omega_sq"] for item in records),
        "all_low_nonnegative": all(item["low_omega_sq"] >= -1.0e-12 for item in records),
        "all_high_nonnegative": all(item["high_omega_sq"] >= -1.0e-12 for item in records),
    }


def uet_o2_thermal_stability_boundary_contract() -> dict[str, Any]:
    """Return the boundary equation and its non-promotion boundary."""

    return {
        "status": "ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY",
        "equations": {
            "condensed_control": "q=Z*mu^2-m_eff(Phi)^2 > 0",
            "phase_curvature": "r_pi(A)=-q+lambda*A^2",
            "stable_boundary": "A_boundary^2=q/lambda from r_pi(A_boundary)=0",
            "radial_curvature_at_boundary": "r_sigma(A_boundary)=2*q",
            "stable_domain": "A^2 >= q/lambda for the quadratic condensed witness",
            "thermal_potential_boundary": "Omega_thermal(A,T) is evaluated only where both quadratic roots are positive",
        },
        "units": {
            "unit_lane": "natural",
            "A_squared_q_lambda": "natural amplitude squared",
            "r_sigma_r_pi": "natural mass squared",
            "Phi": "fixed action response input; no SI map",
        },
        "scope": {
            "background": "homogeneous condensed O(2) amplitude at fixed Phi",
            "thermal_order": "quadratic Gaussian determinant only",
            "boundary_type": "quadratic stability boundary, not self-consistent finite-temperature stationary boundary",
            "vacuum_counterterm": "NOT_INCLUDED",
            "interacting_self_energy": "NOT_INCLUDED",
            "normal_two_fluid_completion": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "not identified with amplitude, mass, or charge",
            "Phi": "fixed effective response input; not temperature, metric, or particle",
            "R_gen": "derived history trace only; absent from the determinant and has no feedback",
            "R_obs": "not included in the action-derived lane",
        },
        "data_role": "ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY",
        "claim_boundary": "This closes the analytic lower boundary of the declared quadratic condensed stability domain and records a thermal-only one-sided witness. It does not close a renormalized finite-temperature effective action, an interior stationary phase boundary, interacting self-energy, transport, microscopic SK/KMS matching, SI Phi calibration, external validation, or Full Topic 13.",
    }


__all__ = [
    "O2ThermalStabilityBoundary",
    "thermal_stability_boundary",
    "phase_curvature_at_amplitude",
    "mode_stability_witness",
    "uet_o2_thermal_stability_boundary_contract",
]
