"""Conservative continuum-collocation collision operator for Topic 13.

This lane connects the action-derived exact two-to-two sample to the finite
temperature momentum basis used by the full-moment response lane.  Exact
channel legs are mapped into the basis by an explicit interpolation matrix,
then the conserved charge and four-momentum moments are removed with the same
Gram projector used by the finite-grid interface.  The action-derived width
operator supplies the continuum-collocation diagonal and the mapped channel
operator is retained as an explicit vertex correction.

The result is a finite-cutoff conservative collocation interface.  It is not a
continuum-limit proof, a microscopic Bethe-Salpeter vertex, a full SK action
match, a physical Kubo coefficient, an SI observable, or a calibration of
alpha_Phi_K.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cosh, exp, expm1, isfinite, sinh

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_energy_momentum_conserving_bethe_salpeter import (
    energy_momentum_conserving_bs_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


CONTINUUM_COLLISION_STATUS = (
    "PASS_ACTION_DERIVED_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE"
)


@dataclass(frozen=True)
class ContinuumCollisionOperatorState:
    """Finite-cutoff conservative collocation and algebraic vertex values."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    momentum_cutoff: float
    radial_order: int
    angular_order: int
    transition_quadrature_order: int
    transition_channel_count: int
    transition_interpolation_order: int
    state_count: int
    transition_state_count: int
    state_species_signs: tuple[float, ...]
    state_momenta: tuple[tuple[float, float, float], ...]
    state_energies: tuple[float, ...]
    susceptibility_weights: tuple[float, ...]
    collision_widths: tuple[float, ...]
    transition_channel_rates: tuple[float, ...]
    exact_channel_invariant_residuals: tuple[tuple[float, float, float, float, float], ...]
    exact_channel_detailed_balance_residuals: tuple[float, ...]
    invariant_rank: int
    interpolation_column_sum_residual: float
    basis_coverage_count: int
    transition_support_component_count: int
    transition_support_connected: bool
    raw_mapped_invariant_residual: float
    projected_mapped_invariant_residual: float
    projection_correction_relative_norm: float
    continuum_operator: tuple[tuple[float, ...], ...]
    action_width_operator: tuple[tuple[float, ...], ...]
    transition_vertex_operator: tuple[tuple[float, ...], ...]
    collision_operator_eigenvalues: tuple[float, ...]
    collision_conservation_residual: float
    operator_symmetry_residual: float
    positive_semidefinite_min_eigenvalue: float
    null_mode_count: int
    positive_mode_rate: float
    transition_vertex_trace_ratio: float
    vertex_decomposition_residual: float
    source_vector: tuple[float, ...]
    projected_source_vector: tuple[float, ...]
    source_constraint_residual: float
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
    continuum_limit_completed: bool = False
    microscopic_bethe_salpeter_match_completed: bool = False
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_CONSERVATIVE_CONTINUUM_COLLOCATION_NOT_MICROSCOPIC"
    )
    moment_direction_rule: str = "axis6"
    transition_coordinate_map: str = "legacy_z_interpolation"


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


def _bose_frequency(argument: float) -> float:
    x = _positive(argument, "beta frequency")
    return exp(-x) if x > 50.0 else 1.0 / expm1(x)


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _retarded_response(
    source: np.ndarray,
    frequency: float,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
) -> complex:
    projected = eigenvectors.T @ source
    response = 0.0j
    for coefficient, eigenvalue in zip(projected, eigenvalues):
        if eigenvalue <= 1.0e-12 and frequency == 0.0:
            continue
        response += float(coefficient * coefficient) / (eigenvalue - 1.0j * frequency)
    return complex(response)


def _bethe_salpeter_residual(
    operator: np.ndarray,
    frequency: float,
    reference_rate: float,
) -> float:
    identity = np.eye(operator.shape[0], dtype=float)
    bare = np.linalg.inv(reference_rate * identity - 1.0j * frequency * identity)
    kernel = reference_rate * identity - operator
    full = np.linalg.inv(operator - 1.0j * frequency * identity)
    ladder = bare + bare @ kernel @ full
    return float(np.linalg.norm(ladder - full) / max(np.linalg.norm(full), 1.0))


def _union_find_component_count(
    support_rows: np.ndarray,
    state_count: int,
) -> tuple[int, int]:
    parent = list(range(state_count))
    covered = np.zeros(state_count, dtype=bool)

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(first: int, second: int) -> None:
        left = find(first)
        right = find(second)
        if left != right:
            parent[right] = left

    for row in support_rows:
        indices = np.flatnonzero(row)
        if indices.size == 0:
            continue
        covered[indices] = True
        first = int(indices[0])
        for index in indices[1:]:
            union(first, int(index))
    roots = {find(index) for index in np.flatnonzero(covered)}
    return len(roots), int(np.count_nonzero(covered))


def _interpolation_matrix(
    exact_signs: tuple[float, ...],
    exact_momenta: tuple[tuple[float, float, float], ...],
    exact_energies: tuple[float, ...],
    basis_signs: tuple[float, ...],
    basis_momenta: tuple[tuple[float, float, float], ...],
    basis_energies: tuple[float, ...],
    *,
    cutoff: float,
    support_order: int,
) -> np.ndarray:
    basis_momentum_array = np.asarray(basis_momenta, dtype=float)
    basis_energy_array = np.asarray(basis_energies, dtype=float)
    scale = max(float(cutoff), 1.0)
    matrix = np.zeros((len(basis_signs), len(exact_signs)), dtype=float)
    for column, (sign, momentum, energy) in enumerate(
        zip(exact_signs, exact_momenta, exact_energies)
    ):
        compatible = np.asarray(
            [index for index, basis_sign in enumerate(basis_signs) if basis_sign == sign],
            dtype=int,
        )
        if compatible.size == 0:
            raise ValueError("exact channel species has no continuum basis state")
        momentum_delta = basis_momentum_array[compatible] - np.asarray(momentum, dtype=float)
        energy_delta = basis_energy_array[compatible] - float(energy)
        distance = (
            np.sum(momentum_delta * momentum_delta, axis=1) + energy_delta * energy_delta
        ) / (scale * scale)
        order = np.argsort(distance, kind="stable")[: min(int(support_order), compatible.size)]
        bandwidth = max(float(distance[order[-1]]), 0.05)
        coefficients = np.exp(-distance[order] / bandwidth)
        coefficients /= float(np.sum(coefficients))
        matrix[compatible[order], column] = coefficients
    return matrix


def _weighted_transition_rows(vectors, interpolation, exact_weights, basis_weights):
    """Pull back channel rows when interpolation acts on psi, not sqrt(w)*psi."""
    v, s = np.asarray(vectors), np.asarray(interpolation)
    we, wb = np.asarray(exact_weights), np.asarray(basis_weights)
    if we.ndim != 1 or wb.ndim != 1 or s.shape != (len(wb), len(we)) or v.ndim != 2 or v.shape[1] != len(we):
        raise ValueError("incompatible transition coordinate dimensions")
    if any(not np.all(np.isfinite(a)) for a in (v, s, we, wb)) or np.any(we <= 0) or np.any(wb <= 0):
        raise ValueError("finite arrays and positive susceptibility weights required")
    return ((v * np.sqrt(we)) @ s.T) / np.sqrt(wb)[None, :]


def continuum_collision_operator_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    radial_order: int = 8,
    collision_integration_order: int = 24,
    angular_order: int = 24,
    cutoff_factor: float = 48.0,
    transition_quadrature_order: int = 24,
    transition_channel_count: int = 64,
    transition_interpolation_order: int = 40,
    retarded_frequency_over_rate: tuple[float, ...] = (0.0, 0.5, 1.0, 2.0),
    kms_frequency_over_temperature: tuple[float, ...] = (0.25, 0.5, 1.0),
    bs_frequency_over_rate: tuple[float, ...] = (0.5, 1.0, 2.0),
    _direction_rule: str = "axis6",
    _transition_map: str = "legacy_z_interpolation",
) -> ContinuumCollisionOperatorState:
    """Build the conservative finite-cutoff continuum-collocation operator."""

    if _transition_map not in ("legacy_z_interpolation", "weighted_psi_pullback"):
        raise ValueError("unknown transition coordinate map")

    if isinstance(radial_order, bool) or int(radial_order) != radial_order or int(radial_order) < 8:
        raise ValueError("radial_order must be an integer >= 8")
    if isinstance(angular_order, bool) or int(angular_order) != angular_order or int(angular_order) < 24:
        raise ValueError("angular_order must be an integer >= 24")
    if isinstance(collision_integration_order, bool) or int(collision_integration_order) != collision_integration_order:
        raise ValueError("collision_integration_order must be an integer")
    if int(collision_integration_order) < 24:
        raise ValueError("collision_integration_order must be >= 24")
    if isinstance(transition_quadrature_order, bool) or int(transition_quadrature_order) != transition_quadrature_order:
        raise ValueError("transition_quadrature_order must be an integer")
    if int(transition_quadrature_order) < 24:
        raise ValueError("transition_quadrature_order must be >= 24")
    if isinstance(transition_channel_count, bool) or int(transition_channel_count) != transition_channel_count:
        raise ValueError("transition_channel_count must be an integer")
    if int(transition_channel_count) < 8:
        raise ValueError("transition_channel_count must be >= 8")
    if isinstance(transition_interpolation_order, bool) or int(transition_interpolation_order) != transition_interpolation_order:
        raise ValueError("transition_interpolation_order must be an integer")
    if int(transition_interpolation_order) < 2:
        raise ValueError("transition_interpolation_order must be >= 2")

    def ordered_nonnegative(values: tuple[float, ...], name: str) -> tuple[float, ...]:
        if not values:
            raise ValueError(f"{name} must not be empty")
        result = tuple(_finite(value, name) for value in values)
        if tuple(sorted(result)) != result or any(value < 0.0 for value in result):
            raise ValueError(f"{name} must be sorted and non-negative")
        return result

    response_ratios = ordered_nonnegative(
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
    base = energy_momentum_conserving_bs_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=int(radial_order),
        collision_integration_order=int(collision_integration_order),
        angular_order=int(angular_order),
        cutoff_factor=cutoff_factor,
        retarded_frequency_over_rate=response_ratios,
        kms_frequency_over_temperature=kms_ratios,
        bs_frequency_over_rate=bs_ratios,
        include_final_state_bose_enhancement=True,
        _direction_rule=_direction_rule,
    )
    exact = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=int(transition_quadrature_order),
        channel_count=int(transition_channel_count),
        cutoff_factor=max(float(cutoff_factor), 36.0),
        retarded_frequency_over_rate=response_ratios,
        kms_frequency_over_temperature=kms_ratios,
        bs_frequency_over_rate=bs_ratios,
    )

    projector = np.asarray(base.projector, dtype=float)
    invariant_columns = np.asarray(base.conserved_invariants, dtype=float)
    basis_weights = np.asarray(base.susceptibility_weights, dtype=float)
    width_array = np.asarray(base.collision_widths, dtype=float)
    base_operator = np.asarray(base.collision_operator, dtype=float)
    interpolation = _interpolation_matrix(
        exact.state_species_signs,
        exact.state_momenta,
        exact.state_energies,
        base.state_species_signs,
        base.state_momenta,
        base.state_energies,
        cutoff=base.momentum_cutoff,
        support_order=int(transition_interpolation_order),
    )
    exact_vectors = np.asarray(exact.transition_vectors, dtype=float)
    if _transition_map == "weighted_psi_pullback":
        mapped_rows = _weighted_transition_rows(
            exact_vectors, interpolation, exact.state_weights, basis_weights
        )
    else:
        mapped_rows = exact_vectors @ interpolation.T
    projected_rows = mapped_rows @ projector
    transition_rates = np.asarray(exact.channel_rates, dtype=float)
    transition_vertex = projected_rows.T @ np.diag(transition_rates) @ projected_rows
    operator = base_operator + transition_vertex

    raw_invariant_residual = float(
        np.linalg.norm(mapped_rows @ invariant_columns)
        / max(np.linalg.norm(mapped_rows) * np.linalg.norm(invariant_columns), 1.0)
    )
    projected_invariant_residual = float(
        np.linalg.norm(projected_rows @ invariant_columns)
        / max(np.linalg.norm(projected_rows) * np.linalg.norm(invariant_columns), 1.0)
    )
    projection_correction_relative_norm = float(
        np.linalg.norm(mapped_rows - projected_rows) / max(np.linalg.norm(mapped_rows), 1.0)
    )
    interpolation_column_sum_residual = float(
        np.max(np.abs(np.sum(interpolation, axis=0) - 1.0))
    )
    support_rows = (
        (np.abs(exact_vectors) > 0.0) @ (interpolation > 0.0).T > 0
    )
    component_count, basis_coverage_count = _union_find_component_count(
        support_rows,
        int(base.state_count),
    )

    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    positive_eigenvalues = eigenvalues[eigenvalues > 1.0e-12]
    positive_rate = _positive(float(np.mean(positive_eigenvalues)), "positive mode rate")
    source = np.asarray(base.source_vector, dtype=float)
    projected_source = np.asarray(base.projected_source_vector, dtype=float)
    frequencies = tuple(positive_rate * ratio for ratio in response_ratios)
    responses = tuple(
        _retarded_response(projected_source, frequency, eigenvalues, eigenvectors)
        for frequency in frequencies
    )
    kms_frequencies = tuple(base.temperature * ratio for ratio in kms_ratios)
    kms_responses = tuple(
        _retarded_response(projected_source, frequency, eigenvalues, eigenvectors)
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
        _bethe_salpeter_residual(operator, frequency, positive_rate)
        for frequency in bs_frequencies
    )
    entropy_witness = _positive(
        float(np.dot(projected_source, operator @ projected_source) / base.temperature),
        "entropy production witness",
    )
    conservation_residual = float(np.linalg.norm(operator @ invariant_columns))
    symmetry_residual = float(np.linalg.norm(operator - operator.T))
    vertex_trace_ratio = float(
        np.trace(transition_vertex) / max(np.trace(base_operator), 1.0e-300)
    )
    decomposition_residual = float(
        np.linalg.norm(operator - base_operator - transition_vertex)
        / max(np.linalg.norm(operator), 1.0)
    )
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
        raise FloatingPointError("continuum-collocation response is not finite")

    return ContinuumCollisionOperatorState(
        temperature=base.temperature,
        chemical_potential=base.chemical_potential,
        space_response=base.space_response,
        effective_mass=base.effective_mass,
        momentum_cutoff=base.momentum_cutoff,
        radial_order=base.radial_order,
        angular_order=base.angular_order,
        transition_quadrature_order=int(transition_quadrature_order),
        transition_channel_count=exact.channel_count,
        transition_interpolation_order=int(transition_interpolation_order),
        state_count=base.state_count,
        transition_state_count=exact.state_count,
        state_species_signs=tuple(base.state_species_signs),
        state_momenta=tuple(base.state_momenta),
        state_energies=tuple(base.state_energies),
        susceptibility_weights=tuple(float(value) for value in basis_weights),
        collision_widths=tuple(float(value) for value in width_array),
        transition_channel_rates=tuple(float(value) for value in transition_rates),
        exact_channel_invariant_residuals=tuple(exact.channel_invariant_residuals),
        exact_channel_detailed_balance_residuals=tuple(exact.channel_detailed_balance_residuals),
        invariant_rank=base.invariant_rank,
        interpolation_column_sum_residual=interpolation_column_sum_residual,
        basis_coverage_count=basis_coverage_count,
        transition_support_component_count=component_count,
        transition_support_connected=component_count == 1,
        raw_mapped_invariant_residual=raw_invariant_residual,
        projected_mapped_invariant_residual=projected_invariant_residual,
        projection_correction_relative_norm=projection_correction_relative_norm,
        continuum_operator=_matrix_tuple(operator),
        action_width_operator=_matrix_tuple(base_operator),
        transition_vertex_operator=_matrix_tuple(transition_vertex),
        collision_operator_eigenvalues=tuple(float(value) for value in eigenvalues),
        collision_conservation_residual=conservation_residual,
        operator_symmetry_residual=symmetry_residual,
        positive_semidefinite_min_eigenvalue=float(np.min(eigenvalues)),
        null_mode_count=int(np.sum(eigenvalues <= 1.0e-12)),
        positive_mode_rate=positive_rate,
        transition_vertex_trace_ratio=vertex_trace_ratio,
        vertex_decomposition_residual=decomposition_residual,
        source_vector=tuple(float(value) for value in source),
        projected_source_vector=tuple(float(value) for value in projected_source),
        source_constraint_residual=float(np.linalg.norm(invariant_columns.T @ projected_source)),
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
        moment_direction_rule=base.moment_direction_rule,
        transition_coordinate_map=_transition_map,
    )


def continuum_collision_operator_contract() -> dict[str, object]:
    """Return equations, units, and explicit finite-cutoff boundaries."""

    return {
        "status": CONTINUUM_COLLISION_STATUS,
        "equations": {
            "continuum_basis": "w_(s,k,n)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk*dOmega/(4*pi)",
            "conserved_invariants": "I_A=(q_s,E_k,p_x,p_y,p_z)*sqrt(w_(s,k,n)); Q=orth(I_A); P=I-Q*Q^T",
            "exact_channel_mapping": "u_c=B*v_c; B maps exact channel legs to the declared momentum basis by normalized local interpolation",
            "weighted_psi_candidate": "U=V sqrt(W_exact) B.T inv_sqrt(W_basis); legacy map remains default comparator",
            "conservative_channel_projection": "u_c^P=P*u_c",
            "action_width_operator": "L_width=P*diag(Gamma_action_s(k))*P",
            "transition_vertex_operator": "K_transition=sum_c W_c*u_c^P*(u_c^P)^T",
            "continuum_collocation_operator": "L_cont=L_width+K_transition; L_cont*I_A=0; L_cont>=0",
            "retarded_response": "G_R=(L_cont-i*omega*I)^(-1); K_R=b_perp^T*G_R*b_perp",
            "bethe_salpeter_identity": "G_0=(gamma_ref*I-i*omega*I)^(-1); K_BS=gamma_ref*I-L_cont; G_R=G_0+G_0*K_BS*G_R",
            "wightman_matching": "G^>=rho*(1+n_B); G^<=rho*n_B; rho=2*Im(K_R)",
            "kms_ratio": "G^>/G^<=exp(beta_th*omega)",
            "entropy_witness": "sigma_formal=b_perp^T*L_cont*b_perp/T>=0",
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
            "action-derived elastic two-to-two sample plus finite-temperature momentum-basis "
            "collocation, explicit interpolation, and Gram-projected conservative vertex correction"
        ),
        "observable": "finite-cutoff conservative momentum-current response and algebraic vertex/KMS interface",
        "data_role": "ACTION_DERIVED_CONSERVATIVE_CONTINUUM_COLLOCATION_NOT_MICROSCOPIC",
        "included": {
            "action_derived_exact_channel_sample": True,
            "shared_continuum_momentum_basis": True,
            "explicit_interpolation_matrix": True,
            "charge_energy_momentum_projection": True,
            "connected_transition_support_audit": True,
            "positive_semidefinite_operator": True,
            "algebraic_vertex_decomposition": True,
            "algebraic_bethe_salpeter_identity": True,
            "algebraic_sk_kms_fdt_interface": True,
        },
        "excluded": {
            "continuum_limit": True,
            "microscopic_bethe_salpeter_vertex": True,
            "microscopic_sk_action_match": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_dissipative_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only a finite-cutoff action-derived conservative continuum-collocation "
            "operator and algebraic vertex/KMS interface. The interpolation and Gram projection "
            "are declared formal numerical mappings; this is not a continuum-limit proof, a "
            "microscopic Bethe-Salpeter vertex, a microscopic SK action match, a physical Kubo "
            "coefficient, an SI map, an alpha_Phi_K calibration, TTG validation, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "CONTINUUM_COLLISION_STATUS",
    "ContinuumCollisionOperatorState",
    "continuum_collision_operator_state",
    "continuum_collision_operator_contract",
]
