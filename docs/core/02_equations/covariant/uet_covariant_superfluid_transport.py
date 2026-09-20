"""Covariant zero-temperature superfluid and longitudinal Kubo bridge.

The O(2) finite-density action fixes the ideal ``P(X, Phi)`` sector, where
``X=-xi_mu xi^mu`` and ``xi_mu=nabla_mu theta+A_mu``.  Dissipation is not
contained in that single-copy conservative action.  This module therefore
keeps the ideal current/stress exact at tree level and requires explicit,
provenanced Kubo coefficient records before any dissipative calculation runs.

Version 1 is a natural-unit, Landau-frame, longitudinal control.  It is not a
complete finite-temperature two-fluid theory and does not import the derived
history trace as state or feedback.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Final

import numpy as np

from docs.core.uet_covariant_response import validate_lorentz_metric
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
    o2_equilibrium_state,
)

O2_SUPERFLUID_TRANSPORT_OPERATOR_MODE: Final[str] = (
    "o2_superfluid_transport_v1"
)
O2_SUPERFLUID_TRANSPORT_STATUS: Final[str] = (
    "COVARIANT_T0_IDEAL_SUPERFLUID_WITH_KUBO_MATCHING_INTERFACE"
)
O2_SUPERFLUID_TRANSPORT_CONTROLLER: Final[str] = (
    "physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing"
)

_MATCHED_EVIDENCE = frozenset(
    {"KUBO_MATCHED", "SOURCE_LOCKED", "EXTERNALLY_MATCHED"}
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
class KuboCoefficientRecord:
    """A transport value tied to a state point and retarded correlator."""

    coefficient_name: str
    value: float | None
    units: str
    hydrodynamic_frame: str
    temperature: float
    chemical_potential: float
    space_response: float
    correlator_formula_id: str
    source_path_or_url: str
    source_hash: str
    evidence_status: str

    def __post_init__(self) -> None:
        if not self.coefficient_name.strip():
            raise ValueError("coefficient_name must be non-empty")
        if self.value is not None and not isfinite(float(self.value)):
            raise ValueError("Kubo coefficient value must be finite when present")
        for name in ("temperature", "chemical_potential", "space_response"):
            _finite_scalar(getattr(self, name), name)
        if not self.units.strip():
            raise ValueError("units must be declared")
        if self.hydrodynamic_frame != "Landau":
            raise NotImplementedError("transport v1 supports only the Landau frame")
        if not self.correlator_formula_id.strip():
            raise ValueError("correlator_formula_id must be non-empty")
        if not self.evidence_status.strip():
            raise ValueError("evidence_status must be non-empty")

    @property
    def ready(self) -> bool:
        """Whether the record can drive a dissipative calculation."""

        return bool(
            self.value is not None
            and self.evidence_status in _MATCHED_EVIDENCE
            and self.source_path_or_url.strip()
            and self.source_hash.strip()
        )

    @property
    def ready_as_synthetic_control(self) -> bool:
        """Whether an explicitly simulation-only record is complete."""

        return bool(
            self.value is not None
            and self.evidence_status == "SYNTHETIC_CONTROL"
            and self.source_path_or_url.startswith("internal://")
            and self.source_hash.strip()
        )


@dataclass(frozen=True)
class SuperfluidHydroState:
    """Local hydrodynamic variables for the v1 superfluid control."""

    temperature: float
    chemical_potential: float
    four_velocity: Any
    phase_gradient: Any
    space_response: float
    background_gauge: Any | None = None

    def __post_init__(self) -> None:
        _finite_scalar(self.temperature, "temperature")
        _finite_scalar(self.chemical_potential, "chemical_potential")
        _finite_scalar(self.space_response, "space_response")
        _vector4(self.four_velocity, "four_velocity")
        _vector4(self.phase_gradient, "phase_gradient")
        if self.background_gauge is not None:
            _vector4(self.background_gauge, "background_gauge")


@dataclass(frozen=True)
class SuperfluidTransportConfig:
    """Natural-unit Landau-frame controls and explicit Kubo records."""

    eos: O2FiniteDensityEOSConfig = field(
        default_factory=O2FiniteDensityEOSConfig
    )
    coefficient_records: tuple[KuboCoefficientRecord, ...] = ()
    hydrodynamic_frame: str = "Landau"
    unit_lane: str = "natural"
    josephson_tolerance: float = 1.0e-12
    entropy_tolerance: float = 1.0e-12
    state_match_tolerance: float = 1.0e-10
    require_josephson: bool = True
    allow_synthetic_controls: bool = False

    def __post_init__(self) -> None:
        if self.hydrodynamic_frame != "Landau":
            raise NotImplementedError("transport v1 supports only the Landau frame")
        if self.unit_lane != "natural":
            raise NotImplementedError("transport v1 supports only natural units")
        for name in (
            "josephson_tolerance",
            "entropy_tolerance",
            "state_match_tolerance",
        ):
            value = _finite_scalar(getattr(self, name), name)
            if value <= 0.0:
                raise ValueError(f"{name} must be positive")
        names = [record.coefficient_name for record in self.coefficient_records]
        if len(names) != len(set(names)):
            raise ValueError("coefficient_records must have unique names")


def _gauge_invariant_phase_gradient(state: SuperfluidHydroState) -> np.ndarray:
    gradient = _vector4(state.phase_gradient, "phase_gradient")
    if state.background_gauge is None:
        return gradient
    return gradient + _vector4(state.background_gauge, "background_gauge")


def spatial_projector(
    metric: Any,
    four_velocity: Any,
    *,
    inverse_metric: Any | None = None,
) -> np.ndarray:
    """Return ``Delta^{mu nu}=g^{mu nu}+u^mu u^nu`` for signature -+++ ."""

    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    velocity = _vector4(four_velocity, "four_velocity")
    norm = float(velocity @ g @ velocity)
    if abs(norm + 1.0) > 1.0e-10:
        raise ValueError("four_velocity must be future timelike and normalized to -1")
    return np.asarray(inverse + np.outer(velocity, velocity), dtype=float)


def josephson_residual(
    state: SuperfluidHydroState,
    metric: Any,
) -> float:
    """Return the ideal Josephson residual ``u^mu xi_mu + mu``."""

    g, _ = validate_lorentz_metric(metric)
    velocity = _vector4(state.four_velocity, "four_velocity")
    norm = float(velocity @ g @ velocity)
    if abs(norm + 1.0) > 1.0e-10:
        raise ValueError("four_velocity must be normalized to -1")
    xi_covariant = _gauge_invariant_phase_gradient(state)
    return float(velocity @ xi_covariant + state.chemical_potential)


def superfluid_invariants(
    state: SuperfluidHydroState,
    metric: Any,
    config: SuperfluidTransportConfig,
    *,
    inverse_metric: Any | None = None,
) -> dict[str, Any]:
    """Return the covariant phase invariants used by the ideal constitutive law."""

    if abs(state.temperature) > config.state_match_tolerance:
        raise NotImplementedError(
            "the action-derived v1 EOS is T=0; a normal finite-temperature component is open"
        )
    g, inverse = validate_lorentz_metric(metric, inverse_metric)
    velocity = _vector4(state.four_velocity, "four_velocity")
    norm = float(velocity @ g @ velocity)
    if abs(norm + 1.0) > config.state_match_tolerance:
        raise ValueError("four_velocity must be normalized to -1")
    xi_covariant = _gauge_invariant_phase_gradient(state)
    xi_contravariant = inverse @ xi_covariant
    frame_mu = -float(velocity @ xi_covariant)
    residual = frame_mu - state.chemical_potential
    if config.require_josephson and abs(residual) > config.josephson_tolerance:
        raise ValueError(
            "state chemical_potential does not satisfy u^mu*xi_mu=-mu"
        )
    projector = inverse + np.outer(velocity, velocity)
    xi_perp = projector @ xi_covariant
    xi_sq = float(xi_covariant @ xi_contravariant)
    invariant_x = -xi_sq
    if invariant_x <= 0.0:
        raise ValueError("superfluid phase gradient must be timelike (X>0)")
    mass_sq = effective_mass_sq(state.space_response, config.eos)
    q = config.eos.matter.matter_kinetic * invariant_x - mass_sq
    scale = max(1.0, abs(config.eos.matter.matter_kinetic * invariant_x), abs(mass_sq))
    if q <= config.eos.branch_tolerance * scale:
        raise ValueError("ideal superfluid constitutive law requires the condensed branch")
    return {
        "metric": g,
        "inverse_metric": inverse,
        "four_velocity": velocity,
        "xi_covariant": xi_covariant,
        "xi_contravariant": xi_contravariant,
        "xi_perp_contravariant": xi_perp,
        "frame_chemical_potential": frame_mu,
        "josephson_residual": residual,
        "invariant_X": invariant_x,
        "effective_mass_sq": mass_sq,
        "condensate_control": q,
    }


def ideal_superfluid_coefficients(
    state: SuperfluidHydroState,
    metric: Any,
    config: SuperfluidTransportConfig,
    *,
    inverse_metric: Any | None = None,
) -> dict[str, float]:
    """Return pressure and stiffness derived from the same ``P(X,Phi)``."""

    invariants = superfluid_invariants(
        state, metric, config, inverse_metric=inverse_metric
    )
    q = float(invariants["condensate_control"])
    quartic = config.eos.matter.matter_quartic
    stiffness = config.eos.matter.matter_kinetic * q / quartic
    pressure = q * q / (4.0 * quartic)
    frame_mu = float(invariants["frame_chemical_potential"])
    density = stiffness * frame_mu
    return {
        "pressure": pressure,
        "superfluid_stiffness": stiffness,
        "frame_charge_density": density,
        "amplitude_sq": q / quartic,
        "response_source": (
            0.5
            * config.eos.response.epsilon_nc
            * config.eos.matter.response_coupling
            * q
            / quartic
        ),
    }


def ideal_superfluid_current(
    state: SuperfluidHydroState,
    metric: Any,
    config: SuperfluidTransportConfig,
    *,
    inverse_metric: Any | None = None,
) -> np.ndarray:
    """Return ``N^mu=(Z*q/lambda)*xi^mu`` from the pressure derivative."""

    invariants = superfluid_invariants(
        state, metric, config, inverse_metric=inverse_metric
    )
    coefficients = ideal_superfluid_coefficients(
        state, metric, config, inverse_metric=inverse_metric
    )
    return np.asarray(
        coefficients["superfluid_stiffness"]
        * invariants["xi_contravariant"],
        dtype=float,
    )


def ideal_superfluid_stress_tensor(
    state: SuperfluidHydroState,
    metric: Any,
    config: SuperfluidTransportConfig,
    *,
    inverse_metric: Any | None = None,
) -> np.ndarray:
    """Return the contravariant action-derived ``T^{mu nu}``.

    For the pure T=0 branch this is ``f_s xi^mu xi^nu+p g^mu nu``.  It reduces
    to the perfect-fluid form when the counterflow vanishes.  A separate normal
    component is intentionally not invented.
    """

    invariants = superfluid_invariants(
        state, metric, config, inverse_metric=inverse_metric
    )
    coefficients = ideal_superfluid_coefficients(
        state, metric, config, inverse_metric=inverse_metric
    )
    xi = invariants["xi_contravariant"]
    return np.asarray(
        coefficients["superfluid_stiffness"] * np.outer(xi, xi)
        + coefficients["pressure"] * invariants["inverse_metric"],
        dtype=float,
    )


def _record(
    config: SuperfluidTransportConfig,
    state: SuperfluidHydroState,
    coefficient_name: str,
    *,
    positive: bool = False,
) -> float:
    matches = [
        item
        for item in config.coefficient_records
        if item.coefficient_name == coefficient_name
    ]
    if not matches:
        raise RuntimeError(
            f"missing KuboCoefficientRecord for {coefficient_name!r}; no default is allowed"
        )
    item = matches[0]
    ready = item.ready or (
        config.allow_synthetic_controls and item.ready_as_synthetic_control
    )
    if not ready:
        raise RuntimeError(
            f"KuboCoefficientRecord for {coefficient_name!r} lacks matched provenance"
        )
    if abs(item.temperature - state.temperature) > config.state_match_tolerance:
        raise RuntimeError(f"{coefficient_name!r} temperature does not match the state")
    if abs(item.chemical_potential - state.chemical_potential) > config.state_match_tolerance:
        raise RuntimeError(f"{coefficient_name!r} chemical potential does not match the state")
    if abs(item.space_response - state.space_response) > config.state_match_tolerance:
        raise RuntimeError(f"{coefficient_name!r} Phi does not match the state")
    value = float(item.value)
    if positive and value <= 0.0:
        raise ValueError(f"{coefficient_name} must be positive")
    return value


def longitudinal_onsager_matrix(
    state: SuperfluidHydroState,
    config: SuperfluidTransportConfig,
) -> np.ndarray:
    """Return the sourced 2x2 charge/phase Onsager matrix."""

    conductivity = _record(config, state, "regular_conductivity")
    phase_relaxation = _record(config, state, "phase_relaxation")
    cross = _record(config, state, "charge_phase_cross")
    matrix = np.array(
        [[conductivity, cross], [cross, phase_relaxation]], dtype=float
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    if float(np.min(eigenvalues)) < -config.entropy_tolerance:
        raise ValueError("longitudinal Onsager matrix must be positive-semidefinite")
    return matrix


def entropy_production(
    thermodynamic_forces: Any,
    state: SuperfluidHydroState,
    config: SuperfluidTransportConfig,
) -> float:
    """Return ``X^T L X`` for the selected longitudinal dissipative sector."""

    forces = np.asarray(thermodynamic_forces, dtype=float)
    if forces.shape != (2,) or not np.all(np.isfinite(forces)):
        raise ValueError("thermodynamic_forces must be a finite vector of shape (2,)")
    matrix = longitudinal_onsager_matrix(state, config)
    production = float(forces @ matrix @ forces)
    if production < -config.entropy_tolerance:
        raise RuntimeError("entropy production is negative beyond tolerance")
    return production


def causal_longitudinal_current_rate(
    current: float,
    chemical_potential_gradient: float,
    state: SuperfluidHydroState,
    config: SuperfluidTransportConfig,
) -> float:
    """Return ``dJ/dt=(-J-sigma_reg*grad(mu))/tau_J``."""

    flux = _finite_scalar(current, "current")
    force = _finite_scalar(
        chemical_potential_gradient, "chemical_potential_gradient"
    )
    conductivity = _record(config, state, "regular_conductivity")
    relaxation = _record(config, state, "relaxation_time", positive=True)
    return float((-flux - conductivity * force) / relaxation)


def causal_transport_diagnostics(
    state: SuperfluidHydroState,
    metric: Any,
    config: SuperfluidTransportConfig,
) -> dict[str, float | bool]:
    """Return ``D=sigma_reg/chi`` and the telegraph characteristic speed."""

    if abs(josephson_residual(state, metric)) > config.josephson_tolerance:
        raise ValueError("causal diagnostics require an equilibrium Josephson state")
    eos_state = o2_equilibrium_state(
        state.chemical_potential, state.space_response, config.eos
    )
    if eos_state.branch != "condensed" or not eos_state.susceptibility:
        raise ValueError("causal diagnostics require positive condensed susceptibility")
    conductivity = _record(config, state, "regular_conductivity")
    relaxation = _record(config, state, "relaxation_time", positive=True)
    if conductivity < 0.0:
        raise ValueError("regular_conductivity must be non-negative")
    diffusion = conductivity / eos_state.susceptibility
    speed_sq = diffusion / relaxation
    return {
        "susceptibility": eos_state.susceptibility,
        "regular_conductivity": conductivity,
        "diffusion_coefficient": diffusion,
        "relaxation_time": relaxation,
        "characteristic_speed_sq": speed_sq,
        "within_natural_light_cone": speed_sq <= 1.0 + 1.0e-12,
    }


def linear_mode_spectrum(
    wavenumber: float,
    state: SuperfluidHydroState,
    metric: Any,
    config: SuperfluidTransportConfig,
) -> dict[str, Any]:
    """Return ideal Goldstone frequencies and causal regular-current modes."""

    k = _finite_scalar(wavenumber, "wavenumber")
    if k < 0.0:
        raise ValueError("wavenumber must be non-negative")
    diagnostics = causal_transport_diagnostics(state, metric, config)
    eos_state = o2_equilibrium_state(
        state.chemical_potential, state.space_response, config.eos
    )
    if eos_state.sound_speed_sq is None:
        raise ValueError("Goldstone speed is undefined outside the condensed branch")
    sound_speed = float(np.sqrt(eos_state.sound_speed_sq))
    diffusion = float(diagnostics["diffusion_coefficient"])
    relaxation = float(diagnostics["relaxation_time"])
    discriminant = complex(1.0 - 4.0 * relaxation * diffusion * k * k)
    root = np.sqrt(discriminant)
    return {
        "goldstone_angular_frequencies": np.array(
            [-sound_speed * k, sound_speed * k], dtype=float
        ),
        "causal_regular_growth_rates": np.array(
            [(-1.0 - root) / (2.0 * relaxation), (-1.0 + root) / (2.0 * relaxation)],
            dtype=complex,
        ),
        "sound_speed_sq": eos_state.sound_speed_sq,
        **diagnostics,
    }


def covariant_superfluid_transport_contract() -> dict[str, Any]:
    """Return achieved scope, forbidden shortcuts, and the next controller."""

    return {
        "status": O2_SUPERFLUID_TRANSPORT_STATUS,
        "operator_mode": O2_SUPERFLUID_TRANSPORT_OPERATOR_MODE,
        "ideal_pressure": "tree_level_P_of_X_Phi_from_O2_action",
        "ideal_current": "N^mu=(Z*q/lambda)*xi^mu",
        "ideal_stress": "T^mu_nu=f_s*xi^mu*xi^nu+p*g^mu_nu",
        "hydrodynamic_frame": "Landau",
        "temperature_scope": "T_ZERO_PURE_SUPERFLUID_ONLY",
        "normal_component": "OPEN_NOT_DERIVED",
        "dissipative_scope": "MINIMAL_LONGITUDINAL_KUBO_INTERFACE",
        "transport_values": "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS",
        "synthetic_controls": "EXPLICIT_OPT_IN_SIMULATION_ONLY",
        "entropy_gate": "SYMMETRIC_POSITIVE_SEMIDEFINITE_ONSAGER_MATRIX",
        "causal_extension": "MAXWELL_CATTANEO_REGULAR_CURRENT_CONTROL",
        "full_superfluid_transport_tensor": "DEFERRED",
        "curved_3p1_solver": "NOT_IMPLEMENTED",
        "si_lane": "BLOCKED",
        "trace_input": False,
        "trace_backreaction": False,
        "topic_0_11_status_impact": "NONE",
        "topic_0_19_status_impact": "NONE",
        "next_controller": O2_SUPERFLUID_TRANSPORT_CONTROLLER,
    }
