"""Layer 2 -> 3, wave D4: a divider for systems held together by gravity (negative heat capacity).

Question (author, 2026-11-21: the earlier divider waves thought only in thermodynamics, while the
author's picture is gravity: mass piles up, black holes, orbits): waves D1-D3 assumed a store that
cools as it loses energy. A self-gravitating system does the opposite. What happens to "dividing
entropy" then?

Setting. A self-gravitating ideal gas in virial equilibrium (2K + U = 0) has E = -K = -(3/2) N k T,
so its heat capacity is C = dE/dT = -(3/2) N k < 0. It exchanges heat with a divider through a
power-law contact J = G (T^n - T_c^n)/n, with n = 1 linear and n = 4 radiation, as in wave D3.

[AI derivation]
D1  Runaway against a cold divider. dT/dt = -J/C. With C < 0 and T > T_c the system loses energy
    and heats up, so it moves away from the divider instead of towards it. Linear contact:
        T(t) = T_c + (T0 - T_c) exp(G t / |C|)       (C > 0 gives the ordinary decay to T_c);
    radiation into a divider at T_c = 0 diverges in finite time,
        t* = 4 |C| / (3 G T0^3) ,  t(T) = (4 |C| / (3 G)) (T0^-3 - T^-3).
    The usable fraction of each unit of energy lost, 1 - T_c/T, rises with time, the reverse of
    wave D1, where it falls. A gravitating system does not run down to its divider; it contracts
    and heats until another process stops it (nuclear burning, degeneracy pressure, or collapse).
D2  When can a gravitating system reach equilibrium with a divider? Two bodies in contact, C1 < 0
    (bound by gravity) and C2 > 0 (the divider, finite), conserve C1 T1 + C2 T2. The temperature
    gap g = T1 - T2 obeys dg/dt = -G g (1/C1 + 1/C2) for a linear contact, so
        equilibrium is stable  iff  C2 < |C1| ,   runaway  iff  C2 > |C1|
    (Lynden-Bell and Wood 1968). A divider with unlimited capacity (space, the CMB: C2 -> infinity)
    always gives runaway. Total entropy C1 ln T1 + C2 ln T2 still rises at every moment; in the
    runaway it rises without bound, so there is no state of maximum entropy to settle into.
D3  The clock is not tau = Ex/W of a running-down store but the runaway time |C|/G (linear) or t*
    (radiation). For a star this is the Kelvin-Helmholtz time t_KH ~ G M^2 / (R L), about 31 Myr for
    the Sun, which nuclear burning outlasts by a factor of about 300.

[AI interpretation] For gravitating matter a cold divider does not let the system settle; it
drives the contraction that the author describes as mass piling up. Self-gravitating systems can
also divide entropy inside themselves: a core (C1 < 0) passes entropy to its halo (C2), and the
core runs away when the halo can hold more than |C1|.

Nearest known theory: thermodynamics of self-gravitating systems (Lynden-Bell and Wood 1968,
Padmanabhan 1990), the gravothermal catastrophe, and the Kelvin-Helmholtz time. Not UET-distinct.
The parent action fixes none of N, G, T_c. Left out: the internal structure that sets C for real
stars (C = -(3/2) N k is the ideal-gas virial value), black holes as dividers, cosmic expansion.
"""

from __future__ import annotations

from math import exp, log

import numpy as np
from scipy.integrate import solve_ivp

G_NEWTON = 6.67430e-11        # m^3 kg^-1 s^-2 (CODATA 2018)
M_SUN = 1.98847e30            # kg (IAU nominal G M_sun / G)
R_SUN = 6.957e8               # m (IAU 2015 nominal)
L_SUN = 3.828e26              # W (IAU 2015 nominal)
YEAR = 3.15576e7              # s (Julian year)


def virial_heat_capacity(N: float, k: float = 1.0) -> float:
    """C = dE/dT for a self-gravitating ideal gas in virial equilibrium: E = -(3/2) N k T."""

    return -1.5 * N * k


def transfer(G: float, T_h: float, T_c: float, n: float) -> float:
    return G * (T_h ** n - T_c ** n) / n


def evolve_against_divider(C: float, T0: float, T_c: float, G: float, n: float, t_end: float,
                           t_eval=None, T_stop: float | None = None):
    """General path: integrate C dT/dt = -J(T) for a store of heat capacity C (any sign)."""

    def rhs(t, y):
        return [-transfer(G, y[0], T_c, n) / C]

    events = None
    if T_stop is not None:
        def stop(t, y):
            return y[0] - T_stop
        stop.terminal = True
        events = stop
    return solve_ivp(rhs, (0.0, t_end), [T0], method="DOP853", rtol=1e-12, atol=1e-14 * T0,
                     t_eval=t_eval, events=events)


def linear_closed_form(C: float, T0: float, T_c: float, G: float, t: float) -> float:
    return T_c + (T0 - T_c) * exp(-G * t / C)


def radiative_time_to(T: float, C: float, T0: float, G: float) -> float:
    """Time for a C < 0 store to heat from T0 to T while radiating (n = 4) to a divider at 0 K."""

    return 4.0 * abs(C) / (3.0 * G) * (T0 ** -3 - T ** -3)


def radiative_blowup_time(C: float, T0: float, G: float) -> float:
    return 4.0 * abs(C) / (3.0 * G * T0 ** 3)


def two_body_rhs(C1: float, C2: float, G: float):
    def rhs(t, y):
        J = G * (y[0] - y[1])  # linear contact, heat from body 1 to body 2
        return [-J / C1, J / C2]
    return rhs


def evolve_two_body(C1: float, C2: float, T1: float, T2: float, G: float, t_end: float, t_eval=None):
    return solve_ivp(two_body_rhs(C1, C2, G), (0.0, t_end), [T1, T2], method="DOP853",
                     rtol=1e-12, atol=1e-14 * max(T1, T2), t_eval=t_eval)


def gap_rate(C1: float, C2: float, G: float) -> float:
    """lambda in g(t) = g0 exp(lambda t): runaway when lambda > 0, i.e. when C2 > |C1| with C1 < 0."""

    return -G * (1.0 / C1 + 1.0 / C2)


def jacobian_eigenvalues(C1: float, C2: float, G: float) -> np.ndarray:
    """Eigenvalues of the linear two-body system, computed from its matrix (second route)."""

    A = np.array([[-G / C1, G / C1], [G / C2, -G / C2]])
    return np.linalg.eigvals(A)


def two_body_entropy(C1: float, C2: float, T1: float, T2: float) -> float:
    return C1 * log(T1) + C2 * log(T2)


def kelvin_helmholtz_time(M: float = M_SUN, R: float = R_SUN, L: float = L_SUN) -> float:
    """t_KH = G M^2 / (R L), the order-of-magnitude contraction time (seconds)."""

    return G_NEWTON * M * M / (R * L)
