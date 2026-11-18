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

from typing import Callable

import mpmath as mp

Kinematics = Callable[[object], tuple[object, object, object]]

# All arithmetic runs in mpmath at this precision. The combinations are differences of order v^2 from 1;
# in 64-bit floats the rounding of c_S (about 1e-16) divided by v^2 swamped the 1e-12 precision of the
# Michelson-Morley data (T022 first run, 2026-11-18). 60 digits keep the model error far below the data.
DPS = 60


def _one_way_time(lx, ly, v, sign: int):
    """Sigma time for light to cross a rod vector (lx, ly) whose far end moves at v along x.

    Outbound (sign = +1): |(lx + v t, ly)| = t.  Return (sign = -1): |(lx - v t, ly)| = t.
    Solved exactly: (1 - v^2) t^2 - 2 sign v lx t - (lx^2 + ly^2) = 0, positive root.
    """
    a = 1 - v * v
    b = -2 * sign * v * lx
    c = -(lx * lx + ly * ly)
    return (-b + mp.sqrt(b * b - 4 * a * c)) / (2 * a)


def two_way_light_speed(v, theta, kinematics: Kinematics, length=1):
    """Two-way speed of light in the laboratory for a rod of proper length `length` at angle theta."""
    with mp.workdps(DPS):
        v, theta, length = mp.mpf(v), mp.mpf(theta), mp.mpf(length)
        a, b, d = kinematics(v)
        lx = length * mp.cos(theta) / b
        ly = length * mp.sin(theta) / d
        t_sigma = _one_way_time(lx, ly, v, +1) + _one_way_time(lx, ly, v, -1)
        return 2 * length / (a * t_sigma)


def boost_matrix(v):
    """Boost of the parent action's local frame, the same matrix as uet_lorentz_time.boost_matrix (c = 1)."""
    g = 1 / mp.sqrt(1 - v * v)
    return mp.matrix([[g, -g * v], [-g * v, g]])


def lorentz_from_boost(v):
    """a, b, d read off the boost matrix.

    Clock at rest in S, worldline (t, x) = (1, v) per unit Sigma time: its S time is the first row of the
    boost applied to (1, v), which is 1/gamma. Rod at rest in S: a Sigma separation (0, dx) at fixed Sigma
    time has S length boost[1, 1] dx = gamma dx. A boost along x does not act on y: d = 1.
    """
    m = boost_matrix(v)
    a = m[0, 0] * 1 + m[0, 1] * v
    b = m[1, 0] * 0 + m[1, 1] * 1
    return a, b, mp.mpf(1)


def galilean(v):
    """Absolute time and rigid rods."""
    return mp.mpf(1), mp.mpf(1), mp.mpf(1)


def contraction_only(v):
    """Lorentz-FitzGerald contraction without time dilation."""
    return mp.mpf(1), 1 / mp.sqrt(1 - v * v), mp.mpf(1)


def rms_combinations(kinematics: Kinematics, v="1e-6") -> dict[str, float]:
    """1 - c_S(theta) = v^2 [P_MM sin^2 theta + P_KT] at small v, from the exact light-travel times.

    P_KT from theta = 0, P_MM + P_KT from theta = pi/2; theta = pi/4 is reported as a check of the
    sin^2 form (residual_quarter). Higher orders enter at relative size v^2.
    """
    with mp.workdps(DPS):
        v = mp.mpf(v)
        y = {th: (1 - two_way_light_speed(v, th, kinematics)) / (v * v) for th in (0, mp.pi / 4, mp.pi / 2)}
        p_kt = y[0]
        p_mm = y[mp.pi / 2] - p_kt
        resid = y[mp.pi / 4] - (p_mm / 2 + p_kt)
        a, b, d = kinematics(v)
        return {"P_MM": float(p_mm), "P_KT": float(p_kt), "residual_quarter": float(resid),
                "alpha": float((a - 1) / v**2), "beta": float((b - 1) / v**2), "delta": float((d - 1) / v**2)}
