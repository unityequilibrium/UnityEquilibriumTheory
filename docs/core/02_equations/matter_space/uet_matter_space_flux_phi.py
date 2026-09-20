"""Couple the named conserved C flux branch to the causal Phi lane."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple

import numpy as np

from docs.core.uet_matter_space import MatterSpaceConfig, MatterSpaceState
from docs.core.uet_matter_space_causal import (
    _advance_local_root,
    causal_space_discrete_energy,
)
from docs.core.uet_matter_space_flux_telegraph import (
    FluxTelegraphConfig,
    flux_telegraph_energy,
    flux_telegraph_step,
)
from docs.core.uet_spatial import integral_1d, laplacian_1d, validate_dx, validate_field_1d


FLUX_PHI_COUPLED_OPERATOR_MODE = "matter_space_conserved_flux_phi_coupled_v1"


def _default_phi_config() -> MatterSpaceConfig:
    return MatterSpaceConfig(
        a_matter=0.0,
        b_matter=1.0,
        kappa_matter=1.0,
        mobility_matter=0.04,
        a_space=0.8,
        b_space=0.6,
        kappa_space=0.2,
        mobility_space=0.5,
        tau_space=0.7,
        coupling_g=0.15,
        matter_dynamics="conserved",
        boundary_condition="zero_flux",
        unit_lane="normalized",
        stability_safety=0.2,
    )


@dataclass(frozen=True)
class FluxPhiCoupledConfig:
    """Normalized configuration for the named coupled branch."""

    C: FluxTelegraphConfig = field(default_factory=FluxTelegraphConfig)
    Phi: MatterSpaceConfig = field(default_factory=_default_phi_config)

    def __post_init__(self) -> None:
        if self.C.boundary_condition != self.Phi.boundary_condition:
            raise ValueError("C and Phi boundary conditions must match")
        if not np.isclose(self.C.coupling_g, self.Phi.coupling_g):
            raise ValueError("C and Phi coupling_g must match")

    @property
    def causal_speed(self) -> float:
        return float(max(self.C.characteristic_speed, self.Phi.space_speed))


def _coupling_energy(
    C: np.ndarray,
    Phi: np.ndarray,
    dx: float,
    config: FluxPhiCoupledConfig,
) -> float:
    return float(integral_1d(-0.5 * config.C.coupling_g * C**2 * Phi, dx))


def coupled_energy(
    C: np.ndarray,
    flux: np.ndarray,
    Phi: np.ndarray,
    previous_Phi: np.ndarray,
    dt: float,
    dx: float,
    config: FluxPhiCoupledConfig,
) -> float:
    """Return one combined two-level energy without double-counting coupling."""

    matter = validate_field_1d(C, "C")
    response = validate_field_1d(Phi, "Phi")
    previous = validate_field_1d(previous_Phi, "previous_Phi")
    if matter.shape != response.shape or matter.shape != previous.shape:
        raise ValueError("C, Phi, and previous_Phi must share one shape")
    spacing = validate_dx(dx)
    c_energy = flux_telegraph_energy(matter, flux, spacing, config.C, response)
    phi_energy = causal_space_discrete_energy(
        response, previous, matter, dt, spacing, config.Phi
    )
    return float(c_energy + phi_energy - _coupling_energy(matter, response, spacing, config))


def _causal_phi_step_any_cfl(
    state: MatterSpaceState,
    previous_phi: np.ndarray,
    dt: float,
    dx: float,
    config: MatterSpaceConfig,
) -> Tuple[MatterSpaceState, np.ndarray, dict[str, Any]]:
    """Use the same local discrete-gradient root with CFL in (0, 1]."""

    step = float(dt)
    spacing = validate_dx(dx)
    previous = validate_field_1d(previous_phi, "previous_phi")
    if previous.shape != state.space_response.shape:
        raise ValueError("previous_phi must match Phi shape")
    cfl = config.space_speed * step / spacing
    if cfl <= 0.0 or cfl > 1.0 + 1.0e-12:
        raise ValueError(f"causal Phi CFL must be in (0,1], received {cfl:.12g}")
    current = state.space_response
    spatial_force = -config.kappa_space * laplacian_1d(
        current, spacing, config.boundary_condition
    )
    next_phi = np.empty_like(current)
    max_root_residual = 0.0
    root_iterations = 0
    for index in range(current.size):
        next_phi[index], iterations, residual = _advance_local_root(
            current[index],
            previous[index],
            state.C[index],
            spatial_force[index],
            0.0,
            step,
            config,
        )
        root_iterations = max(root_iterations, iterations)
        max_root_residual = max(max_root_residual, residual)
    updated = MatterSpaceState(
        state.C.copy(),
        next_phi,
        (next_phi - previous) / (2.0 * step),
    )
    return updated, current.copy(), {
        "cfl": float(cfl),
        "max_root_residual": float(max_root_residual),
        "root_iterations_max": int(root_iterations),
    }


def flux_phi_coupled_step(
    C: np.ndarray,
    flux: np.ndarray,
    Phi: np.ndarray,
    previous_Phi: np.ndarray,
    dt: float,
    dx: float,
    config: FluxPhiCoupledConfig,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    """Advance C and Phi from the same old-time coupling state."""

    matter = validate_field_1d(C, "C")
    response = validate_field_1d(Phi, "Phi")
    previous = validate_field_1d(previous_Phi, "previous_Phi")
    if matter.shape != response.shape or matter.shape != previous.shape:
        raise ValueError("C, Phi, and previous_Phi must share one shape")
    spacing = validate_dx(dx)
    step = float(dt)
    if step <= 0.0 or not np.isfinite(step):
        raise ValueError("dt must be finite and positive")

    energy_before = coupled_energy(
        matter, flux, response, previous, step, spacing, config
    )
    c_energy_before = flux_telegraph_energy(
        matter, flux, spacing, config.C, response
    )
    phi_energy_before = causal_space_discrete_energy(
        response, previous, matter, step, spacing, config.Phi
    )
    coupling_before = _coupling_energy(matter, response, spacing, config)
    next_C, next_flux, c_ledger = flux_telegraph_step(
        matter, flux, step, spacing, config.C, response
    )
    phi_state = MatterSpaceState(
        matter,
        response,
        (response - previous) / (2.0 * step),
    )
    updated_phi, old_phi, phi_ledger = _causal_phi_step_any_cfl(
        phi_state,
        previous,
        step,
        spacing,
        config.Phi,
    )
    next_Phi = updated_phi.space_response
    c_energy_after_old_phi = flux_telegraph_energy(
        next_C, next_flux, spacing, config.C, response
    )
    phi_energy_after_old_C = causal_space_discrete_energy(
        next_Phi, old_phi, matter, step, spacing, config.Phi
    )
    energy_after = coupled_energy(
        next_C, next_flux, next_Phi, old_phi, step, spacing, config
    )
    split_energy_after = (
        c_energy_after_old_phi + phi_energy_after_old_C - coupling_before
    )
    coupling_exchange_work = energy_after - split_energy_after
    phi_damping_work = (
        np.sum((next_Phi - previous) ** 2)
        * spacing
        / (4.0 * config.Phi.mobility_space * step)
    )
    expected_delta = (
        -c_ledger["dissipation_work"]
        - phi_damping_work
        + coupling_exchange_work
    )
    actual_delta = energy_after - energy_before
    residual = actual_delta - expected_delta
    # Keep the ledger scale identical to the named C branch: the normalized
    # energy lane uses an absolute floor of one rather than a dt-dependent
    # scale that could make a small timestep look artificially compliant.
    residual_scale = max(abs(energy_before), 1.0)
    return next_C, next_flux, next_Phi, old_phi, {
        "operator_mode": FLUX_PHI_COUPLED_OPERATOR_MODE,
        "C_cfl": c_ledger["cfl"],
        "Phi_cfl": phi_ledger["cfl"],
        "energy_before": float(energy_before),
        "energy_after": float(energy_after),
        "expected_delta": float(expected_delta),
        "actual_delta": float(actual_delta),
        "coupling_exchange_work": float(coupling_exchange_work),
        "combined_energy_residual": float(residual),
        "combined_energy_scale": float(residual_scale),
        "combined_energy_relative_residual": float(abs(residual) / residual_scale),
        "C_substep_energy_residual": float(c_ledger["energy_residual"]),
        "Phi_substep_energy_residual": float(
            phi_energy_after_old_C - phi_energy_before + phi_damping_work
        ),
        "C_mass_drift": c_ledger["mass_drift"],
        "Phi_root_residual": phi_ledger["max_root_residual"],
        "field_clipping_applied": False,
        "cone_padding_applied": False,
        "parameter_fitting_applied": False,
        "trace_backreaction": False,
        "unit_lane": config.C.unit_lane,
    }


__all__ = [
    "FLUX_PHI_COUPLED_OPERATOR_MODE",
    "FluxPhiCoupledConfig",
    "coupled_energy",
    "flux_phi_coupled_step",
]
