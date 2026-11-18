"""Observation layer, wave O8: the rest of the Lorentz transformation, Michelson-Morley and Kennedy-Thorndike.

T013 (wave O7) tested time dilation through the Ives-Stilwell observable. The other parts of the Lorentz
transformation, length contraction along and across the motion, are tested by the isotropy of the
two-way speed of light (Michelson-Morley) and its independence of the laboratory velocity
(Kennedy-Thorndike).

Kinematic test theory (Robertson; Mansouri and Sexl). In a preferred frame Sigma light moves isotropically
with speed 1. A laboratory S moves at speed v along x. Clocks at rest in S tick at rate a(v) relative to
Sigma time; rods at rest in S have length 1/b(v) along the motion and 1/d(v) across it, measured in Sigma:

    a = 1 + alpha v^2,   b = 1 + beta v^2,   d = 1 + delta v^2   (to order v^2).

No formula for the light speed is assumed here. two_way_light_speed() sends light out and back along a
rod of proper length L at angle theta in S, solves the two light-travel times in Sigma exactly, and
converts the round-trip time to the laboratory clock. To order v^2 the result is

    c_S(theta) = 1 - v^2 [ (beta - delta - 1/2) sin^2 theta + (alpha - beta + 1) ],

so P_MM = beta - delta - 1/2 is the orientation dependence and P_KT = alpha - beta + 1 the velocity
dependence. Published papers write these combinations with different sign conventions; every
convention is zero for the Lorentz transformation.

The parent action (Theory Card UET_PARENT v1) is generally covariant, so its local frame is Lorentzian:
the boost of uet_lorentz_time.py gives a = 1/gamma (moving clock), b = gamma (the boost of x' = gamma
(x - v t)), d = 1 (a boost along x leaves y unchanged). Then c_S = 1 exactly for every v and theta.

Controls (must not pass): absolute time with rigid rods (a = b = d = 1, Galilean) gives P_MM = -1/2 and
P_KT = 1; Lorentz-FitzGerald contraction without time dilation (a = 1, b = gamma, d = 1) gives P_MM = 0
but P_KT = 1/2, so it passes Michelson-Morley and fails Kennedy-Thorndike.
"""

from __future__ import annotations

from math import cos, sin, sqrt
from typing import Callable

import numpy as np

Kinematics = Callable[[float], tuple[float, float, float]]


def _one_way_time(lx: float, ly: float, v: float, sign: int) -> float:
    """Sigma time for light to cross a rod vector (lx, ly) whose far end moves at v along x.

    Outbound (sign = +1): |(lx + v t, ly)| = t.  Return (sign = -1): |(lx - v t, ly)| = t.
    Solved exactly: (1 - v^2) t^2 - 2 sign v lx t - (lx^2 + ly^2) = 0, positive root.
    """
    a = 1.0 - v * v
    b = -2.0 * sign * v * lx
    c = -(lx * lx + ly * ly)
    return (-b + sqrt(b * b - 4.0 * a * c)) / (2.0 * a)


def two_way_light_speed(v: float, theta: float, kinematics: Kinematics, length: float = 1.0) -> float:
    """Two-way speed of light in the laboratory for a rod of proper length `length` at angle theta."""
    a, b, d = kinematics(v)
    lx = length * cos(theta) / b
    ly = length * sin(theta) / d
    t_sigma = _one_way_time(lx, ly, v, +1) + _one_way_time(lx, ly, v, -1)
    t_lab = a * t_sigma
    return 2.0 * length / t_lab


def lorentz_from_boost(v: float) -> tuple[float, float, float]:
    """a, b, d read off the boost matrix of the parent action's local frame (uet_lorentz_time.boost_matrix).

    Clock at rest in S at x' = 0, i.e. x = v t:  t' = gamma (t - v x) = t / gamma, so a = 1/gamma.
    Rod at rest in S: x' = gamma (x - v t), so a Sigma length dx at fixed t is gamma dx in S: b = gamma.
    A boost along x does not act on y: d = 1.
    """
    g = 1.0 / sqrt(1.0 - v * v)
    boost = np.array([[g, -g * v], [-g * v, g]])
    # Clock worldline (t, x) = (1, v): its S time per unit Sigma time is the first row of the boost.
    a = float(boost[0] @ np.array([1.0, v]))
    # Rod: Sigma separation (0, dx) at fixed Sigma time has S length boost[1, 1] * dx.
    b = float(boost[1] @ np.array([0.0, 1.0]))
    return a, b, 1.0


def galilean(v: float) -> tuple[float, float, float]:
    """Absolute time and rigid rods."""
    return 1.0, 1.0, 1.0


def contraction_only(v: float) -> tuple[float, float, float]:
    """Lorentz-FitzGerald contraction without time dilation."""
    return 1.0, 1.0 / sqrt(1.0 - v * v), 1.0


def rms_combinations(kinematics: Kinematics, v: float = 1e-3) -> dict[str, float]:
    """Fit 1 - c_S(theta) = v^2 [P_MM sin^2 theta + P_KT] at small v from the exact light-travel times."""
    thetas = np.linspace(0.0, np.pi, 13)
    y = np.array([1.0 - two_way_light_speed(v, th, kinematics) for th in thetas]) / (v * v)
    design = np.column_stack([np.sin(thetas) ** 2, np.ones_like(thetas)])
    (p_mm, p_kt), *_ = np.linalg.lstsq(design, y, rcond=None)
    a, b, d = kinematics(v)
    return {"P_MM": float(p_mm), "P_KT": float(p_kt),
            "alpha": (a - 1.0) / v**2, "beta": (b - 1.0) / v**2, "delta": (d - 1.0) / v**2}
