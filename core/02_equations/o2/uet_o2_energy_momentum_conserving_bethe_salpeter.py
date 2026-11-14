"""Finite-grid energy-momentum conserving response for Topic 13.

This lane extends the action-derived momentum collision widths to an explicit
six-direction momentum grid by default, with an opt-in weighted fourteen-node
research rule. A Gram projector preserves charge, energy, and
the three spatial momentum moments.  The projected operator is then written
as an algebraic Bethe-Salpeter resolvent and paired with an algebraic KMS/FDT
interface.

The construction is a controlled finite-dimensional interface.  It is not a
microscopic transition kernel, a field-theoretic Bethe-Salpeter vertex, a full
SK action match, a physical Kubo coefficient, or an SI observable.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import cosh, exp, expm1, isfinite, pi, sinh, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import (
    _bose,
    _collision_width,
    _normal_state_inputs,
    _quadrature,
)


ENERGY_MOMENTUM_BS_STATUS = (
    "PASS_ACTION_DERIVED_FULL_MOMENT_CONSERVING_BS_INTERFACE_LANE"
)
_DIRECTIONS = (
    (1.0, 0.0, 0.0),
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
    (0.0, 0.0, -1.0),
)


def _moment_direction_rule(name: str):
    """Dimensionless quadrature controls, not material parameters."""
    if name == "axis6":
        return _DIRECTIONS, (1.0 / 6.0,) * 6
    if name == "axis_cube14":
        corners = tuple(tuple(v / sqrt(3.0) for v in node)
                        for node in product((-1.0, 1.0), repeat=3))
        return _DIRECTIONS + corners, (1.0 / 15.0,) * 6 + (3.0 / 40.0,) * 8
    raise ValueError("unknown moment direction rule")


@dataclass(frozen=True)
class EnergyMomentumConservingBSState:
    """Finite-grid moment-conserving response and matching quantities."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    momentum_cutoff: float
    radial_order: int
    collision_integration_order: int
    angular_order: int
    direction_count: int
    state_count: int
    state_species_signs: tuple[float, ...]
    state_momenta: tuple[tuple[float, float, float], ...]
    state_energies: tuple[float, ...]
    charge_by_state: tuple[float, ...]
    susceptibility_weights: tuple[float, ...]
    collision_widths: tuple[float, ...]
    conserved_invariants: tuple[tuple[float, ...], ...]
    projector: tuple[tuple[float, ...], ...]
    collision_operator: tuple[tuple[float, ...], ...]
    collision_operator_eigenvalues: tuple[float, ...]
    invariant_rank: int
    invariant_projection_residual: float
    collision_conservation_residual: float
    operator_symmetry_residual: float
    source_vector: tuple[float, ...]
    projected_source_vector: tuple[float, ...]
    source_constraint_residual: float
    positive_semidefinite_min_eigenvalue: float
    positive_mode_rate: float
    collision_width_relative_spread: float
    retarded_frequency_over_rate: tuple[float, ...]
    retarded_response_real: tuple[float, ...]
    retarded_response_imag: tuple[float, ...]
    dc_response: float
    kms_frequency_over_temperature: tuple[float, ...]
    kms_spectral_density: tuple[float, ...]
    kms_greater: tuple[float, ...]
    kms_lesser: tuple[float, ...]
    kms_noise: tuple[float, ...]
    kms_ratio: tuple[float, ...]
    kms_target_ratio: tuple[float, ...]
    kms_noise_target: tuple[float, ...]
    bs_frequency_over_rate: tuple[float, ...]
    bs_match_residuals: tuple[float, ...]
    entropy_production_witness: float
    finite_cutoff_boundary_declared: bool = True
    full_energy_momentum_constraints_included: bool = True
    microscopic_bethe_salpeter_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_DISCRETE_MOMENT_CONSERVING_BS_INTERFACE_NOT_MICROSCOPIC"
    )
    moment_direction_rule: str = "axis6"


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


def _radial_quadrature(order: int, upper: float) -> tuple[np.ndarray, np.ndarray]:
    if isinstance(order, bool) or int(order) != order or int(order) < 8:
        raise ValueError("radial order must be an integer >= 8")
    nodes, weights = np.polynomial.legendre.leggauss(int(order))
    return 0.5 * upper * (nodes + 1.0), 0.5 * upper * weights


def _bose_frequency(argument: float) -> float:
    x = _positive(argument, "beta frequency")
    return exp(-x) if x > 50.0 else 1.0 / expm1(x)


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _retarded_response(
    operator: np.ndarray,
    source: np.ndarray,
    frequency: float,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> complex:
    projected = eigenvectors.T @ source
    response = 0.0j
    for coefficient, eigenvalue in zip(projected, eigenvalues):
        if eigenvalue <= 1.0e-14 and frequency == 0.0:
            continue
        denominator = eigenvalue - 1.0j * frequency
        response += float(coefficient * coefficient) / denominator
    del operator
    return complex(response)


def _algebraic_bethe_salpeter_residual(
    operator: np.ndarray,
    frequency: float,
    reference_rate: float,
) -> float:
    state_count = operator.shape[0]
    identity = np.eye(state_count, dtype=float)
    bare_inverse = reference_rate * identity - 1.0j * frequency * identity
    bare = np.linalg.inv(bare_inverse)
    kernel = reference_rate * identity - operator
    full = np.linalg.inv(operator - 1.0j * frequency * identity)
    ladder = bare + bare @ kernel @ full
    return float(np.linalg.norm(ladder - full) / max(np.linalg.norm(full), 1.0))


def energy_momentum_conserving_bs_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 12,
    collision_integration_order: int = 36,
    angular_order: int = 24,
    cutoff_factor: float = 48.0,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    kms_frequency_over_temperature: tuple[float, ...] = (0.25, 0.5, 1.0),
    bs_frequency_over_rate: tuple[float, ...] = (0.5, 1.0, 2.0),
    include_final_state_bose_enhancement: bool = True,
    _direction_rule: str = "axis6",
) -> EnergyMomentumConservingBSState:
    """Evaluate the finite-grid full-moment conserving interface."""

    if not include_final_state_bose_enhancement:
        raise ValueError("this lane requires the corrected quantum collision width")
    if isinstance(collision_integration_order, bool) or int(collision_integration_order) != collision_integration_order:
        raise ValueError("collision_integration_order must be an integer")
    if int(collision_integration_order) < 24:
        raise ValueError("collision_integration_order must be >= 24")
    if isinstance(angular_order, bool) or int(angular_order) != angular_order:
        raise ValueError("angular_order must be an integer")
    if int(angular_order) < 24:
        raise ValueError("angular_order must be >= 24")

    def _ordered_nonnegative(values: tuple[float, ...], name: str) -> tuple[float, ...]:
        if not values:
            raise ValueError(f"{name} must not be empty")
        result = tuple(_finite(value, name) for value in values)
        if tuple(sorted(result)) != result or any(value < 0.0 for value in result):
            raise ValueError(f"{name} must be sorted and non-negative")
        return result

    response_ratios = _ordered_nonnegative(
        retarded_frequency_over_rate, "retarded_frequency_over_rate"
    )
    if response_ratios[0] != 0.0:
        raise ValueError("retarded_frequency_over_rate must start at zero")
    kms_ratios = tuple(
        _positive(value, "kms_frequency_over_temperature")
        for value in kms_frequency_over_temperature
    )
    if tuple(sorted(kms_ratios)) != kms_ratios:
        raise ValueError("kms_frequency_over_temperature must be sorted")
    bs_ratios = tuple(
        _positive(value, "bs_frequency_over_rate") for value in bs_frequency_over_rate
    )
    if tuple(sorted(bs_ratios)) != bs_ratios:
        raise ValueError("bs_frequency_over_rate must be sorted")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    t, mu, mass, mu_eff, quartic = _normal_state_inputs(
        temperature, chemical_potential, space_response, config
    )
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    cutoff = max(cutoff_factor * t, cutoff_factor * mass, cutoff_factor * mu_eff, 1.0)
    radial_nodes, radial_weights = _radial_quadrature(radial_order, cutoff)
    collision_nodes, collision_weights = _quadrature(
        int(collision_integration_order), cutoff
    )
    angle_nodes, angle_weights = _quadrature(int(angular_order), 2.0)
    angle_nodes = angle_nodes - 1.0

    state_signs: list[float] = []
    momenta: list[tuple[float, float, float]] = []
    energies: list[float] = []
    charges: list[float] = []
    susceptibility: list[float] = []
    widths: list[float] = []
    source: list[float] = []
    radial_measure = 1.0 / (2.0 * np.pi * np.pi)
    directions, direction_weights = _moment_direction_rule(_direction_rule)
    for sign in (-1.0, 1.0):
        for momentum, momentum_weight in zip(radial_nodes, radial_weights):
            p = float(momentum)
            energy = sqrt(p * p + mass * mass)
            occupation = _bose(energy - sign * mu_eff, t)
            width = _collision_width(
                p,
                sign,
                t,
                mass,
                mu_eff,
                quartic,
                collision_nodes,
                collision_weights,
                angle_nodes,
                angle_weights,
                include_final_state_bose_enhancement=True,
            )
            base_weight = (
                float(momentum_weight)
                * p
                * p
                * radial_measure
                * occupation
                * (1.0 + occupation)
                / t
            )
            for direction, direction_weight in zip(directions, direction_weights):
                px, py, pz = (p * float(value) for value in direction)
                weight = _positive(base_weight * direction_weight, "state weight")
                state_signs.append(sign)
                momenta.append((px, py, pz))
                energies.append(energy)
                charges.append(sign)
                susceptibility.append(weight)
                widths.append(_positive(width, "collision width"))
                source.append(sign * (px / energy) * sqrt(weight))

    state_count = len(widths)
    weight_array = np.asarray(susceptibility, dtype=float)
    energy_array = np.asarray(energies, dtype=float)
    charge_array = np.asarray(charges, dtype=float)
    momentum_array = np.asarray(momenta, dtype=float)
    invariant_columns = np.column_stack(
        (
            charge_array * np.sqrt(weight_array),
            energy_array * np.sqrt(weight_array),
            momentum_array[:, 0] * np.sqrt(weight_array),
            momentum_array[:, 1] * np.sqrt(weight_array),
            momentum_array[:, 2] * np.sqrt(weight_array),
        )
    )
    invariant_rank = int(np.linalg.matrix_rank(invariant_columns, tol=1.0e-12))
    if invariant_rank != 5:
        raise ValueError("charge and four-momentum invariants must be independent")
    orthonormal, _ = np.linalg.qr(invariant_columns, mode="reduced")
    projector = np.eye(state_count, dtype=float) - orthonormal @ orthonormal.T
    width_array = np.asarray(widths, dtype=float)
    operator = projector @ np.diag(width_array) @ projector
    source_array = np.asarray(source, dtype=float)
    projected_source = projector @ source_array
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    positive_eigenvalues = eigenvalues[eigenvalues > 1.0e-12]
    positive_rate = _positive(float(np.mean(positive_eigenvalues)), "positive mode rate")

    frequencies = tuple(positive_rate * ratio for ratio in response_ratios)
    responses = tuple(
        _retarded_response(operator, projected_source, frequency, eigenvalues, eigenvectors)
        for frequency in frequencies
    )
    kms_frequencies = tuple(t * ratio for ratio in kms_ratios)
    kms_responses = tuple(
        _retarded_response(operator, projected_source, frequency, eigenvalues, eigenvectors)
        for frequency in kms_frequencies
    )
    spectral = tuple(2.0 * response.imag for response in kms_responses)
    occupations = tuple(_bose_frequency(ratio) for ratio in kms_ratios)
    greater = tuple(rho * (1.0 + occupation) for rho, occupation in zip(spectral, occupations))
    lesser = tuple(rho * occupation for rho, occupation in zip(spectral, occupations))
    noise = tuple(g + l for g, l in zip(greater, lesser))
    target_ratio = tuple(exp(ratio) for ratio in kms_ratios)
    kms_ratio = tuple(g / l for g, l in zip(greater, lesser))
    noise_target = tuple(
        rho * cosh(0.5 * ratio) / sinh(0.5 * ratio)
        for rho, ratio in zip(spectral, kms_ratios)
    )
    bs_frequencies = tuple(positive_rate * ratio for ratio in bs_ratios)
    bs_residuals = tuple(
        _algebraic_bethe_salpeter_residual(operator, frequency, positive_rate)
        for frequency in bs_frequencies
    )
    entropy_witness = _positive(
        float(np.dot(projected_source, operator @ projected_source) / t),
        "entropy production witness",
    )
    invariant_projection_residual = float(np.linalg.norm(projector @ orthonormal))
    conservation_residual = float(np.linalg.norm(operator @ invariant_columns))
    source_constraint_residual = float(np.linalg.norm(orthonormal.T @ projected_source))
    symmetry_residual = float(np.linalg.norm(operator - operator.T))
    spread = (float(np.max(width_array)) - float(np.min(width_array))) / float(np.mean(width_array))
    values = (
        *eigenvalues,
        *[response.real for response in responses],
        *[response.imag for response in responses],
        *spectral,
        *greater,
        *lesser,
        *noise,
        *kms_ratio,
        *noise_target,
        *bs_residuals,
        entropy_witness,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("energy-momentum conserving response is not finite")

    return EnergyMomentumConservingBSState(
        temperature=t,
        chemical_potential=mu,
        space_response=float(space_response),
        effective_mass=mass,
        momentum_cutoff=float(cutoff),
        radial_order=int(radial_order),
        collision_integration_order=int(collision_integration_order),
        angular_order=int(angular_order),
        direction_count=len(directions),
        state_count=state_count,
        state_species_signs=tuple(state_signs),
        state_momenta=tuple(momenta),
        state_energies=tuple(float(value) for value in energies),
        charge_by_state=tuple(charges),
        susceptibility_weights=tuple(susceptibility),
        collision_widths=tuple(widths),
        conserved_invariants=_matrix_tuple(invariant_columns),
        projector=_matrix_tuple(projector),
        collision_operator=_matrix_tuple(operator),
        collision_operator_eigenvalues=tuple(float(value) for value in eigenvalues),
        invariant_rank=invariant_rank,
        invariant_projection_residual=invariant_projection_residual,
        collision_conservation_residual=conservation_residual,
        operator_symmetry_residual=symmetry_residual,
        source_vector=tuple(float(value) for value in source_array),
        projected_source_vector=tuple(float(value) for value in projected_source),
        source_constraint_residual=source_constraint_residual,
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
        positive_mode_rate=positive_rate,
        collision_width_relative_spread=spread,
        retarded_frequency_over_rate=response_ratios,
        retarded_response_real=tuple(float(response.real) for response in responses),
        retarded_response_imag=tuple(float(response.imag) for response in responses),
        dc_response=float(responses[0].real),
        kms_frequency_over_temperature=kms_ratios,
        kms_spectral_density=spectral,
        kms_greater=greater,
        kms_lesser=lesser,
        kms_noise=noise,
        kms_ratio=kms_ratio,
        kms_target_ratio=target_ratio,
        kms_noise_target=noise_target,
        bs_frequency_over_rate=bs_ratios,
        bs_match_residuals=bs_residuals,
        entropy_production_witness=entropy_witness,
        moment_direction_rule=_direction_rule,
    )


def energy_momentum_conserving_bs_contract() -> dict[str, object]:
    """Return equations, units, and the explicit microscopic boundary."""

    return {
        "status": ENERGY_MOMENTUM_BS_STATUS,
        "fourier_convention": "exp(-i omega t); G_R=(L-i*omega*I)^(-1)",
        "equations": {
            "state_weight": "w_(s,k,n)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk*dOmega/(4*pi)",
            "conserved_invariants": "I_A=(q_s,E_k,p_x,p_y,p_z)*sqrt(w_(s,k,n))",
            "orthonormal_constraint": "Q=orth(I_A); P=I-Q*Q^T",
            "collision_operator": "L=P*diag(Gamma_s(k))*P; L*Q=0; L>=0",
            "current_source": "b_(s,k,n)=q_s*(p_x/E_k)*sqrt(w_(s,k,n)); b_perp=P*b",
            "retarded_response": "G_R(omega)=(L-i*omega*I)^(-1); K_R=b_perp^T*G_R*b_perp",
            "bare_resolvent": "G_0=(gamma_ref*I-i*omega*I)^(-1)",
            "bethe_salpeter_kernel": "K_BS=gamma_ref*I-L",
            "bethe_salpeter_identity": "G_R=G_0+G_0*K_BS*G_R; G_R^(-1)=G_0^(-1)-K_BS",
            "wightman_matching": "G^>=rho*(1+n_B); G^<=rho*n_B; rho=2*Im(K_R)",
            "kms_ratio": "G^>/G^<=exp(beta_th*omega)",
            "fdt_noise": "N=G^>+G^<=rho*coth(beta_th*omega/2)",
            "entropy_witness": "sigma_formal=b_perp^T*L*b_perp/T>=0",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_rate_momentum_energy": "energy",
            "response_spectral_density_entropy_production": "formal natural-unit lane quantities",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived quantum collision widths plus finite discrete charge and "
            "four-momentum conserving Gram projection and algebraic Bethe-Salpeter identity"
        ),
        "observable": "finite-grid momentum-current response and formal algebraic ladder/KMS interface",
        "data_role": "ACTION_DERIVED_FINITE_DISCRETE_MOMENT_CONSERVING_BS_INTERFACE_NOT_MICROSCOPIC",
        "included": {
            "charge_conservation": True,
            "energy_conservation": True,
            "three_momentum_conservation": True,
            "six_direction_momentum_grid": True,
            "positive_semidefinite_collision_operator": True,
            "algebraic_bethe_salpeter_resolvent_identity": True,
            "algebraic_sk_kms_fdt_interface": True,
            "formal_entropy_positivity": True,
        },
        "excluded": {
            "microscopic_two_to_two_transition_kernel": True,
            "microscopic_bethe_salpeter_vertex": True,
            "microscopic_sk_action_match": True,
            "cutoff_limit": True,
            "physical_kubo_coefficient": True,
            "entropy_current_in_curved_3_plus_1": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only a finite-grid action-derived charge and four-momentum "
            "conserving response plus algebraic Bethe-Salpeter/KMS interface. It is not "
            "a microscopic vertex or SK action match, physical Kubo coefficient, SI map, "
            "alpha_Phi_K calibration, TTG validation, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "ENERGY_MOMENTUM_BS_STATUS",
    "EnergyMomentumConservingBSState",
    "energy_momentum_conserving_bs_state",
    "energy_momentum_conserving_bs_contract",
]
