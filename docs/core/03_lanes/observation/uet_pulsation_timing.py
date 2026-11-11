"""Observation layer, wave O5: P2 applied to a pulsating star in a binary orbit.

A star that pulsates with phase phi(t) = nu t moves on a Kepler orbit. By P1 the observer receives
the phase emitted at the retarded time; by P2 the gap between the received phase and a fixed-distance
reference is the rate nu times the extra record age. The extra age is the light-travel time across
the orbit, the time delay

    tau(t) = -(a1 sin i / c) (1 - e^2) / (1 + e cos f) sin(f + varpi)       (Murphy et al. 2016, eq. 2)

and the same orbit gives the line-of-sight velocity measured by spectroscopy

    v_r(t) = K1 [cos(f + varpi) + e cos varpi],   K1 = 2 pi a1 sin i / (P sqrt(1 - e^2)).

Identity linking the two observables: d tau / dt = -v_r / c. So the delay amplitude predicted from an
RV-only orbit is a1 sin i / c = K1 P sqrt(1 - e^2) / (2 pi c). A world without retarded observation
(signals that arrive instantly) would show tau = 0 whatever the orbit.

Units: time in the caller's unit, c given explicitly.
"""

from __future__ import annotations

from math import pi, sqrt

import numpy as np
from scipy.optimize import brentq

C_KM_S = 299_792.458


def eccentric_anomaly(mean_anomaly: float, e: float) -> float:
    """Solve Kepler's equation E - e sin E = M by bracketed root search (0 <= e < 1)."""
    m = (mean_anomaly + pi) % (2 * pi) - pi
    return brentq(lambda x: x - e * np.sin(x) - m, -pi - 1.0, pi + 1.0, xtol=1e-14)


def true_anomaly(t: float, period: float, t_peri: float, e: float) -> float:
    big_e = eccentric_anomaly(2 * pi * (t - t_peri) / period, e)
    return 2.0 * np.arctan2(sqrt(1 + e) * np.sin(big_e / 2), sqrt(1 - e) * np.cos(big_e / 2))


def line_of_sight_position(t: float, period: float, t_peri: float, e: float, varpi: float, a_sini: float) -> float:
    """z(t) = r sin(f + varpi) sin i, positive away from the observer."""
    f = true_anomaly(t, period, t_peri, e)
    return a_sini * (1 - e * e) / (1 + e * np.cos(f)) * np.sin(f + varpi)


def time_delay(t: float, period: float, t_peri: float, e: float, varpi: float, a_sini_over_c: float) -> float:
    """tau(t) of Murphy et al. (2016) eq. 2, the sign convention of that paper."""
    return -line_of_sight_position(t, period, t_peri, e, varpi, a_sini_over_c)


def radial_velocity(t: float, period: float, t_peri: float, e: float, varpi: float, a_sini: float) -> float:
    k1 = 2 * pi * a_sini / (period * sqrt(1 - e * e))
    f = true_anomaly(t, period, t_peri, e)
    return k1 * (np.cos(f + varpi) + e * np.cos(varpi))


def a_sini_over_c_from_rv(k1: float, period: float, e: float, c: float = C_KM_S) -> float:
    """Delay amplitude implied by an RV-only orbit: K1 P sqrt(1 - e^2) / (2 pi c)."""
    return k1 * period * sqrt(1 - e * e) / (2 * pi * c)


def delay_half_range(e: float, varpi: float, a_sini_over_c: float) -> float:
    """(max tau - min tau) / 2 = a1 sin i / c * sqrt(1 - e^2 cos^2 varpi) (closed form)."""
    return a_sini_over_c * sqrt(1 - (e * np.cos(varpi)) ** 2)
