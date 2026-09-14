"""Conserved-current bridge from covariant matter to normalized Model-B dynamics.

The covariant O(2) matter pilot supplies an exactly conserved on-shell Noether
current ``N^mu``.  This module makes the next, explicitly constitutive, step:
after choosing a local fluid frame, the charge density and spatial current are
coarse grained into a normalized cell density ``C`` and a face flux ``J``.

The finite-relaxation law

``tau_J d_t J + J = -M_C grad(mu_C)``

is paired with exact discrete continuity.  Its adiabatic limit is the
conserved Cahn-Hilliard/Model-B equation used by ``matter_space_coupled_v1``.
This is not a microscopic derivation of the transport coefficients.  It also
does not make the full gradient-energy or spinodal system relativistically
causal: the fourth-order ultraviolet principal part requires an augmented
first-order hyperbolic closure that is deliberately left as a blocker.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_response import validate_lorentz_metric
from docs.core.uet_matter_space import (
    MatterSpaceConfig,
    MatterSpaceState,
    matter_space_rhs,
)
from docs.core.uet_spatial import (
    face_gradient_1d,
    gradient_energy_integral_1d,
    integral_1d,
    laplacian_1d,
    validate_boundary,
    validate_dx,
    validate_field_1d,
)

COVARIANT_DIFFUSION_STATUS: Final[str] = (
    "PARTIAL_CONSTITUTIVE_NOETHER_CURRENT_TO_MODEL_B_BRIDGE"
)


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _vector4(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (4,):
        raise ValueError(f"{name} must have shape (4,), got {result.shape}")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


@dataclass(frozen=True)
class CurrentDecomposition:
    """Frame decomposition ``N^mu = n u^mu + j^mu``."""

    density: float
    spatial_current: np.ndarray
    reconstruction_error: float
    orthogonality_error: float


def decompose_noether_current(
    metric: Any,
    four_velocity: Any,
    noether_current: Any,
    *,
    inverse_metric: Any | None = None,
) -> CurrentDecomposition:
    """Project a contravariant current along and orthogonal to ``u^mu``.

    The convention is metric signature ``(-,+,+,+)`` and ``u_mu u^mu=-1``.
    The operation is exact kinematics; interpreting the projected density as a
    thermodynamic variable still requires the declared coarse-graining map.
    """

    g, _ = validate_lorentz_metric(metric, inverse_metric)
    velocity = _vector4(four_velocity, "four_velocity")
    current = _vector4(noether_current, "noether_current")
    covariant_velocity = g @ velocity
    norm = float(np.dot(covariant_velocity, velocity))
    if not np.isclose(norm, -1.0, rtol=0.0, atol=1e-10):
        raise ValueError("four_velocity must satisfy u_mu u^mu = -1")
    density = -float(np.dot(covariant_velocity, current))
    spatial = current - density * velocity
    reconstructed = density * velocity + spatial
    return CurrentDecomposition(
        density=density,
        spatial_current=np.asarray(spatial, dtype=float),
        reconstruction_error=float(np.max(np.abs(reconstructed - current))),
        orthogonality_error=abs(float(np.dot(covariant_velocity, spatial))),
    )


@dataclass(frozen=True)
class ConservedCurrentBridgeConfig:
    """Natural-to-normalized controls for the constitutive current bridge."""

    a_matter: float = 1.0
    b_matter: float = 1.0
    kappa_matter: float = 0.0
    mobility_matter: float = 1.0
    tau_current: float = 0.25
    coupling_base: float = 0.25
    epsilon_nc: float = 1.0
    density_scale: float = 1.0
    length_scale: float = 1.0
    time_scale: float = 1.0
    boundary_condition: str = "periodic"
    unit_lane: str = "natural_to_normalized"

    def __post_init__(self) -> None:
        values = {
            "a_matter": self.a_matter,
            "b_matter": self.b_matter,
            "kappa_matter": self.kappa_matter,
            "mobility_matter": self.mobility_matter,
            "tau_current": self.tau_current,
            "coupling_base": self.coupling_base,
            "epsilon_nc": self.epsilon_nc,
            "density_scale": self.density_scale,
            "length_scale": self.length_scale,
            "time_scale": self.time_scale,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("current-bridge coefficients must be finite")
        for name in (
            "b_matter",
            "mobility_matter",
            "tau_current",
            "density_scale",
            "length_scale",
            "time_scale",
        ):
            if float(getattr(self, name)) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.kappa_matter < 0.0:
            raise ValueError("kappa_matter must be non-negative")
        if self.coupling_base < 0.0:
            raise ValueError("coupling_base must be non-negative")
        if self.epsilon_nc < 0.0:
            raise ValueError("epsilon_nc must be non-negative")
        validate_boundary(self.boundary_condition)
        if self.unit_lane != "natural_to_normalized":
            raise NotImplementedError(
                "the current bridge supports only unit_lane='natural_to_normalized'"
            )

    @property
    def effective_coupling(self) -> float:
        """Return the regular nested coupling ``epsilon_nc * coupling_base``."""

        return float(self.epsilon_nc * self.coupling_base)

    @property
    def normalized_light_speed(self) -> float:
        """Return ``c_hat = time_scale / length_scale`` for natural ``c=1``."""

        return float(self.time_scale / self.length_scale)

    @property
    def natural_current_scale(self) -> float:
        """Return the scale ``n_0 L/T`` used for the spatial current."""

        return float(self.density_scale * self.length_scale / self.time_scale)


def normalize_local_charge_and_current(
    density: Any,
    spatial_current_component: Any,
    config: ConservedCurrentBridgeConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """Map natural charge density/current to normalized ``(C, J)``."""

    natural_density = np.asarray(density, dtype=float)
    natural_current = np.asarray(spatial_current_component, dtype=float)
    if natural_density.shape != natural_current.shape:
        raise ValueError("density and spatial current must share one shape")
    if not np.all(np.isfinite(natural_density)) or not np.all(
        np.isfinite(natural_current)
    ):
        raise ValueError("density and spatial current must be finite")
    return (
        natural_density / config.density_scale,
        natural_current / config.natural_current_scale,
    )


@dataclass
class ConservedCurrentState:
    """Normalized cell density and finite-volume face current."""

    C: np.ndarray
    matter_flux: np.ndarray

    def __post_init__(self) -> None:
        density = validate_field_1d(self.C, "C").copy()
        flux = np.asarray(self.matter_flux, dtype=float)
        if flux.ndim != 1 or not np.all(np.isfinite(flux)):
            raise ValueError("matter_flux must be a finite one-dimensional array")
        self.C = density
        self.matter_flux = flux.copy()

    def copy(self) -> "ConservedCurrentState":
        return ConservedCurrentState(self.C.copy(), self.matter_flux.copy())


def _validate_space_response(value: Any, shape: tuple[int, ...]) -> np.ndarray:
    response = validate_field_1d(value, "space_response")
    if response.shape != shape:
        raise ValueError("space_response must match C")
    return response


def _validate_state(
    state: ConservedCurrentState,
    config: ConservedCurrentBridgeConfig,
) -> ConservedCurrentState:
    expected = state.C.size if config.boundary_condition == "periodic" else state.C.size + 1
    if state.matter_flux.shape != (expected,):
        raise ValueError(
            f"matter_flux must have shape ({expected},) for {config.boundary_condition}"
        )
    if config.boundary_condition == "zero_flux":
        scale = max(float(np.max(np.abs(state.matter_flux))), 1.0)
        if max(abs(state.matter_flux[0]), abs(state.matter_flux[-1])) > 1e-12 * scale:
            raise ValueError("zero_flux requires both boundary face currents to vanish")
    return state


def face_divergence_1d(
    face_flux: Any,
    n_cells: int,
    dx: float,
    boundary_condition: str = "periodic",
) -> np.ndarray:
    """Return the conservative divergence of a face-centred current."""

    spacing = validate_dx(dx)
    boundary = validate_boundary(boundary_condition)
    flux = np.asarray(face_flux, dtype=float)
    expected = n_cells if boundary == "periodic" else n_cells + 1
    if flux.shape != (expected,) or not np.all(np.isfinite(flux)):
        raise ValueError(f"face_flux must be finite with shape ({expected},)")
    if boundary == "periodic":
        return (flux - np.roll(flux, 1)) / spacing
    return (flux[1:] - flux[:-1]) / spacing


def face_integral_1d(
    face_value: Any,
    dx: float,
) -> float:
    """Return the finite-volume face sum using the cell-width measure."""

    spacing = validate_dx(dx)
    value = np.asarray(face_value, dtype=float)
    if value.ndim != 1 or not np.all(np.isfinite(value)):
        raise ValueError("face_value must be a finite one-dimensional array")
    return float(np.sum(value) * spacing)


def conditioned_matter_free_energy(
    C: Any,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> float:
    """Return ``F_C[C | Phi]`` whose derivative is the bridge potential."""

    density = validate_field_1d(C, "C")
    response = _validate_space_response(space_response, density.shape)
    spacing = validate_dx(dx)
    local = (
        0.5 * config.a_matter * np.square(density)
        + 0.25 * config.b_matter * np.power(density, 4)
        - 0.5
        * config.effective_coupling
        * np.square(density)
        * response
    )
    gradient = 0.5 * config.kappa_matter * gradient_energy_integral_1d(
        density, spacing, config.boundary_condition
    )
    return float(integral_1d(local, spacing) + gradient)


def conditioned_matter_chemical_potential(
    C: Any,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> np.ndarray:
    """Return the exact discrete derivative ``delta F_C/delta C``."""

    density = validate_field_1d(C, "C")
    response = _validate_space_response(space_response, density.shape)
    laplacian = laplacian_1d(
        density, validate_dx(dx), config.boundary_condition
    )
    return (
        config.a_matter * density
        + config.b_matter * np.power(density, 3)
        - config.kappa_matter * laplacian
        - config.effective_coupling * density * response
    )


def equilibrium_matter_flux(
    chemical_potential: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> np.ndarray:
    """Return the adiabatic/Fickian face flux ``-M_C grad(mu_C)``."""

    potential = validate_field_1d(chemical_potential, "chemical_potential")
    return -config.mobility_matter * face_gradient_1d(
        potential, validate_dx(dx), config.boundary_condition
    )


def causal_current_rhs(
    state: ConservedCurrentState,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(dC, dJ, mu_C, J_eq)`` for the finite-relaxation bridge."""

    physical = _validate_state(state, config)
    response = _validate_space_response(space_response, physical.C.shape)
    chemical = conditioned_matter_chemical_potential(
        physical.C, response, dx, config
    )
    equilibrium = equilibrium_matter_flux(chemical, dx, config)
    density_rate = -face_divergence_1d(
        physical.matter_flux,
        physical.C.size,
        dx,
        config.boundary_condition,
    )
    flux_rate = (equilibrium - physical.matter_flux) / config.tau_current
    return density_rate, flux_rate, chemical, equilibrium


def model_b_rhs(
    C: Any,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> np.ndarray:
    """Return the adiabatic conserved gradient-flow rate."""

    chemical = conditioned_matter_chemical_potential(
        C, space_response, dx, config
    )
    return config.mobility_matter * laplacian_1d(
        chemical, validate_dx(dx), config.boundary_condition
    )


def compare_adiabatic_limit(
    C: Any,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> dict[str, Any]:
    """Compare exact equilibrium-current continuity with Model B."""

    density = validate_field_1d(C, "C")
    chemical = conditioned_matter_chemical_potential(
        density, space_response, dx, config
    )
    equilibrium = equilibrium_matter_flux(chemical, dx, config)
    from_current = -face_divergence_1d(
        equilibrium, density.size, dx, config.boundary_condition
    )
    target = model_b_rhs(density, space_response, dx, config)
    difference = from_current - target
    return {
        "equilibrium_flux": equilibrium,
        "continuity_rhs": from_current,
        "model_b_rhs": target,
        "difference": difference,
        "max_abs_difference": float(np.max(np.abs(difference))),
    }


def current_extended_energy(
    state: ConservedCurrentState,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> float:
    """Return ``F_C + tau_J/(2 M_C) integral J^2``."""

    physical = _validate_state(state, config)
    free_energy = conditioned_matter_free_energy(
        physical.C, space_response, dx, config
    )
    current_storage = (
        config.tau_current
        / (2.0 * config.mobility_matter)
        * face_integral_1d(np.square(physical.matter_flux), dx)
    )
    return float(free_energy + current_storage)


def current_energy_balance(
    state: ConservedCurrentState,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
) -> dict[str, float]:
    """Return the exact semi-discrete closed-system energy identity."""

    physical = _validate_state(state, config)
    dC, dJ, chemical, _ = causal_current_rhs(
        physical, space_response, dx, config
    )
    free_energy_rate = integral_1d(chemical * dC, dx)
    storage_rate = (
        config.tau_current
        / config.mobility_matter
        * face_integral_1d(physical.matter_flux * dJ, dx)
    )
    dissipation = face_integral_1d(
        np.square(physical.matter_flux) / config.mobility_matter, dx
    )
    closure = free_energy_rate + storage_rate + dissipation
    return {
        "free_energy_rate": free_energy_rate,
        "current_storage_rate": storage_rate,
        "current_dissipation": dissipation,
        "closure_residual": closure,
    }


def matter_equation_config_from_current_bridge(
    config: ConservedCurrentBridgeConfig,
    template: MatterSpaceConfig | None = None,
) -> MatterSpaceConfig:
    """Map bridge coefficients into the conserved matter equation only.

    The existing matter-space operator requires a strictly positive gradient
    coefficient.  The local ``kappa_matter=0`` causal control therefore stays
    in this module and is not represented as a full matter-space config.
    """

    if config.kappa_matter <= 0.0:
        raise ValueError(
            "matter-space equation mapping requires kappa_matter > 0"
        )
    base = MatterSpaceConfig() if template is None else template
    return replace(
        base,
        a_matter=config.a_matter,
        b_matter=config.b_matter,
        kappa_matter=config.kappa_matter,
        mobility_matter=config.mobility_matter,
        coupling_g=config.effective_coupling,
        matter_dynamics="conserved",
        boundary_condition=config.boundary_condition,
        unit_lane="normalized",
    )


def compare_matter_space_conserved_rhs(
    C: Any,
    space_response: Any,
    dx: float,
    config: ConservedCurrentBridgeConfig,
    template: MatterSpaceConfig | None = None,
) -> dict[str, Any]:
    """Compare the bridge Model-B limit with ``matter_space_coupled_v1``."""

    density = validate_field_1d(C, "C")
    response = _validate_space_response(space_response, density.shape)
    mapped = matter_equation_config_from_current_bridge(config, template)
    state = MatterSpaceState(density, response, np.zeros_like(density))
    matter_space_rate, _, _, _, _ = matter_space_rhs(state, dx, mapped)
    bridge_rate = model_b_rhs(density, response, dx, config)
    difference = bridge_rate - matter_space_rate
    return {
        "mapped_config": mapped,
        "bridge_model_b_rhs": bridge_rate,
        "matter_space_rhs": matter_space_rate,
        "difference": difference,
        "max_abs_difference": float(np.max(np.abs(difference))),
    }


def principal_symbol_diagnostics(
    C: Any,
    space_response: Any,
    config: ConservedCurrentBridgeConfig,
) -> dict[str, Any]:
    """Report where a strict causal interpretation is and is not allowed."""

    density = validate_field_1d(C, "C")
    response = _validate_space_response(space_response, density.shape)
    local_curvature = (
        config.a_matter
        + 3.0 * config.b_matter * np.square(density)
        - config.effective_coupling * response
    )
    minimum = float(np.min(local_curvature))
    maximum = float(np.max(local_curvature))
    local_convex = minimum > 0.0
    gradient_term_present = config.kappa_matter > 0.0
    maximum_local_speed = (
        float(np.sqrt(config.mobility_matter * maximum / config.tau_current))
        if local_convex
        else None
    )
    within_light_cone = bool(
        maximum_local_speed is not None
        and maximum_local_speed <= config.normalized_light_speed * (1.0 + 1e-12)
    )
    if not local_convex:
        status = "BLOCKED_NONCONVEX_OR_SPINODAL"
    elif gradient_term_present:
        status = "BLOCKED_FOURTH_ORDER_UV_CAUSALITY"
    elif not within_light_cone:
        status = "FAIL_SUPERLUMINAL_PARAMETERIZATION"
    else:
        status = "PASS_LOCAL_CONVEX_MAXWELL_CATTANEO"
    return {
        "status": status,
        "minimum_local_curvature": minimum,
        "maximum_local_curvature": maximum,
        "local_convex": local_convex,
        "gradient_term_present": gradient_term_present,
        "maximum_local_characteristic_speed": maximum_local_speed,
        "normalized_light_speed": config.normalized_light_speed,
        "within_normalized_light_cone": within_light_cone,
        "strict_causal_claim_allowed": status
        == "PASS_LOCAL_CONVEX_MAXWELL_CATTANEO",
        "high_k_phase_speed_coefficient": (
            float(
                np.sqrt(
                    config.mobility_matter
                    * config.kappa_matter
                    / config.tau_current
                )
            )
            if gradient_term_present
            else 0.0
        ),
        "full_phase_field_note": (
            "for kappa_matter>0, omega/k grows asymptotically like "
            "sqrt(M_C*kappa_C/tau_J)*k; finite flux relaxation alone does "
            "not establish a relativistic causal cone"
        ),
    }


def current_bridge_contract() -> dict[str, Any]:
    """Return ontology, achieved scope, and the next controlling blocker."""

    return {
        "status": COVARIANT_DIFFUSION_STATUS,
        "covariant_input": "on_shell_global_O2_Noether_current",
        "frame_decomposition": "N^mu=n*u^mu+j^mu_with_u_mu*j^mu=0",
        "normalized_density": "C=n/density_scale_after_declared_coarse_graining",
        "forbidden_identification": "C_is_not_the_scalar_amplitude_sqrt(chi_1^2+chi_2^2)",
        "continuity_equation": "d_t C + div J = 0",
        "constitutive_equation": "tau_J*d_t J + J = -M_C*grad(mu_C)",
        "nested_coupling": "g_effective=epsilon_nc*coupling_base",
        "gr_null_behavior": "epsilon_nc=0_removes_matter_space_coupling_without_division",
        "adiabatic_limit": "J_to_-M_C_grad(mu_C)_and_Model_B",
        "energy_identity": "d_t(F_C+tau_J*int(J^2)/(2M_C))=-int(J^2/M_C)",
        "local_convex_causal_control": "IMPLEMENTED",
        "full_gradient_phase_field_causality": "BLOCKED_FOURTH_ORDER_UV",
        "spinodal_hyperbolicity": "BLOCKED_NONCONVEX",
        "microscopic_transport_derivation": "BLOCKED_CTP_KMS_MATCHING",
        "derived_trace_imported": False,
        "derived_trace_backreaction": False,
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing",
    }
