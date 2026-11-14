"""Observation layer, wave O1: delayed observation and the gap between record and present.

Thought experiment v3 (docs/core/THOUGHT_EXPERIMENT.md), principles P1 and P2:

    P1  y(t_o) = O[X_s(t_e)] + eta,  t_e solves  t_e + |x_o - x_s(t_e)| / u = t_o
    P2  Delta(t_o) = X_s(t_o) - X_s(t_e)  ~  dX_s/dt * a,   a = t_o - t_e >= tau = r/u

The retarded time is found by a bracketed root search (general code path). An independent
closed form for uniform motion (a quadratic in t_e) serves as the reference. A source whose
speed is below the signal speed u has a unique, monotone solution because
d/dt_e [t_e + |x_o - x_s|/u] = 1 - v_radial/u > 0.

Units: arbitrary but consistent (u is the signal speed, e.g. c = 1).
"""

from __future__ import annotations

from math import sqrt
from typing import Callable

import numpy as np
from scipy.optimize import brentq

Position = Callable[[float], np.ndarray]


def retarded_time(t_obs: float, x_obs, source_position: Position, signal_speed: float, source_speed_bound: float) -> float:
    """Emission time t_e of the signal received at ``t_obs`` at ``x_obs``.

    ``source_speed_bound`` must be below ``signal_speed`` (no signal can be outrun).
    """

    if not (0.0 <= source_speed_bound < signal_speed):
        raise ValueError("source speed bound must satisfy 0 <= v_max < u")
    x_obs = np.asarray(x_obs, dtype=float)

    def residual(t_e: float) -> float:
        return t_e + float(np.linalg.norm(x_obs - np.asarray(source_position(t_e), dtype=float))) / signal_speed - t_obs

    distance_now = float(np.linalg.norm(x_obs - np.asarray(source_position(t_obs), dtype=float)))
    low = t_obs - distance_now / (signal_speed - source_speed_bound) - 1.0  # residual(low) < 0 by the speed bound
    return brentq(residual, low, t_obs, xtol=1e-14, rtol=1e-14, maxiter=200)


def retarded_time_uniform_motion(t_obs: float, x_obs, x0, velocity, signal_speed: float) -> float:
    """Closed form for x_s(t) = x0 + v t: |x0 - x_obs + v t_e| = u (t_obs - t_e), earlier root."""

    r0 = np.asarray(x0, dtype=float) - np.asarray(x_obs, dtype=float)
    v = np.asarray(velocity, dtype=float)
    u = signal_speed
    # |r0 + v t|^2 = u^2 (T - t)^2  ->  (v.v - u^2) t^2 + 2 (r0.v + u^2 T) t + (r0.r0 - u^2 T^2) = 0
    a = float(v @ v) - u * u
    b = 2.0 * (float(r0 @ v) + u * u * t_obs)
    c = float(r0 @ r0) - u * u * t_obs * t_obs
    if abs(a) < 1e-300:
        return -c / b
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        raise ValueError("no real retarded time")
    roots = [(-b + s * sqrt(disc)) / (2.0 * a) for s in (+1.0, -1.0)]
    valid = [t for t in roots if t <= t_obs + 1e-12 and t_obs - t >= 0.0]
    return min(valid, key=lambda t: abs(t_obs - t - np.linalg.norm(r0 + v * t) / u))


def record_age(t_obs: float, t_emit: float) -> float:
    return t_obs - t_emit


def gap(t_obs: float, t_emit: float, state: Callable[[float], np.ndarray]) -> np.ndarray:
    """Delta = X_s(t_o) - X_s(t_e): the error of treating the record as the present."""

    return np.asarray(state(t_obs), dtype=float) - np.asarray(state(t_emit), dtype=float)


def first_order_gap(rate_at_emission, age: float) -> np.ndarray:
    """P2 at first order: Delta ~ dX/dt(t_e) * a."""

    return np.asarray(rate_at_emission, dtype=float) * age
