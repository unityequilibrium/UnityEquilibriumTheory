"""Observation layer, wave O7: P3, relativity of simultaneity, and the Ives-Stilwell observable.

Thought experiment v3, P3: the "now" of a distant event has no definition that all observers share. In
the parent action (a generally covariant scalar-tensor theory, Theory Card UET_PARENT v1) the local
frame is Lorentzian, so two inertial observers are related by a boost (c = 1):

    t' = gamma (t - beta x),   x' = gamma (x - beta t).

Two events simultaneous in S (dt = 0) are separated by dt' = -gamma beta dx in S': the offset of
"now" grows with distance and with relative velocity (P3).

Ives-Stilwell observable. A two-level system moves with speed beta through a laboratory. A laser beam
of lab frequency nu travelling along (parallel) or against (antiparallel) the motion is resonant when
its frequency in the atom's rest frame equals nu_0. The rest-frame frequency comes from boosting the
photon four-vector (omega, k) = nu (1, +-1); no formula is assumed:

    nu_p resonant (parallel):      boost(nu_p, +nu_p)  -> nu_0
    nu_a resonant (antiparallel):  boost(nu_a, -nu_a)  -> nu_0.

The product nu_a nu_p / nu_0^2 is then exactly 1 for every beta (the boost is a hyperbolic rotation).
Alternatives that lose relative simultaneity and time dilation (absolute time, Galilean Doppler shift
omega' = omega (1 -+ beta)) give 1 / (1 - beta^2) instead, so epsilon = sqrt(nu_a nu_p / nu_0^2) - 1 is
gamma - 1 ~ beta^2 / 2 there and zero in the Lorentzian case.
"""

from __future__ import annotations

from math import sqrt

import numpy as np
from scipy.optimize import brentq


def gamma(beta: float) -> float:
    return 1.0 / sqrt(1.0 - beta * beta)


def boost_matrix(beta: float) -> np.ndarray:
    g = gamma(beta)
    return np.array([[g, -g * beta], [-g * beta, g]])


def simultaneity_offset(beta: float, dx: float) -> float:
    """dt' for two events with dt = 0 and separation dx, from the boost matrix."""
    return float((boost_matrix(beta) @ np.array([0.0, dx]))[0])


def rest_frame_frequency(nu_lab: float, beta: float, direction: int) -> float:
    """Frequency of a photon (nu, direction * nu) in the frame moving at +beta, by boosting its four-vector."""
    return float((boost_matrix(beta) @ np.array([nu_lab, direction * nu_lab]))[0])


def galilean_rest_frame_frequency(nu_lab: float, beta: float, direction: int) -> float:
    """Absolute-time Doppler shift: nu' = nu (1 - direction beta). No time dilation, no relativity of simultaneity."""
    return nu_lab * (1.0 - direction * beta)


def resonant_laser_frequency(nu_0: float, beta: float, direction: int, shift=rest_frame_frequency) -> float:
    return brentq(lambda nu: shift(nu, beta, direction) - nu_0, 0.01 * nu_0, 100.0 * nu_0, xtol=1e-14 * nu_0, rtol=1e-15)


def ives_stilwell_epsilon(beta: float, shift=rest_frame_frequency, nu_0: float = 1.0) -> float:
    """epsilon = sqrt(nu_a nu_p / nu_0^2) - 1 with the resonant laser frequencies found by root search."""
    nu_p = resonant_laser_frequency(nu_0, beta, +1, shift)
    nu_a = resonant_laser_frequency(nu_0, beta, -1, shift)
    return sqrt(nu_a * nu_p / nu_0**2) - 1.0
