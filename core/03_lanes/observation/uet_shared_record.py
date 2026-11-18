"""Observation layer, wave O2: a shared record needs causal contact (thought experiment v3, P4).

Model: an open harmonic chain of N oscillators with nearest-neighbour coupling,

    H = sum_i [ p_i^2/2 + w0^2 x_i^2/2 ] + (kappa/2) sum_i (x_i - x_{i+1})^2 .

Dispersion w(q)^2 = w0^2 + 4 kappa sin^2(q/2); group velocity v_g = kappa sin q / w(q) <= sqrt(kappa) cos(q/2),
so every signal travels at most at c = sqrt(kappa). The initial state is a PRODUCT of thermal states of the
uncoupled oscillators: no site holds any information about any other at t = 0, I(A:B) = 0.

For classical Gaussian states the shared record of two sites A and B is the mutual information

    I(A:B) = S(A) + S(B) - S(AB),   S = 1/2 ln det(2 pi e C)   (nats).

Two sites can share a record only through causal contact: either one lies in the other's past cone
(direct contact, t >= d/c) or their past cones overlap (a common source, t >= d/(2c)). The second
condition is the earlier one, so  t_contact = d / (2 c).  Outside it the mutual information is
super-exponentially small (the linear dynamics has no exactly sharp front, a Lieb-Robinson-type tail).
"""

from __future__ import annotations

from math import pi, sqrt

import numpy as np
from scipy.linalg import expm


def chain_generator(n_sites: int, kappa: float, w0: float) -> np.ndarray:
    """Matrix A of z' = A z for z = (x_1..x_N, p_1..p_N); open boundaries."""

    k = np.zeros((n_sites, n_sites))
    k[np.diag_indices(n_sites)] = w0**2
    for i in range(n_sites - 1):
        k[i, i] += kappa
        k[i + 1, i + 1] += kappa
        k[i, i + 1] -= kappa
        k[i + 1, i] -= kappa
    a = np.zeros((2 * n_sites, 2 * n_sites))
    a[:n_sites, n_sites:] = np.eye(n_sites)
    a[n_sites:, :n_sites] = -k
    return a


def max_group_velocity(kappa: float, w0: float, samples: int = 200001) -> float:
    q = np.linspace(1e-6, pi, samples)  # q = 0 is 0/0 when w0 = 0; the limit there is sqrt(kappa)
    omega = np.sqrt(w0**2 + 4.0 * kappa * np.sin(q / 2.0) ** 2)
    return float(np.max(kappa * np.sin(q) / omega))


def signal_speed_bound(kappa: float) -> float:
    """c = sqrt(kappa): sup of the group velocity over all w0 >= 0."""

    return sqrt(kappa)


def product_thermal_covariance(n_sites: int, w0: float, temperature: float) -> np.ndarray:
    var_x = np.full(n_sites, temperature / w0**2)
    var_p = np.full(n_sites, temperature)
    return np.diag(np.concatenate([var_x, var_p]))


def evolve_covariance(generator: np.ndarray, covariance: np.ndarray, time: float) -> np.ndarray:
    m = expm(generator * time)
    return m @ covariance @ m.T


def _entropy(sub: np.ndarray) -> float:
    sign, logdet = np.linalg.slogdet(2.0 * pi * np.e * sub)
    if sign <= 0:
        raise ValueError("covariance is not positive definite")
    return 0.5 * logdet


def mutual_information(covariance: np.ndarray, site_a: int, site_b: int, n_sites: int) -> float:
    a = [site_a, n_sites + site_a]
    b = [site_b, n_sites + site_b]
    ab = a + b
    return (_entropy(covariance[np.ix_(a, a)]) + _entropy(covariance[np.ix_(b, b)])
            - _entropy(covariance[np.ix_(ab, ab)]))


def contact_time(distance: float, speed: float) -> float:
    """Earliest time two sites a distance apart can share a record: overlap of past cones."""

    return distance / (2.0 * speed)
