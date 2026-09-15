"""External first-order hyperbolic Cahn-Hilliard comparator.

This module transcribes the normalized one-dimensional periodic system in
Dhaouadi, Dumbser, and Gavrilyuk (2025), DOI 10.1098/rspa.2024.0606.
It is an external mathematical comparator, not a UET derivation.

The paper's auxiliary phase variable ``varphi`` is represented here as
``auxiliary_phase``.  It is an order-parameter regularization variable and is
not the UET effective space-response variable.  Likewise, no derived trace is
accepted by any physical equation in this module.

For the symmetric double-well potential ``g(C)=(C**2-1)**2/4``, the system is

    C_t + d_x(q/tau) = 0
    q_t + d_x(g'(C)+alpha*(C-varphi)) = -q/tau
    w_t - gamma*d_x(p) = alpha*(C-varphi)
    p_t - d_x(w)/beta = 0
    varphi_t = w/beta

with augmented energy

    E = integral [g(C) + gamma*p**2/2 + alpha*(C-varphi)**2/2
                  + w**2/(2*beta) + q**2/(2*tau)] dx.

The periodic central derivative is skew-adjoint, so the semi-discrete balance
implemented below closes at roundoff.  This v1 module is a formula evaluator;
it deliberately does not present an explicit time integrator as a validated
production solver.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import numpy as np

from .uet_spatial import integral_1d, validate_dx, validate_field_1d

HYPERBOLIC_PHASE_FIELD_STATUS: Final[str] = (
    "EXTERNAL_FORMULA_COMPARATOR_NOT_UET_DERIVATION"
)
HYPERBOLIC_PHASE_FIELD_SOURCE_DOI: Final[str] = "10.1098/rspa.2024.0606"
HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV: Final[str] = "2408.03862"


def _finite_scalar(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class HyperbolicPhaseFieldConfig:
    """Normalized coefficients for the external comparator.

    ``alpha_penalty``, ``beta_wave``, ``tau_flux``, and ``gamma_gradient`` map
    directly to the source paper's ``alpha``, ``beta``, ``tau``, and ``gamma``.
    Strict hyperbolicity is diagnosed, rather than silently enforced, because
    blocked parameterizations are useful negative controls.
    """

    alpha_penalty: float = 1.25
    beta_wave: float = 0.5
    tau_flux: float = 0.5
    gamma_gradient: float = 0.25
    normalized_light_speed: float = 1.0
    boundary_condition: str = "periodic"
    unit_lane: str = "normalized"

    def __post_init__(self) -> None:
        for name in (
            "alpha_penalty",
            "beta_wave",
            "tau_flux",
            "gamma_gradient",
            "normalized_light_speed",
        ):
            value = _finite_scalar(getattr(self, name), name)
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.boundary_condition != "periodic":
            raise NotImplementedError(
                "the external comparator v1 supports only periodic 1D fields"
            )
        if self.unit_lane != "normalized":
            raise NotImplementedError(
                "the external comparator v1 supports only unit_lane='normalized'"
            )

    @property
    def alpha_critical(self) -> float:
        """Return ``abs(min g''(C))=1`` for the symmetric double well."""

        return 1.0


@dataclass
class HyperbolicPhaseFieldState:
    """Cell-centred state of the external first-order system."""

    C: np.ndarray
    flux_impulse: np.ndarray
    auxiliary_rate: np.ndarray
    gradient_proxy: np.ndarray
    auxiliary_phase: np.ndarray

    def __post_init__(self) -> None:
        fields = {
            "C": self.C,
            "flux_impulse": self.flux_impulse,
            "auxiliary_rate": self.auxiliary_rate,
            "gradient_proxy": self.gradient_proxy,
            "auxiliary_phase": self.auxiliary_phase,
        }
        validated = {
            name: validate_field_1d(value, name).copy()
            for name, value in fields.items()
        }
        shape = validated["C"].shape
        if any(value.shape != shape for value in validated.values()):
            raise ValueError("all hyperbolic phase-field state arrays must match C")
        for name, value in validated.items():
            setattr(self, name, value)

    def copy(self) -> "HyperbolicPhaseFieldState":
        return HyperbolicPhaseFieldState(
            self.C.copy(),
            self.flux_impulse.copy(),
            self.auxiliary_rate.copy(),
            self.gradient_proxy.copy(),
            self.auxiliary_phase.copy(),
        )


@dataclass(frozen=True)
class HyperbolicPhaseFieldRates:
    """Time derivatives plus the augmented chemical potential."""

    C: np.ndarray
    flux_impulse: np.ndarray
    auxiliary_rate: np.ndarray
    gradient_proxy: np.ndarray
    auxiliary_phase: np.ndarray
    augmented_chemical_potential: np.ndarray


def periodic_central_derivative(field: Any, dx: float) -> np.ndarray:
    """Return the periodic skew-adjoint central derivative."""

    value = validate_field_1d(field, "field")
    spacing = validate_dx(dx)
    return (np.roll(value, -1) - np.roll(value, 1)) / (2.0 * spacing)


def double_well_potential(C: Any) -> np.ndarray:
    """Return ``g(C)=(C**2-1)**2/4``."""

    value = np.asarray(C, dtype=float)
    if not np.all(np.isfinite(value)):
        raise ValueError("C must be finite")
    return 0.25 * np.square(np.square(value) - 1.0)


def double_well_derivative(C: Any) -> np.ndarray:
    """Return ``g'(C)=C**3-C``."""

    value = np.asarray(C, dtype=float)
    if not np.all(np.isfinite(value)):
        raise ValueError("C must be finite")
    return np.power(value, 3) - value


def double_well_curvature(C: Any) -> np.ndarray:
    """Return ``g''(C)=3*C**2-1``."""

    value = np.asarray(C, dtype=float)
    if not np.all(np.isfinite(value)):
        raise ValueError("C must be finite")
    return 3.0 * np.square(value) - 1.0


def augmented_chemical_potential(
    C: Any,
    auxiliary_phase: Any,
    config: HyperbolicPhaseFieldConfig,
) -> np.ndarray:
    """Return ``g'(C)+alpha*(C-varphi)`` from the source system."""

    density = validate_field_1d(C, "C")
    phase = validate_field_1d(auxiliary_phase, "auxiliary_phase")
    if density.shape != phase.shape:
        raise ValueError("auxiliary_phase must match C")
    return double_well_derivative(density) + config.alpha_penalty * (
        density - phase
    )


def hyperbolic_phase_field_rhs(
    state: HyperbolicPhaseFieldState,
    dx: float,
    config: HyperbolicPhaseFieldConfig,
) -> HyperbolicPhaseFieldRates:
    """Evaluate the semi-discrete first-order external comparator."""

    spacing = validate_dx(dx)
    chemical = augmented_chemical_potential(
        state.C, state.auxiliary_phase, config
    )
    physical_flux = state.flux_impulse / config.tau_flux
    density_rate = -periodic_central_derivative(physical_flux, spacing)
    flux_rate = (
        -periodic_central_derivative(chemical, spacing)
        - state.flux_impulse / config.tau_flux
    )
    auxiliary_rate_rate = (
        config.gamma_gradient
        * periodic_central_derivative(state.gradient_proxy, spacing)
        + config.alpha_penalty * (state.C - state.auxiliary_phase)
    )
    gradient_rate = periodic_central_derivative(
        state.auxiliary_rate, spacing
    ) / config.beta_wave
    phase_rate = state.auxiliary_rate / config.beta_wave
    return HyperbolicPhaseFieldRates(
        C=density_rate,
        flux_impulse=flux_rate,
        auxiliary_rate=auxiliary_rate_rate,
        gradient_proxy=gradient_rate,
        auxiliary_phase=phase_rate,
        augmented_chemical_potential=chemical,
    )


def hyperbolic_phase_field_energy(
    state: HyperbolicPhaseFieldState,
    dx: float,
    config: HyperbolicPhaseFieldConfig,
) -> float:
    """Return the source paper's augmented Lyapunov functional."""

    density = (
        double_well_potential(state.C)
        + 0.5 * config.gamma_gradient * np.square(state.gradient_proxy)
        + 0.5
        * config.alpha_penalty
        * np.square(state.C - state.auxiliary_phase)
        + np.square(state.auxiliary_rate) / (2.0 * config.beta_wave)
        + np.square(state.flux_impulse) / (2.0 * config.tau_flux)
    )
    return integral_1d(density, validate_dx(dx))


def hyperbolic_phase_field_energy_balance(
    state: HyperbolicPhaseFieldState,
    dx: float,
    config: HyperbolicPhaseFieldConfig,
) -> dict[str, float]:
    """Return the exact periodic semi-discrete Lyapunov identity."""

    rates = hyperbolic_phase_field_rhs(state, dx, config)
    chemical = rates.augmented_chemical_potential
    phase_derivative = -config.alpha_penalty * (
        state.C - state.auxiliary_phase
    )
    energy_rate = integral_1d(
        chemical * rates.C
        + (state.flux_impulse / config.tau_flux) * rates.flux_impulse
        + (state.auxiliary_rate / config.beta_wave) * rates.auxiliary_rate
        + config.gamma_gradient
        * state.gradient_proxy
        * rates.gradient_proxy
        + phase_derivative * rates.auxiliary_phase,
        dx,
    )
    dissipation = integral_1d(
        np.square(state.flux_impulse / config.tau_flux), dx
    )
    return {
        "energy_rate": energy_rate,
        "flux_dissipation": dissipation,
        "closure_residual": energy_rate + dissipation,
    }


def gradient_constraint_residual(
    state: HyperbolicPhaseFieldState,
    dx: float,
) -> np.ndarray:
    """Return ``p-D(varphi)`` for the source consistency constraint."""

    return state.gradient_proxy - periodic_central_derivative(
        state.auxiliary_phase, dx
    )


def gradient_constraint_rate_residual(
    state: HyperbolicPhaseFieldState,
    dx: float,
    config: HyperbolicPhaseFieldConfig,
) -> np.ndarray:
    """Return ``p_t-D(varphi_t)``, which vanishes semi-discretely."""

    rates = hyperbolic_phase_field_rhs(state, dx, config)
    return rates.gradient_proxy - periodic_central_derivative(
        rates.auxiliary_phase, dx
    )


def principal_matrix(
    background_C: float,
    config: HyperbolicPhaseFieldConfig,
) -> np.ndarray:
    """Return the 1D quasilinear principal matrix at a background state."""

    background = _finite_scalar(background_C, "background_C")
    curvature = float(double_well_curvature(np.array([background]))[0])
    alpha = config.alpha_penalty
    return np.array(
        [
            [0.0, 1.0 / config.tau_flux, 0.0, 0.0, 0.0],
            [curvature + alpha, 0.0, 0.0, 0.0, -alpha],
            [0.0, 0.0, 0.0, -config.gamma_gradient, 0.0],
            [0.0, 0.0, -1.0 / config.beta_wave, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )


def analytic_characteristic_speeds(
    background_C: float,
    config: HyperbolicPhaseFieldConfig,
) -> np.ndarray:
    """Return the five source-paper characteristic speeds in 1D."""

    curvature = float(
        double_well_curvature(np.array([_finite_scalar(background_C, "background_C")]))[
            0
        ]
    )
    matter_square = (curvature + config.alpha_penalty) / config.tau_flux
    wave_square = config.gamma_gradient / config.beta_wave
    matter = np.sqrt(matter_square) if matter_square >= 0.0 else np.nan
    wave = np.sqrt(wave_square)
    return np.array([-matter, -wave, 0.0, wave, matter], dtype=float)


def hyperbolicity_diagnostics(
    C: Any,
    config: HyperbolicPhaseFieldConfig,
) -> dict[str, Any]:
    """Report strict hyperbolicity and the separate normalized-light-cone gate."""

    density = validate_field_1d(C, "C")
    shifted_curvature = double_well_curvature(density) + config.alpha_penalty
    minimum = float(np.min(shifted_curvature))
    maximum = float(np.max(shifted_curvature))
    strictly_hyperbolic = minimum > 0.0
    matter_speed = (
        float(np.sqrt(maximum / config.tau_flux))
        if strictly_hyperbolic
        else None
    )
    auxiliary_speed = float(
        np.sqrt(config.gamma_gradient / config.beta_wave)
    )
    maximum_speed = (
        max(matter_speed, auxiliary_speed) if matter_speed is not None else None
    )
    subluminal = bool(
        maximum_speed is not None
        and maximum_speed <= config.normalized_light_speed * (1.0 + 1e-12)
    )
    if not strictly_hyperbolic:
        status = "BLOCKED_NOT_STRICTLY_HYPERBOLIC"
    elif not subluminal:
        status = "HYPERBOLIC_BUT_FAILS_NORMALIZED_LIGHT_CONE"
    else:
        status = "PASS_FIXED_PARAMETER_HYPERBOLIC_SUBLUMINAL_CONTROL"
    return {
        "status": status,
        "minimum_alpha_plus_g_second": minimum,
        "maximum_alpha_plus_g_second": maximum,
        "strictly_hyperbolic": strictly_hyperbolic,
        "matter_characteristic_speed_max": matter_speed,
        "auxiliary_characteristic_speed": auxiliary_speed,
        "maximum_characteristic_speed": maximum_speed,
        "normalized_light_speed": config.normalized_light_speed,
        "within_normalized_light_cone": subluminal,
        "paper_hyperbolicity_condition": "alpha_penalty > 1 for strict double-well hyperbolicity",
        "relativistic_note": (
            "finite mathematical characteristic speeds do not by themselves "
            "establish a covariant or uniformly subluminal UET completion"
        ),
    }


def quasistatic_auxiliary_phase(
    C: Any,
    dx: float,
    config: HyperbolicPhaseFieldConfig,
) -> np.ndarray:
    """Solve ``(alpha-gamma*D^2)varphi=alpha*C`` on the periodic grid."""

    density = validate_field_1d(C, "C")
    spacing = validate_dx(dx)
    modes = 2.0 * np.pi * np.fft.fftfreq(density.size)
    derivative_square = -np.square(np.sin(modes) / spacing)
    denominator = config.alpha_penalty - config.gamma_gradient * derivative_square
    phase_hat = config.alpha_penalty * np.fft.fft(density) / denominator
    return np.asarray(np.fft.ifft(phase_hat).real, dtype=float)


def compare_augmented_to_cahn_hilliard_chemical(
    C: Any,
    dx: float,
    config: HyperbolicPhaseFieldConfig,
) -> dict[str, Any]:
    """Compare the quasistatic augmented chemical potential with Cahn-Hilliard."""

    density = validate_field_1d(C, "C")
    phase = quasistatic_auxiliary_phase(density, dx, config)
    proxy = periodic_central_derivative(phase, dx)
    augmented = augmented_chemical_potential(density, phase, config)
    target = double_well_derivative(density) - config.gamma_gradient * (
        periodic_central_derivative(
            periodic_central_derivative(density, dx), dx
        )
    )
    phase_form = double_well_derivative(density) - config.gamma_gradient * (
        periodic_central_derivative(proxy, dx)
    )
    difference = augmented - target
    return {
        "auxiliary_phase": phase,
        "gradient_proxy": proxy,
        "augmented_chemical_potential": augmented,
        "cahn_hilliard_chemical_potential": target,
        "quasistatic_phase_form": phase_form,
        "quasistatic_constraint_max_abs": float(
            np.max(np.abs(augmented - phase_form))
        ),
        "max_abs_difference": float(np.max(np.abs(difference))),
        "relative_l2_difference": float(
            np.linalg.norm(difference)
            / max(np.linalg.norm(target), np.finfo(float).tiny)
        ),
    }


def paper_asymptotic_scaling_diagnostics(
    gamma_values: Any,
    *,
    background_C: float = 0.0,
    normalized_light_speed: float = 1.0,
) -> dict[str, Any]:
    """Evaluate the paper scaling ``alpha=1/gamma, tau=beta=gamma**2``.

    The asymptotic scaling recovers the parabolic Cahn-Hilliard equation, but
    its characteristic speeds diverge as ``gamma`` decreases.  This function
    makes that non-uniform causal limit explicit.
    """

    values = np.asarray(gamma_values, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("gamma_values must be a one-dimensional array of length >=2")
    if not np.all(np.isfinite(values)) or np.any(values <= 0.0):
        raise ValueError("gamma_values must be finite and positive")
    curvature = float(
        double_well_curvature(np.array([_finite_scalar(background_C, "background_C")]))[
            0
        ]
    )
    alpha = 1.0 / values
    tau = np.square(values)
    beta = np.square(values)
    matter_speeds = np.sqrt((alpha + curvature) / tau)
    auxiliary_speeds = np.sqrt(values / beta)
    maxima = np.maximum(matter_speeds, auxiliary_speeds)
    ordering = np.argsort(values)[::-1]
    ordered_speeds = maxima[ordering]
    speed_increases_as_gamma_decreases = bool(
        np.all(np.diff(ordered_speeds) > 0.0)
    )
    return {
        "gamma_values": values,
        "alpha_values": alpha,
        "tau_values": tau,
        "beta_values": beta,
        "matter_characteristic_speeds": matter_speeds,
        "auxiliary_characteristic_speeds": auxiliary_speeds,
        "maximum_characteristic_speeds": maxima,
        "normalized_light_speed": float(normalized_light_speed),
        "all_subluminal": bool(np.all(maxima <= float(normalized_light_speed))),
        "speed_increases_as_gamma_decreases": speed_increases_as_gamma_decreases,
        "uniform_subluminal_parabolic_limit": False,
        "interpretation": (
            "the fixed-parameter system is hyperbolic, while the parabolic "
            "Cahn-Hilliard recovery is a singular non-uniform causal limit"
        ),
    }


def hyperbolic_phase_field_contract() -> dict[str, Any]:
    """Return provenance, ontology, achieved scope, and blocked claims."""

    return {
        "status": HYPERBOLIC_PHASE_FIELD_STATUS,
        "source_doi": HYPERBOLIC_PHASE_FIELD_SOURCE_DOI,
        "source_arxiv": HYPERBOLIC_PHASE_FIELD_SOURCE_ARXIV,
        "role": "external_first_order_hyperbolic_phase_field_comparator",
        "spatial_scope": "normalized_1D_periodic_formula_evaluator",
        "physical_order_parameter": "C",
        "auxiliary_phase": "paper_varphi_order_parameter_regularization",
        "auxiliary_rate": "paper_w_equals_beta_times_varphi_t",
        "gradient_proxy": "paper_p_equals_grad_varphi_when_constraint_is_prepared",
        "flux_impulse": "paper_q_with_physical_mass_flux_q_over_tau",
        "forbidden_identifications": [
            "auxiliary_phase_is_not_UET_space_response",
            "auxiliary_phase_is_not_information_or_trace",
            "flux_impulse_is_not_a_new_particle_or_matter_species",
            "external_comparator_is_not_a_UET_derivation",
        ],
        "mass_conservation": "IMPLEMENTED_SEMI_DISCRETE_PERIODIC",
        "lyapunov_identity": "IMPLEMENTED_SEMI_DISCRETE_PERIODIC",
        "gradient_constraint_involution": "IMPLEMENTED_SEMI_DISCRETE_PERIODIC",
        "fixed_parameter_hyperbolicity": "IMPLEMENTED_WITH_EXPLICIT_CONDITION",
        "normalized_light_cone": "SEPARATE_PARAMETER_GATE",
        "cahn_hilliard_limit": "SINGULAR_NOT_UNIFORMLY_SUBLUMINAL",
        "trace_input": False,
        "trace_backreaction": False,
        "uet_covariant_derivation": "BLOCKED",
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": (
            "uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing"
        ),
    }
