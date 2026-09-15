"""Invariant vector current Galerkin lane for Topic 13.

The module evaluates one isotropic Cartesian block of the vector collision
operator.  The collision operator itself preserves momentum event by event and
uses no posterior conservation projector.  A separate Landau-frame projector
is applied only to current sources.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_invariant_galerkin_collision_operator import (
    _center_of_mass_frame,
    _outgoing_center_of_mass_event,
)
from docs.core.uet_o2_invariant_rate_collision_operator import _action_amplitude
from docs.core.uet_o2_kinetic_collision_kubo import _bose, _normal_state_inputs


INVARIANT_VECTOR_CURRENT_STATUS = (
    "PASS_SCOPED_INVARIANT_VECTOR_CURRENT_GALERKIN"
)


@dataclass(frozen=True)
class InvariantVectorCurrentState:
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
    raw_collision_loss_quadratic_form: tuple[tuple[float, ...], ...]
    collision_operator: tuple[tuple[float, ...], ...]
    collision_operator_eigenvalues: tuple[float, ...]
    relative_eigenvalue_tolerance: float
    null_mode_count: int
    positive_mode_count: int
    operator_trace: float
    positive_mode_rate: float
    gram_identity_residual: float
    operator_symmetry_residual: float
    positive_semidefinite_min_eigenvalue: float
    momentum_null_residual: float
    maximum_event_charge_residual: float
    maximum_event_energy_residual: float
    maximum_event_momentum_residual: float
    maximum_detailed_balance_residual: float
    normalized_momentum_null_vector: tuple[float, ...]
    normalized_charge_current_source: tuple[float, ...]
    normalized_grand_heat_current_source: tuple[float, ...]
    landau_projected_charge_current_source: tuple[float, ...]
    landau_projected_grand_heat_current_source: tuple[float, ...]
    charge_source_momentum_overlap: float
    heat_source_momentum_overlap: float
    projected_heat_charge_rank_residual: float
    projected_source_rank: int
    charge_response_form: float
    heat_response_form: float
    dissipative_subspace_full_rank: bool
    posterior_collision_projection_used: bool = False
    landau_source_projection_used: bool = True
    scalar_vector_tensor_completion: bool = False
    dressed_ladder_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    xie_2026_accessed: bool = False
    parameter_fitting_performed: bool = False


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _vector_features(
    sign: int,
    momentum: np.ndarray,
    energy: float,
    mass: float,
    energy_span: float,
    feature_order: int,
) -> np.ndarray:
    result = np.zeros((2 * feature_order, 3), dtype=float)
    offset = 0 if sign == -1 else feature_order
    y = (energy - mass) / energy_span
    powers = np.power(y, np.arange(feature_order))
    result[offset : offset + feature_order] = powers[:, None] * momentum[None, :] / mass
    return result


def invariant_vector_current_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 8,
    incoming_angular_order: int = 4,
    outgoing_angular_order: int = 4,
    outgoing_azimuth_order: int = 4,
    feature_order: int = 4,
    cutoff_factor: float = 12.0,
) -> InvariantVectorCurrentState:
    """Evaluate one isotropic vector collision and current-source block."""

    controls = {
        "radial_order": (radial_order, 4),
        "incoming_angular_order": (incoming_angular_order, 4),
        "outgoing_angular_order": (outgoing_angular_order, 4),
        "outgoing_azimuth_order": (outgoing_azimuth_order, 4),
        "feature_order": (feature_order, 3),
    }
    for name, (value, minimum) in controls.items():
        if isinstance(value, bool) or int(value) != value or int(value) < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if not np.isfinite(cutoff_factor) or cutoff_factor <= 0.0:
        raise ValueError("cutoff_factor must be positive and finite")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    response = config.eos.response
    if abs(space_response - response.phi_equilibrium) > config.phase_tolerance:
        raise NotImplementedError(
            "the vector Galerkin v1 requires the declared normal response background"
        )
    t, mu, mass, mu_eff, _quartic = _normal_state_inputs(
        temperature, chemical_potential, space_response, config
    )
    cutoff = cutoff_factor * max(t, mass, abs(mu_eff))
    energy_span = sqrt(cutoff * cutoff + mass * mass) - mass
    radial_x, radial_w = np.polynomial.legendre.leggauss(int(radial_order))
    radial_p = 0.5 * cutoff * (radial_x + 1.0)
    radial_dp = 0.5 * cutoff * radial_w
    radial_e = np.sqrt(radial_p * radial_p + mass * mass)
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
    beta_thermal = 1.0 / t
    gram = np.zeros((dimension, dimension), dtype=float)
    raw_charge_source = np.zeros(dimension, dtype=float)
    raw_heat_source = np.zeros(dimension, dtype=float)
    d3p_prefactor = 4.0 * pi / (2.0 * pi) ** 3

    for sign in (-1, 1):
        offset = 0 if sign == -1 else int(feature_order)
        for momentum, dp, energy in zip(radial_p, radial_dp, radial_e):
            occupation = float(_bose(float(energy) - sign * mu_eff, t))
            y = (float(energy) - mass) / energy_span
            powers = np.power(y, np.arange(int(feature_order)))
            susceptibility_measure = (
                beta_thermal
                * d3p_prefactor
                * momentum
                * momentum
                * dp
                * occupation
                * (1.0 + occupation)
                / 3.0
            )
            vector_feature_magnitudes = momentum / mass * powers
            block = slice(offset, offset + int(feature_order))
            gram[block, block] += susceptibility_measure * np.outer(
                vector_feature_magnitudes, vector_feature_magnitudes
            )
            charge_current_magnitude = sign * momentum / float(energy)
            grand_heat_magnitude = (
                (float(energy) - mu_eff * sign) * momentum / float(energy)
            )
            raw_charge_source[block] += (
                susceptibility_measure
                * vector_feature_magnitudes
                * charge_current_magnitude
            )
            raw_heat_source[block] += (
                susceptibility_measure
                * vector_feature_magnitudes
                * grand_heat_magnitude
            )
    gram_eigenvalues, gram_eigenvectors = np.linalg.eigh(gram)
    gram_tolerance = 1.0e-13 * float(np.max(gram_eigenvalues))
    if np.min(gram_eigenvalues) <= gram_tolerance:
        raise FloatingPointError("vector Galerkin Gram matrix is not positive definite")
    inverse_sqrt_gram = (
        gram_eigenvectors
        @ np.diag(1.0 / np.sqrt(gram_eigenvalues))
        @ gram_eigenvectors.T
    )
    gram_identity_residual = float(
        np.linalg.norm(inverse_sqrt_gram @ gram @ inverse_sqrt_gram - np.eye(dimension))
    )
    raw_form = np.zeros((dimension, dimension), dtype=float)
    raw_loss_form = np.zeros((dimension, dimension), dtype=float)
    max_charge = 0.0
    max_energy = 0.0
    max_momentum = 0.0
    max_balance = 0.0
    event_count = 0
    species_pairs = ((-1, -1), (-1, 1), (1, -1), (1, 1))

    for p1_mag, dp1, e1 in zip(radial_p, radial_dp, radial_e):
        p1 = np.array((0.0, 0.0, float(p1_mag)))
        d_pi_one = (
            4.0
            * pi
            * p1_mag
            * p1_mag
            * dp1
            / ((2.0 * pi) ** 3 * 2.0 * e1)
        )
        for p2_mag, dp2, e2 in zip(radial_p, radial_dp, radial_e):
            for cosine_in, weight_in in zip(incoming_cos, incoming_w):
                sine_in = sqrt(1.0 - float(cosine_in) ** 2)
                p2 = np.array(
                    (float(p2_mag) * sine_in, 0.0, float(p2_mag) * float(cosine_in))
                )
                invariant_s, p_star, root_s, boost, ex, ey, ez = (
                    _center_of_mass_frame(float(e1), p1, float(e2), p2, mass)
                )
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
                    d_phi_two = (
                        p_star
                        / (16.0 * pi * pi * root_s)
                        * weight_out
                        * azimuth_weight
                    )
                    for azimuth in azimuths:
                        e3, p3, e4, p4 = _outgoing_center_of_mass_event(
                            root_s, p_star, boost, ex, ey, ez,
                            float(cosine_out), float(azimuth)
                        )
                        max_energy = max(max_energy, abs(float(e1 + e2 - e3 - e4)))
                        max_momentum = max(
                            max_momentum, float(np.linalg.norm(p1 + p2 - p3 - p4))
                        )
                        for q1, q2 in species_pairs:
                            q3, q4 = q1, q2
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
                                (q1, q2, q3, q4),
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
                            feature_one = _vector_features(
                                q1, p1, float(e1), mass, energy_span, int(feature_order)
                            )
                            feature_two = _vector_features(
                                q2, p2, float(e2), mass, energy_span, int(feature_order)
                            )
                            feature_three = _vector_features(
                                q3, p3, e3, mass, energy_span, int(feature_order)
                            )
                            feature_four = _vector_features(
                                q4, p4, e4, mass, energy_span, int(feature_order)
                            )
                            delta = (
                                feature_one + feature_two - feature_three - feature_four
                            )
                            raw_form += weight * (delta @ delta.T) / 3.0
                            raw_loss_form += weight * (
                                feature_one @ feature_one.T
                                + feature_two @ feature_two.T
                                + feature_three @ feature_three.T
                                + feature_four @ feature_four.T
                            ) / 3.0
                            event_count += 1
    operator = inverse_sqrt_gram @ raw_form @ inverse_sqrt_gram
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    relative_tolerance = 1.0e-11 * float(np.max(np.abs(eigenvalues)))
    positive_mask = eigenvalues > relative_tolerance
    positive = eigenvalues[positive_mask]
    if positive.size == 0:
        raise FloatingPointError("no resolved vector dissipative modes")
    raw_momentum_coeff = np.zeros(dimension, dtype=float)
    raw_momentum_coeff[0] = mass
    raw_momentum_coeff[int(feature_order)] = mass
    momentum_null = np.linalg.inv(inverse_sqrt_gram) @ raw_momentum_coeff
    momentum_null /= np.linalg.norm(momentum_null)
    momentum_residual = float(
        np.linalg.norm(operator @ momentum_null)
        / max(np.linalg.norm(operator), 1.0e-300)
    )
    normalized_charge = inverse_sqrt_gram @ raw_charge_source
    normalized_heat = inverse_sqrt_gram @ raw_heat_source
    projector = np.eye(dimension) - np.outer(momentum_null, momentum_null)
    projected_charge = projector @ normalized_charge
    projected_heat = projector @ normalized_heat
    charge_overlap = float(np.dot(momentum_null, normalized_charge))
    heat_overlap = float(np.dot(momentum_null, normalized_heat))
    rank_scale = max(
        np.linalg.norm(projected_heat),
        abs(mu_eff) * np.linalg.norm(projected_charge),
        1.0e-300,
    )
    rank_residual = float(
        np.linalg.norm(projected_heat + mu_eff * projected_charge) / rank_scale
    )
    source_matrix = np.column_stack((projected_charge, projected_heat))
    source_rank_tolerance = 1.0e-10 * float(np.max(np.linalg.svd(source_matrix, compute_uv=False)))
    projected_rank = int(np.linalg.matrix_rank(source_matrix, tol=source_rank_tolerance))
    inverse_operator = (
        eigenvectors[:, positive_mask]
        @ np.diag(1.0 / positive)
        @ eigenvectors[:, positive_mask].T
    )
    charge_response = float(projected_charge @ inverse_operator @ projected_charge)
    heat_response = float(projected_heat @ inverse_operator @ projected_heat)
    return InvariantVectorCurrentState(
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
        raw_collision_loss_quadratic_form=_matrix_tuple(raw_loss_form),
        collision_operator=_matrix_tuple(operator),
        collision_operator_eigenvalues=tuple(float(value) for value in eigenvalues),
        relative_eigenvalue_tolerance=relative_tolerance,
        null_mode_count=int(np.sum(~positive_mask)),
        positive_mode_count=int(positive.size),
        operator_trace=float(np.trace(operator)),
        positive_mode_rate=float(np.mean(positive)),
        gram_identity_residual=gram_identity_residual,
        operator_symmetry_residual=float(np.linalg.norm(operator - operator.T)),
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
        momentum_null_residual=momentum_residual,
        maximum_event_charge_residual=max_charge,
        maximum_event_energy_residual=max_energy,
        maximum_event_momentum_residual=max_momentum,
        maximum_detailed_balance_residual=max_balance,
        normalized_momentum_null_vector=tuple(float(value) for value in momentum_null),
        normalized_charge_current_source=tuple(float(value) for value in normalized_charge),
        normalized_grand_heat_current_source=tuple(float(value) for value in normalized_heat),
        landau_projected_charge_current_source=tuple(float(value) for value in projected_charge),
        landau_projected_grand_heat_current_source=tuple(float(value) for value in projected_heat),
        charge_source_momentum_overlap=charge_overlap,
        heat_source_momentum_overlap=heat_overlap,
        projected_heat_charge_rank_residual=rank_residual,
        projected_source_rank=projected_rank,
        charge_response_form=charge_response,
        heat_response_form=heat_response,
        dissipative_subspace_full_rank=int(positive.size) == dimension - 1,
    )


def invariant_vector_current_contract() -> dict[str, object]:
    return {
        "status": INVARIANT_VECTOR_CURRENT_STATUS,
        "equations": {
            "vector_features": "F_qk^i=(p^i/m)*y(E)^k",
            "vector_quadratic_form": "Q_ab^(l=1)=(beta/12)*sum_events W_without_beta DeltaF_a dot DeltaF_b",
            "vector_operator": "L_vector=G_vector^(-1/2) Q_vector G_vector^(-1/2)",
            "charge_source": "J_charge^i=q*p^i/E",
            "grand_heat_source": "J_Q^i=(E-mu*q)*p^i/E=P^i-mu*J_charge^i",
            "landau_rank_boundary": "P_perp J_Q=-mu*P_perp J_charge",
        },
        "unit_contract": {
            "collision_operator": 1,
            "charge_source_function": 0,
            "grand_heat_source_function": 1,
            "charge_response_form": 1,
            "heat_response_form": 3,
        },
        "included": {
            "isotropic_vector_block": True,
            "eventwise_momentum_conservation": True,
            "landau_source_projection": True,
            "charge_heat_source_rank_test": True,
        },
        "excluded": {
            "independent_heat_channel_in_elastic_equal_mass_lane": True,
            "tensor_shear_basis": True,
            "additional_normal_or_response_species": True,
            "dressed_retarded_ladder": True,
            "physical_Kubo_or_SI_coefficient": True,
        },
        "claim_boundary": (
            "Finite vector Galerkin and Landau-frame source-rank result only; "
            "not a complete heat-transport coefficient or dressed ladder."
        ),
    }


__all__ = [
    "INVARIANT_VECTOR_CURRENT_STATUS",
    "InvariantVectorCurrentState",
    "invariant_vector_current_state",
    "invariant_vector_current_contract",
]
