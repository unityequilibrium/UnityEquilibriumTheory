"""Layer 2 -> 3, wave D18: does an orbiting body settle by itself where its motion no longer resists?

Question (author, 2026-11-24): a body does not just get pulled by a large mass; orbiting it is the point
where the motion is "not too damaging", a motion that does not resist; forced motion is temporary. Tidal
locking and orbit circularization are the measured cases (AI choice of example, see AUTHOR_PROPOSITION 4).

Model: a body of mass m and moment of inertia I spins at omega about the orbit normal and orbits a mass M
on a Kepler ellipse (a, e). In the body's own frame the tidal field of M is
    T_ij = G M (3 n_i n_j - delta_ij) / r^3,
and a deformable body is flexed at the rate dT/dt seen in its frame. For any linear body with a short
response delay (constant time lag, Darwin-Hut), the dissipated power is proportional to the orbit
average F = < |dT/dt|_body^2 > (Frobenius norm): F is the "resistance" of the motion [AI interpretation].

[AI derivation]
D18a Body-frame rate: dT/dt|_body = R^T (dT/dt - omega [J, T]) R with J the generator of rotation about z,
     so F = < |dT/dt - omega [J, T]|^2 > over one orbit (the norm does not see the rotation R).
D18b Circular orbit, spin mismatch Delta = n - omega: F = 18 (G M / a^3)^2 Delta^2.
D18c F = 0 if and only if e = 0 and omega = n (the field is then fixed in the body). With omega = n and
     small e the field's strength swings by 3 e (r^-3) and its direction librates by 2 e (f - M), so
         F = (27 + 36) (G M / a^3)^2 n^2 e^2 + O(e^4) = 63 (G M / a^3)^2 n^2 e^2 + O(e^4):
     a locked body on an ellipse still flexes.
D18d The same state is where the motion costs least: at fixed total angular momentum
         L = I omega + mu sqrt(G M_t a (1 - e^2)),   E = I omega^2 / 2 - G M m / (2 a),
     every stationary point has e = 0 and omega = n, and it is a minimum of E if and only if the orbital
     angular momentum exceeds three times the spin angular momentum, mu a^2 > 3 I (Darwin 1879, Hut 1980).
     Below that the no-flex state is a saddle: the system cannot settle there (it spirals in).

Consequence [AI interpretation]: "settling where the motion does not resist" has a measurable form: the
system sheds energy through flexing (F > 0) until F = 0, and that end state is the lowest-energy motion it
can reach with the angular momentum it has, if one exists. Nobody steers it there. Nearest known theory:
tidal evolution (Darwin, Hut, Zahn). Not UET-distinct.
"""

from __future__ import annotations

from math import pi, sqrt

import numpy as np
from scipy.optimize import brentq

G = 6.67430e-11
J_Z = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]])


def kepler_positions(a: float, e: float, M_t: float, N: int):
    """Positions on one orbit at N equally spaced times; returns (r_vec array, period)."""

    n = sqrt(G * M_t / a ** 3)
    Ms = 2.0 * pi * np.arange(N) / N
    E = Ms.copy() if e < 0.8 else np.full(N, pi)
    for _ in range(60):
        E = E - (E - e * np.sin(E) - Ms) / (1.0 - e * np.cos(E))
    x = a * (np.cos(E) - e)
    y = a * sqrt(1.0 - e * e) * np.sin(E)
    return np.stack([x, y, np.zeros(N)], axis=1), 2.0 * pi / n


def tidal_tensor(rv, M: float):
    r = np.linalg.norm(rv)
    nh = rv / r
    return G * M * (3.0 * np.outer(nh, nh) - np.eye(3)) / r ** 3


def flex_rate(a: float, e: float, omega: float, M: float, m: float, N: int = 256) -> float:
    """F = orbit average of |dT/dt|^2 in the body frame (spectral time derivative)."""

    pos, period = kepler_positions(a, e, M + m, N)
    T = np.array([tidal_tensor(p, M) for p in pos])
    k = 2.0 * pi * np.fft.fftfreq(N, d=period / N)
    dT = np.real(np.fft.ifft(1j * k[:, None, None] * np.fft.fft(T, axis=0), axis=0))
    comm = np.einsum("ij,tjk->tik", J_Z, T) - np.einsum("tij,jk->tik", T, J_Z)
    D = dT - omega * comm
    return float(np.mean(np.sum(D * D, axis=(1, 2))))


def flex_rate_circular(a: float, omega: float, M: float, m: float) -> float:
    n = sqrt(G * (M + m) / a ** 3)
    return 18.0 * (G * M / a ** 3) ** 2 * (n - omega) ** 2


def mean_motion(a: float, M_t: float) -> float:
    return sqrt(G * M_t / a ** 3)


def energy(I: float, omega: float, a: float, M: float, m: float) -> float:
    return 0.5 * I * omega ** 2 - G * M * m / (2.0 * a)


def angular_momentum(I: float, omega: float, a: float, e: float, M: float, m: float) -> float:
    mu = M * m / (M + m)
    return I * omega + mu * sqrt(G * (M + m) * a * (1.0 - e * e))


def energy_at_fixed_L(a: float, e: float, L: float, I: float, M: float, m: float) -> float:
    mu = M * m / (M + m)
    omega = (L - mu * sqrt(G * (M + m) * a * (1.0 - e * e))) / I
    return energy(I, omega, a, M, m)


def synchronous_states(L: float, I: float, M: float, m: float, a_lo: float, a_hi: float, n_grid: int = 4000):
    """Roots a of I n(a) + mu sqrt(G M_t a) = L (circular, omega = n), bracketed on a log grid."""

    mu, Mt = M * m / (M + m), M + m
    f = lambda a: I * mean_motion(a, Mt) + mu * sqrt(G * Mt * a) - L
    grid = np.geomspace(a_lo, a_hi, n_grid)
    vals = [f(x) for x in grid]
    roots = []
    for i in range(n_grid - 1):
        if vals[i] == 0.0 or vals[i] * vals[i + 1] < 0:
            roots.append(brentq(f, grid[i], grid[i + 1], xtol=1e-15 * grid[i], rtol=1e-15))
    return roots


def is_stable_synchronous(a: float, I: float, M: float, m: float) -> bool:
    """Darwin-Hut: the synchronous circular state is an energy minimum iff mu a^2 > 3 I."""

    mu = M * m / (M + m)
    return mu * a * a > 3.0 * I


def illustration_earth_moon() -> dict:
    """Earth flexed by the Moon now, and the Moon flexed by Earth (locked, e = 0.0549); literature values."""

    M_E, M_M, a, e_M = 5.9722e24, 7.342e22, 3.844e8, 0.0549
    n = mean_motion(a, M_E + M_M)
    omega_E = 2.0 * pi / 86164.0905
    earth = flex_rate_circular(a, omega_E, M_M, M_E)
    moon = flex_rate(a, e_M, n, M_E, M_M)
    scale_e = (G * M_M / a ** 3) ** 2 * n ** 2
    scale_m = (G * M_E / a ** 3) ** 2 * n ** 2
    return {"earth_flex_in_units_A2n2": earth / scale_e, "moon_flex_in_units_A2n2": moon / scale_m}


if __name__ == "__main__":
    print(illustration_earth_moon())
