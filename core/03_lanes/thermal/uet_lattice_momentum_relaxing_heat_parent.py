"""Synthetic lattice heat-transport parent for Topic 13.

The construction is a standard-physics comparator in the lattice rest frame.
It demonstrates the structural role of momentum-relaxing collisions without
claiming a UET-to-material match or supplying a physical Kubo coefficient.
Natural units hbar = c = k_B = 1 are used throughout.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi

import numpy as np


LATTICE_HEAT_PARENT_STATUS = "PASS_SCOPED_LATTICE_HEAT_PARENT"


@dataclass(frozen=True)
class LatticeHeatParentState:
    temperature: float
    sound_speed: float
    momentum_cutoff: float
    radial_order: int
    normal_rate: float
    resistive_rate: float
    source_norm_squared: float
    source_momentum_overlap: float
    normal_minimum_eigenvalue: float
    normal_symmetry_residual: float
    normal_momentum_null_residual: float
    total_minimum_eigenvalue: float
    total_symmetry_residual: float
    resistive_momentum_relaxation_rate: float
    finite_steady_conductivity: bool
    conductivity_natural: float | None
    analytic_conductivity_natural: float | None
    conductivity_relative_residual: float | None
    minimum_entropy_quadratic_eigenvalue: float
    unit_lane: str = "natural_3p1_hbar_c_kB_1"
    conductivity_unit: str = "E^2"
    forcing_class: str = "lattice_rest_frame_temperature_gradient"
    normal_collision_origin: str = "synthetic_symmetric_psd_control"
    resistive_collision_origin: str = "external_synthetic_control_not_derived_or_fitted"
    physical_kubo_coefficient_emitted: bool = False
    uet_mapping_claimed: bool = False
    xie_2026_accessed: bool = False
    parameter_fitting_performed: bool = False


def _bose(energy: np.ndarray, temperature: float) -> np.ndarray:
    x = energy / temperature
    return 1.0 / np.expm1(x)


def lattice_momentum_relaxing_heat_parent_state(
    temperature: float = 0.25,
    sound_speed: float = 0.6,
    normal_rate: float = 0.20,
    resistive_rate: float = 0.025,
    *,
    cutoff_factor: float = 12.0,
    radial_order: int = 64,
) -> LatticeHeatParentState:
    """Build the finite Debye-mode collision parent and solve its heat response.

    Rates and temperature have energy dimension. The whitened heat source has
    dimension E^(3/2), so ``source.T @ collision^-1 @ source`` has E^2.
    """

    scalars = (temperature, sound_speed, normal_rate, resistive_rate, cutoff_factor)
    if not all(np.isfinite(value) for value in scalars):
        raise ValueError("all scalar inputs must be finite")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    if sound_speed <= 0.0 or sound_speed > 1.0:
        raise ValueError("sound_speed must lie in (0,1]")
    if normal_rate <= 0.0:
        raise ValueError("normal_rate must be positive")
    if resistive_rate < 0.0:
        raise ValueError("resistive_rate must be nonnegative")
    if cutoff_factor <= 0.0:
        raise ValueError("cutoff_factor must be positive")
    if isinstance(radial_order, bool) or int(radial_order) != radial_order:
        raise ValueError("radial_order must be an integer")
    if int(radial_order) < 4:
        raise ValueError("radial_order must be at least four")

    order = int(radial_order)
    cutoff = cutoff_factor * temperature / sound_speed
    nodes, weights = np.polynomial.legendre.leggauss(order)
    momentum = 0.5 * cutoff * (nodes + 1.0)
    dp = 0.5 * cutoff * weights
    energy = sound_speed * momentum
    occupation = _bose(energy, temperature)
    measure = 4.0 * pi / (2.0 * pi) ** 3 * momentum**2 * dp
    covariance_weight = measure * occupation * (1.0 + occupation) / 3.0

    raw_momentum_mode = np.sqrt(covariance_weight) * momentum
    momentum_norm = float(np.linalg.norm(raw_momentum_mode))
    if momentum_norm <= 0.0:
        raise FloatingPointError("momentum mode has zero norm")
    momentum_mode = raw_momentum_mode / momentum_norm

    beta = 1.0 / temperature
    heat_source = (
        np.sqrt(covariance_weight) * beta * energy * sound_speed
    )
    source_norm_squared = float(heat_source @ heat_source)
    source_overlap = float(
        abs(heat_source @ momentum_mode) / np.sqrt(source_norm_squared)
    )

    identity = np.eye(order)
    projector = np.outer(momentum_mode, momentum_mode)
    normal_collision = normal_rate * (identity - projector)
    resistive_collision = resistive_rate * identity
    total_collision = normal_collision + resistive_collision
    normal_eigenvalues = np.linalg.eigvalsh(normal_collision)
    total_eigenvalues = np.linalg.eigvalsh(total_collision)
    normal_null_residual = float(
        np.linalg.norm(normal_collision @ momentum_mode) / normal_rate
    )
    normal_symmetry_residual = float(
        np.linalg.norm(normal_collision - normal_collision.T)
        / max(np.linalg.norm(normal_collision), 1.0e-300)
    )
    total_symmetry_residual = float(
        np.linalg.norm(total_collision - total_collision.T)
        / max(np.linalg.norm(total_collision), 1.0e-300)
    )
    momentum_relaxation = float(momentum_mode @ resistive_collision @ momentum_mode)

    conductivity = None
    analytic = None
    response_residual = None
    finite_response = resistive_rate > 0.0
    if finite_response:
        response = np.linalg.solve(total_collision, heat_source)
        conductivity = float(heat_source @ response)
        # Linear Debye dispersion makes the heat source parallel to momentum.
        analytic = source_norm_squared / resistive_rate
        response_residual = float(
            abs(conductivity - analytic) / max(abs(analytic), 1.0e-300)
        )

    return LatticeHeatParentState(
        temperature=float(temperature),
        sound_speed=float(sound_speed),
        momentum_cutoff=float(cutoff),
        radial_order=order,
        normal_rate=float(normal_rate),
        resistive_rate=float(resistive_rate),
        source_norm_squared=source_norm_squared,
        source_momentum_overlap=source_overlap,
        normal_minimum_eigenvalue=float(normal_eigenvalues[0]),
        normal_symmetry_residual=normal_symmetry_residual,
        normal_momentum_null_residual=normal_null_residual,
        total_minimum_eigenvalue=float(total_eigenvalues[0]),
        total_symmetry_residual=total_symmetry_residual,
        resistive_momentum_relaxation_rate=momentum_relaxation,
        finite_steady_conductivity=finite_response,
        conductivity_natural=conductivity,
        analytic_conductivity_natural=analytic,
        conductivity_relative_residual=response_residual,
        minimum_entropy_quadratic_eigenvalue=float(total_eigenvalues[0]),
    )
