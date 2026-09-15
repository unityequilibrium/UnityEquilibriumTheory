"""Conditional quadratic G/r material-response lane, not physical calibration."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from docs.core.uet_dynamic_thermoelastic_response import DynamicMaterialMode, _vector


@dataclass(frozen=True)
class ReciprocalThermalMode:
    material: DynamicMaterialMode
    matrix: np.ndarray
    metric: np.ndarray
    heat_port: np.ndarray
    force_port: np.ndarray
    dissipation_metric: np.ndarray
    entropy_phi: float
    response_kinetic: float
    response_curvature_q: float
    response_damping: float
    schur_margin: float

    @property
    def phi_index(self):
        return len(self.material.matrix)

    @property
    def pi_index(self):
        return self.phi_index+1

    def initial_state(self, entropy, *, phi=0., pi=0., strain=None,
                      strain_rate=None, flux=0.):
        if not np.isfinite([entropy, phi, pi]).all():
            raise ValueError("finite entropy and response initial state required")
        base = self.material.initial_state(entropy-self.entropy_phi*phi,
                                           strain, strain_rate, flux)
        return np.r_[base, phi, pi]

    def entropy(self, state):
        x = _vector(state, len(self.matrix))
        m = self.material
        return float(m.thermal_stress@x[:3]+m.heat_capacity*x[6]/m.temperature
                     +self.entropy_phi*x[self.phi_index])

    def balance(self, state, *, heat=0., force=0.):
        x = _vector(state, len(self.matrix))
        if not np.isfinite([heat, force]).all():
            raise ValueError("finite external ports required")
        dx = self.matrix@x+self.heat_port*heat+self.force_port*force
        m = self.material
        power = x[6]*heat/m.temperature+x[self.pi_index]*force
        loss = float(x@self.dissipation_metric@x)
        flux = x[7] if m.relaxation > 0 else m.conductivity*m.q*x[6]
        entropy_rate = self.entropy(dx)
        return dict(availability=float(x@self.metric@x/2),
                    availability_rate=float(x@self.metric@dx),
                    external_power=float(power), dissipation=loss,
                    entropy_production_budget=loss/m.temperature,
                    balance_residual=float(x@self.metric@dx-power+loss),
                    linear_entropy_residual=float(entropy_rate-(heat-m.q*flux)/m.temperature))

    def evolve_constant(self, times, initial, *, heat=0., force=0.):
        times = np.asarray(times, dtype=float)
        if times.ndim != 1 or not np.isfinite(times).all() or np.any(times < 0):
            raise ValueError("finite nonnegative times required")
        if not np.isfinite([heat, force]).all():
            raise ValueError("finite external ports required")
        size = len(self.matrix)
        x = _vector(initial, size)
        augmented = np.zeros((size+1, size+1))
        augmented[:size, :size] = self.matrix
        augmented[:size, size] = self.heat_port*heat+self.force_port*force
        return np.array([(expm(augmented*t)@np.r_[x, 1.])[:size] for t in times]).reshape((-1, size))

    def laplace_transfer(self, s):
        """Independent 2x2 elimination, outputs (theta,phi), inputs (Q,f)."""
        m = self.material
        if not np.isfinite(s):
            raise ValueError("finite frequency required")
        if 1+m.relaxation*s == 0:
            raise np.linalg.LinAlgError("singular flux elimination; use full resolvent")
        d = m.acoustic+m.rho*s*s/m.q**2*np.eye(3)
        db = np.linalg.solve(d, m.thermal_stress)
        dh = np.linalg.solve(d, m.coupling)
        h = m.thermal_stress@dh-self.entropy_phi
        u = (m.heat_capacity*s+m.conductivity*m.q**2/(1+m.relaxation*s)
             +m.temperature*s*(m.thermal_stress@db))
        v = (self.response_kinetic*s*s+self.response_damping*s
             +self.response_curvature_q-m.coupling@dh)
        return np.linalg.solve(np.array([[u, -m.temperature*s*h], [h, v]]), np.eye(2))


def reciprocal_mode(material: DynamicMaterialMode, *, entropy_phi: float,
                    response_kinetic: float, response_curvature: float,
                    response_gradient: float, response_damping: float) -> ReciprocalThermalMode:
    """Extend, never mutate, the prescribed-Phi material comparator.

    All inputs are declared total local coefficients, not automatically
    identified with physical UET/material parameters. No noise is supplied.
    """
    values = [entropy_phi, response_kinetic, response_curvature,
              response_gradient, response_damping]
    if not np.isfinite(values).all() or response_kinetic <= 0:
        raise ValueError("finite coefficients and positive response kinetic required")
    if response_gradient < 0 or response_damping < 0:
        raise ValueError("nonnegative gradient and damping required")
    m = material
    a_q = response_curvature+response_gradient*m.q*m.q
    schur = float(a_q-m.coupling@np.linalg.solve(m.acoustic, m.coupling))
    if schur <= 0:
        raise ValueError("nonpositive coupled availability Schur margin; no stabilization applied")
    n = len(m.matrix)
    phi, pi = n, n+1
    matrix, metric, loss = (np.zeros((n+2, n+2)) for _ in range(3))
    matrix[:n, :n], metric[:n, :n] = m.matrix, m.metric
    matrix[:n, phi] = m.phi_port
    matrix[6, pi] = -m.temperature*entropy_phi/m.heat_capacity
    matrix[phi, pi] = 1.
    matrix[pi, :3] = -m.coupling/response_kinetic
    matrix[pi, 6] = entropy_phi/response_kinetic
    matrix[pi, phi] = -a_q/response_kinetic
    matrix[pi, pi] = -response_damping/response_kinetic
    metric[:3, phi] = metric[phi, :3] = m.coupling
    metric[phi, phi], metric[pi, pi] = a_q, response_kinetic
    if m.relaxation > 0:
        loss[7, 7] = 1/(m.temperature*m.conductivity)
    else:
        loss[6, 6] = m.conductivity*m.q*m.q/m.temperature
    loss[pi, pi] = response_damping
    heat_port, force_port = np.zeros(n+2), np.zeros(n+2)
    heat_port[:n], force_port[pi] = m.heat_port, 1/response_kinetic
    return ReciprocalThermalMode(m, matrix, metric, heat_port, force_port, loss,
                                 entropy_phi, response_kinetic, a_q, response_damping, schur)
