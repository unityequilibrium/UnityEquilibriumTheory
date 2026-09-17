"""Tree-level finite-density equation of state for the covariant O(2) pilot.

The conservative matter action in :mod:`docs.core.uet_covariant_matter` can be
written in polar variables ``chi=A exp(i theta)``.  For a homogeneous phase
``theta=-mu*t`` its equilibrium grand-potential density is

``Omega=(m_eff^2-Z*mu^2) A^2/2 + lambda A^4/4``.

This module performs only that tree-level mean-field reduction.  It does not
derive transport coefficients, a finite-temperature normal component, the
phase-field gradient coefficient, or an SI conversion.  The response scalar
changes ``m_eff^2`` through the same reciprocal action coupling already used
by the covariant matter pilot.  A derived history trace is neither accepted
nor used as feedback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, sqrt
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import (
    CovariantResponseConfig,
    response_displacement,
)

O2_FINITE_DENSITY_EOS_STATUS: Final[str] = (
    "TREE_LEVEL_FINITE_DENSITY_O2_MEAN_FIELD_DERIVATION"
)
O2_FINITE_DENSITY_EOS_CONTROLLER: Final[str] = (
    "covariant_superfluid_kubo_transport_and_entropy_matching_missing"
)


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class O2FiniteDensityEOSConfig:
    """Configuration inherited from the conservative response/matter action."""

    matter: CovariantMatterConfig = field(default_factory=CovariantMatterConfig)
    response: CovariantResponseConfig = field(
        default_factory=CovariantResponseConfig
    )
    branch_tolerance: float = 1.0e-12
    inversion_tolerance: float = 1.0e-13
    inversion_max_iterations: int = 256
    phase_convention: str = "theta_equals_minus_mu_t"
    metric_signature: str = "minus_plus_plus_plus"
    unit_lane: str = "natural"

    def __post_init__(self) -> None:
        if self.matter.unit_lane != "natural":
            raise NotImplementedError("EOS v1 requires natural-unit matter input")
        if self.response.unit_lane != "natural":
            raise NotImplementedError("EOS v1 requires natural-unit response input")
        if not isfinite(float(self.branch_tolerance)) or self.branch_tolerance <= 0:
            raise ValueError("branch_tolerance must be positive and finite")
        if (
            not isfinite(float(self.inversion_tolerance))
            or self.inversion_tolerance <= 0
        ):
            raise ValueError("inversion_tolerance must be positive and finite")
        if (
            isinstance(self.inversion_max_iterations, bool)
            or int(self.inversion_max_iterations) != self.inversion_max_iterations
            or int(self.inversion_max_iterations) < 32
        ):
            raise ValueError("inversion_max_iterations must be an integer >= 32")
        if self.phase_convention != "theta_equals_minus_mu_t":
            raise NotImplementedError(
                "EOS v1 locks theta=-mu*t so positive mu has positive charge"
            )
        if self.metric_signature != "minus_plus_plus_plus":
            raise NotImplementedError("EOS v1 requires metric signature (-,+,+,+)")
        if self.unit_lane != "natural":
            raise NotImplementedError("EOS v1 supports only unit_lane='natural'")


@dataclass(frozen=True)
class O2EOSState:
    """Equilibrium thermodynamic state relative to the normal vacuum branch."""

    branch: str
    chemical_potential: float
    space_response: float
    effective_mass_sq: float
    condensate_control: float
    amplitude: float
    grand_potential: float
    pressure: float
    charge_density: float
    energy_density: float
    susceptibility: float | None
    sound_speed_sq: float | None
    response_source: float
    stability: str
    helmholtz_free_energy: float | None = None
    helmholtz_response_derivative: float | None = None


def effective_mass_sq(
    phi: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return ``m^2-epsilon_nc*h*(Phi-Phi_*)`` from the parent action."""

    response = _finite_scalar(phi, "phi")
    return float(
        config.matter.matter_mass_sq
        - config.response.epsilon_nc
        * config.matter.response_coupling
        * response_displacement(response, config.response)
    )


def condensate_control(
    chemical_potential: float,
    phi: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Return ``q=Z*mu^2-m_eff^2`` selecting the mean-field branch."""

    mu = _finite_scalar(chemical_potential, "chemical_potential")
    return float(config.matter.matter_kinetic * mu * mu - effective_mass_sq(phi, config))


def _branch(q: float, mu: float, mass_sq: float, config: O2FiniteDensityEOSConfig) -> str:
    scale = max(
        1.0,
        abs(config.matter.matter_kinetic * mu * mu),
        abs(mass_sq),
    )
    tolerance = config.branch_tolerance * scale
    if q > tolerance:
        return "condensed"
    if q < -tolerance:
        return "normal"
    return "critical_boundary"


def o2_equilibrium_state(
    chemical_potential: float,
    phi: float,
    config: O2FiniteDensityEOSConfig,
) -> O2EOSState:
    """Return the stable homogeneous grand-canonical tree-level state.

    At the critical boundary the one-sided susceptibility and sound speed are
    deliberately left undefined.  Callers must choose a phase instead of
    silently differentiating through the branch change.
    """

    mu = _finite_scalar(chemical_potential, "chemical_potential")
    response = _finite_scalar(phi, "phi")
    mass_sq = effective_mass_sq(response, config)
    q = config.matter.matter_kinetic * mu * mu - mass_sq
    branch = _branch(q, mu, mass_sq, config)
    if branch != "condensed":
        return O2EOSState(
            branch=branch,
            chemical_potential=mu,
            space_response=response,
            effective_mass_sq=mass_sq,
            condensate_control=q,
            amplitude=0.0,
            grand_potential=0.0,
            pressure=0.0,
            charge_density=0.0,
            energy_density=0.0,
            susceptibility=0.0 if branch == "normal" else None,
            sound_speed_sq=None,
            response_source=0.0,
            stability=("STABLE_NORMAL" if branch == "normal" else "MARGINAL"),
        )

    kinetic = config.matter.matter_kinetic
    quartic = config.matter.matter_quartic
    amplitude_sq = q / quartic
    pressure = q * q / (4.0 * quartic)
    density = kinetic * mu * q / quartic
    susceptibility = kinetic * (3.0 * kinetic * mu * mu - mass_sq) / quartic
    denominator = 3.0 * kinetic * mu * mu - mass_sq
    sound_speed_sq = q / denominator
    response_source = (
        0.5
        * config.response.epsilon_nc
        * config.matter.response_coupling
        * amplitude_sq
    )
    stability = "STABLE_CONDENSED"
    if susceptibility <= 0.0 or not (0.0 <= sound_speed_sq <= 1.0 + 1.0e-12):
        stability = "UNSTABLE_OR_ACAUSAL_PARAMETER_POINT"
    return O2EOSState(
        branch=branch,
        chemical_potential=mu,
        space_response=response,
        effective_mass_sq=mass_sq,
        condensate_control=q,
        amplitude=sqrt(amplitude_sq),
        grand_potential=-pressure,
        pressure=pressure,
        charge_density=density,
        energy_density=mu * density - pressure,
        susceptibility=susceptibility,
        sound_speed_sq=sound_speed_sq,
        response_source=response_source,
        stability=stability,
    )


def _density_on_condensed_branch(
    mu_magnitude: float,
    mass_sq: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    kinetic = config.matter.matter_kinetic
    q = kinetic * mu_magnitude * mu_magnitude - mass_sq
    if q <= 0.0:
        return 0.0
    return kinetic * mu_magnitude * q / config.matter.matter_quartic


def chemical_potential_from_charge_density(
    charge_density: float,
    phi: float,
    config: O2FiniteDensityEOSConfig,
) -> float:
    """Invert the condensed EOS by monotone bracketing, not root ordering.

    For non-zero signed charge there is one stable condensed root with the
    same sign as the charge.  At zero charge the thermodynamic reference
    ``mu=0`` is selected explicitly.
    """

    density = _finite_scalar(charge_density, "charge_density")
    response = _finite_scalar(phi, "phi")
    if density == 0.0:
        return 0.0
    target = abs(density)
    mass_sq = effective_mass_sq(response, config)
    kinetic = config.matter.matter_kinetic
    lower = sqrt(max(mass_sq, 0.0) / kinetic)
    upper = max(
        lower + 1.0,
        2.0
        * (config.matter.matter_quartic * target / (kinetic * kinetic))
        ** (1.0 / 3.0),
    )
    while _density_on_condensed_branch(upper, mass_sq, config) < target:
        upper *= 2.0
        if not isfinite(upper):
            raise RuntimeError("failed to bracket the canonical EOS root")

    scale = max(1.0, target)
    for _ in range(int(config.inversion_max_iterations)):
        midpoint = 0.5 * (lower + upper)
        value = _density_on_condensed_branch(midpoint, mass_sq, config)
        if abs(value - target) <= config.inversion_tolerance * scale:
            return float(np.copysign(midpoint, density))
        if value < target:
            lower = midpoint
        else:
            upper = midpoint
    midpoint = 0.5 * (lower + upper)
    residual = abs(_density_on_condensed_branch(midpoint, mass_sq, config) - target)
    if residual > 10.0 * config.inversion_tolerance * scale:
        raise RuntimeError("canonical EOS inversion did not converge")
    return float(np.copysign(midpoint, density))


def o2_helmholtz_state(
    charge_density: float,
    phi: float,
    config: O2FiniteDensityEOSConfig,
) -> O2EOSState:
    """Return the canonical state ``f(n,Phi)=mu*n-p``."""

    density = _finite_scalar(charge_density, "charge_density")
    mu = chemical_potential_from_charge_density(density, phi, config)
    state = o2_equilibrium_state(mu, phi, config)
    if density != 0.0 and state.branch != "condensed":
        raise RuntimeError("non-zero charge did not select the condensed branch")
    density_scale = max(1.0, abs(density))
    if abs(state.charge_density - density) > 20.0 * config.inversion_tolerance * density_scale:
        raise RuntimeError("canonical EOS inversion failed its density residual")
    free_energy = mu * density - state.pressure
    return O2EOSState(
        **{
            **state.__dict__,
            "charge_density": density,
            "energy_density": free_energy,
            "helmholtz_free_energy": free_energy,
            "helmholtz_response_derivative": -state.response_source,
        }
    )


def o2_eos_derivatives(
    chemical_potential: float,
    phi: float,
    config: O2FiniteDensityEOSConfig,
) -> dict[str, float | str]:
    """Return analytic grand-canonical derivatives away from the phase edge."""

    state = o2_equilibrium_state(chemical_potential, phi, config)
    if state.branch == "critical_boundary":
        raise ValueError(
            "EOS derivatives are one-sided at q=0; choose normal or condensed branch"
        )
    inverse_susceptibility = (
        None
        if state.susceptibility in (None, 0.0)
        else 1.0 / state.susceptibility
    )
    return {
        "branch": state.branch,
        "dp_dmu": state.charge_density,
        "d2p_dmu2": state.susceptibility or 0.0,
        "dp_dphi_at_fixed_mu": state.response_source,
        "df_dphi_at_fixed_n": -state.response_source,
        "d2f_dn2": inverse_susceptibility if inverse_susceptibility is not None else 0.0,
    }


def o2_finite_density_eos_contract() -> dict[str, Any]:
    """Return the exact scope and next unresolved physical layer."""

    return {
        "status": O2_FINITE_DENSITY_EOS_STATUS,
        "conserved_coordinate": "signed_global_O2_Noether_charge_density",
        "phase_convention": "theta=-mu*t",
        "metric_signature": "(-,+,+,+)",
        "unit_lane": "natural",
        "normal_branch": "q<=0_with_boundary_reported_separately",
        "condensed_branch": "q=Z*mu^2-m_eff^2>0",
        "pressure_origin": "tree_level_stationary_O2_grand_potential",
        "canonical_inversion": "deterministic_monotone_stable_branch",
        "response_reciprocity": "same_action_coupling",
        "symmetric_double_well": "CONSTITUTIVE_COMPARATOR_NOT_DERIVED",
        "gradient_coefficient": "OPEN_GRADIENT_EFT_MATCHING",
        "finite_temperature_normal_component": "NOT_DERIVED",
        "transport_coefficients": "NOT_DERIVED_FROM_CONSERVATIVE_ACTION",
        "trace_input": False,
        "trace_backreaction": False,
        "next_controller": O2_FINITE_DENSITY_EOS_CONTROLLER,
    }
