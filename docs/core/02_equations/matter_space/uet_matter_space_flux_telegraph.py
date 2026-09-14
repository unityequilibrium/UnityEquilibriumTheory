"""Named conserved finite-cone flux branch for the matter-space lane.

This branch keeps C as a conserved coordinate and introduces a face flux as a
physical state. It is separate from ``matter_space_coupled_v1`` and sets the
branch C gradient-energy coefficient to zero, because the declared local
gradient class has a fourth-order high-frequency principal symbol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

import numpy as np

from docs.core.uet_spatial import (
    face_gradient_1d,
    integral_1d,
    validate_boundary,
    validate_dx,
    validate_field_1d,
)


FLUX_TELEGRAPH_OPERATOR_MODE = "matter_space_conserved_flux_telegraph_v1"


@dataclass(frozen=True)
class FluxTelegraphConfig:
    """Normalized branch coefficients; these are not SI constants."""

    a_C: float = 0.8
    b_C: float = 1.0
    mobility_C: float = 0.04
    tau_C: float = 0.7
    coupling_g: float = 0.15
    boundary_condition: str = "zero_flux"
    unit_lane: str = "normalized"
    kappa_C: float = 0.0

    def __post_init__(self) -> None:
        values = {
            "a_C": self.a_C,
            "b_C": self.b_C,
            "mobility_C": self.mobility_C,
            "tau_C": self.tau_C,
            "coupling_g": self.coupling_g,
            "kappa_C": self.kappa_C,
        }
        if not all(np.isfinite(float(value)) for value in values.values()):
            raise ValueError("flux-telegraph coefficients must be finite")
        if self.a_C <= 0.0 or self.b_C < 0.0:
            raise ValueError("a_C must be positive and b_C must be non-negative")
        if self.mobility_C <= 0.0 or self.tau_C <= 0.0:
            raise ValueError("mobility_C and tau_C must be positive")
        if self.coupling_g < 0.0:
            raise ValueError("coupling_g must be non-negative")
        if self.kappa_C != 0.0:
            raise ValueError("the named finite-cone branch requires kappa_C=0")
        if self.unit_lane != "normalized":
            raise NotImplementedError("the branch currently supports normalized units only")
        validate_boundary(self.boundary_condition)

    @property
    def characteristic_speed(self) -> float:
        """Linearized finite-cone speed around C=Phi=0."""

        return float(np.sqrt(self.mobility_C * self.a_C / self.tau_C))


def _face_count(size: int, boundary: str) -> int:
    return size if boundary == "periodic" else size + 1


def _validate_flux(flux: np.ndarray, size: int, boundary: str) -> np.ndarray:
    value = np.asarray(flux, dtype=float)
    expected = _face_count(size, boundary)
    if value.ndim != 1 or value.size != expected:
        raise ValueError(f"flux must contain {expected} faces for {boundary}")
    if not np.all(np.isfinite(value)):
        raise ValueError("flux contains non-finite values")
    checked = value.copy()
    if boundary == "zero_flux":
        checked[0] = 0.0
        checked[-1] = 0.0
    return checked


def _face_divergence(flux: np.ndarray, dx: float, boundary: str) -> np.ndarray:
    spacing = validate_dx(dx)
    if boundary == "periodic":
        return (flux - np.roll(flux, 1)) / spacing
    return (flux[1:] - flux[:-1]) / spacing


def local_chemical_potential(
    C: np.ndarray,
    Phi: Optional[np.ndarray],
    config: FluxTelegraphConfig,
) -> np.ndarray:
    """Return the branch-local chemical potential with no C gradient term."""

    matter = validate_field_1d(C, "C")
    response = np.zeros_like(matter) if Phi is None else validate_field_1d(Phi, "Phi")
    if response.shape != matter.shape:
        raise ValueError("Phi must match C shape")
    return (
        config.a_C * matter
        + config.b_C * matter**3
        - config.coupling_g * matter * response
    )


def flux_telegraph_energy(
    C: np.ndarray,
    flux: np.ndarray,
    dx: float,
    config: FluxTelegraphConfig,
    Phi: Optional[np.ndarray] = None,
) -> float:
    """Return the branch energy including flux inertia and local coupling."""

    matter = validate_field_1d(C, "C")
    spacing = validate_dx(dx)
    face_flux = _validate_flux(flux, matter.size, config.boundary_condition)
    response = np.zeros_like(matter) if Phi is None else validate_field_1d(Phi, "Phi")
    if response.shape != matter.shape:
        raise ValueError("Phi must match C shape")
    local = (
        0.5 * config.a_C * matter**2
        + 0.25 * config.b_C * matter**4
        - 0.5 * config.coupling_g * matter**2 * response
    )
    kinetic = config.tau_C / (2.0 * config.mobility_C) * face_flux**2
    return float(integral_1d(local, spacing) + np.sum(kinetic) * spacing)


def flux_telegraph_step(
    C: np.ndarray,
    previous_flux: np.ndarray,
    dt: float,
    dx: float,
    config: FluxTelegraphConfig,
    Phi: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Advance one local conserved flux-telegraph step.

    The Crank-Nicolson damping factor is paired with a conservative explicit
    flux update. The spatial stencil is nearest-neighbor, so CFL is a
    domain-of-dependence contract rather than a padding rule.
    """

    matter = validate_field_1d(C, "C")
    spacing = validate_dx(dx)
    step = float(dt)
    if not np.isfinite(step) or step <= 0.0:
        raise ValueError("dt must be finite and positive")
    boundary = config.boundary_condition
    old_flux = _validate_flux(previous_flux, matter.size, boundary)
    response = np.zeros_like(matter) if Phi is None else validate_field_1d(Phi, "Phi")
    if response.shape != matter.shape:
        raise ValueError("Phi must match C shape")

    cfl = config.characteristic_speed * step / spacing
    if cfl > 1.0 + 1.0e-12:
        raise ValueError(f"flux-telegraph CFL exceeds one: {cfl:.12g}")

    energy_before = flux_telegraph_energy(matter, old_flux, spacing, config, response)
    chemical_potential = local_chemical_potential(matter, response, config)
    gradient = face_gradient_1d(chemical_potential, spacing, boundary)
    half_damping = step / (2.0 * config.tau_C)
    damping = (1.0 - half_damping) / (1.0 + half_damping)
    drive = (
        step
        * config.mobility_C
        / config.tau_C
        / (1.0 + half_damping)
    )
    new_flux = damping * old_flux - drive * gradient
    if boundary == "zero_flux":
        new_flux[0] = 0.0
        new_flux[-1] = 0.0
    next_C = matter - step * _face_divergence(new_flux, spacing, boundary)
    energy_after = flux_telegraph_energy(next_C, new_flux, spacing, config, response)
    dissipation = float(np.sum(new_flux**2) * spacing / config.mobility_C)
    mass_before = integral_1d(matter, spacing)
    mass_after = integral_1d(next_C, spacing)
    return next_C, new_flux, {
        "operator_mode": FLUX_TELEGRAPH_OPERATOR_MODE,
        "cfl": float(cfl),
        "mass_before": float(mass_before),
        "mass_after": float(mass_after),
        "mass_drift": float(mass_after - mass_before),
        "energy_before": float(energy_before),
        "energy_after": float(energy_after),
        "dissipation_work": float(step * dissipation),
        "energy_residual": float(energy_after - energy_before + step * dissipation),
        "field_clipping_applied": False,
        "cone_padding_applied": False,
        "parameter_fitting_applied": False,
        "trace_backreaction": False,
        "unit_lane": config.unit_lane,
        "kappa_C": config.kappa_C,
    }


__all__ = [
    "FLUX_TELEGRAPH_OPERATOR_MODE",
    "FluxTelegraphConfig",
    "flux_telegraph_energy",
    "flux_telegraph_step",
    "local_chemical_potential",
]
