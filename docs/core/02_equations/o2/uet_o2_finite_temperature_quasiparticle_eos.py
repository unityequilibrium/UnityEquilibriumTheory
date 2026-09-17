"""Finite-temperature O(2) quasiparticle EOS lane for Topic 13.

This module adds a deliberately named approximation to the covariant O(2)
action: the tree-level condensate branch is combined with the thermal
quasiparticle determinant, while vacuum counterterms and interacting thermal
self-energy corrections are excluded.  It is useful for closing the
thermodynamic identities of a finite-temperature lane, but it is not a Kubo
transport calculation or an SI observable map.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, expm1, isfinite, log, log1p, pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    condensate_control,
    effective_mass_sq,
)


FINITE_T_QUASIPARTICLE_EOS_STATUS = (
    "PASS_ACTION_DERIVED_TREE_CONDENSATE_THERMAL_QUASIPARTICLE_EOS"
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


def _quadrature(order: int, cutoff: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 32:
        raise ValueError("quadrature_order must be an integer >= 32")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    return 0.5 * cutoff * (nodes + 1.0), 0.5 * cutoff * weights


def _thermal_log(argument: float) -> float:
    """Return ``-log(1-exp(-argument))`` for a positive argument."""

    x = _positive(argument, "thermal argument")
    if x > 50.0:
        return exp(-x)
    if x > log(2.0):
        return -log1p(-exp(-x))
    return -log(-expm1(-x))


@dataclass(frozen=True)
class FiniteTemperatureO2QuasiparticleConfig:
    """Numerical controls for the named finite-temperature EOS lane."""

    eos: O2FiniteDensityEOSConfig = field(default_factory=O2FiniteDensityEOSConfig)
    quadrature_order: int = 192
    cutoff_factor: float = 70.0
    derivative_step: float = 1.0e-4
    phase_tolerance: float = 1.0e-10

    def __post_init__(self) -> None:
        if self.eos.unit_lane != "natural":
            raise NotImplementedError("the quasiparticle lane requires natural units")
        _positive(self.cutoff_factor, "cutoff_factor")
        _positive(self.derivative_step, "derivative_step")
        _positive(self.phase_tolerance, "phase_tolerance")
        if isinstance(self.quadrature_order, bool) or int(self.quadrature_order) != self.quadrature_order:
            raise ValueError("quadrature_order must be an integer")
        if int(self.quadrature_order) < 32:
            raise ValueError("quadrature_order must be at least 32")


@dataclass(frozen=True)
class FiniteTemperatureO2State:
    """Thermodynamic state on either the normal or condensed branch."""

    branch: str
    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    condensate_amplitude: float
    pressure: float
    charge_density: float
    entropy_density: float
    energy_density: float
    susceptibility: float
    goldstone_energy_at_zero_momentum: float
    data_role: str = "ACTION_DERIVED_APPROXIMATE_EOS_NOT_TRANSPORT"


def _effective_chemical_potential(
    chemical_potential: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    # Canonical field normalization rescales mass, not time or chemical potential.
    return abs(
        _finite(chemical_potential, "chemical_potential")
    )


def _condensed_amplitude_sq(
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    q = condensate_control(chemical_potential, space_response, config.eos)
    if q <= config.phase_tolerance:
        raise ValueError("the condensed quasiparticle lane requires q > tolerance")
    quartic = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    return q / quartic


def condensed_quasiparticle_energies(
    momentum: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> tuple[float, float]:
    """Return the two tree-background O(2) quasiparticle energies.

    With ``A`` fixed by the tree stationary condition, the branches are

    ``E_+/-^2 = k^2+B +/- sqrt(B^2+4 mu^2 k^2)``,

    where ``B=2 mu^2+lambda A^2/Z``. Phi is held fixed; this is not
    the three-mode live-Phi spectrum. The lower root is rationalized
    to retain its small-momentum limit without clipping.
    """

    k = _finite(momentum, "momentum")
    if k < 0.0:
        raise ValueError("momentum must be non-negative")
    mu = _finite(chemical_potential, "chemical_potential")
    mass_sq = effective_mass_sq(space_response, config.eos)
    if mass_sq <= 0.0:
        raise ValueError("effective mass squared must be positive")
    z = _positive(config.eos.matter.matter_kinetic, "matter_kinetic")
    lam = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    amplitude_sq = _condensed_amplitude_sq(mu, space_response, config)
    radial_control = lam * amplitude_sq / z
    b_value = 2.0 * mu * mu + radial_control
    upper_sq = k * k + b_value + sqrt(
        b_value * b_value + 4.0 * mu * mu * k * k
    )
    lower_sq = k * k * (k * k + 2.0 * radial_control) / upper_sq
    if not all(isfinite(value) for value in (upper_sq, lower_sq)):
        raise FloatingPointError("quasiparticle energies must be finite")
    return sqrt(upper_sq), sqrt(lower_sq)


def _thermal_pressure_normal(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    t = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    mass_sq = effective_mass_sq(space_response, config.eos)
    if mass_sq <= 0.0:
        raise ValueError("effective mass squared must be positive")
    z = _positive(config.eos.matter.matter_kinetic, "matter_kinetic")
    mass = sqrt(mass_sq / z)
    mu_eff = _effective_chemical_potential(mu, config)
    if mu_eff >= mass:
        raise ValueError("normal branch requires effective chemical potential below mass")
    cutoff = max(
        config.cutoff_factor * t,
        config.cutoff_factor * mass,
        config.cutoff_factor * mu_eff,
        1.0,
    )
    momenta, weights = _quadrature(config.quadrature_order, cutoff)
    energy = np.sqrt(momenta * momenta + mass_sq / z)
    measure = momenta * momenta / (2.0 * pi**2)
    values = np.array(
        [
            _thermal_log(float((value - mu_eff) / t))
            + _thermal_log(float((value + mu_eff) / t))
            for value in energy
        ],
        dtype=float,
    )
    return float(t * np.sum(weights * measure * values))


def _thermal_pressure_condensed(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    t = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    mass_sq = effective_mass_sq(space_response, config.eos)
    if mass_sq <= 0.0:
        raise ValueError("effective mass squared must be positive")
    z = _positive(config.eos.matter.matter_kinetic, "matter_kinetic")
    mass = sqrt(mass_sq / z)
    mu_eff = _effective_chemical_potential(mu, config)
    amplitude_sq = _condensed_amplitude_sq(mu, space_response, config)
    lam = _positive(config.eos.matter.matter_quartic, "matter_quartic")
    q = condensate_control(mu, space_response, config.eos)
    tree_pressure = q * q / (4.0 * lam)
    cutoff = max(
        config.cutoff_factor * t,
        config.cutoff_factor * mass,
        config.cutoff_factor * mu_eff,
        config.cutoff_factor * sqrt(lam * amplitude_sq / z),
        1.0,
    )
    momenta, weights = _quadrature(config.quadrature_order, cutoff)
    thermal_integrand = []
    for momentum in momenta:
        e_plus, e_minus = condensed_quasiparticle_energies(
            float(momentum), mu, space_response, config
        )
        thermal_integrand.append(
            _thermal_log(e_plus / t) + _thermal_log(e_minus / t)
        )
    measure = momenta * momenta / (2.0 * pi**2)
    thermal_pressure = float(t * np.sum(weights * measure * np.asarray(thermal_integrand)))
    return float(tree_pressure + thermal_pressure)


def quasiparticle_pressure(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> float:
    """Return the declared tree-condensate plus thermal quasiparticle pressure."""

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    t = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    q = condensate_control(mu, phi, config.eos)
    if q > config.phase_tolerance:
        return _thermal_pressure_condensed(t, mu, phi, config)
    if q < -config.phase_tolerance:
        return _thermal_pressure_normal(t, mu, phi, config)
    raise ValueError("the critical phase boundary is one-sided and not evaluated")


def _central_difference(function, value: float, step: float) -> float:
    h = step * max(1.0, abs(float(value)))
    return (function(value + h) - function(value - h)) / (2.0 * h)


def finite_temperature_o2_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
) -> FiniteTemperatureO2State:
    """Evaluate the normal or condensed thermodynamic branch."""

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    t = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    q = condensate_control(mu, phi, config.eos)
    branch = "condensed" if q > config.phase_tolerance else "normal"
    pressure = quasiparticle_pressure(t, mu, phi, config)
    pressure_mu = lambda candidate: quasiparticle_pressure(t, candidate, phi, config)
    pressure_t = lambda candidate: quasiparticle_pressure(candidate, mu, phi, config)
    charge_density = _central_difference(pressure_mu, mu, config.derivative_step)
    entropy_density = _central_difference(pressure_t, t, config.derivative_step)
    susceptibility = _central_difference(
        lambda candidate: _central_difference(
            lambda nested: quasiparticle_pressure(t, nested, phi, config),
            candidate,
            config.derivative_step,
        ),
        mu,
        config.derivative_step,
    )
    energy_density = -pressure + t * entropy_density + mu * charge_density
    mass_sq = effective_mass_sq(phi, config.eos)
    amplitude = (
        sqrt(_condensed_amplitude_sq(mu, phi, config)) if branch == "condensed" else 0.0
    )
    goldstone = (
        condensed_quasiparticle_energies(0.0, mu, phi, config)[1]
        if branch == "condensed"
        else float("nan")
    )
    values = (
        pressure,
        charge_density,
        entropy_density,
        energy_density,
        susceptibility,
    )
    if not all(isfinite(value) for value in values):
        raise FloatingPointError("finite-temperature EOS produced a non-finite value")
    return FiniteTemperatureO2State(
        branch=branch,
        temperature=t,
        chemical_potential=mu,
        space_response=phi,
        effective_mass=sqrt(mass_sq),
        condensate_amplitude=amplitude,
        pressure=pressure,
        charge_density=charge_density,
        entropy_density=entropy_density,
        energy_density=energy_density,
        susceptibility=susceptibility,
        goldstone_energy_at_zero_momentum=goldstone,
    )


def finite_temperature_o2_quasiparticle_contract() -> dict[str, object]:
    """Return the lane equations and its explicit non-promotion boundary."""

    return {
        "status": FINITE_T_QUASIPARTICLE_EOS_STATUS,
        "response_policy": "FIXED_PHI_BACKGROUND",
        "spectrum_revision": "FIXED_PHI_CANONICAL_V2",
        "equations": {
            "tree_grand_potential": "Omega_0=(m_eff^2-Z*mu^2)A^2/2+lambda*A^4/4",
            "condensate": "A_*^2=(Z*mu^2-m_eff^2)/lambda for q>0",
            "quasiparticles": "E_+/-^2=k^2+B +/- sqrt(B^2+4*mu^2*k^2); B=2*mu^2+lambda*A_*^2/Z",
            "normal_quasiparticles": "E_+/-=sqrt(k^2+m_eff^2/Z) +/- mu",
            "canonical_field_map": "chi_c=sqrt(Z)*chi; m_c^2=m_eff^2/Z; lambda_c=lambda/Z^2",
            "determinant": "(E^2-k^2)*(E^2-k^2-2*q/Z)-4*mu^2*E^2=0",
            "pressure": "p_2f=-Omega_0(A_*)+p_qp(T,mu,Phi)",
            "thermodynamic_derivatives": "n=partial_mu p; s=partial_T p; epsilon=-p+T*s+mu*n",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "T_mu_m_eff": "natural energy",
            "effective_mass_field": "sqrt(m_eff^2) is retained as the mass parameter; the normal canonical gap is sqrt(m_eff^2/Z)",
            "p_epsilon": "natural energy density",
            "n": "natural charge density",
            "s": "natural entropy density",
            "Phi": "action response input; not temperature",
            "C": "not relabeled as charge density",
        },
        "closed_scope": "fixed-Phi tree condensate plus thermal quasiparticle thermodynamic lane with normal and condensed branches",
        "excluded_scope": "vacuum counterterm completion, interacting thermal self-energy, physical Kubo/transport/SK-KMS matching, heat flux, SI Phi map, alpha_Phi_K, and TTG validation",
        "R_gen": "derived history trace only; not a state or feedback term",
        "data_role": "ACTION_DERIVED_APPROXIMATE_EOS_NOT_TRANSPORT",
        "claim_boundary": "This is an action-derived approximate finite-temperature EOS lane. It is not a complete interacting two-fluid theory, physical transport closure, SI calibration, or external validation.",
    }


__all__ = [
    "FINITE_T_QUASIPARTICLE_EOS_STATUS",
    "FiniteTemperatureO2QuasiparticleConfig",
    "FiniteTemperatureO2State",
    "condensed_quasiparticle_energies",
    "quasiparticle_pressure",
    "finite_temperature_o2_state",
    "finite_temperature_o2_quasiparticle_contract",
]
