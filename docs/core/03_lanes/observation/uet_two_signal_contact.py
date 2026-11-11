"""Observation layer, wave O6: P4 with two different signal speeds, and a Bose-Hubbard quench as the case.

Thought experiment v3, P4: two records can be shared only through causal contact. Wave O2 found that the
earliest contact between two sites is through a common past, at t = d / (2 c) when both outgoing signals
travel at the same maximal speed c. This module generalises it to a pair emitted from one event with
different maximal speeds c_a and c_b (a doublon and a holon, for example):

    t_contact(d) = d / (c_a + c_b)                                  (closed form)

and checks the closed form by a direct search over the position of the common source. Equivalently the
front of correlations cannot move faster than c_a + c_b, the maximal relative group velocity of the pair.
The earlier, direct-contact-only reading of P4 would give t >= d / max(c_a, c_b), a front no faster than
max(c_a, c_b).

Case: quench of a one-dimensional Bose-Hubbard chain from a Mott insulator (Cheneau et al., Nature 481, 484
(2012)). In their effective model of doublon and holon quasiparticles (n <= 2 per site, first order in J/U),
with energies (units J = a_lat = hbar = 1)

    e_d(k) = -J cos k + 1/2 sqrt[(U - 6 J cos k)^2 + 32 J^2 sin^2 k]
    e_h(k) = +J cos k + 1/2 sqrt[(U - 6 J cos k)^2 + 32 J^2 sin^2 k]

a pair (doublon k, holon -k) is created on one site, and the maximal relative speed is
v_max = max_k d(e_d + e_h)/dk. These dispersions are the published model, inherited, not re-derived here;
the physics tests check the geometry, the limits U/J -> infinity (doublon 4, holon 2, pair 6) and the
published closed form v_max ~ 6 [1 - 16 J^2 / (9 U^2)].
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar


def contact_time(d: float, c_a: float, c_b: float) -> float:
    """Earliest time at which two sites a distance d apart can share a record through a common past."""
    return d / (c_a + c_b)


def contact_time_by_search(d: float, c_a: float, c_b: float) -> float:
    """Same quantity by brute force: minimise over the source position x_s in [0, d] the time
    max(x_s / c_a, (d - x_s) / c_b) needed for both signals to arrive."""
    res = minimize_scalar(lambda x: max(x / c_a, (d - x) / c_b), bounds=(0.0, d), method="bounded",
                          options={"xatol": 1e-13 * d})
    return float(res.fun)


def direct_contact_time(d: float, c_a: float, c_b: float) -> float:
    """Direct-contact-only reading: one site must lie in the past cone of the other."""
    return d / max(c_a, c_b)


def quasiparticle_energies(k: np.ndarray, u_over_j: float) -> tuple[np.ndarray, np.ndarray]:
    j = 1.0
    root = 0.5 * np.sqrt((u_over_j - 6 * j * np.cos(k)) ** 2 + 32 * j**2 * np.sin(k) ** 2)
    return -j * np.cos(k) + root, j * np.cos(k) + root


def _grid(samples: int) -> np.ndarray:
    return np.linspace(0.0, np.pi, samples)


def pair_front_velocity_bound(u_over_j: float, samples: int = 400_001) -> float:
    """v_max = max_k d(e_d + e_h)/dk, in units of J a_lat / hbar (Cheneau et al. 2012, Eq. 17)."""
    k = _grid(samples)
    e_d, e_h = quasiparticle_energies(k, u_over_j)
    return float(np.max(np.gradient(e_d + e_h, k)))


def single_signal_speeds(u_over_j: float, samples: int = 400_001) -> tuple[float, float]:
    """(max |de_d/dk|, max |de_h/dk|): the largest speed of any one quasiparticle."""
    k = _grid(samples)
    e_d, e_h = quasiparticle_energies(k, u_over_j)
    return float(np.max(np.abs(np.gradient(e_d, k)))), float(np.max(np.abs(np.gradient(e_h, k))))


def published_closed_form(u_over_j: float) -> float:
    """v_max ~ 6 [1 - 16 / (9 (U/J)^2)], the large-U/J expression quoted in the source."""
    return 6.0 * (1.0 - 16.0 / (9.0 * u_over_j**2))
