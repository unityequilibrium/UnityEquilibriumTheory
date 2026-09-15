"""Conditional bulk grating response; no data, dynamics or SI calibration."""

from __future__ import annotations

import numpy as np


def mandel(tensor: np.ndarray) -> np.ndarray:
    t = np.asarray(tensor, dtype=float)
    if t.shape != (3, 3) or not np.isfinite(t).all():
        raise ValueError("expected a finite 3x3 tensor")
    scale = max(float(np.max(np.abs(t))), np.finfo(float).tiny)
    if np.max(np.abs(t - t.T)) > 1e-12 * scale:
        raise ValueError("tensor must be symmetric")
    return np.array([t[0, 0], t[1, 1], t[2, 2],
                     np.sqrt(2)*t[1, 2], np.sqrt(2)*t[0, 2], np.sqrt(2)*t[0, 1]])


def tensor(vector: np.ndarray) -> np.ndarray:
    v = _vector(vector, 6)
    return np.array([[v[0], v[5]/np.sqrt(2), v[4]/np.sqrt(2)],
                     [v[5]/np.sqrt(2), v[1], v[3]/np.sqrt(2)],
                     [v[4]/np.sqrt(2), v[3]/np.sqrt(2), v[2]]])


def _vector(value: np.ndarray, size: int) -> np.ndarray:
    v = np.asarray(value, dtype=float)
    if v.shape != (size,) or not np.isfinite(v).all():
        raise ValueError(f"expected a finite length-{size} vector")
    return v


def strain_map(direction: np.ndarray) -> np.ndarray:
    n = _vector(direction, 3)
    scale = float(np.max(np.abs(n)))
    if scale == 0:
        raise ValueError("nonzero wavevector direction required; q=0 is a separate problem")
    n = n/scale
    x, y, z = n/np.linalg.norm(n)
    return np.array([[x, 0, 0], [0, y, 0], [0, 0, z],
                     [0, z/np.sqrt(2), y/np.sqrt(2)],
                     [z/np.sqrt(2), 0, x/np.sqrt(2)],
                     [y/np.sqrt(2), x/np.sqrt(2), 0]])


def isotropic_stiffness(bulk: float, shear: float) -> np.ndarray:
    if not np.isfinite([bulk, shear]).all() or min(bulk, shear) <= 0:
        raise ValueError("positive finite bulk and shear moduli required")
    identity = np.array([1., 1., 1., 0., 0., 0.])
    return 2*shear*np.eye(6) + (bulk - 2*shear/3)*np.outer(identity, identity)


def spatial_response(*, stiffness, expansion, coupling, direction,
                     temperature: float, heat_capacity: float,
                     phi_response: float, response_curvature: float) -> dict:
    """Solve a nonzero-q mode with ds=0; coefficients use declared natural units.

    Returns the homogeneous comparison as well, without substituting its full
    zero-stress condition for bulk mechanical equilibrium. Negative Schur
    margins are returned explicitly, not silently clipped or admitted.
    """
    k = np.asarray(stiffness, dtype=float)
    if k.shape != (6, 6) or not np.isfinite(k).all():
        raise ValueError("expected finite 6x6 Mandel stiffness")
    scale = float(np.max(np.abs(k)))
    if scale == 0 or np.max(np.abs(k-k.T)) > 1e-12*scale:
        raise ValueError("symmetric positive stiffness required")
    if np.min(np.linalg.eigvalsh(k/scale)) <= 0:
        raise ValueError("positive definite stiffness required")
    alpha, g = _vector(expansion, 6), _vector(coupling, 6)
    if not np.isfinite([temperature, heat_capacity, phi_response, response_curvature]).all():
        raise ValueError("finite thermodynamic inputs required")
    if min(temperature, heat_capacity, response_curvature) <= 0:
        raise ValueError("positive T, heat capacity and response curvature required")
    bmap = strain_map(direction)
    beta = k @ alpha
    acoustic = bmap.T @ k @ bmap
    b, h = bmap.T @ beta, bmap.T @ g
    block = np.block([[acoustic, -b[:, None]],
                      [b[None, :], np.array([[heat_capacity/temperature]])]])
    solution = np.linalg.solve(block, np.r_[-h*phi_response, 0.])
    strain, dt = bmap @ solution[:3], float(solution[3])
    compliance = bmap @ np.linalg.solve(acoustic, bmap.T)
    capacity = float(heat_capacity + temperature*beta @ compliance @ beta)
    gain = float(temperature*(beta @ compliance @ g)/capacity)
    homogeneous_capacity = float(heat_capacity + temperature*alpha @ k @ alpha)
    homogeneous_gain = float(temperature*(alpha @ g)/homogeneous_capacity)
    free_strain = np.linalg.solve(k, beta*homogeneous_gain*phi_response - g*phi_response)
    compatible_free = bmap @ np.linalg.lstsq(bmap, free_strain, rcond=None)[0]
    stress = k @ strain - beta*dt + g*phi_response
    return {
        "strain": strain.tolist(), "displacement_gradient_amplitude": solution[:3].tolist(),
        "delta_temperature": dt, "gain_per_phi_response": gain,
        "closed_form_temperature": gain*phi_response,
        "effective_heat_capacity": capacity,
        "stress": stress.tolist(),
        "mechanical_residual": float(np.linalg.norm(bmap.T @ stress)),
        "entropy_residual": float(beta @ strain + heat_capacity*dt/temperature),
        "directional_fixed_T_schur_margin": float(response_curvature-g @ compliance @ g),
        "homogeneous_fixed_T_schur_margin": float(response_curvature-g @ np.linalg.solve(k, g)),
        "homogeneous_gain_per_phi_response": homogeneous_gain,
        "homogeneous_strain": free_strain.tolist(),
        "homogeneous_incompatible_strain_norm": float(np.linalg.norm(free_strain-compatible_free)),
    }
