"""Invariant-rate finite collision operator candidate for Topic 13.

This module repairs the energy dimension of the older finite transition
operator without overwriting it.  Exact elastic channel kinematics are reused,
but each channel receives a Lorentz-invariant phase-space cell and the declared
charge-resolved contact-plus-response tree amplitude.

The angular cell is still a finite representative sampling.  The result is
therefore not a connected continuum collision operator, a self-consistent
width, or a physical Kubo coefficient.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import _bose


INVARIANT_RATE_COLLISION_STATUS = (
    "PASS_SCOPED_INVARIANT_RATE_FINITE_REPRESENTATIVE_OPERATOR"
)


@dataclass(frozen=True)
class InvariantRateCollisionState:
    temperature: float
    chemical_potential: float
    effective_mass: float
    channel_count: int
    channel_weights: tuple[float, ...]
    channel_cosines: tuple[float, ...]
    collision_operator: tuple[tuple[float, ...], ...]
    collision_operator_eigenvalues: tuple[float, ...]
    operator_trace: float
    relative_eigenvalue_tolerance: float
    positive_mode_rate: float
    operator_symmetry_residual: float
    positive_semidefinite_min_eigenvalue: float
    collision_conservation_residual: float
    maximum_channel_invariant_residual: float
    maximum_detailed_balance_residual: float
    legacy_rate_ratio_min: float
    legacy_rate_ratio_max: float
    finite_representative_boundary_declared: bool = True
    connected_continuum_operator_completed: bool = False
    self_consistent_width_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    xie_2026_accessed: bool = False
    parameter_fitting_performed: bool = False


def _action_amplitude(
    invariant_s: float,
    cosine: float,
    charges: tuple[int, int, int, int],
    config: FiniteTemperatureO2QuasiparticleConfig,
) -> float:
    """Return the canonically normalized tree contact-plus-Phi amplitude."""

    eos = config.eos
    matter = eos.matter
    response = eos.response
    z = matter.matter_kinetic
    mass_sq = matter.matter_mass_sq / z
    coupling = matter.matter_quartic / (z * z)
    response_mass_sq = response.response_mass_sq / response.response_kinetic
    cubic = (
        sqrt(response.epsilon_nc)
        * matter.response_coupling
        / (z * sqrt(response.response_kinetic))
    )
    if invariant_s <= 4.0 * mass_sq or abs(cosine) > 1.0:
        raise ValueError("strict elastic physical kinematics required")
    if sum(charges[:2]) != sum(charges[2:]):
        return 0.0
    p_sq = invariant_s / 4.0 - mass_sq
    mandelstam = (
        invariant_s,
        -2.0 * p_sq * (1.0 - cosine),
        -2.0 * p_sq * (1.0 + cosine),
    )
    q1, q2, q3, q4 = charges
    factors = (
        int(q1 == -q2 and q3 == -q4),
        int(q1 == q3 and q2 == q4),
        int(q1 == q4 and q2 == q3),
    )
    result = 2.0 * coupling * sum(factors)
    if cubic:
        if response_mass_sq >= 4.0 * mass_sq:
            raise ValueError("s-channel pole region requires a resummed branch")
        for factor, invariant in zip(factors, mandelstam):
            if factor:
                result += cubic * cubic / (invariant - response_mass_sq)
    return float(result)


def invariant_rate_collision_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 24,
    channel_count: int = 6,
) -> InvariantRateCollisionState:
    """Build a finite representative invariant-rate collision operator."""

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    exact = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=quadrature_order,
        channel_count=channel_count,
    )
    t = exact.temperature
    mu_eff = chemical_potential - config.eos.matter.response_coupling * space_response
    momenta = np.asarray(exact.state_momenta, dtype=float)
    energies = np.asarray(exact.state_energies, dtype=float)
    signs = np.asarray(exact.state_species_signs, dtype=int)
    state_weights = np.asarray(exact.state_weights, dtype=float)
    vectors = np.asarray(exact.transition_vectors, dtype=float)
    beta_thermal = 1.0 / t
    angular_cell = 4.0 * pi / channel_count
    weights: list[float] = []
    cosines: list[float] = []

    for channel in range(channel_count):
        leg = slice(4 * channel, 4 * channel + 4)
        p1, p2, p3, _p4 = momenta[leg]
        e1, e2, e3, e4 = energies[leg]
        q1, q2, q3, q4 = (int(value) for value in signs[leg])
        total_p = p1 + p2
        invariant_s = (e1 + e2) ** 2 - float(np.dot(total_p, total_p))
        p_star_sq = invariant_s / 4.0 - exact.effective_mass**2
        if p_star_sq <= 0.0:
            raise ValueError("strictly open elastic phase space required")
        mandelstam_t = (e1 - e3) ** 2 - float(np.dot(p1 - p3, p1 - p3))
        cosine = 1.0 + mandelstam_t / (2.0 * p_star_sq)
        if abs(cosine) > 1.0:
            raise FloatingPointError("channel reconstruction left physical angular support")
        f = [
            float(_bose(energy - sign * mu_eff, t))
            for energy, sign in zip((e1, e2, e3, e4), (q1, q2, q3, q4))
        ]
        # Recover d^3p quadrature cells from w=d^3p f(1+f)/T.
        d3p_one = state_weights[4 * channel] * t / (f[0] * (1.0 + f[0]))
        d3p_two = state_weights[4 * channel + 1] * t / (f[1] * (1.0 + f[1]))
        d_pi_one = d3p_one / (2.0 * e1)
        d_pi_two = d3p_two / (2.0 * e2)
        d_phi_two_cell = (
            sqrt(p_star_sq) / (16.0 * pi * pi * sqrt(invariant_s)) * angular_cell
        )
        amplitude = _action_amplitude(
            invariant_s, cosine, (q1, q2, q3, q4), config
        )
        final_symmetry = 2.0 if q3 == q4 else 1.0
        bose_weight = f[0] * f[1] * (1.0 + f[2]) * (1.0 + f[3])
        channel_weight = (
            beta_thermal
            * d_pi_one
            * d_pi_two
            * d_phi_two_cell
            * amplitude**2
            * bose_weight
            / final_symmetry
        )
        if not np.isfinite(channel_weight) or channel_weight <= 0.0:
            raise FloatingPointError("invariant channel weight must be positive and finite")
        weights.append(float(channel_weight))
        cosines.append(float(cosine))

    weight_array = np.asarray(weights)
    operator = vectors.T @ np.diag(weight_array) @ vectors
    eigenvalues = np.linalg.eigvalsh(operator)
    max_abs = float(np.max(np.abs(eigenvalues)))
    relative_tolerance = 1.0e-12 * max_abs
    positive = eigenvalues[eigenvalues > relative_tolerance]
    if positive.size == 0:
        raise FloatingPointError("no resolved positive collision mode")
    invariant_matrix = np.column_stack(
        (
            signs * np.sqrt(state_weights),
            energies * np.sqrt(state_weights),
            momenta[:, 0] * np.sqrt(state_weights),
            momenta[:, 1] * np.sqrt(state_weights),
            momenta[:, 2] * np.sqrt(state_weights),
        )
    )
    invariant_scale = max(float(np.linalg.norm(operator)), 1.0e-300)
    conservation = float(np.linalg.norm(operator @ invariant_matrix) / invariant_scale)
    channel_residual = float(np.max(np.abs(np.asarray(exact.channel_invariant_residuals))))
    legacy_rates = np.asarray(exact.channel_rates)
    ratio = weight_array / legacy_rates
    return InvariantRateCollisionState(
        temperature=t,
        chemical_potential=chemical_potential,
        effective_mass=exact.effective_mass,
        channel_count=channel_count,
        channel_weights=tuple(float(value) for value in weight_array),
        channel_cosines=tuple(cosines),
        collision_operator=tuple(tuple(float(value) for value in row) for row in operator),
        collision_operator_eigenvalues=tuple(float(value) for value in eigenvalues),
        operator_trace=float(np.trace(operator)),
        relative_eigenvalue_tolerance=relative_tolerance,
        positive_mode_rate=float(np.mean(positive)),
        operator_symmetry_residual=float(np.linalg.norm(operator - operator.T)),
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
        collision_conservation_residual=conservation,
        maximum_channel_invariant_residual=channel_residual,
        maximum_detailed_balance_residual=float(
            max(exact.channel_detailed_balance_residuals)
        ),
        legacy_rate_ratio_min=float(np.min(ratio)),
        legacy_rate_ratio_max=float(np.max(ratio)),
    )


def invariant_rate_collision_contract() -> dict[str, object]:
    return {
        "status": INVARIANT_RATE_COLLISION_STATUS,
        "equations": {
            "measure": "dPi=d^3p/[(2pi)^3 2E]",
            "channel_weight": "W_c=beta*dPi1*dPi2*dPhi2_cell*|M_contact+M_Phi|^2*f1*f2*(1+f3)*(1+f4)/S_final",
            "state_weight": "w_i=d^3p_i*f_i*(1+f_i)/T",
            "transition_vector": "v_c=(+1/sqrt(w1),+1/sqrt(w2),-1/sqrt(w3),-1/sqrt(w4))",
            "operator": "L_rate=sum_c W_c*v_c*v_c^T",
        },
        "unit_contract": {
            "beta": -1,
            "dPi1_dPi2": 4,
            "dPhi2_cell": 0,
            "amplitude_squared": 0,
            "channel_weight": 3,
            "transition_vector_each": -1,
            "collision_operator": 1,
        },
        "derivation_class": "invariant_phase_space_finite_representative_candidate",
        "claim_boundary": (
            "Closes the rate dimension, finite-channel PSD and exact conservation only. "
            "The angular cell is representative, not a converged connected continuum operator."
        ),
    }


__all__ = [
    "INVARIANT_RATE_COLLISION_STATUS",
    "InvariantRateCollisionState",
    "invariant_rate_collision_state",
    "invariant_rate_collision_contract",
]
