"""Action-derived dilute-gas collision lane for Topic 13 transport.

This lane derives a positive relaxation rate from a declared constant-amplitude
2-to-2 phase-space kernel in the normal O(2) branch.  It is a controlled
kinetic comparator in natural units.  Final-state Bose enhancement is available
only through an explicit elastic outgoing-state factor; ladder vertex
corrections, condensed scattering, and microscopic SK matching remain outside
its scope.  The resulting finite coefficient is therefore not a physical Kubo
value or an SI observable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_density_eos import (
    condensate_control,
    effective_mass_sq,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


KINETIC_COLLISION_KUBO_STATUS = "PASS_ACTION_DERIVED_DILUTE_KINETIC_COLLISION_LANE"


@dataclass(frozen=True)
class KineticCollisionState:
    """Normal-branch comparator; mass and quartic are canonical-field values."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    quartic_coupling: float
    drude_weight_by_species: tuple[float, float]
    collision_width_by_species: tuple[float, float]
    kinetic_coefficient_by_species: tuple[float, float]
    drude_weight: float
    kinetic_coefficient: float
    quadrature_order: int
    angular_order: int
    momentum_cutoff: float
    reference_momentum: float
    final_state_bose_enhancement_included: bool = False
    ladder_vertex_resummation_included: bool = False
    physical_kubo_coefficient_emitted: bool = False
    data_role: str = "ACTION_DERIVED_DILUTE_KINETIC_COMPARATOR_NOT_PHYSICAL_KUBO"


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


def _bose(energy: float, temperature: float) -> float:
    x = _positive(energy / temperature, "Bose argument")
    return exp(-x) if x > 50.0 else 1.0 / expm1(x)


def _quadrature(order: int, upper: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 24:
        raise ValueError("quadrature order must be an integer >= 24")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    return 0.5 * upper * (nodes + 1.0), 0.5 * upper * weights


def _normal_state_inputs(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> tuple[float, float, float, float, float]:
    t = _positive(temperature, "temperature")
    mu = _finite(chemical_potential, "chemical_potential")
    phi = _finite(space_response, "space_response")
    mass_sq = effective_mass_sq(phi, config.eos)
    z = _positive(config.eos.matter.matter_kinetic, "matter kinetic coefficient")
    mass = sqrt(_positive(mass_sq, "effective mass squared") / z)
    # Field normalization does not rescale time or erase the charge sign.
    mu_eff = mu
    if condensate_control(mu, phi, config.eos) >= -config.phase_tolerance:
        raise ValueError("kinetic collision lane requires a strict normal branch")
    if abs(mu_eff) >= mass:
        raise ValueError("normal branch requires chemical potential below the mass")
    quartic = _positive(config.eos.matter.matter_quartic, "quartic coupling") / z**2
    return t, mu, mass, mu_eff, quartic


def _relative_velocity(
    energy_one: float,
    energy_two: float,
    momentum_one: float,
    momentum_two: float,
    cosine: float,
    mass_sq: float,
) -> tuple[float, float]:
    dot = energy_one * energy_two - momentum_one * momentum_two * cosine
    s = 2.0 * (mass_sq + dot)
    if s <= 4.0 * mass_sq:
        return 0.0, max(s, 4.0 * mass_sq)
    flux_sq = dot * dot - mass_sq * mass_sq
    relative = sqrt(max(flux_sq, 0.0)) / (energy_one * energy_two)
    return relative, s


def _final_state_bose_factor(
    energy_one: float,
    energy_two: float,
    momentum_one: float,
    momentum_two: float,
    cosine: float,
    mass_sq: float,
    temperature: float,
    mu_eff: float,
    outgoing_sign_one: float,
    outgoing_sign_two: float,
    final_angle_nodes: np.ndarray,
    final_angle_weights: np.ndarray,
) -> float:
    """Average elastic two-body Bose enhancement in the lab frame."""

    total_energy = energy_one + energy_two
    total_momentum_sq = (
        momentum_one * momentum_one
        + momentum_two * momentum_two
        + 2.0 * momentum_one * momentum_two * cosine
    )
    invariant_s = 2.0 * (mass_sq + energy_one * energy_two - momentum_one * momentum_two * cosine)
    if invariant_s <= 4.0 * mass_sq:
        return 1.0
    root_s = sqrt(invariant_s)
    gamma_cm = total_energy / root_s
    beta_cm = sqrt(max(total_momentum_sq, 0.0)) / total_energy
    p_star = sqrt(max(invariant_s / 4.0 - mass_sq, 0.0))
    e_star = root_s / 2.0
    average = 0.0
    for final_cosine, final_weight in zip(final_angle_nodes, final_angle_weights):
        energy_three = gamma_cm * (e_star + beta_cm * p_star * float(final_cosine))
        energy_four = gamma_cm * (e_star - beta_cm * p_star * float(final_cosine))
        factor = 1.0 + _bose(energy_three - outgoing_sign_one * mu_eff, temperature)
        factor *= 1.0 + _bose(energy_four - outgoing_sign_two * mu_eff, temperature)
        average += float(final_weight) * factor
    return 0.5 * average


def _collision_width(
    momentum: float,
    species_sign: float,
    temperature: float,
    mass: float,
    mu_eff: float,
    quartic: float,
    momentum_nodes: np.ndarray,
    momentum_weights: np.ndarray,
    angle_nodes: np.ndarray,
    angle_weights: np.ndarray,
    *,
    include_final_state_bose_enhancement: bool = False,
) -> float:
    energy_one = sqrt(momentum * momentum + mass * mass)
    width = 0.0
    for scatterer_sign in (-1.0, 1.0):
        for p, p_weight in zip(momentum_nodes, momentum_weights):
            energy_two = sqrt(float(p) * float(p) + mass * mass)
            occupation = _bose(energy_two - scatterer_sign * mu_eff, temperature)
            angular = 0.0
            for cosine, angle_weight in zip(angle_nodes, angle_weights):
                relative, invariant_s = _relative_velocity(
                    energy_one,
                    energy_two,
                    momentum,
                    float(p),
                    float(cosine),
                    mass * mass,
                )
                cross_section = quartic * quartic / (16.0 * pi * invariant_s)
                final_state_factor = 1.0
                if include_final_state_bose_enhancement:
                    final_state_factor = _final_state_bose_factor(
                        energy_one,
                        energy_two,
                        momentum,
                        float(p),
                        float(cosine),
                        mass * mass,
                        temperature,
                        mu_eff,
                        species_sign,
                        scatterer_sign,
                        angle_nodes,
                        angle_weights,
                    )
                angular += float(angle_weight) * relative * cross_section * final_state_factor
            measure = float(p) * float(p) / (4.0 * pi * pi)
            width += float(p_weight) * measure * occupation * angular
    return _positive(width, "collision width")


def _drude_weight(
    momentum_nodes: np.ndarray,
    momentum_weights: np.ndarray,
    species_sign: float,
    temperature: float,
    mass: float,
    mu_eff: float,
) -> float:
    value = 0.0
    for momentum, weight in zip(momentum_nodes, momentum_weights):
        energy = sqrt(float(momentum) * float(momentum) + mass * mass)
        occupation = _bose(energy - species_sign * mu_eff, temperature)
        value += float(weight) * float(momentum) ** 4 * occupation * (1.0 + occupation)
    return _positive(value / (6.0 * pi * pi * temperature), "Drude weight")


def kinetic_collision_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 64,
    angular_order: int = 48,
    cutoff_factor: float = 24.0,
    include_final_state_bose_enhancement: bool = False,
) -> KineticCollisionState:
    """Evaluate the declared normal-branch dilute-gas collision comparator."""

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    t, mu, mass, mu_eff, quartic = _normal_state_inputs(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    cutoff_factor = _positive(cutoff_factor, "cutoff factor")
    if isinstance(angular_order, bool) or int(angular_order) != angular_order:
        raise ValueError("angular order must be an integer")
    if int(angular_order) < 24:
        raise ValueError("angular order must be >= 24")
    cutoff = max(cutoff_factor * t, cutoff_factor * mass, cutoff_factor * abs(mu_eff), 1.0)
    momentum_nodes, momentum_weights = _quadrature(quadrature_order, cutoff)
    angle_nodes, angle_weights = _quadrature(angular_order, 2.0)
    angle_nodes = angle_nodes - 1.0
    reference_momentum = max(t, mass, abs(mu_eff))
    drude = tuple(
        _drude_weight(
            momentum_nodes,
            momentum_weights,
            sign,
            t,
            mass,
            mu_eff,
        )
        for sign in (-1.0, 1.0)
    )
    widths = tuple(
        _collision_width(
            float(momentum),
            sign,
            t,
            mass,
            mu_eff,
            quartic,
            momentum_nodes,
            momentum_weights,
            angle_nodes,
            angle_weights,
            include_final_state_bose_enhancement=include_final_state_bose_enhancement,
        )
        for sign in (-1.0, 1.0)
        for momentum in (reference_momentum,)
    )
    kinetic = tuple(drude_value / width for drude_value, width in zip(drude, widths))
    values = (*drude, *widths, *kinetic)
    if not all(isfinite(value) and value > 0.0 for value in values):
        raise FloatingPointError("kinetic collision state is not finite and positive")
    return KineticCollisionState(
        temperature=t,
        chemical_potential=mu,
        space_response=float(space_response),
        effective_mass=mass,
        quartic_coupling=quartic,
        drude_weight_by_species=tuple(float(value) for value in drude),
        collision_width_by_species=tuple(float(value) for value in widths),
        kinetic_coefficient_by_species=tuple(float(value) for value in kinetic),
        drude_weight=float(sum(drude)),
        kinetic_coefficient=float(sum(kinetic)),
        quadrature_order=int(quadrature_order),
        angular_order=int(angular_order),
        momentum_cutoff=float(cutoff),
        reference_momentum=float(reference_momentum),
        final_state_bose_enhancement_included=bool(include_final_state_bose_enhancement),
    )


def kinetic_collision_contract() -> dict[str, object]:
    """Return the equations, units, and excluded physical scope."""

    return {
        "status": KINETIC_COLLISION_KUBO_STATUS,
        "normalization_revision": "CANONICAL_NORMAL_KINETIC_V2",
        "amplitude_convention": "UNIT_CHANNEL_COMPARATOR_NOT_FULL_ACTION_TENSOR",
        "species_order": [-1, 1],
        "equations": {
            "canonical_field_map": "chi_c=sqrt(Z)*chi; m_c^2=m_eff^2/Z; lambda_c=lambda/Z^2; mu_c=mu",
            "normal_dispersion": "E_s(k)=sqrt(k^2+m_c^2)-s*mu, s in {-1,+1}",
            "constant_amplitude_cross_section": "sigma_comparator(s)=lambda_c^2/(16*pi*s); channel normalization is not the full action tensor",
            "collision_kernel": "Gamma_s(k)=sum_r integral[d^3p/(2*pi)^3] f_r(E_p) v_rel sigma_22(s) B_34(s;T,mu)",
            "static_weight": "D_s=(1/3) integral[d^3k/(2*pi)^3] k^2[-partial_E f_s]",
            "kinetic_response": "K_kin=sum_s D_s/Gamma_s(k_ref), k_ref=max(T,m_c,abs(mu))",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "mass_temperature_mu": "energy",
            "lambda": "dimensionless canonical lambda_c=lambda_action/Z^2 in returned state",
            "sigma_22": "inverse energy squared",
            "collision_width": "energy/inverse time",
            "D": "formal static response weight",
            "K_kin": "formal kinetic comparator coefficient",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "action-derived constant-amplitude dilute-gas 2-to-2 phase-space comparator; not full quantum transport",
        "observable": "finite-temperature normal collision width and kinetic transport comparator",
        "data_role": "ACTION_DERIVED_DILUTE_KINETIC_COMPARATOR_NOT_PHYSICAL_KUBO",
        "included": {
            "normal_branch": True,
            "constant_amplitude_2_to_2_kernel": True,
            "deterministic_quadrature": True,
            "positivity_and_cutoff_checks": True,
        },
        "excluded": {
            "final_state_bose_enhancement": "optional elastic outgoing-state factor; enabled only by explicit lane parameter",
            "ladder_vertex_resummation": True,
            "condensed_scattering": True,
            "microscopic_SK_KMS_match": True,
            "full_action_tensor_and_channel_symmetry_matching": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes only a named action-derived dilute-gas kinetic comparator. It does not emit a physical Kubo coefficient, SI observable, alpha_Phi_K, TTG prediction, or Full Topic 13 closure.",
    }


__all__ = [
    "KINETIC_COLLISION_KUBO_STATUS",
    "KineticCollisionState",
    "kinetic_collision_state",
    "kinetic_collision_contract",
]
