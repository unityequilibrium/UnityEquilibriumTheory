"""Linear bulk material comparator, not a fitted or self-consistent UET model."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from docs.core.uet_thermoelastic_spatial_compatibility import strain_map


@dataclass(frozen=True)
class DynamicMaterialMode:
    matrix: np.ndarray
    phi_port: np.ndarray
    heat_port: np.ndarray
    metric: np.ndarray
    acoustic: np.ndarray
    thermal_stress: np.ndarray
    coupling: np.ndarray
    q: float
    rho: float
    temperature: float
    heat_capacity: float
    conductivity: float
    relaxation: float

    def initial_state(self, entropy: float, strain=None, strain_rate=None,
                      flux: float = 0.) -> np.ndarray:
        if not np.isfinite([entropy, flux]).all():
            raise ValueError("finite entropy/flux required")
        v = np.zeros(3) if strain is None else _vector(strain, 3)
        w = np.zeros(3) if strain_rate is None else _vector(strain_rate, 3)
        x = np.zeros(len(self.matrix))
        x[:3], x[3:6] = v, w
        x[6] = self.temperature*(entropy-self.thermal_stress@v)/self.heat_capacity
        if self.relaxation > 0:
            x[7] = flux
        elif flux != 0:
            raise ValueError("Fourier flux is constitutive, not an independent initial state")
        return x

    def evolve_constant(self, times, initial, phi: float = 0., heat: float = 0.) -> np.ndarray:
        times = np.asarray(times, dtype=float)
        if times.ndim != 1 or not np.isfinite(times).all() or np.any(times < 0):
            raise ValueError("finite nonnegative sample times required")
        if not np.isfinite([phi, heat]).all():
            raise ValueError("finite external sources required")
        size = len(self.matrix)
        x = _vector(initial, size)
        augmented = np.zeros((size+1, size+1))
        augmented[:size, :size] = self.matrix
        augmented[:size, size] = self.phi_port*phi+self.heat_port*heat
        return np.array([(expm(augmented*t) @ np.r_[x, 1.])[:size] for t in times]).reshape((-1, size))

    def laplace_transfer(self, s: complex) -> np.ndarray:
        """Independent displacement elimination; raises at a singular subblock."""
        if not np.isfinite(s):
            raise ValueError("finite Laplace frequency required")
        if 1+self.relaxation*s == 0:
            raise np.linalg.LinAlgError("flux elimination is singular; use the full state resolvent")
        d = self.acoustic+self.rho*s*s/self.q**2*np.eye(3)
        db = np.linalg.solve(d, self.thermal_stress)
        dh = np.linalg.solve(d, self.coupling)
        denominator = (self.heat_capacity*s
                       + self.conductivity*self.q**2/(1+self.relaxation*s)
                       + self.temperature*s*(self.thermal_stress@db))
        if denominator == 0:
            raise np.linalg.LinAlgError("zero transfer denominator; no pole regularization is applied")
        return np.array([self.temperature*s*(self.thermal_stress@dh), 1.])/denominator

    def balance(self, state, phi: float = 0., heat: float = 0.) -> dict:
        x = _vector(state, len(self.matrix))
        if not np.isfinite([phi, heat]).all():
            raise ValueError("finite external sources required")
        dx = self.matrix@x+self.phi_port*phi+self.heat_port*heat
        power = -phi*(self.coupling@x[3:6])+x[6]*heat/self.temperature
        if self.relaxation > 0:
            dissipation = x[7]**2/(self.temperature*self.conductivity)
        else:
            dissipation = self.conductivity*self.q**2*x[6]**2/self.temperature
        return {"availability": float(x@self.metric@x/2),
                "availability_rate": float(x@self.metric@dx),
                "external_power": float(power), "dissipation": float(dissipation),
                "balance_residual": float(x@self.metric@dx-power+dissipation)}


def _vector(value, size):
    x = np.asarray(value, dtype=float)
    if x.shape != (size,) or not np.isfinite(x).all():
        raise ValueError(f"finite length-{size} vector required")
    return x


def material_mode(*, stiffness, expansion, coupling, direction, q: float,
                  rho: float, temperature: float, heat_capacity: float,
                  conductivity: float, relaxation: float) -> DynamicMaterialMode:
    """Conductivity is the supplied directional n.k_tensor.n, not a UET output.

    tau=0 assembles Fourier directly; tau>0 requires positive conductivity.
    Phi is an external force port. A full coupled model needs its reciprocal
    equation and independent coefficient/initialization provenance.
    """
    parameters = [q, rho, temperature, heat_capacity, conductivity, relaxation]
    if not np.isfinite(parameters).all() or min(q, rho, temperature, heat_capacity) <= 0:
        raise ValueError("finite positive q, rho, T and heat capacity required")
    if conductivity < 0 or relaxation < 0 or (relaxation > 0 and conductivity == 0):
        raise ValueError("nonnegative k/tau; Cattaneo requires k>0")
    k = np.asarray(stiffness, dtype=float)
    if k.shape != (6, 6) or not np.isfinite(k).all():
        raise ValueError("finite 6x6 Mandel stiffness required")
    scale = float(np.max(np.abs(k)))
    if scale == 0 or np.max(np.abs(k-k.T)) > 1e-12*scale:
        raise ValueError("symmetric positive stiffness required")
    if np.min(np.linalg.eigvalsh(k/scale)) <= 0:
        raise ValueError("positive definite stiffness required")
    bmap = strain_map(direction)
    acoustic = bmap.T@k@bmap
    b = bmap.T@k@_vector(expansion, 6)
    h = bmap.T@_vector(coupling, 6)
    size = 8 if relaxation > 0 else 7
    matrix, metric = np.zeros((size, size)), np.zeros((size, size))
    matrix[:3, 3:6] = np.eye(3)
    matrix[3:6, :3] = -q*q/rho*acoustic
    matrix[3:6, 6] = q*q/rho*b
    matrix[6, 3:6] = -temperature/heat_capacity*b
    metric[:3, :3] = acoustic
    metric[3:6, 3:6] = rho/(q*q)*np.eye(3)
    metric[6, 6] = heat_capacity/temperature
    if relaxation > 0:
        matrix[6, 7] = -q/heat_capacity
        matrix[7, 6] = conductivity*q/relaxation
        matrix[7, 7] = -1/relaxation
        metric[7, 7] = relaxation/(temperature*conductivity)
    else:
        matrix[6, 6] = -conductivity*q*q/heat_capacity
    phi_port, heat_port = np.zeros(size), np.zeros(size)
    phi_port[3:6] = -q*q/rho*h
    heat_port[6] = 1/heat_capacity
    return DynamicMaterialMode(matrix, phi_port, heat_port, metric, acoustic, b, h,
                               q, rho, temperature, heat_capacity, conductivity, relaxation)
