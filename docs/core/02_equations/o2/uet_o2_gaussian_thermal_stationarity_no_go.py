"""Scoped no-go for thermal-only Gaussian condensate stationarity.

For the declared tree potential plus stable off-shell Gaussian determinant,
the derivative with respect to ``x=A^2`` is positive throughout the condensed
stable domain ``x >= q/lambda``.  This closes only the thermal-only Gaussian
stationarity question; vacuum counterterms and interacting self-energy can
change the conclusion and remain separate branches.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
)
from docs.core.uet_o2_gaussian_offshell_background import off_shell_mode_omega_sq


@dataclass(frozen=True)
class O2GaussianThermalStationarityNoGo:
    """Proof data for the thermal-only Gaussian stationarity no-go."""

    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    condensate_control: float
    quartic_coupling: float
    kinetic_coefficient: float
    x_boundary: float
    unit_lane: str = "natural"
    thermal_only: bool = True
    stable_domain: str = "x=A^2 >= q/lambda"
    vacuum_counterterm_included: bool = False
    interacting_self_energy_included: bool = False
    no_go_scope: str = "tree potential plus stable thermal Gaussian determinant"
    data_role: str = "ACTION_DERIVED_THERMAL_GAUSSIAN_STATIONARITY_NO_GO"


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def stationarity_no_go_contract() -> dict[str, Any]:
    """Return the algebraic no-go proof and its explicit boundary."""

    return {
        "status": "SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY",
        "equations": {
            "x_definition": "x=A^2",
            "condensed_control": "q=Z*mu^2-m_eff(Phi)^2 > 0",
            "stable_domain": "x >= q/lambda from r_pi=-q+lambda*x >= 0",
            "tree_derivative": "partial_x Omega_tree=0.5*(-q+lambda*x) >= 0",
            "mode_roots": "omega_+-^2=k^2+0.5*(a_sigma+a_pi+4*mu^2) +- 0.5*sqrt(D)",
            "curvature_entries": "a_sigma=(-q+3*lambda*x)/Z; a_pi=(-q+lambda*x)/Z",
            "discriminant": "D=(a_sigma-a_pi)^2+8*mu^2*(a_sigma+a_pi)+16*mu^4+16*mu^2*k^2",
            "mode_derivatives": "partial_x omega_+-^2=2*lambda/Z +- partial_x(sqrt(D))/2",
            "thermal_derivative": "partial_(omega^2)[T*log(1-exp(-omega/T))]=n_B(omega/T)/(2*omega) > 0",
            "no_go": "partial_x(Omega_tree+Omega_G)>0 for T>0, x>=q/lambda, and stable modes; no stationary point exists in this scoped domain",
        },
        "proof_assumptions": [
            "T > 0",
            "q > 0",
            "lambda > 0",
            "Z > 0",
            "x >= q/lambda",
            "both quadratic mode roots are positive for k>0",
        ],
        "scope": {
            "included": "tree homogeneous potential plus thermal Gaussian quadratic determinant",
            "vacuum_counterterm": "NOT_INCLUDED",
            "interacting_self_energy": "NOT_INCLUDED",
            "renormalized_finite_temperature_action": "NOT_INCLUDED",
            "normal_two_fluid_completion": "NOT_INCLUDED",
            "physical_kubo": "NOT_INCLUDED",
            "sk_kms": "NOT_MATCHED_MICROSCOPICALLY",
        },
        "ontology": {
            "C": "not identified with amplitude A, mass, or charge",
            "Phi": "fixed effective response input; not temperature, metric, or particle",
            "R_gen": "derived history trace only; absent from the determinant and has no feedback",
            "R_obs": "not included in the action-derived lane",
        },
        "data_role": "ACTION_DERIVED_THERMAL_GAUSSIAN_STATIONARITY_NO_GO",
        "claim_boundary": "This is a scoped algebraic no-go for a stationary condensate within the declared tree plus stable thermal Gaussian domain. It does not rule out a stationary solution after vacuum renormalization, finite-temperature self-energy, interactions, or a different branch, and it does not close a physical finite-temperature phase transition, EOS, transport, SI map, or Full Topic 13.",
    }


def thermal_gaussian_stationarity_no_go(
    chemical_potential: float,
    space_response: float,
    config: O2FiniteDensityEOSConfig,
) -> O2GaussianThermalStationarityNoGo:
    """Return the scoped no-go proof data for a condensed control point."""

    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    mass_sq = float(effective_mass_sq(phi, config))
    z = float(config.matter.matter_kinetic)
    quartic = float(config.matter.matter_quartic)
    q = z * mu * mu - mass_sq
    if q <= 0.0:
        raise ValueError("thermal Gaussian stationarity no-go requires q > 0")
    if z <= 0.0 or quartic <= 0.0:
        raise ValueError("thermal Gaussian stationarity no-go requires Z>0 and lambda>0")
    x_boundary = q / quartic
    values = (mass_sq, q, z, quartic, x_boundary)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("thermal Gaussian stationarity no-go is not finite")
    return O2GaussianThermalStationarityNoGo(
        chemical_potential=mu,
        space_response=phi,
        effective_mass_sq=mass_sq,
        condensate_control=q,
        quartic_coupling=quartic,
        kinetic_coefficient=z,
        x_boundary=x_boundary,
    )


def mode_omega_sq_x_derivatives(
    wavenumber: float,
    x: float,
    chemical_potential: float,
    proof: O2GaussianThermalStationarityNoGo,
) -> tuple[float, float, float, float, float]:
    """Return roots, their x-derivatives, and the discriminant margin.

    The derivative is analytic in ``x=A^2``.  The returned margin is
    ``4*D-(L*x+8*mu^2)^2`` with ``L=2*lambda/Z``; positivity of this margin
    proves the lower-root derivative is positive in the stated domain.
    """

    k = _finite(wavenumber, "wavenumber")
    x = _finite(x, "x")
    mu = proof.chemical_potential
    if k < 0.0 or x < proof.x_boundary:
        raise ValueError("mode derivative witness requires k>=0 and x>=x_boundary")
    if x == 0.0:
        raise ValueError("mode derivative witness requires positive x")
    lam = proof.quartic_coupling
    z = proof.kinetic_coefficient
    q = proof.condensate_control
    a_sigma = (-q + 3.0 * lam * x) / z
    a_pi = (-q + lam * x) / z
    discriminant = (
        (a_sigma - a_pi) ** 2
        + 8.0 * mu * mu * (a_sigma + a_pi)
        + 16.0 * mu**4
        + 16.0 * mu * mu * k * k
    )
    if discriminant <= 0.0:
        raise FloatingPointError("mode derivative requires positive discriminant")
    root = sqrt(discriminant)
    base = k * k + 0.5 * (a_sigma + a_pi + 4.0 * mu * mu)
    low = base - 0.5 * root
    high = base + 0.5 * root
    L = 2.0 * lam / z
    derivative_discriminant = 2.0 * L * L * x + 16.0 * mu * mu * L
    base_derivative = L
    root_derivative = derivative_discriminant / (4.0 * root)
    low_derivative = base_derivative - root_derivative
    high_derivative = base_derivative + root_derivative
    margin = 4.0 * discriminant - (L * x + 8.0 * mu * mu) ** 2
    values = (low, high, low_derivative, high_derivative, margin)
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("mode derivative witness is not finite")
    return float(low), float(high), float(low_derivative), float(high_derivative), float(margin)


def tree_derivative_x(x: float, proof: O2GaussianThermalStationarityNoGo) -> float:
    """Return the tree grand-potential derivative with respect to x=A^2."""

    x = _finite(x, "x")
    if x < proof.x_boundary:
        raise ValueError("tree derivative witness requires x>=x_boundary")
    return float(0.5 * (-proof.condensate_control + proof.quartic_coupling * x))


__all__ = [
    "O2GaussianThermalStationarityNoGo",
    "stationarity_no_go_contract",
    "thermal_gaussian_stationarity_no_go",
    "mode_omega_sq_x_derivatives",
    "tree_derivative_x",
]
