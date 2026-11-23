"""Layer 2 -> 3, wave D11: one free-falling mass alone in a universe - can its fall burn anything?

Question (author, 2026-11-23): suppose a universe that begins with only one mass, falling freely, and
nothing else to divide the disorder its behaviour makes. Can this universe be modelled at all, and
what does it give? D7 and D9 did not model it: they used the measured Lambda and a horizon bath (a
divider), and D9's Hawking radiation is itself a second thing. Here nothing is added: GR, one body,
no Lambda.

Standard inputs. General relativity; outside any isolated spherical body the metric is Schwarzschild
and static (Birkhoff); far-field radiation from the multipole expansion, whose lowest radiating order
is the mass quadrupole, P = G/(5 c^5) <dddQ_ij dddQ_ij> with Q the trace-free second moment.

[AI derivation]
D11a A lone body's fall emits nothing. Its mass (monopole) is conserved; its mass dipole has
     d^2 D/dt^2 = dp/dt = 0 (momentum conservation); and a body in free fall with nothing else present
     moves uniformly in any inertial frame, so Q_ij(t) is quadratic in t and dddQ = 0: P = 0 exactly.
     A spherical pulsation also emits nothing (Q_TF = 0 at all times; Birkhoff). Free fall alone is
     locally indistinguishable from rest (an accelerometer reads 0), so for a lone body "falling" and
     "being still" are the same state.
D11b What can make it lose energy needs something else:
     - its own non-spherical internal motion (parts of itself), e.g. a rigid body spinning at omega:
         P = (32 G / (5 c^5)) (I1 - I2)^2 omega^6;
     - a second body m at separation d (circular orbit):
         P = (32/5) G^4 M^2 m^2 (M + m) / (c^5 d^5),
       which vanishes as m^2 when the second body goes away;
     - Lambda, through the horizon bath of wave D7 (excluded by the author's setup).
D11c Number (illustrative): the Sun alone emits 0 W by falling; the Sun with the Earth at 1 AU emits
     about 196 W of gravitational waves, 5e-25 of its luminosity.

Consequence [AI interpretation]: the author's one-object universe can be modelled in GR, and there it
does nothing: a lone free fall uses no energy and produces no entropy. In standard physics every
divider is "something else": another body, the body's own parts, or Lambda. The author's step
"space makes things move, so they behave and burn energy" has no equation in GR for a single body; if
UET keeps that step, it has to supply its own law for it, and that law would differ from GR here.

Nearest known theory: Birkhoff's theorem, the equivalence principle, the quadrupole formula (Einstein
1918; Peters and Mathews 1963). Not UET-distinct. Left out: quantum effects (Hawking radiation needs a
horizon, i.e. a black hole), the body's own internal thermodynamics, higher multipoles.
"""

from __future__ import annotations

import numpy as np

G = 6.67430e-11
C_LIGHT = 2.99792458e8
M_SUN = 1.98892e30
M_EARTH = 5.9722e24
AU = 1.495978707e11
L_SUN = 3.828e26


def quadrupole_tf(masses, positions) -> np.ndarray:
    """Trace-free mass quadrupole Q_ij = sum m (x_i x_j - delta_ij r^2/3)."""

    m = np.asarray(masses, float)
    x = np.asarray(positions, float)
    S = np.einsum("a,ai,aj->ij", m, x, x)
    return S - np.eye(3) * np.trace(S) / 3.0


def dddq_finite_difference(trajectory, t: float, h: float) -> np.ndarray:
    """Third time derivative of Q from positions at t +- h, t +- 2h. Exact for Q polynomial of degree <= 4."""

    q = {k: quadrupole_tf(*trajectory(t + k * h)) for k in (-2, -1, 1, 2)}
    return (q[2] - 2.0 * q[1] + 2.0 * q[-1] - q[-2]) / (2.0 * h ** 3)


def dddq_spectral(trajectory, period: float, n: int = 32) -> np.ndarray:
    """Third time derivative of Q at n samples over one period, by spectral differentiation (general path)."""

    ts = np.arange(n) * period / n
    Q = np.array([quadrupole_tf(*trajectory(t)) for t in ts])
    k = 2.0 * np.pi * np.fft.fftfreq(n, d=period / n)
    return np.real(np.fft.ifft((1j * k)[:, None, None] ** 3 * np.fft.fft(Q, axis=0), axis=0))


def power_from_dddq(dddq) -> float:
    """Quadrupole formula; dddq is one 3x3 matrix or an array of them (averaged)."""

    d = np.asarray(dddq, float)
    return float(G / (5.0 * C_LIGHT ** 5) * np.mean(np.einsum("...ij,...ij->...", d, d)))


def binary_trajectory(M: float, m: float, d: float):
    omega = np.sqrt(G * (M + m) / d ** 3)
    rM, rm = d * m / (M + m), d * M / (M + m)

    def traj(t):
        u = np.array([np.cos(omega * t), np.sin(omega * t), 0.0])
        return [M, m], [-rM * u, rm * u]

    return traj, 2.0 * np.pi / omega


def binary_power_closed_form(M: float, m: float, d: float) -> float:
    return 32.0 / 5.0 * G ** 4 * M ** 2 * m ** 2 * (M + m) / (C_LIGHT ** 5 * d ** 5)


def rotating_trajectory(masses, body_positions, omega: float):
    """Rigid body spinning at omega about z, which must be a principal axis."""

    x0 = np.asarray(body_positions, float)

    def traj(t):
        c, s = np.cos(omega * t), np.sin(omega * t)
        R = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        return masses, x0 @ R.T

    return traj, 2.0 * np.pi / omega


def rotating_power_closed_form(masses, body_positions, omega: float) -> float:
    """32 G (I1 - I2)^2 omega^6 / (5 c^5); I1 - I2 from the in-plane second moments about the centre of mass."""

    m = np.asarray(masses, float)
    x = np.asarray(body_positions, float)
    x = x - (m[:, None] * x).sum(0) / m.sum()
    S = np.einsum("a,ai,aj->ij", m, x[:, :2], x[:, :2])
    w = np.linalg.eigvalsh(S)
    return 32.0 * G * (w[1] - w[0]) ** 2 * omega ** 6 / (5.0 * C_LIGHT ** 5)


def translating_trajectory(masses, body_positions, velocity):
    x0 = np.asarray(body_positions, float)
    v = np.asarray(velocity, float)
    return lambda t: (masses, x0 + v * t)


def pulsating_octahedron(m: float, r0: float, amp: float, omega: float):
    axes = np.vstack([np.eye(3), -np.eye(3)])
    return lambda t: ([m] * 6, axes * (r0 + amp * np.sin(omega * t))), 2.0 * np.pi / omega


def sun_alone_and_with_earth() -> dict:
    p = binary_power_closed_form(M_SUN, M_EARTH, AU)
    return {"sun_alone_W": 0.0, "sun_earth_W": p, "fraction_of_luminosity": p / L_SUN}
