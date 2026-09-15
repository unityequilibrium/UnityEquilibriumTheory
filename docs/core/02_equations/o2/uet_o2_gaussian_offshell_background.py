"""Off-shell finite-temperature Gaussian background boundary for the O(2) lane.

This module extends the declared natural-unit O(2) quadratic determinant from
the tree-level stationary amplitude to an arbitrary homogeneous amplitude
``A`` at fixed ``Phi``.  It evaluates only the thermal Bose contribution on
the stable part of that off-shell branch.  Vacuum terms, interacting
self-energy, and a self-consistent renormalized phase boundary remain outside
the lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi, sqrt
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)


@dataclass(frozen=True)
class O2GaussianOffShellBackgroundState:
    """Thermal-only Gaussian potential for a homogeneous O(2) amplitude."""

    temperature: float
    chemical_potential: float
    space_response: float
    amplitude: float
    condensate_control: float
    radial_curvature: float
    phase_curvature: float
    tree_grand_potential: float
    thermal_grand_potential: float
    grand_potential: float
    momentum_cutoff: float
    quadrature_order: int
    unit_lane: str = "natural"
    thermal_only: bool = True
    vacuum_counterterm_included: bool = False
    interacting_self_energy_included: bool = False
    response_fluctuation_included: bool = False
    data_role: str = (
        "ACTION_DERIVED_OFFSHELL_GAUSSIAN_THERMAL_BACKGROUND_BOUNDARY"
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


def off_shell_curvatures(
    amplitude: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> tuple[float, float, float]:
    """Return ``(q, r_sigma, r_pi)`` for the homogeneous rotating background.

    The two curvatures are the Hessian entries before division by the matter
    kinetic coefficient ``Z``.  At ``A^2=q/lambda`` they reduce to ``(2q,0)``
    and therefore recover the existing stationary condensate determinant.
    """

    amplitude = _finite(amplitude, "amplitude")
    if amplitude < 0.0:
        raise ValueError("amplitude must be non-negative")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(phi, config))
    z = float(config.matter.matter_kinetic)
    quartic = float(config.matter.matter_quartic)
    q = z * mu * mu - mass_sq
    amplitude_sq = amplitude * amplitude
    radial = -q + 3.0 * quartic * amplitude_sq
    phase = -q + quartic * amplitude_sq
    return float(q), float(radial), float(phase)


def off_shell_mode_omega_sq(
    wavenumber: float,
    amplitude: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> tuple[float, float]:
    """Return the two off-shell quadratic roots, which may be negative.

    With ``a_sigma=r_sigma/Z`` and ``a_pi=r_pi/Z``, the determinant is

    ``(y-k^2-a_sigma)(y-k^2-a_pi)-4*mu^2*y``.

    Negative roots are returned rather than clipped so the audit can expose
    an unstable background instead of hiding it.
    """

    k = _finite(wavenumber, "wavenumber")
    if k < 0.0:
        raise ValueError("wavenumber must be non-negative")
    mu = _finite(chemical_potential, "chemical_potential")
    q, radial, phase = off_shell_curvatures(
        amplitude, mu, space_response, config
    )
    del q
    z = float(config.matter.matter_kinetic)
    a_sigma = radial / z
    a_pi = phase / z
    sum_term = a_sigma + a_pi + 4.0 * mu * mu
    discriminant = (
        (a_sigma - a_pi) ** 2
        + 8.0 * mu * mu * (a_sigma + a_pi)
        + 16.0 * mu**4
        + 16.0 * mu * mu * k * k
    )
    if discriminant < -1.0e-12:
        raise FloatingPointError("off-shell mode discriminant is negative")
    root = sqrt(max(discriminant, 0.0))
    base = k * k + 0.5 * sum_term
    return float(base - 0.5 * root), float(base + 0.5 * root)


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    momenta = 0.5 * cutoff * (nodes + 1.0)
    scaled_weights = 0.5 * cutoff * weights
    return momenta, scaled_weights


def _cutoff(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    amplitude: float,
    config: O2FiniteDensityEOSConfig,
    cutoff_factor: float,
) -> float:
    factor = _positive(cutoff_factor, "cutoff_factor")
    mass_sq = float(effective_mass_sq(space_response, config))
    _, radial, phase = off_shell_curvatures(
        amplitude, chemical_potential, space_response, config
    )
    scale = max(
        temperature,
        abs(chemical_potential),
        sqrt(max(mass_sq, 0.0)),
        sqrt(abs(radial) / config.matter.matter_kinetic),
        sqrt(abs(phase) / config.matter.matter_kinetic),
        1.0,
    )
    return factor * scale


def tree_grand_potential(
    amplitude: float,
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return the tree-level homogeneous grand-potential density."""

    amplitude = _finite(amplitude, "amplitude")
    if amplitude < 0.0:
        raise ValueError("amplitude must be non-negative")
    mu = _finite(chemical_potential, "chemical_potential")
    mass_sq = float(effective_mass_sq(space_response, config))
    z = float(config.matter.matter_kinetic)
    quartic = float(config.matter.matter_quartic)
    return float(0.5 * (mass_sq - z * mu * mu) * amplitude**2 + 0.25 * quartic * amplitude**4)


def off_shell_gaussian_thermal_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    amplitude: float,
    config: O2FiniteDensityEOSConfig,
    *,
    quadrature_order: int = 192,
    cutoff_factor: float = 70.0,
) -> O2GaussianOffShellBackgroundState:
    """Evaluate the thermal determinant when both off-shell roots are stable."""

    temperature = _positive(temperature, "temperature")
    amplitude = _finite(amplitude, "amplitude")
    if amplitude < 0.0:
        raise ValueError("amplitude must be non-negative")
    cutoff = _cutoff(
        temperature,
        chemical_potential,
        space_response,
        amplitude,
        config,
        cutoff_factor,
    )
    momenta, weights = _quadrature(int(quadrature_order), cutoff)
    measure = momenta * momenta / (2.0 * pi**2)
    thermal = 0.0
    for index, k in enumerate(momenta):
        low_sq, high_sq = off_shell_mode_omega_sq(
            float(k), amplitude, chemical_potential, space_response, config
        )
        if low_sq <= 0.0 or high_sq <= 0.0:
            raise FloatingPointError(
                "thermal off-shell determinant encountered a non-positive mode"
            )
        low = sqrt(low_sq)
        high = sqrt(high_sq)
        thermal += weights[index] * measure[index] * temperature * (
            np.log1p(-np.exp(-low / temperature))
            + np.log1p(-np.exp(-high / temperature))
        )
    q, radial, phase = off_shell_curvatures(
        amplitude, chemical_potential, space_response, config
    )
    tree = tree_grand_potential(
        amplitude, chemical_potential, space_response, config
    )
    total = tree + thermal
    values = (q, radial, phase, tree, thermal, total)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("off-shell Gaussian potential is not finite")
    return O2GaussianOffShellBackgroundState(
        temperature=temperature,
        chemical_potential=float(chemical_potential),
        space_response=float(space_response),
        amplitude=amplitude,
        condensate_control=q,
        radial_curvature=radial,
        phase_curvature=phase,
        tree_grand_potential=tree,
        thermal_grand_potential=float(thermal),
        grand_potential=float(total),
        momentum_cutoff=cutoff,
        quadrature_order=int(quadrature_order),
    )


def uet_o2_gaussian_offshell_background_contract() -> dict[str, Any]:
    """Return the off-shell boundary scope and explicit exclusions."""

    return {
        "status": "ACTION_DERIVED_OFFSHELL_GAUSSIAN_THERMAL_BACKGROUND_BOUNDARY",
        "equations": {
            "tree_grand_potential": "Omega_tree(A)=0.5*(m_eff(Phi)^2-Z*mu^2)*A^2+0.25*lambda*A^4",
            "radial_curvature": "r_sigma=-q+3*lambda*A^2",
            "phase_curvature": "r_pi=-q+lambda*A^2",
            "off_shell_determinant": "(y-k^2-r_sigma/Z)*(y-k^2-r_pi/Z)-4*mu^2*y=0",
            "thermal_grand_potential": "Omega_G(A,T)=T integral sum_a log(1-exp(-omega_a(A)/T)) d^3k/(2*pi)^3",
            "tree_background": "A_tree^2=q/lambda for q=Z*mu^2-m_eff(Phi)^2>0",
        },
        "units": {
            "unit_lane": "natural",
            "A_mu_T_omega_k": "natural energy powers from the declared O(2) action",
            "grand_potential": "natural thermodynamic density",
            "Phi": "fixed action response input; no SI map",
        },
        "scope": {
            "background": "homogeneous off-shell amplitude at fixed Phi",
            "thermal_order": "Gaussian quadratic Bose determinant only",
            "stable_domain": "both quadratic roots must be positive at quadrature nodes",
            "vacuum_counterterm": "NOT_INCLUDED",
            "interacting_self_energy": "NOT_INCLUDED",
            "normal_two_fluid_completion": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "not identified with matter amplitude A or O(2) charge",
            "Phi": "fixed effective response input; not temperature, metric, or particle",
            "R_gen": "derived history trace only; absent from the determinant and has no feedback",
            "R_obs": "not included in the action-derived lane",
        },
        "data_role": "ACTION_DERIVED_OFFSHELL_GAUSSIAN_THERMAL_BACKGROUND_BOUNDARY",
        "claim_boundary": "This closes the off-shell Hessian and thermal-only stable-domain diagnostic. It does not close a renormalized self-consistent finite-temperature phase boundary, vacuum loop terms, interacting self-energy, normal-fluid transport, microscopic SK/KMS matching, SI Phi calibration, external validation, or global UET closure.",
    }


__all__ = [
    "O2GaussianOffShellBackgroundState",
    "off_shell_curvatures",
    "off_shell_mode_omega_sq",
    "tree_grand_potential",
    "off_shell_gaussian_thermal_state",
    "uet_o2_gaussian_offshell_background_contract",
]
