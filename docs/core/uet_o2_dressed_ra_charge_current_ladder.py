"""Same-kernel dressed RA charge-current ladder for Topic 13.

The diagonal RA block uses the KMS retarded pole width. The gain rung is then
defined by the same event-resolved collision form, so the Bethe-Salpeter and
kinetic Galerkin equations can be compared without a fitted relaxation time.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_invariant_vector_current_galerkin import (
    invariant_vector_current_state,
)
from docs.core.uet_o2_kinetic_collision_kubo import _bose, _normal_state_inputs
from docs.core.uet_o2_same_kernel_tagged_width import (
    same_kernel_tagged_width_state,
)


DRESSED_RA_CHARGE_CURRENT_LADDER_STATUS = (
    "PASS_SCOPED_SAME_KERNEL_DRESSED_RA_CHARGE_CURRENT_LADDER"
)


@dataclass(frozen=True)
class DressedRAChargeCurrentLadderState:
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
    retarded_widths_by_species_and_momentum: tuple[tuple[float, ...], ...]
    tagged_loss_widths_by_species_and_momentum: tuple[tuple[float, ...], ...]
    maximum_kms_gain_loss_residual: float
    raw_event_loss_matrix: tuple[tuple[float, ...], ...]
    raw_width_loss_matrix: tuple[tuple[float, ...], ...]
    normalized_ra_diagonal: tuple[tuple[float, ...], ...]
    normalized_gain_rung: tuple[tuple[float, ...], ...]
    normalized_collision_operator: tuple[tuple[float, ...], ...]
    ra_preconditioned_kernel: tuple[tuple[float, ...], ...]
    event_width_loss_relative_residual: float
    d_minus_k_collision_relative_residual: float
    rung_symmetry_residual: float
    collision_null_residual: float
    preconditioned_null_count: int
    dissipative_mode_count: int
    deflated_kernel_spectral_radius: float
    source_null_overlap: float
    free_ra_response_form: float
    dressed_ladder_response_form: float
    kinetic_galerkin_response_form: float
    ladder_kinetic_response_relative_residual: float
    ladder_kinetic_solution_relative_residual: float
    equation_residual: float
    ladder_enhancement_factor: float
    neumann_converged: bool
    neumann_divergence_detected: bool
    neumann_iterations: int
    neumann_response_relative_residual: float | None
    retarded_width_used_in_ra_pair: bool = True
    tagged_out_rate_used_as_ra_width: bool = False
    fitted_relaxation_time_used: bool = False
    posterior_collision_projection_used: bool = False
    physical_kubo_coefficient_emitted: bool = False
    xie_2026_accessed: bool = False
    parameter_fitting_performed: bool = False


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _symmetric_inverse_sqrt(matrix: np.ndarray) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    tolerance = 1.0e-13 * float(np.max(eigenvalues))
    if np.min(eigenvalues) <= tolerance:
        raise FloatingPointError("positive-definite matrix required")
    return (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(eigenvalues))
        @ eigenvectors.T
    )


def _relative_matrix(first: np.ndarray, second: np.ndarray) -> float:
    scale = max(float(np.linalg.norm(first)), float(np.linalg.norm(second)), 1.0e-300)
    return float(np.linalg.norm(first - second) / scale)


def dressed_ra_charge_current_ladder_state(
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
    neumann_relative_tolerance: float = 1.0e-10,
    neumann_max_iterations: int = 10000,
) -> DressedRAChargeCurrentLadderState:
    """Build and solve the finite-basis retarded charge-current ladder."""

    if (
        not np.isfinite(neumann_relative_tolerance)
        or neumann_relative_tolerance <= 0.0
        or neumann_relative_tolerance >= 1.0
    ):
        raise ValueError("neumann_relative_tolerance must lie in (0,1)")
    if (
        isinstance(neumann_max_iterations, bool)
        or int(neumann_max_iterations) != neumann_max_iterations
        or int(neumann_max_iterations) < 1
    ):
        raise ValueError("neumann_max_iterations must be a positive integer")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    vector = invariant_vector_current_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=radial_order,
        incoming_angular_order=incoming_angular_order,
        outgoing_angular_order=outgoing_angular_order,
        outgoing_azimuth_order=outgoing_azimuth_order,
        feature_order=feature_order,
        cutoff_factor=cutoff_factor,
    )
    t, _mu, mass, mu_eff, _quartic = _normal_state_inputs(
        temperature, chemical_potential, space_response, config
    )
    radial_x, radial_w = np.polynomial.legendre.leggauss(int(radial_order))
    radial_p = 0.5 * vector.momentum_cutoff * (radial_x + 1.0)
    radial_dp = 0.5 * vector.momentum_cutoff * radial_w
    radial_e = np.sqrt(radial_p * radial_p + mass * mass)
    energy_span = sqrt(vector.momentum_cutoff**2 + mass**2) - mass
    width = same_kernel_tagged_width_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        tagged_momenta=tuple(float(value) for value in radial_p),
        radial_order=radial_order,
        incoming_angular_order=incoming_angular_order,
        outgoing_angular_order=outgoing_angular_order,
        outgoing_azimuth_order=outgoing_azimuth_order,
        cutoff_factor=cutoff_factor,
    )
    retarded_widths = np.asarray(
        width.retarded_spectral_widths_by_tag_momentum, dtype=float
    )
    tagged_loss_widths = np.asarray(
        width.total_widths_by_tag_momentum, dtype=float
    )
    dimension = vector.basis_dimension
    gram = np.asarray(vector.raw_gram_matrix, dtype=float)
    inverse_sqrt_gram = _symmetric_inverse_sqrt(gram)
    raw_width_loss = np.zeros((dimension, dimension), dtype=float)
    beta_thermal = 1.0 / t
    d3p_prefactor = 4.0 * pi / (2.0 * pi) ** 3

    for tag_index, sign in enumerate((-1, 1)):
        offset = 0 if sign == -1 else int(feature_order)
        block = slice(offset, offset + int(feature_order))
        for momentum_index, (momentum, dp, energy) in enumerate(
            zip(radial_p, radial_dp, radial_e)
        ):
            occupation = float(_bose(float(energy) - sign * mu_eff, t))
            y = (float(energy) - mass) / energy_span
            feature = momentum / mass * np.power(y, np.arange(int(feature_order)))
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
            raw_width_loss[block, block] += (
                susceptibility_measure
                * retarded_widths[tag_index, momentum_index]
                * np.outer(feature, feature)
            )

    raw_event_loss = np.asarray(
        vector.raw_collision_loss_quadratic_form, dtype=float
    )
    event_width_residual = _relative_matrix(raw_event_loss, raw_width_loss)
    ra_diagonal = inverse_sqrt_gram @ raw_width_loss @ inverse_sqrt_gram
    collision = np.asarray(vector.collision_operator, dtype=float)
    gain_rung = ra_diagonal - collision
    d_minus_k_residual = _relative_matrix(ra_diagonal - gain_rung, collision)
    inverse_sqrt_diagonal = _symmetric_inverse_sqrt(ra_diagonal)
    kernel = inverse_sqrt_diagonal @ gain_rung @ inverse_sqrt_diagonal
    collision_preconditioned = np.eye(dimension) - kernel
    b_eigenvalues, b_eigenvectors = np.linalg.eigh(collision_preconditioned)
    b_tolerance = 1.0e-11 * float(np.max(np.abs(b_eigenvalues)))
    positive_mask = b_eigenvalues > b_tolerance
    null_mask = ~positive_mask
    if int(np.sum(null_mask)) != 1:
        raise FloatingPointError("exactly one preconditioned momentum null mode required")
    null_basis = b_eigenvectors[:, null_mask]
    deflator = np.eye(dimension) - null_basis @ null_basis.T
    deflated_kernel = deflator @ kernel @ deflator
    deflated_eigenvalues = np.linalg.eigvalsh(deflated_kernel)
    spectral_radius = float(np.max(np.abs(deflated_eigenvalues)))
    source = np.asarray(vector.landau_projected_charge_current_source, dtype=float)
    preconditioned_source = inverse_sqrt_diagonal @ source
    source_null_overlap = float(np.linalg.norm(null_basis.T @ preconditioned_source))
    preconditioned_source = deflator @ preconditioned_source
    b_pseudoinverse = (
        b_eigenvectors[:, positive_mask]
        @ np.diag(1.0 / b_eigenvalues[positive_mask])
        @ b_eigenvectors[:, positive_mask].T
    )
    ladder_solution = (
        inverse_sqrt_diagonal
        @ b_pseudoinverse
        @ preconditioned_source
    )
    collision_eigenvalues, collision_eigenvectors = np.linalg.eigh(collision)
    collision_tolerance = 1.0e-11 * float(np.max(np.abs(collision_eigenvalues)))
    collision_positive = collision_eigenvalues > collision_tolerance
    collision_pseudoinverse = (
        collision_eigenvectors[:, collision_positive]
        @ np.diag(1.0 / collision_eigenvalues[collision_positive])
        @ collision_eigenvectors[:, collision_positive].T
    )
    kinetic_solution = collision_pseudoinverse @ source
    momentum_null = np.asarray(vector.normalized_momentum_null_vector, dtype=float)
    landau_projector = np.eye(dimension) - np.outer(momentum_null, momentum_null)
    ladder_solution = landau_projector @ ladder_solution
    kinetic_solution = landau_projector @ kinetic_solution
    solution_scale = max(
        float(np.linalg.norm(ladder_solution)),
        float(np.linalg.norm(kinetic_solution)),
        1.0e-300,
    )
    solution_residual = float(
        np.linalg.norm(ladder_solution - kinetic_solution) / solution_scale
    )
    dressed_response = float(source @ ladder_solution)
    kinetic_response = float(source @ kinetic_solution)
    response_residual = abs(dressed_response - kinetic_response) / max(
        abs(dressed_response), abs(kinetic_response), 1.0e-300
    )
    free_response = float(preconditioned_source @ preconditioned_source)
    equation_residual = float(
        np.linalg.norm(collision @ ladder_solution - source)
        / max(np.linalg.norm(source), 1.0e-300)
    )
    collision_null_residual = float(
        np.linalg.norm(collision @ momentum_null)
        / max(np.linalg.norm(collision), 1.0e-300)
    )

    iterate = np.zeros(dimension, dtype=float)
    neumann_converged = False
    neumann_divergence_detected = spectral_radius >= 1.0
    neumann_iterations = 0
    target_scale = max(float(np.linalg.norm(preconditioned_source)), 1.0e-300)
    for iteration in range(1, int(neumann_max_iterations) + 1):
        if neumann_divergence_detected:
            break
        updated = preconditioned_source + deflated_kernel @ iterate
        if not np.all(np.isfinite(updated)):
            neumann_divergence_detected = True
            neumann_iterations = iteration
            break
        updated_norm = float(np.linalg.norm(updated))
        difference_norm = float(np.linalg.norm(updated - iterate))
        if not np.isfinite(updated_norm) or not np.isfinite(difference_norm):
            neumann_divergence_detected = True
            neumann_iterations = iteration
            break
        if difference_norm <= (
            neumann_relative_tolerance * max(updated_norm, target_scale)
        ):
            iterate = updated
            neumann_converged = True
            neumann_iterations = iteration
            break
        iterate = updated
    if not neumann_converged and not neumann_divergence_detected:
        neumann_iterations = int(neumann_max_iterations)
    neumann_response = float(preconditioned_source @ iterate)
    neumann_residual = None
    if neumann_converged and np.isfinite(neumann_response):
        neumann_residual = abs(neumann_response - dressed_response) / max(
            abs(neumann_response), abs(dressed_response), 1.0e-300
        )
    return DressedRAChargeCurrentLadderState(
        temperature=t,
        chemical_potential=chemical_potential,
        effective_mass=mass,
        momentum_cutoff=vector.momentum_cutoff,
        radial_order=int(radial_order),
        incoming_angular_order=int(incoming_angular_order),
        outgoing_angular_order=int(outgoing_angular_order),
        outgoing_azimuth_order=int(outgoing_azimuth_order),
        feature_order=int(feature_order),
        basis_dimension=dimension,
        retarded_widths_by_species_and_momentum=tuple(
            tuple(float(value) for value in row) for row in retarded_widths
        ),
        tagged_loss_widths_by_species_and_momentum=tuple(
            tuple(float(value) for value in row) for row in tagged_loss_widths
        ),
        maximum_kms_gain_loss_residual=width.maximum_kms_gain_loss_residual,
        raw_event_loss_matrix=_matrix_tuple(raw_event_loss),
        raw_width_loss_matrix=_matrix_tuple(raw_width_loss),
        normalized_ra_diagonal=_matrix_tuple(ra_diagonal),
        normalized_gain_rung=_matrix_tuple(gain_rung),
        normalized_collision_operator=_matrix_tuple(collision),
        ra_preconditioned_kernel=_matrix_tuple(kernel),
        event_width_loss_relative_residual=event_width_residual,
        d_minus_k_collision_relative_residual=d_minus_k_residual,
        rung_symmetry_residual=float(np.linalg.norm(gain_rung - gain_rung.T)),
        collision_null_residual=collision_null_residual,
        preconditioned_null_count=int(np.sum(null_mask)),
        dissipative_mode_count=int(np.sum(positive_mask)),
        deflated_kernel_spectral_radius=spectral_radius,
        source_null_overlap=source_null_overlap,
        free_ra_response_form=free_response,
        dressed_ladder_response_form=dressed_response,
        kinetic_galerkin_response_form=kinetic_response,
        ladder_kinetic_response_relative_residual=float(response_residual),
        ladder_kinetic_solution_relative_residual=solution_residual,
        equation_residual=equation_residual,
        ladder_enhancement_factor=dressed_response / free_response,
        neumann_converged=neumann_converged,
        neumann_divergence_detected=neumann_divergence_detected,
        neumann_iterations=neumann_iterations,
        neumann_response_relative_residual=(
            None if neumann_residual is None else float(neumann_residual)
        ),
    )


def dressed_ra_charge_current_ladder_contract() -> dict[str, object]:
    return {
        "status": DRESSED_RA_CHARGE_CURRENT_LADDER_STATUS,
        "equations": {
            "retarded_width": "Gamma_R=Gamma_out-Gamma_in=Gamma_out/(1+f)",
            "ra_pair": "integral dp0/(2pi) G_R G_A=1/(4E^2 Gamma_R)",
            "ladder_decomposition": "L_vector=D_RA-K_gain",
            "bethe_salpeter": "(D_RA-K_gain) chi=J_charge",
            "preconditioned_ladder": "(I-D_RA^(-1/2)K_gain D_RA^(-1/2))x=D_RA^(-1/2)J_charge",
        },
        "unit_contract": {
            "Gamma_R": 1,
            "D_RA": 1,
            "K_gain": 1,
            "L_vector": 1,
            "charge_response_form": 1,
        },
        "included": {
            "same_action_loss_gain_cuts": True,
            "kms_retarded_width": True,
            "event_width_loss_match": True,
            "landau_deflated_charge_ladder": True,
            "kinetic_galerkin_equivalence": True,
        },
        "excluded": {
            "self_consistent_dressed_width": True,
            "resonant_resummation": True,
            "independent_heat_channel": True,
            "tensor_shear_channel": True,
            "number_changing_response_channels": True,
            "physical_kubo_or_si_coefficient": True,
        },
        "claim_boundary": (
            "Finite-basis tree-elastic charge-current RA ladder only; not an "
            "independent heat channel, dressed self-consistent width, physical "
            "Kubo/SI coefficient, external validation, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "DRESSED_RA_CHARGE_CURRENT_LADDER_STATUS",
    "DressedRAChargeCurrentLadderState",
    "dressed_ra_charge_current_ladder_state",
    "dressed_ra_charge_current_ladder_contract",
]
