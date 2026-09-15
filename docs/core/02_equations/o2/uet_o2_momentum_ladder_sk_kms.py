"""Momentum-dependent conserving response and SK/KMS interface for Topic 13.

This lane evaluates the corrected action-derived collision kernel on a radial
momentum grid, then builds a weighted charge-conserving resolvent.  The
resolvent supplies a finite-frequency response and an algebraic Wightman/KMS
interface.  It is intentionally not a microscopic Bethe-Salpeter solution,
not a full energy-momentum conserving collision operator, and not a physical
Kubo or SI coefficient.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cosh, exp, expm1, isfinite, sinh, sqrt

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


MOMENTUM_LADDER_SK_KMS_STATUS = (
    "PASS_ACTION_DERIVED_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE"
)


@dataclass(frozen=True)
class MomentumLadderSKKMSState:
    """Momentum-grid response and algebraic KMS quantities."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    momentum_cutoff: float
    momentum_nodes: tuple[float, ...]
    momentum_weights: tuple[float, ...]
    state_species_signs: tuple[float, ...]
    charge_by_state: tuple[float, ...]
    susceptibility_weights: tuple[float, ...]
    collision_widths: tuple[float, ...]
    charge_conserved_vector: tuple[float, ...]
    projector: tuple[tuple[float, ...], ...]
    collision_operator: tuple[tuple[float, ...], ...]
    collision_operator_eigenvalues: tuple[float, ...]
    positive_mode_rate: float
    source_vector: tuple[float, ...]
    projected_source_vector: tuple[float, ...]
    charge_conservation_residual: float
    operator_symmetry_residual: float
    source_projection_residual: float
    positive_semidefinite_min_eigenvalue: float
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
    entropy_production_witness: float
    quadrature_order: int
    collision_integration_order: int
    angular_order: int
    final_state_bose_enhancement_included: bool = True
    momentum_dependent_resolvent_included: bool = True
    microscopic_bethe_salpeter_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    data_role: str = (
        "ACTION_DERIVED_MOMENTUM_LADDER_SK_KMS_INTERFACE_NOT_PHYSICAL_KUBO"
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


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _bose_frequency(argument: float) -> float:
    x = _positive(argument, "beta frequency")
    return exp(-x) if x > 50.0 else 1.0 / expm1(x)


def _retarded_response(
    operator: np.ndarray,
    source: np.ndarray,
    omega: float,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> complex:
    """Evaluate b^T (L - i omega I)^-1 b on the projected subspace."""

    projections = eigenvectors.T @ source
    if omega == 0.0:
        scale = max(float(np.max(eigenvalues)), 1.0)
        mask = eigenvalues > 1.0e-12 * scale
        if not np.any(mask):
            raise FloatingPointError("no dissipative mode remains after projection")
        return complex(np.sum(projections[mask] ** 2 / eigenvalues[mask]), 0.0)
    identity = np.eye(operator.shape[0], dtype=float)
    solved = np.linalg.solve(operator - 1j * omega * identity, source)
    return complex(np.vdot(source, solved))


def momentum_ladder_sk_kms_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 32,
    collision_integration_order: int = 48,
    angular_order: int = 32,
    cutoff_factor: float = 48.0,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    kms_frequency_over_temperature: tuple[float, ...] = (0.25, 0.5, 1.0),
    include_final_state_bose_enhancement: bool = True,
) -> MomentumLadderSKKMSState:
    """Evaluate the declared momentum-dependent response interface."""

    if not include_final_state_bose_enhancement:
        raise ValueError("this lane requires the corrected quantum collision width")
    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    if int(quadrature_order) < 8:
        raise ValueError("quadrature_order must be >= 8")
    if isinstance(collision_integration_order, bool) or int(collision_integration_order) != collision_integration_order:
        raise ValueError("collision_integration_order must be an integer")
    if int(collision_integration_order) < 24:
        raise ValueError("collision_integration_order must be >= 24")
    if isinstance(angular_order, bool) or int(angular_order) != angular_order:
        raise ValueError("angular_order must be an integer")
    if int(angular_order) < 24:
        raise ValueError("angular_order must be >= 24")
    if not retarded_frequency_over_rate:
        raise ValueError("retarded_frequency_over_rate must not be empty")
    response_ratios = tuple(
        _finite(value, "retarded_frequency_over_rate")
        for value in retarded_frequency_over_rate
    )
    if tuple(sorted(response_ratios)) != response_ratios or response_ratios[0] != 0.0:
        raise ValueError("retarded_frequency_over_rate must be sorted and start at zero")
    if any(value < 0.0 for value in response_ratios):
        raise ValueError("retarded_frequency_over_rate must be non-negative")
    if not kms_frequency_over_temperature:
        raise ValueError("kms_frequency_over_temperature must not be empty")
    kms_ratios = tuple(
        _positive(value, "kms_frequency_over_temperature")
        for value in kms_frequency_over_temperature
    )
    if tuple(sorted(kms_ratios)) != kms_ratios:
        raise ValueError("kms_frequency_over_temperature must be sorted")

    config = config or FiniteTemperatureO2QuasiparticleConfig()
    t, mu, mass, mu_eff, quartic = _normal_state_inputs(
        temperature,
        chemical_potential,
        space_response,
        config,
    )
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    cutoff = max(cutoff_factor * t, cutoff_factor * mass, cutoff_factor * mu_eff, 1.0)
    momentum_nodes_array, momentum_weights_array = _quadrature(
        int(quadrature_order), cutoff
    )
    collision_nodes_array, collision_weights_array = _quadrature(
        int(collision_integration_order), cutoff
    )
    angle_nodes, angle_weights = _quadrature(int(angular_order), 2.0)
    angle_nodes = angle_nodes - 1.0
    signs = (-1.0, 1.0)
    state_signs: list[float] = []
    charges: list[float] = []
    susceptibility: list[float] = []
    widths: list[float] = []
    source: list[float] = []
    radial_measure = 1.0 / (2.0 * np.pi * np.pi)
    for sign in signs:
        charge = sign
        for momentum, momentum_weight in zip(
            momentum_nodes_array,
            momentum_weights_array,
        ):
            p = float(momentum)
            energy = sqrt(p * p + mass * mass)
            occupation = _bose(energy - sign * mu_eff, t)
            susceptibility_weight = (
                float(momentum_weight)
                * p
                * p
                * radial_measure
                * occupation
                * (1.0 + occupation)
                / t
            )
            width = _collision_width(
                p,
                sign,
                t,
                mass,
                mu_eff,
                quartic,
                collision_nodes_array,
                collision_weights_array,
                angle_nodes,
                angle_weights,
                include_final_state_bose_enhancement=True,
            )
            state_signs.append(sign)
            charges.append(charge)
            susceptibility.append(_positive(susceptibility_weight, "susceptibility weight"))
            widths.append(_positive(width, "momentum collision width"))
            source.append(charge * (p / energy) * sqrt(susceptibility[-1]))

    state_count = len(widths)
    if state_count < 4:
        raise ValueError("momentum ladder requires at least four state points")
    width_array = np.asarray(widths, dtype=float)
    susceptibility_array = np.asarray(susceptibility, dtype=float)
    charge_array = np.asarray(charges, dtype=float)
    conserved = charge_array * np.sqrt(susceptibility_array)
    conserved_norm = _positive(float(np.dot(conserved, conserved)), "conserved norm")
    projector = np.eye(state_count, dtype=float) - np.outer(conserved, conserved) / conserved_norm
    operator = projector @ np.diag(width_array) @ projector
    source_array = np.asarray(source, dtype=float)
    projected_source = projector @ source_array
    positive_rate = _positive(float(np.mean(width_array)), "positive mode rate")
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    frequencies = tuple(positive_rate * ratio for ratio in response_ratios)
    responses = tuple(
        _retarded_response(
            operator,
            projected_source,
            frequency,
            eigenvalues,
            eigenvectors,
        )
        for frequency in frequencies
    )
    kms_frequencies = tuple(t * ratio for ratio in kms_ratios)
    kms_responses = tuple(
        _retarded_response(
            operator,
            projected_source,
            frequency,
            eigenvalues,
            eigenvectors,
        )
        for frequency in kms_frequencies
    )
    spectral = tuple(max(2.0 * response.imag, 0.0) for response in kms_responses)
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
    entropy_witness = _positive(
        float(np.dot(projected_source, operator @ projected_source) / t),
        "entropy production witness",
    )
    residuals = (
        float(np.linalg.norm(operator @ conserved)),
        float(np.linalg.norm(operator - operator.T)),
        float(np.dot(conserved, projected_source)),
    )
    spread = (float(np.max(width_array)) - float(np.min(width_array))) / float(np.mean(width_array))
    values = (*eigenvalues, *[response.real for response in responses], *[response.imag for response in responses], *spectral, *greater, *lesser, *noise, *kms_ratio, *noise_target, entropy_witness)
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("momentum ladder response is not finite")

    return MomentumLadderSKKMSState(
        temperature=t,
        chemical_potential=mu,
        space_response=float(space_response),
        effective_mass=mass,
        momentum_cutoff=float(cutoff),
        momentum_nodes=tuple(float(value) for value in momentum_nodes_array),
        momentum_weights=tuple(float(value) for value in momentum_weights_array),
        state_species_signs=tuple(state_signs),
        charge_by_state=tuple(charges),
        susceptibility_weights=tuple(susceptibility),
        collision_widths=tuple(widths),
        charge_conserved_vector=tuple(float(value) for value in conserved),
        projector=_matrix_tuple(projector),
        collision_operator=_matrix_tuple(operator),
        collision_operator_eigenvalues=tuple(float(value) for value in eigenvalues),
        positive_mode_rate=positive_rate,
        source_vector=tuple(float(value) for value in source_array),
        projected_source_vector=tuple(float(value) for value in projected_source),
        charge_conservation_residual=residuals[0],
        operator_symmetry_residual=residuals[1],
        source_projection_residual=residuals[2],
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
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
        entropy_production_witness=entropy_witness,
        quadrature_order=int(quadrature_order),
        collision_integration_order=int(collision_integration_order),
        angular_order=int(angular_order),
    )


def momentum_ladder_sk_kms_contract() -> dict[str, object]:
    """Return equations, units, and the explicit matching boundary."""

    return {
        "status": MOMENTUM_LADDER_SK_KMS_STATUS,
        "fourier_convention": "exp(-i omega t); K_R=(L-i*omega*I)^(-1) on the projected subspace",
        "equations": {
            "susceptibility_weight": "w_s(k)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk",
            "conserved_charge_vector": "c_(s,k)=q_s*sqrt(w_s(k)), q_s in {-1,+1}",
            "conserving_projector": "P=I-c*c^T/(c^T*c)",
            "momentum_collision_operator": "L=P*diag(Gamma_s(k))*P, L*c=0, L>=0",
            "current_source": "b_(s,k)=q_s*(k/E_s(k))*sqrt(w_s(k)); b_perp=P*b",
            "retarded_response": "K_R(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp",
            "spectral_convention": "rho(omega)=2*Im(K_R(omega)) >= 0 for omega>0 in this relaxation convention",
            "wightman_matching": "G^>(omega)=rho*(1+n_B), G^<(omega)=rho*n_B",
            "kms_ratio": "G^>(omega)/G^<(omega)=exp(beta_th*omega)",
            "fdt_noise": "N(omega)=G^>(omega)+G^<(omega)=rho*coth(beta_th*omega/2)",
            "entropy_witness": "sigma_formal=b_perp^T*L*b_perp/T >= 0",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_rate": "energy",
            "momentum": "energy",
            "response": "formal momentum-grid response quantity",
            "spectral_density": "formal response spectral quantity",
            "entropy_production": "formal natural-unit witness",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived quantum collision widths on a momentum grid plus "
            "weighted charge-conserving matrix resolvent and algebraic KMS interface"
        ),
        "observable": "momentum-dependent relative response and formal KMS/FDT correlator interface",
        "data_role": "ACTION_DERIVED_MOMENTUM_LADDER_SK_KMS_INTERFACE_NOT_PHYSICAL_KUBO",
        "included": {
            "momentum_dependent_quantum_collision_width": True,
            "weighted_charge_conservation": True,
            "positive_semidefinite_projected_operator": True,
            "finite_frequency_retarded_response": True,
            "algebraic_wightman_kms_fdt_matching": True,
            "formal_entropy_positivity": True,
            "quadrature_refinement": True,
        },
        "excluded": {
            "full_energy_momentum_conserving_collision_operator": True,
            "microscopic_bethe_salpeter_vertex_match": True,
            "microscopic_SK_action_match": True,
            "physical_Kubo_coefficient": True,
            "entropy_current_divergence_in_curved_3_plus_1": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only a named action-derived momentum-grid conserving "
            "response and algebraic KMS/FDT interface at a declared finite cutoff. It does not establish a "
            "microscopic Bethe-Salpeter or SK/KMS match, a physical Kubo "
            "coefficient, an SI observable, alpha_Phi_K, TTG validation, or Full "
            "Topic 13 closure."
        ),
    }


__all__ = [
    "MOMENTUM_LADDER_SK_KMS_STATUS",
    "MomentumLadderSKKMSState",
    "momentum_ladder_sk_kms_state",
    "momentum_ladder_sk_kms_contract",
]
