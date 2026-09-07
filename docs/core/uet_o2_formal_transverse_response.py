"""Formal static transverse quasiparticle response for Topic 13.

The declared thermal quasiparticle branches are given a small isotropic
Doppler shift ``E_a(k; v)=E_a(k)+k.v+O(v^2)``.  The resulting positive
static momentum susceptibility is a formal natural-unit response of the
approximate determinant.  It is not a retarded Kubo coefficient and is not
relabeled as a Landau normal mass density.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    effective_mass_sq,
    condensate_control,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    condensed_quasiparticle_energies,
)


FORMAL_TRANSVERSE_RESPONSE_STATUS = "PASS_FORMAL_STATIC_TRANSVERSE_QUASIPARTICLE_RESPONSE"


@dataclass(frozen=True)
class FormalTransverseResponse:
    """Static response quantities at one natural-unit equilibrium state."""

    branch: str
    temperature: float
    chemical_potential: float
    space_response: float
    normal_momentum_susceptibility: float
    condensate_phase_stiffness: float
    quadrature_order: int
    cutoff_factor: float
    data_role: str = "ACTION_DERIVED_FORMAL_STATIC_RESPONSE_NOT_KUBO"


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return result


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    return 0.5 * cutoff * (nodes + 1.0), 0.5 * cutoff * weights


def _minus_bose_derivative(energy: float, temperature: float) -> float:
    x = _positive(energy / temperature, "dimensionless Bose argument")
    if x > 50.0:
        occupation = exp(-x)
    else:
        occupation = 1.0 / expm1(x)
    return occupation * (1.0 + occupation) / temperature


def _branch_energies(
    momentum: float,
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> tuple[float, ...]:
    del temperature
    q = condensate_control(chemical_potential, space_response, config.eos)
    tolerance = config.phase_tolerance
    if q > tolerance:
        return condensed_quasiparticle_energies(
            momentum, chemical_potential, space_response, config
        )
    if q < -tolerance:
        mass_sq = effective_mass_sq(space_response, config.eos)
        if mass_sq <= 0.0:
            raise ValueError("effective mass squared must be positive")
        z = _positive(config.eos.matter.matter_kinetic, "matter_kinetic")
        mass = sqrt(mass_sq / z)
        mu_eff = abs(float(chemical_potential))
        if mu_eff >= mass:
            raise ValueError("normal branch requires effective chemical potential below mass")
        energy = sqrt(momentum * momentum + mass_sq / z)
        return (energy - mu_eff, energy + mu_eff)
    raise ValueError("the critical phase boundary is not evaluated")


def formal_transverse_quasiparticle_response(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> FormalTransverseResponse:
    """Return the static Doppler-response witness and tree phase stiffness.

    The response is

    ``chi_perp^qp = (1/3) sum_a integral d^3k/(2*pi)^3 k^2
    [-partial n_B(E_a)/partial E_a]``.

    ``chi_perp^qp`` is a momentum-susceptibility proxy for the declared
    quasiparticle determinant.  It is not a retarded correlator or an SI
    transport coefficient.
    """

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    t = _positive(temperature, "temperature")
    mu = float(chemical_potential)
    phi = float(space_response)
    if not isfinite(mu) or not isfinite(phi):
        raise ValueError("chemical_potential and space_response must be finite")
    q = condensate_control(mu, phi, config.eos)
    branch = "condensed" if q > config.phase_tolerance else "normal"
    mass_sq = effective_mass_sq(phi, config.eos)
    z = _positive(config.eos.matter.matter_kinetic, "matter_kinetic")
    mass = sqrt(_positive(mass_sq, "effective_mass_squared") / z)
    mu_eff = abs(mu)
    cutoff = max(
        config.cutoff_factor * t,
        config.cutoff_factor * mass,
        config.cutoff_factor * mu_eff,
        1.0,
    )
    momenta, weights = _quadrature(config.quadrature_order, cutoff)
    integrand = []
    for momentum in momenta:
        energies = _branch_energies(float(momentum), t, mu, phi, config)
        integrand.append(
            sum(_minus_bose_derivative(float(energy), t) for energy in energies)
        )
    susceptibility = float(
        np.sum(
            weights
            * momenta**4
            / (6.0 * pi**2)
            * np.asarray(integrand, dtype=float)
        )
    )
    phase_stiffness = float(
        z * q / _positive(config.eos.matter.matter_quartic, "matter_quartic")
    ) if q > config.phase_tolerance else 0.0
    values = (susceptibility, phase_stiffness)
    if not all(isfinite(value) and value >= 0.0 for value in values):
        raise FloatingPointError("formal transverse response is non-finite or negative")
    return FormalTransverseResponse(
        branch=branch,
        temperature=t,
        chemical_potential=mu,
        space_response=phi,
        normal_momentum_susceptibility=susceptibility,
        condensate_phase_stiffness=phase_stiffness,
        quadrature_order=int(config.quadrature_order),
        cutoff_factor=float(config.cutoff_factor),
    )


def formal_transverse_response_contract() -> dict[str, object]:
    """Return equations, units, and the non-promotion boundary."""

    return {
        "status": FORMAL_TRANSVERSE_RESPONSE_STATUS,
        "response_policy": "FIXED_PHI_BACKGROUND",
        "spectrum_revision": "FIXED_PHI_CANONICAL_V2",
        "equations": {
            "normal_quasiparticles": "E_+/-=sqrt(k^2+m_eff^2/Z) +/- mu",
            "normal_enthalpy_check": "chi_perp=epsilon+p for the ideal relativistic normal gas only",
            "doppler_shift": "E_a(k;v)=E_a(k)+k.v+O(v^2)",
            "normal_momentum_susceptibility": "chi_perp_qp=(1/3) sum_a integral[d^3k/(2*pi)^3] k^2[-partial_E n_B(E_a)]",
            "tree_condensate_phase_stiffness": "f_s_tree=Z*(Z*mu^2-m_eff^2)/lambda for condensed q>0",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "chi_perp_qp": "formal natural-unit momentum susceptibility",
            "f_s_tree": "natural-unit phase stiffness",
            "normal_density_label": "not Landau normal mass density",
            "Phi": "effective response input; not temperature",
            "C": "not relabeled as charge density",
            "R_gen": "derived history trace only; not a state or feedback term",
        },
        "derivation_class": "action-derived approximate quasiparticle Doppler-response integral plus tree condensate stiffness",
        "observable": "formal static transverse quasiparticle momentum response",
        "data_role": "ACTION_DERIVED_FORMAL_STATIC_RESPONSE_NOT_KUBO",
        "excluded_scope": "retarded Kubo coefficient, interacting self-energy, full SK/KMS matching, heat flux, SI map, alpha_Phi_K, TTG validation, and external validation",
        "claim_boundary": "This closes a formal static response witness only. It is not a physical Kubo match, Landau normal density, complete two-fluid transport theory, SI calibration, or external validation.",
    }


__all__ = [
    "FORMAL_TRANSVERSE_RESPONSE_STATUS",
    "FormalTransverseResponse",
    "formal_transverse_quasiparticle_response",
    "formal_transverse_response_contract",
]
