"""Thermal Gaussian mass-source matching; no vacuum or material calibration."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from docs.core.uet_covariant_matter import CovariantMatterConfig
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_thermoelastic_spatial_compatibility import strain_map


def canonical_sources(matter: CovariantMatterConfig, response: CovariantResponseConfig,
                      deformation_raw) -> dict:
    d = np.asarray(deformation_raw, dtype=float)
    if d.shape != (6,) or not np.isfinite(d).all():
        raise ValueError("finite length-six Mandel mass-source deformation required")
    return {"mass_squared": matter.matter_mass_sq/matter.matter_kinetic,
            "eta": response.epsilon_nc*matter.response_coupling/matter.matter_kinetic,
            "deformation": d/matter.matter_kinetic}


@lru_cache(maxsize=8)
def _quadrature(order: int):
    x, w = np.polynomial.legendre.leggauss(order)
    u, w = (x+1)/2, w/2
    u.setflags(write=False)
    w.setflags(write=False)
    return u, w


def thermal_moments(temperature: float, mass_squared: float, order: int = 160) -> dict:
    if not np.isfinite([temperature, mass_squared]).all() or min(temperature, mass_squared) <= 0:
        raise ValueError("positive finite T and mass squared required on the normal branch")
    if isinstance(order, bool) or not isinstance(order, (int, np.integer)) or order < 16:
        raise ValueError("integer quadrature order >=16 required")
    u, weights = _quadrature(order)
    # Map the open quadrature nodes onto the full radial half-line, without a cutoff.
    momentum = temperature*u/(1-u)
    measure = weights*temperature/(1-u)**2*momentum**2/(2*np.pi**2)
    energy = np.sqrt(momentum**2+mass_squared)
    z = energy/temperature
    occupation = np.exp(-z)/(-np.expm1(-z))
    variance = occupation*(1+occupation)
    log_partition = np.log(-np.expm1(-z))
    return {
        "free_energy": float(2*temperature*(measure@log_partition)),
        "mass_derivative": float(measure@(occupation/energy)),
        "mass_second_derivative": float(-.5*(measure@(occupation/energy**3+variance/(temperature*energy**2)))),
        "mass_temperature_derivative": float(measure@variance/temperature**2),
        "heat_capacity": float(2*(measure@(energy**2*variance))/temperature**2),
        "entropy": float(2*(measure@(z*occupation-log_partition))),
    }


def deformed_free_energy(temperature: float, sources: dict, delta_phi: float,
                         strain, order: int = 160) -> float:
    eps = np.asarray(strain, dtype=float)
    if eps.shape != (6,) or not np.isfinite(eps).all() or not np.isfinite(delta_phi):
        raise ValueError("finite strain and Phi displacement required")
    mass_squared = sources["mass_squared"]-sources["eta"]*delta_phi+sources["deformation"]@eps
    return thermal_moments(temperature, mass_squared, order)["free_energy"]


def thermal_matching(temperature: float, sources: dict, order: int = 160) -> dict:
    d = np.asarray(sources["deformation"], dtype=float)
    eta = float(sources["eta"])
    if d.shape != (6,) or not np.isfinite(d).all() or not np.isfinite(eta):
        raise ValueError("finite canonical mass sources required")
    moments = thermal_moments(temperature, sources["mass_squared"], order)
    fxx, fxt = moments["mass_second_derivative"], moments["mass_temperature_derivative"]
    source_vector = np.r_[-eta, d]
    return {
        "moments": moments,
        "G": -eta*d*fxx,
        "entropy_phi_coefficient": eta*fxt,
        "delta_stiffness": np.outer(d, d)*fxx,
        "delta_phi_curvature": eta**2*fxx,
        "delta_thermal_stress": -d*fxt,
        "delta_heat_capacity": moments["heat_capacity"],
        "phi_strain_hessian": np.outer(source_vector, source_vector)*fxx,
    }


def isentropic_matched_response(*, stiffness, thermal_stress, coupling,
                                entropy_phi_coefficient: float, temperature: float,
                                heat_capacity: float, direction, delta_phi: float) -> dict:
    """Use declared TOTAL coefficients; do not auto-add loops to measured material data."""
    k = np.asarray(stiffness, dtype=float)
    beta, g = np.asarray(thermal_stress, dtype=float), np.asarray(coupling, dtype=float)
    if k.shape != (6, 6) or beta.shape != (6,) or g.shape != (6,):
        raise ValueError("six-component Mandel tensors required")
    if not all(np.isfinite(x).all() for x in (k, beta, g)):
        raise ValueError("finite tensor coefficients required")
    scale = float(np.max(np.abs(k)))
    if scale == 0 or np.max(np.abs(k-k.T)) > 1e-12*scale or np.min(np.linalg.eigvalsh(k/scale)) <= 0:
        raise ValueError("symmetric positive total stiffness required")
    if not np.isfinite([entropy_phi_coefficient, temperature, heat_capacity, delta_phi]).all() or min(temperature, heat_capacity) <= 0:
        raise ValueError("finite coefficients and positive T/c required")
    bm = strain_map(direction)
    a, b, h = bm.T@k@bm, bm.T@beta, bm.T@g
    block = np.block([[a, -b[:, None]], [b[None, :], np.array([[heat_capacity/temperature]])]])
    solved = np.linalg.solve(block, np.r_[-h*delta_phi, -entropy_phi_coefficient*delta_phi])
    denominator = heat_capacity+temperature*b@np.linalg.solve(a, b)
    indirect = temperature*(b@np.linalg.solve(a, h))/denominator
    direct = -temperature*entropy_phi_coefficient/denominator
    return {"delta_temperature": float(solved[3]), "gain": float(indirect+direct),
            "strain_only_gain": float(indirect), "direct_entropy_gain": float(direct),
            "strain": bm@solved[:3],
            "entropy_residual": float(b@solved[:3]+heat_capacity*solved[3]/temperature+entropy_phi_coefficient*delta_phi),
            "mechanical_residual": float(np.linalg.norm(a@solved[:3]-b*solved[3]+h*delta_phi))}
