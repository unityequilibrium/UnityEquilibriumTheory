"""Charge-resolved invariant Galerkin collision operator for Topic 13.

The scalar isotropic normal-state lane evaluates the linearized two-to-two
collision quadratic form over multiple radial shells and incoming/outgoing
angles.  Charge and four-momentum are conserved at every quadrature event;
no posterior conservation projector is used.

This is a finite-cutoff scalar Galerkin candidate.  It is not yet a complete
vector/tensor transport basis, a continuum-limit proof, a self-consistent
quasiparticle width, or a physical Kubo coefficient.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_invariant_rate_collision_operator import _action_amplitude
from docs.core.uet_o2_kinetic_collision_kubo import _bose, _normal_state_inputs


INVARIANT_GALERKIN_COLLISION_STATUS = (
    "PASS_SCOPED_CHARGE_RESOLVED_INVARIANT_GALERKIN_COLLISION"
)


@dataclass(frozen=True)
class InvariantGalerkinCollisionState:
    temperature: float
    chemical_potential: float
    effective_mass: float
    momentum_cutoff: float
    radial_order: int
    incoming_angular_order: int
    outgoing_angular_order: int
    outgoing_azimuth_order: int
    feature_order: int
    basis_dimension: int
    collision_event_count: int
    raw_gram_matrix: tuple[tuple[float, ...], ...]
    raw_collision_quadratic_form: tuple[tuple[float, ...], ...]
    collision_operator: tuple[tuple[float, ...], ...]
    collision_operator_eigenvalues: tuple[float, ...]
    relative_eigenvalue_tolerance: float
    null_mode_count: int
    positive_mode_count: int
    positive_mode_rate: float
    operator_trace: float
    gram_identity_residual: float
    operator_symmetry_residual: float
    positive_semidefinite_min_eigenvalue: float
    collision_invariant_residual: float
    maximum_event_charge_residual: float
    maximum_event_energy_residual: float
    maximum_event_momentum_residual: float
    maximum_detailed_balance_residual: float
    minimum_channel_weight: float
    maximum_channel_weight: float
    dissipative_subspace_full_rank: bool
    posterior_conservation_projection_used: bool = False
    scalar_isotropic_basis_only: bool = True
    continuum_limit_completed: bool = False
    vector_tensor_transport_basis_completed: bool = False
    self_consistent_width_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    xie_2026_accessed: bool = False
    parameter_fitting_performed: bool = False


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _boost(
    energy: float,
    momentum: np.ndarray,
    beta: np.ndarray,
) -> tuple[float, np.ndarray]:
    beta_sq = float(np.dot(beta, beta))
    if beta_sq <= 1.0e-30:
        return float(energy), np.asarray(momentum, dtype=float)
    if beta_sq >= 1.0:
        raise FloatingPointError("two-body center-of-mass boost must be subluminal")
    gamma = 1.0 / sqrt(1.0 - beta_sq)
    parallel = float(np.dot(beta, momentum))
    boosted_energy = gamma * (energy + parallel)
    factor = (gamma - 1.0) * parallel / beta_sq + gamma * energy
    return float(boosted_energy), np.asarray(momentum, dtype=float) + factor * beta


def _feature_vector(
    sign: int,
    energy: float,
    energy_offset: float,
    energy_span: float,
    feature_order: int,
) -> np.ndarray:
    result = np.zeros(2 * feature_order, dtype=float)
    offset = 0 if sign == -1 else feature_order
    x = (energy - energy_offset) / energy_span
    result[offset : offset + feature_order] = np.power(x, np.arange(feature_order))
    return result


def invariant_galerkin_collision_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 6,
    incoming_angular_order: int = 6,
    outgoing_angular_order: int = 6,
    outgoing_azimuth_order: int = 8,
    feature_order: int = 4,
    cutoff_factor: float = 12.0,
) -> InvariantGalerkinCollisionState:
    """Evaluate the finite scalar invariant collision quadratic form."""

    integer_controls = {
        "radial_order": (radial_order, 4),
        "incoming_angular_order": (incoming_angular_order, 4),
        "outgoing_angular_order": (outgoing_angular_order, 4),
        "outgoing_azimuth_order": (outgoing_azimuth_order, 4),
        "feature_order": (feature_order, 3),
    }
    for name, (value, minimum) in integer_controls.items():
        if isinstance(value, bool) or int(value) != value or int(value) < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if not np.isfinite(cutoff_factor) or cutoff_factor <= 0.0:
        raise ValueError("cutoff_factor must be positive and finite")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    response = config.eos.response
    if abs(space_response - response.phi_equilibrium) > config.phase_tolerance:
        raise NotImplementedError(
            "the invariant Galerkin v1 requires the declared normal response background"
        )
    t, mu, mass, mu_eff, _quartic = _normal_state_inputs(
        temperature, chemical_potential, space_response, config
    )
    cutoff = cutoff_factor * max(t, mass, abs(mu_eff))
    radial_x, radial_w = np.polynomial.legendre.leggauss(int(radial_order))
    radial_p = 0.5 * cutoff * (radial_x + 1.0)
    radial_dp = 0.5 * cutoff * radial_w
    incoming_cos, incoming_w = np.polynomial.legendre.leggauss(
        int(incoming_angular_order)
    )
    outgoing_cos, outgoing_w = np.polynomial.legendre.leggauss(
        int(outgoing_angular_order)
    )
    azimuths = 2.0 * pi * (
        np.arange(int(outgoing_azimuth_order), dtype=float) + 0.5
    ) / int(outgoing_azimuth_order)
    azimuth_weight = 2.0 * pi / int(outgoing_azimuth_order)
    dimension = 2 * int(feature_order)
    energy_span = sqrt(cutoff * cutoff + mass * mass) - mass
    gram = np.zeros((dimension, dimension), dtype=float)
    beta_thermal = 1.0 / t
    d3p_radial_prefactor = 4.0 * pi / (2.0 * pi) ** 3

    energies = np.sqrt(radial_p * radial_p + mass * mass)
    for sign in (-1, 1):
        occupations = np.asarray(
            [_bose(energy - sign * mu_eff, t) for energy in energies],
            dtype=float,
        )
        for p, dp, energy, occupation in zip(
            radial_p, radial_dp, energies, occupations
        ):
            feature = _feature_vector(
                sign, float(energy), mass, energy_span, int(feature_order)
            )
            measure = (
                beta_thermal
                * d3p_radial_prefactor
                * p
                * p
                * dp
                * occupation
                * (1.0 + occupation)
            )
            gram += measure * np.outer(feature, feature)
    gram_eigenvalues, gram_eigenvectors = np.linalg.eigh(gram)
    gram_tolerance = 1.0e-13 * float(np.max(gram_eigenvalues))
    if np.min(gram_eigenvalues) <= gram_tolerance:
        raise FloatingPointError("raw Galerkin Gram matrix is not numerically positive definite")
    inverse_sqrt_gram = (
        gram_eigenvectors
        @ np.diag(1.0 / np.sqrt(gram_eigenvalues))
        @ gram_eigenvectors.T
    )
    gram_identity_residual = float(
        np.linalg.norm(inverse_sqrt_gram @ gram @ inverse_sqrt_gram - np.eye(dimension))
    )
    raw_form = np.zeros((dimension, dimension), dtype=float)
    max_charge = 0.0
    max_energy = 0.0
    max_momentum = 0.0
    max_balance = 0.0
    min_weight = float("inf")
    max_weight = 0.0
    event_count = 0
    species_pairs = ((-1, -1), (-1, 1), (1, -1), (1, 1))

    for i, (p1_mag, dp1, e1) in enumerate(zip(radial_p, radial_dp, energies)):
        p1 = np.array((0.0, 0.0, float(p1_mag)))
        d_pi_one = (
            4.0
            * pi
            * p1_mag
            * p1_mag
            * dp1
            / ((2.0 * pi) ** 3 * 2.0 * e1)
        )
        for j, (p2_mag, dp2, e2) in enumerate(zip(radial_p, radial_dp, energies)):
            for cosine_in, weight_in in zip(incoming_cos, incoming_w):
                sine_in = sqrt(1.0 - float(cosine_in) ** 2)
                p2 = np.array(
                    (float(p2_mag) * sine_in, 0.0, float(p2_mag) * float(cosine_in))
                )
                total_energy = float(e1 + e2)
                total_momentum = p1 + p2
                invariant_s = total_energy**2 - float(np.dot(total_momentum, total_momentum))
                p_star_sq = invariant_s / 4.0 - mass * mass
                if p_star_sq <= 0.0:
                    raise FloatingPointError("quadrature event must have open elastic phase space")
                p_star = sqrt(p_star_sq)
                root_s = sqrt(invariant_s)
                boost = total_momentum / total_energy
                e1_star, p1_star = _boost(float(e1), p1, -boost)
                if abs(e1_star - root_s / 2.0) > 1.0e-10 * max(root_s, 1.0):
                    raise FloatingPointError("incoming center-of-mass energy reconstruction failed")
                ez = p1_star / np.linalg.norm(p1_star)
                ey = np.array((0.0, 1.0, 0.0))
                ex = np.cross(ey, ez)
                ex /= np.linalg.norm(ex)
                d_pi_two = (
                    2.0
                    * pi
                    * p2_mag
                    * p2_mag
                    * dp2
                    * weight_in
                    / ((2.0 * pi) ** 3 * 2.0 * e2)
                )
                for cosine_out, weight_out in zip(outgoing_cos, outgoing_w):
                    sine_out = sqrt(1.0 - float(cosine_out) ** 2)
                    d_phi_two = (
                        p_star
                        / (16.0 * pi * pi * root_s)
                        * weight_out
                        * azimuth_weight
                    )
                    for azimuth in azimuths:
                        direction = (
                            float(cosine_out) * ez
                            + sine_out * (cos(azimuth) * ex + sin(azimuth) * ey)
                        )
                        e3, p3 = _boost(root_s / 2.0, p_star * direction, boost)
                        e4, p4 = _boost(root_s / 2.0, -p_star * direction, boost)
                        momentum_residual = p1 + p2 - p3 - p4
                        event_energy_residual = float(e1 + e2 - e3 - e4)
                        max_energy = max(max_energy, abs(event_energy_residual))
                        max_momentum = max(
                            max_momentum, float(np.linalg.norm(momentum_residual))
                        )
                        for q1, q2 in species_pairs:
                            q3, q4 = q1, q2
                            charges = (q1, q2, q3, q4)
                            max_charge = max(
                                max_charge, abs(float(q1 + q2 - q3 - q4))
                            )
                            f1 = float(_bose(float(e1) - q1 * mu_eff, t))
                            f2 = float(_bose(float(e2) - q2 * mu_eff, t))
                            f3 = float(_bose(e3 - q3 * mu_eff, t))
                            f4 = float(_bose(e4 - q4 * mu_eff, t))
                            forward = f1 * f2 * (1.0 + f3) * (1.0 + f4)
                            reverse = f3 * f4 * (1.0 + f1) * (1.0 + f2)
                            max_balance = max(
                                max_balance,
                                abs(forward - reverse)
                                / max(forward, reverse, 1.0e-300),
                            )
                            amplitude = _action_amplitude(
                                invariant_s,
                                float(cosine_out),
                                charges,
                                config,
                            )
                            final_symmetry = 2.0 if q3 == q4 else 1.0
                            weight = (
                                0.25
                                * beta_thermal
                                * d_pi_one
                                * d_pi_two
                                * d_phi_two
                                * amplitude
                                * amplitude
                                * forward
                                / final_symmetry
                            )
                            if not np.isfinite(weight) or weight <= 0.0:
                                raise FloatingPointError(
                                    "collision event weight must be positive and finite"
                                )
                            delta = (
                                _feature_vector(q1, float(e1), mass, energy_span, int(feature_order))
                                + _feature_vector(q2, float(e2), mass, energy_span, int(feature_order))
                                - _feature_vector(q3, e3, mass, energy_span, int(feature_order))
                                - _feature_vector(q4, e4, mass, energy_span, int(feature_order))
                            )
                            raw_form += weight * np.outer(delta, delta)
                            min_weight = min(min_weight, weight)
                            max_weight = max(max_weight, weight)
                            event_count += 1

    operator = inverse_sqrt_gram @ raw_form @ inverse_sqrt_gram
    eigenvalues = np.linalg.eigvalsh(operator)
    relative_tolerance = 1.0e-11 * float(np.max(np.abs(eigenvalues)))
    positive = eigenvalues[eigenvalues > relative_tolerance]
    null_count = int(np.sum(eigenvalues <= relative_tolerance))
    if positive.size == 0:
        raise FloatingPointError("no resolved dissipative Galerkin modes")
    raw_invariants = np.zeros((dimension, 3), dtype=float)
    raw_invariants[0, 0] = 1.0
    raw_invariants[int(feature_order), 1] = 1.0
    raw_invariants[1, 2] = 1.0
    raw_invariants[int(feature_order) + 1, 2] = 1.0
    invariant_vectors = np.linalg.inv(inverse_sqrt_gram) @ raw_invariants
    invariant_residual = float(
        np.linalg.norm(operator @ invariant_vectors)
        / max(np.linalg.norm(operator) * np.linalg.norm(invariant_vectors), 1.0e-300)
    )
    expected_positive = dimension - 3
    return InvariantGalerkinCollisionState(
        temperature=t,
        chemical_potential=mu,
        effective_mass=mass,
        momentum_cutoff=float(cutoff),
        radial_order=int(radial_order),
        incoming_angular_order=int(incoming_angular_order),
        outgoing_angular_order=int(outgoing_angular_order),
        outgoing_azimuth_order=int(outgoing_azimuth_order),
        feature_order=int(feature_order),
        basis_dimension=dimension,
        collision_event_count=event_count,
        raw_gram_matrix=_matrix_tuple(gram),
        raw_collision_quadratic_form=_matrix_tuple(raw_form),
        collision_operator=_matrix_tuple(operator),
        collision_operator_eigenvalues=tuple(float(value) for value in eigenvalues),
        relative_eigenvalue_tolerance=relative_tolerance,
        null_mode_count=null_count,
        positive_mode_count=int(positive.size),
        positive_mode_rate=float(np.mean(positive)),
        operator_trace=float(np.trace(operator)),
        gram_identity_residual=gram_identity_residual,
        operator_symmetry_residual=float(np.linalg.norm(operator - operator.T)),
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
        collision_invariant_residual=invariant_residual,
        maximum_event_charge_residual=max_charge,
        maximum_event_energy_residual=max_energy,
        maximum_event_momentum_residual=max_momentum,
        maximum_detailed_balance_residual=max_balance,
        minimum_channel_weight=float(min_weight),
        maximum_channel_weight=float(max_weight),
        dissipative_subspace_full_rank=int(positive.size) == expected_positive,
    )


def invariant_galerkin_collision_contract() -> dict[str, object]:
    return {
        "status": INVARIANT_GALERKIN_COLLISION_STATUS,
        "equations": {
            "quadratic_form": "Q_ab=(beta/4)*sum_q integral dPi1 dPi2 dPhi2 |M|^2 f1 f2 (1+f3)(1+f4) DeltaF_a DeltaF_b / S_final",
            "hilbert_gram": "G_ab=beta*sum_q integral d^3p/(2pi)^3 f_q(1+f_q) F_a F_b",
            "normalized_operator": "L_rate=G^(-1/2) Q G^(-1/2)",
            "event_invariants": "Delta(q)=Delta(E)=Delta(p_x)=Delta(p_y)=Delta(p_z)=0",
        },
        "unit_contract": {
            "quadratic_form": 3,
            "hilbert_gram": 2,
            "inverse_sqrt_gram_each": -1,
            "collision_operator": 1,
        },
        "included": {
            "charge_resolved_contact_plus_Phi_amplitude": True,
            "multiple_incoming_radial_shells": True,
            "incoming_relative_angle_quadrature": True,
            "outgoing_center_of_mass_solid_angle_quadrature": True,
            "eventwise_charge_energy_momentum_conservation": True,
            "posterior_conservation_projection": False,
        },
        "excluded": {
            "vector_tensor_transport_basis": True,
            "continuum_limit": True,
            "self_consistent_width": True,
            "microscopic_ladder": True,
            "physical_Kubo_or_SI_coefficient": True,
            "alpha_Phi_K": True,
            "external_validation": True,
        },
        "claim_boundary": (
            "Finite-cutoff scalar isotropic Galerkin collision operator only; "
            "not a complete transport basis, continuum proof, physical width or Kubo coefficient."
        ),
    }


__all__ = [
    "INVARIANT_GALERKIN_COLLISION_STATUS",
    "InvariantGalerkinCollisionState",
    "invariant_galerkin_collision_state",
    "invariant_galerkin_collision_contract",
]
