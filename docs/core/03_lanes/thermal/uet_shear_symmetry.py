"""Conditional E2g selection rules, not identification of UET matter."""

import numpy as np


def rotation(angle):
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle), np.cos(angle)]])


def e2_group():
    reflection = np.diag([1., -1.])
    return [rotation(2*k*np.pi/3) @ parity
            for k in range(6) for parity in (np.eye(2), reflection)]


def constraints():
    group = e2_group()
    symmetric_basis = [np.diag([1., 0.]), np.diag([0., 1.]),
                       np.array([[0., 1.], [1., 0.]])/np.sqrt(2)]
    linear = np.vstack([g.T-np.eye(2) for g in group])
    quadratic = np.vstack([np.column_stack([(g.T @ h @ g-h).ravel()
                                            for h in symmetric_basis]) for g in group])
    return linear, quadratic


def pump_doublet(field):
    """Real, in-plane linear polarization only; no Raman coefficient supplied."""
    field = np.asarray(field, dtype=float)
    if field.shape != (2,) or not np.isfinite(field).all():
        raise ValueError('finite real in-plane field required')
    x, y = field
    return np.array([x*x-y*y, 2*x*y])
