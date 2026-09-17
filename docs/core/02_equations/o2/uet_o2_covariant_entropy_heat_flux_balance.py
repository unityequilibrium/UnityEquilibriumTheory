"""Action-derived natural-unit entropy and heat-flux balance for Topic 13.

This module lifts the finite-temperature, action-derived collision operator to
the local covariant entropy-current notation.  The heat source is the standard
Landau-frame energy-current subtraction

    b_i = (E - h q) (p_i / E) sqrt(w),   h = (epsilon + p) / n,

followed by the same charge/four-momentum Gram projection used by the
continuum collision lane.  The resulting response matrix is a finite-cutoff
natural-unit moment response.  It is not a physical SI Kubo coefficient and
does not calibrate Phi, alpha_Phi_K, or TTG.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Any

import numpy as np

from docs.core.uet_covariant_response import validate_lorentz_metric
from docs.core.uet_o2_continuum_collision_operator import (
    ContinuumCollisionOperatorState,
    continuum_collision_operator_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
    finite_temperature_o2_state,
)


COVARIANT_ENTROPY_HEAT_FLUX_STATUS = (
    "PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE"
)
DEFAULT_METRIC = np.diag((-1.0, 1.0, 1.0, 1.0))
DEFAULT_FOUR_VELOCITY = np.array((1.0, 0.0, 0.0, 0.0), dtype=float)
DEFAULT_THERMAL_FORCE_COVARIANT = np.array((0.0, 1.0, 0.0, 0.0), dtype=float)


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


def _vector4(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (4,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite vector with shape (4,)")
    return result


def _matrix_tuple(matrix: np.ndarray) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in matrix)


def _vector_tuple(vector: np.ndarray) -> tuple[float, ...]:
    return tuple(float(value) for value in vector)


def _invariant_columns(state: ContinuumCollisionOperatorState) -> np.ndarray:
    weights = np.asarray(state.susceptibility_weights, dtype=float)
    signs = np.asarray(state.state_species_signs, dtype=float)
    energies = np.asarray(state.state_energies, dtype=float)
    momenta = np.asarray(state.state_momenta, dtype=float)
    return np.column_stack(
        (signs, energies, momenta[:, 0], momenta[:, 1], momenta[:, 2])
    ) * np.sqrt(weights)[:, None]


def _gram_projector(
    state: ContinuumCollisionOperatorState,
) -> tuple[np.ndarray, np.ndarray, float]:
    invariants = _invariant_columns(state)
    orthonormal, _ = np.linalg.qr(invariants, mode="reduced")
    projector = np.eye(invariants.shape[0], dtype=float) - orthonormal @ orthonormal.T
    return projector, invariants, float(np.linalg.norm(projector @ orthonormal))


def lorentz_boost_x(beta: float) -> np.ndarray:
    """Return a proper boost matrix for the ``(-,+,+,+)`` convention."""

    value = _finite(beta, "beta")
    if abs(value) >= 1.0:
        raise ValueError("|beta| must be below one")
    gamma = 1.0 / sqrt(1.0 - value * value)
    return np.array(
        (
            (gamma, -gamma * value, 0.0, 0.0),
            (-gamma * value, gamma, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
        dtype=float,
    )


def covariant_entropy_heat_flux(
    metric: Any,
    four_velocity: Any,
    temperature: float,
    entropy_density: float,
    kappa_natural: float,
    thermal_force_covariant: Any,
) -> dict[str, Any]:
    """Lift a local scalar response to the covariant entropy-current form.

    ``X_T^mu`` is the projected thermal force.  In a physical thermal lane it
    would be ``-Delta^(mu nu)(nabla_nu T + T a_nu)/T``; this function accepts
    that force as an input so the map does not invent a temperature gradient.
    """

    g, inverse = validate_lorentz_metric(metric)
    velocity = _vector4(four_velocity, "four_velocity")
    if abs(float(velocity @ g @ velocity) + 1.0) > 1.0e-10:
        raise ValueError("four_velocity must be normalized to -1")
    temperature = _positive(temperature, "temperature")
    entropy_density = _finite(entropy_density, "entropy_density")
    kappa = _positive(kappa_natural, "kappa_natural")
    force_covariant = _vector4(thermal_force_covariant, "thermal_force_covariant")
    projector = inverse + np.outer(velocity, velocity)
    force_contravariant = projector @ force_covariant
    projected_force_covariant = g @ force_contravariant
    heat_flux = kappa * force_contravariant
    entropy_current = entropy_density * velocity + heat_flux / temperature
    # X=-Delta(grad T+T a)/T is temperature-weighted entropy force.
    entropy_production = float(projected_force_covariant @ heat_flux) / temperature
    return {
        "metric": g,
        "inverse_metric": inverse,
        "projector": projector,
        "four_velocity": velocity,
        "thermal_force_covariant": projected_force_covariant,
        "thermal_force_contravariant": force_contravariant,
        "heat_flux_contravariant": heat_flux,
        "entropy_current_contravariant": entropy_current,
        "entropy_production": entropy_production,
        "force_orthogonality_residual": abs(float(velocity @ g @ force_contravariant)),
        "heat_flux_orthogonality_residual": abs(float(velocity @ g @ heat_flux)),
    }


def _covariant_tensor_entropy_heat_flux(
    metric: Any,
    four_velocity: Any,
    temperature: float,
    entropy_density: float,
    response_tensor: Any,
    thermal_force_covariant: Any,
) -> dict[str, Any]:
    """Lift the full transverse moment response without isotropic averaging."""
    base = covariant_entropy_heat_flux(
        metric, four_velocity, temperature, entropy_density, 1.0,
        thermal_force_covariant,
    )
    tensor = np.asarray(response_tensor, dtype=float)
    if tensor.shape != (4, 4) or not np.all(np.isfinite(tensor)):
        raise ValueError("response_tensor must be finite with shape (4,4)")
    scale = max(float(np.linalg.norm(tensor)), 1.0)
    if np.linalg.norm(tensor-tensor.T) > 1.0e-12*scale:
        raise ValueError("response_tensor must be symmetric")
    velocity = base["four_velocity"]
    g = base["metric"]
    if np.linalg.norm(velocity @ g @ tensor) > 1.0e-12*scale:
        raise ValueError("response_tensor must be transverse")
    if np.min(np.linalg.eigvalsh(tensor)) < -1.0e-8:
        raise ValueError("response_tensor must be positive semidefinite within the existing numerical tolerance")
    heat_flux = tensor @ base["thermal_force_covariant"]
    base.update(
        heat_flux_contravariant=heat_flux,
        entropy_current_contravariant=entropy_density*velocity+heat_flux/temperature,
        entropy_production=float(base["thermal_force_covariant"] @ heat_flux)/temperature,
        heat_flux_orthogonality_residual=abs(float(velocity @ g @ heat_flux)),
    )
    return base


def _boost_tensor_residual(
    metric: np.ndarray,
    velocity: np.ndarray,
    temperature: float,
    entropy_density: float,
    response_tensor: np.ndarray,
    force_covariant: np.ndarray,
    base: dict[str, Any],
) -> float:
    boost = lorentz_boost_x(0.37)
    boosted_velocity = boost @ velocity
    boosted_force_covariant = np.linalg.inv(boost).T @ force_covariant
    boosted = _covariant_tensor_entropy_heat_flux(
        metric,
        boosted_velocity,
        temperature,
        entropy_density,
        boost @ response_tensor @ boost.T,
        boosted_force_covariant,
    )
    scalar_residual = abs(
        float(boosted["entropy_production"]) - float(base["entropy_production"])
    )
    transformed_force = np.linalg.inv(boost).T @ base["thermal_force_covariant"]
    force_residual = float(
        np.linalg.norm(boosted["thermal_force_covariant"] - transformed_force)
    )
    transformed_heat = boost @ base["heat_flux_contravariant"]
    heat_residual = float(
        np.linalg.norm(boosted["heat_flux_contravariant"] - transformed_heat)
    )
    return max(scalar_residual, force_residual, heat_residual)


@dataclass(frozen=True)
class CovariantEntropyHeatFluxBalanceState:
    """Finite-cutoff natural-unit heat-current and entropy-balance witnesses."""

    temperature: float
    chemical_potential: float
    space_response: float
    eos_branch: str
    entropy_density: float
    pressure: float
    energy_density: float
    charge_density: float
    enthalpy_per_charge: float
    operator_state_count: int
    transition_channel_count: int
    heat_response_matrix: tuple[tuple[float, ...], ...]
    kappa_natural: float
    heat_response_isotropy_residual: float
    collision_operator_min_eigenvalue: float
    collision_operator_symmetry_residual: float
    thermal_force_covariant: tuple[float, ...]
    thermal_force_contravariant: tuple[float, ...]
    heat_flux_contravariant: tuple[float, ...]
    entropy_current_contravariant: tuple[float, ...]
    entropy_production: float
    kinetic_entropy_production: float
    entropy_balance_residual: float
    kinetic_equation_residual: float
    charge_balance_residual: float
    energy_balance_residual: float
    momentum_balance_residual: float
    heat_flux_response_residual: float
    force_orthogonality_residual: float
    heat_flux_orthogonality_residual: float
    projector_orthogonality_residual: float
    lorentz_covariance_residual: float
    equilibrium_heat_flux_norm: float
    finite_cutoff_boundary_declared: bool = True
    microscopic_sk_kms_match_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_CUTOFF_NATURAL_MOMENT_RESPONSE_NOT_PHYSICAL_KUBO"
    )
    frame_current_decomposition: dict[str, Any] | None = None


def covariant_entropy_heat_flux_balance_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    metric: Any | None = None,
    four_velocity: Any | None = None,
    thermal_force_covariant: Any | None = None,
    operator_state: ContinuumCollisionOperatorState | None = None,
) -> CovariantEntropyHeatFluxBalanceState:
    """Build the action-derived local rest-frame response and covariant lift."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    metric_array = np.asarray(
        DEFAULT_METRIC if metric is None else metric, dtype=float
    )
    velocity = _vector4(
        DEFAULT_FOUR_VELOCITY if four_velocity is None else four_velocity,
        "four_velocity",
    )
    force_covariant = _vector4(
        DEFAULT_THERMAL_FORCE_COVARIANT
        if thermal_force_covariant is None
        else thermal_force_covariant,
        "thermal_force_covariant",
    )
    if not np.allclose(metric_array, DEFAULT_METRIC, atol=1.0e-12):
        raise NotImplementedError(
            "the finite-cutoff moment map is evaluated in the declared local rest frame"
        )
    if not np.allclose(velocity, DEFAULT_FOUR_VELOCITY, atol=1.0e-12):
        raise NotImplementedError(
            "supply a local rest-frame state; covariant lifting is handled by the projector"
        )
    operator = operator_state or continuum_collision_operator_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        radial_order=8,
        collision_integration_order=24,
        angular_order=24,
        cutoff_factor=48.0,
        transition_quadrature_order=24,
        transition_channel_count=64,
        transition_interpolation_order=40,
    )
    if (
        abs(operator.temperature - temperature) > 1.0e-12
        or abs(operator.chemical_potential - chemical_potential) > 1.0e-12
        or abs(operator.space_response - space_response) > 1.0e-12
    ):
        raise ValueError("operator_state does not match the requested thermodynamic state")
    eos = finite_temperature_o2_state(
        temperature, chemical_potential, space_response, config
    )
    if eos.branch != "normal":
        raise NotImplementedError(
            "this action-derived heat-current lane is restricted to the declared normal quasiparticle branch"
        )
    if abs(eos.charge_density) <= 1.0e-14:
        raise ValueError("Landau heat-current subtraction requires nonzero charge density")
    enthalpy_per_charge = (eos.energy_density + eos.pressure) / eos.charge_density

    projector, invariants, projector_residual = _gram_projector(operator)
    energies = np.asarray(operator.state_energies, dtype=float)
    momenta = np.asarray(operator.state_momenta, dtype=float)
    charges = np.asarray(operator.state_species_signs, dtype=float)
    weights = np.asarray(operator.susceptibility_weights, dtype=float)
    velocities = momenta / energies[:, None]
    heat_sources = np.stack(
        [
            (energies - enthalpy_per_charge * charges)
            * velocities[:, axis]
            * np.sqrt(weights)
            for axis in range(3)
        ],
        axis=1,
    )
    projected_sources = projector @ heat_sources
    collision_operator = np.asarray(operator.continuum_operator, dtype=float)
    collision_operator_symmetric = 0.5 * (
        collision_operator + collision_operator.T
    )
    collision_inverse = np.linalg.pinv(collision_operator_symmetric, rcond=1.0e-12)
    response_matrix = projected_sources.T @ collision_inverse @ projected_sources
    response_matrix = 0.5 * (response_matrix + response_matrix.T)
    diagonal = np.diag(response_matrix)
    kappa_natural = _positive(float(np.trace(response_matrix) / 3.0), "kappa_natural")
    isotropy_residual = float(
        np.max(np.abs(response_matrix - kappa_natural * np.eye(3)))
        / max(kappa_natural, 1.0)
    )

    response_tensor = np.zeros((4, 4), dtype=float)
    response_tensor[1:, 1:] = response_matrix
    covariant = _covariant_tensor_entropy_heat_flux(
        metric_array,
        velocity,
        temperature,
        eos.entropy_density,
        response_tensor,
        force_covariant,
    )
    force_spatial = np.asarray(covariant["thermal_force_contravariant"], dtype=float)[1:]
    distribution_response = collision_inverse @ projected_sources @ force_spatial
    collision_action = collision_operator_symmetric @ distribution_response
    # Susceptibility weights contain f(1+f)/T: the entropy metric is I/T.
    kinetic_entropy = float(distribution_response @ collision_action) / temperature
    entropy_production = float(covariant["entropy_production"])
    heat_response = response_matrix @ force_spatial
    heat_flux_spatial = np.asarray(covariant["heat_flux_contravariant"], dtype=float)[1:]
    kinetic_equation_residual = float(
        np.linalg.norm(collision_action - projected_sources @ force_spatial)
        / max(np.linalg.norm(projected_sources @ force_spatial), 1.0)
    )
    invariant_balance = invariants.T @ collision_action
    charge_balance = float(abs(invariant_balance[0]))
    energy_balance = float(abs(invariant_balance[1]))
    momentum_balance = float(np.linalg.norm(invariant_balance[2:]))
    equilibrium = _covariant_tensor_entropy_heat_flux(
        metric_array,
        velocity,
        temperature,
        eos.entropy_density,
        response_tensor,
        np.zeros(4, dtype=float),
    )
    values = (
        *response_matrix.ravel(),
        kappa_natural,
        entropy_production,
        kinetic_entropy,
        kinetic_equation_residual,
        *invariant_balance,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("covariant heat-flux response is not finite")
    # Raw moments distinguish Landau energy flux from Q-h*V heat response.
    energy_source = momenta * np.sqrt(weights)[:, None]
    charge_source = charges[:, None] * velocities * np.sqrt(weights)[:, None]
    energy_current = np.r_[0.0, energy_source.T @ distribution_response]
    charge_current = np.r_[0.0, charge_source.T @ distribution_response]
    invariant_heat = energy_current - enthalpy_per_charge * charge_current
    landau_entropy = (
        eos.entropy_density * velocity
        + (energy_current - chemical_potential * charge_current) / temperature
    )
    frame_shift = charge_current / eos.charge_density
    eckart_linear_velocity = velocity + frame_shift
    transformed_eckart_entropy = (
        eos.entropy_density * eckart_linear_velocity + invariant_heat / temperature
    )
    frame_decomposition = {
        "revision": "LINEAR_CHARGED_FRAME_CURRENT_V1",
        "evaluation_frame": "LANDAU_ENERGY_FRAME_TO_LINEAR_ORDER",
        "energy_flux_contravariant": _vector_tuple(energy_current),
        "charge_diffusion_contravariant": _vector_tuple(charge_current),
        "invariant_heat_contravariant": _vector_tuple(invariant_heat),
        "landau_entropy_current_contravariant": _vector_tuple(landau_entropy),
        "eckart_entropy_current_in_landau_coordinates_linear": _vector_tuple(transformed_eckart_entropy),
        "eckart_velocity_shift_linear": _vector_tuple(frame_shift),
        "frame_shift_spatial_norm": float(np.linalg.norm(frame_shift[1:])),
        "entropy_frame_identity_residual": float(np.linalg.norm(landau_entropy-transformed_eckart_entropy)),
        "heat_moment_response_residual": float(np.linalg.norm(invariant_heat[1:]-heat_response)),
        "legacy_entropy_current_role": "FORMAL_s_u_PLUS_HEAT_OVER_T_NOT_CANONICAL_LANDAU_CURRENT",
        "legacy_heat_flux_role": "FULL_TENSOR_INVARIANT_HEAT_RESPONSE_NOT_LANDAU_ENERGY_FLUX",
        "response_lift_revision": "FULL_TRANSVERSE_TENSOR_V1",
        "finite_velocity_state_validated": False,
        "claim_boundary": "Linear response coefficients/probes only; a unit force is not a validated finite fluid state. Signed O(2) charge is not material mass.",
    }
    return CovariantEntropyHeatFluxBalanceState(
        frame_current_decomposition=frame_decomposition,
        temperature=operator.temperature,
        chemical_potential=operator.chemical_potential,
        space_response=operator.space_response,
        eos_branch=eos.branch,
        entropy_density=eos.entropy_density,
        pressure=eos.pressure,
        energy_density=eos.energy_density,
        charge_density=eos.charge_density,
        enthalpy_per_charge=float(enthalpy_per_charge),
        operator_state_count=operator.state_count,
        transition_channel_count=operator.transition_channel_count,
        heat_response_matrix=_matrix_tuple(response_matrix),
        kappa_natural=kappa_natural,
        heat_response_isotropy_residual=isotropy_residual,
        collision_operator_min_eigenvalue=float(
            np.min(np.linalg.eigvalsh(collision_operator_symmetric))
        ),
        collision_operator_symmetry_residual=float(
            np.linalg.norm(collision_operator - collision_operator.T)
        ),
        thermal_force_covariant=_vector_tuple(
            np.asarray(covariant["thermal_force_covariant"], dtype=float)
        ),
        thermal_force_contravariant=_vector_tuple(
            np.asarray(covariant["thermal_force_contravariant"], dtype=float)
        ),
        heat_flux_contravariant=_vector_tuple(
            np.asarray(covariant["heat_flux_contravariant"], dtype=float)
        ),
        entropy_current_contravariant=_vector_tuple(
            np.asarray(covariant["entropy_current_contravariant"], dtype=float)
        ),
        entropy_production=entropy_production,
        kinetic_entropy_production=kinetic_entropy,
        entropy_balance_residual=abs(kinetic_entropy - entropy_production),
        kinetic_equation_residual=kinetic_equation_residual,
        charge_balance_residual=charge_balance,
        energy_balance_residual=energy_balance,
        momentum_balance_residual=momentum_balance,
        heat_flux_response_residual=float(np.linalg.norm(heat_response - heat_flux_spatial)),
        force_orthogonality_residual=float(covariant["force_orthogonality_residual"]),
        heat_flux_orthogonality_residual=float(
            covariant["heat_flux_orthogonality_residual"]
        ),
        projector_orthogonality_residual=projector_residual,
        lorentz_covariance_residual=_boost_tensor_residual(
            metric_array,
            velocity,
            temperature,
            eos.entropy_density,
            response_tensor,
            force_covariant,
            covariant,
        ),
        equilibrium_heat_flux_norm=float(
            np.linalg.norm(equilibrium["heat_flux_contravariant"])
        ),
    )


def covariant_entropy_heat_flux_balance_contract() -> dict[str, Any]:
    """Return the equation, unit, evidence, and claim boundary contract."""

    return {
        "status": COVARIANT_ENTROPY_HEAT_FLUX_STATUS,
        "equations": {
            "landau_enthalpy_subtraction": "h=(epsilon+p)/n",
            "heat_current_source": "b_i=(E-h*q)*(p_i/E)*sqrt(w)",
            "conservative_projection": "b_i^perp=P*b_i with P preserving charge and four-momentum null modes",
            "finite_cutoff_response": "K_ab=(b_a^perp)^T*L_cont^+*b_b^perp",
            "covariant_thermal_force": "X_T^mu=-Delta^(mu nu)*(nabla_nu T+T*a_nu)/T",
            "covariant_heat_flux": "q^mu=K^(mu nu)*X_T_nu; K is the full transverse response tensor",
            "entropy_current": "J_S^mu=s*u^mu+q^mu/T",
            "entropy_production": "sigma=X_T_mu*q^mu/T=X_T_mu*K^(mu nu)*X_T_nu/T>=0",
            "scalar_summary": "kappa_natural=trace(K_spatial)/3 is a summary, not the tensor used in the state response",
            "kinetic_entropy_balance": "z=L_cont^+*b_a^perp*X^a; sigma=z^T*L_cont*z/T=X^a*K_ab*X^b/T",
            "entropy_metric": "w_i=m_i*f_i*(1+f_i)/T; delta_f_i=f_i*(1+f_i)*psi_i/T; z_i=sqrt(w_i)*psi_i; delta2(-s)=z^T*z/(2*T)",
            "conserved_dissipative_balance": "I_A^T*L_cont*z=0 for charge, energy, and momentum moments",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_energy": "natural energy",
            "enthalpy_per_charge": "natural energy per signed O(2) charge",
            "thermal_force": "formal natural-unit projected gradient input; no SI temperature gradient supplied",
            "kappa_natural": "finite-cutoff natural moment-response coefficient; not W m^-1 K^-1",
            "heat_flux": "formal natural-unit moment current; not SI heat flux",
            "entropy_current": "formal natural-unit entropy-current notation",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-temperature quasiparticle EOS plus finite-cutoff conservative collision operator, "
            "Landau moment subtraction, pseudoinverse response, and covariant projector lift"
        ),
        "normalization_revision": "SUSCEPTIBILITY_ENTROPY_METRIC_V2",
        "frame_current_contract": {
            "invariant_heat": "q_heat=Q-h*V; Q_L=0 to projected precision",
            "canonical_entropy_current": "S_L=s*u_L+(Q-mu*V)/T",
            "linear_frame_map": "u_E=u_L+V/n+O(V^2); S_E=s*u_E+q_heat/T equals S_L to first order",
            "legacy_entropy_current_contravariant": "Formal s*u+q_heat/T retained for compatibility; NOT canonical Landau entropy current",
            "new_canonical_output": "frame_current_decomposition.landau_entropy_current_contravariant",
            "finite_velocity_scope": "Linear coefficients only; unit driving may yield large formal V/n and is not a physical velocity state",
        },
        "interpretation_blockers": [
            "material_charge_and_nonlinear_frame_map",
            "action_configuration_correspondence",
            "physical_transport_and_microscopic_SK_matching",
        ],
        "observable": (
            "local-rest-frame formal heat-current response, covariant entropy-production scalar, "
            "and conserved charge/energy/momentum dissipative balance"
        ),
        "data_role": "ACTION_DERIVED_INTERNAL_FORMAL_RESPONSE_NO_SOURCE_ROWS_NO_HOLDOUT",
        "included": {
            "landau_energy_current_subtraction": True,
            "charge_energy_momentum_conservation": True,
            "positive_semidefinite_response_matrix": True,
            "covariant_entropy_current_lift": True,
            "entropy_balance_identity": True,
            "local_lorentz_covariance_check": True,
        },
        "excluded": {
            "physical_Kubo_coefficient": True,
            "SI_heat_flux": True,
            "finite_temperature_two_fluid_completion": True,
            "microscopic_SK_action_match": True,
            "curved_3p1_solver": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only a finite-cutoff action-derived natural-unit moment response and its "
            "covariant entropy-current/balance interface on the declared normal quasiparticle lane. "
            "It is not a physical Kubo coefficient, SI heat-flux calibration, complete two-fluid "
            "transport theory, curved 3+1 result, alpha_Phi_K calibration, TTG validation, or Full Topic 13 closure."
        ),
    }


__all__ = [
    "COVARIANT_ENTROPY_HEAT_FLUX_STATUS",
    "CovariantEntropyHeatFluxBalanceState",
    "covariant_entropy_heat_flux",
    "covariant_entropy_heat_flux_balance_state",
    "covariant_entropy_heat_flux_balance_contract",
    "lorentz_boost_x",
]
