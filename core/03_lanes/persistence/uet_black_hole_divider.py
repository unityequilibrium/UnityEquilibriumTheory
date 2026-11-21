"""Layer 2 -> 3, wave D5: a black hole as the divider.

Question (author's picture, AUTHOR_PROPOSITION 2026-11-17: matter flows into black holes, and a
black hole "scrapes space first" for others): if the divider that receives a system's entropy is a
black hole, how does it behave compared with the dividers of waves D1-D4?

Standard black-hole thermodynamics (Bekenstein 1973, Hawking 1975), Schwarzschild, SI units:
    T_H = hbar c^3 / (8 pi G M k)            S = 4 pi G M^2 k / (hbar c)       E = M c^2
    P_H = hbar c^6 / (15360 pi G^2 M^2)     (photon-only Hawking power, no greybody factors)

[AI derivation]
D1  Heat capacity C = dE/dT_H = -8 pi G M^2 k / (hbar c) < 0, and dS/dE = 1/T_H. A black hole that
    receives energy gets heavier and colder: unlike every ordinary divider, which warms as it fills,
    it becomes a better divider the more it takes.
D2  The black hole is the largest divider. S grows as M^2, about 1.05e77 k (M/M_sun)^2; for Sgr A*
    (4.15e6 M_sun) about 1.8e90 k, many orders above the ~1e58 k of a star like the Sun (order of
    magnitude, N k with N ~ 1e57 nucleons). Energy dE moved from a body at T into the hole changes
    the total entropy by dE (1/T_H - 1/T), positive whenever T > T_H (generalised second law), and
    an engine between them can reach efficiency 1 - T_H/T, within about 1e-11 of one for a
    solar-mass hole fed by 5772 K sunlight.
D3  Today the hole is colder than the cosmic background below the crossover mass
    M_eq = hbar c^3 / (8 pi G k T_CMB) = 4.5e22 kg (about 0.008 Earth masses); every stellar or
    larger hole is colder, so net heat flows in and it grows. With the background as a divider of
    unlimited capacity this is the runaway of wave D4 (C1 < 0, C2 -> infinity).
D4  Evaporation is a layer-3 burn with P rising as the store F = M c^2 falls (P ~ F^-2). The
    lifetime is tau = int dF / P = F0 / (3 P0) = 5120 pi G^2 M0^3 / (hbar c^4): one third of the
    naive F0/P0, as C_L3_BURN_LAW_SELECTION requires for an unregulated burner. For one solar mass,
    about 2.1e67 yr (photons only; more emitted species shorten it).

Nearest known theory: black-hole thermodynamics and the generalised second law. Not UET-distinct;
the parent action fixes nothing here. [AI interpretation] In the author's picture this makes the
black hole the coldest and largest place to put entropy, and one that improves as matter piles in.
Left out: rotation and charge (Kerr-Newman), greybody factors, accretion rates, cosmic expansion
cooling the background below T_H in the far future.
"""

from __future__ import annotations

from math import pi

from scipy.integrate import solve_ivp

HBAR = 1.054571817e-34   # J s (exact SI)
C_LIGHT = 299792458.0    # m/s (exact SI)
G_NEWTON = 6.67430e-11   # m^3 kg^-1 s^-2 (CODATA 2018)
K_B = 1.380649e-23       # J/K (exact SI)
M_SUN = 1.98847e30       # kg
M_EARTH = 5.9722e24      # kg
T_CMB = 2.7255           # K (Fixsen 2009)
YEAR = 3.15576e7         # s
M_SGR_A = 4.152e6 * M_SUN  # GRAVITY Collaboration 2019


def hawking_temperature(M: complex) -> complex:
    return HBAR * C_LIGHT ** 3 / (8.0 * pi * G_NEWTON * M * K_B)


def entropy(M: complex) -> complex:
    return 4.0 * pi * G_NEWTON * M * M * K_B / (HBAR * C_LIGHT)


def heat_capacity(M: float) -> float:
    return -8.0 * pi * G_NEWTON * M * M * K_B / (HBAR * C_LIGHT)


def hawking_power(M: float) -> float:
    return HBAR * C_LIGHT ** 6 / (15360.0 * pi * G_NEWTON ** 2 * M * M)


def crossover_mass(T_bath: float = T_CMB) -> float:
    """Mass at which T_H equals the bath temperature; heavier holes are colder and grow."""

    return HBAR * C_LIGHT ** 3 / (8.0 * pi * G_NEWTON * K_B * T_bath)


def evaporation_time_closed_form(M0: float, M_end: float = 0.0) -> float:
    return 5120.0 * pi * G_NEWTON ** 2 * (M0 ** 3 - M_end ** 3) / (HBAR * C_LIGHT ** 4)


def evaporation_time_numeric(M0: float, M_end: float) -> float:
    """General path: integrate dM/dt = -P_H(M)/c^2 in the variable x = M/M0 until x = M_end/M0."""

    P0 = hawking_power(M0)
    t_scale = M0 * C_LIGHT ** 2 / P0  # naive F0/P0

    def rhs(s, y):
        x = y[0]
        return [-1.0 / (x * x)]  # dx/ds with s = t / t_scale

    def reach(s, y):
        return y[0] - M_end / M0
    reach.terminal = True
    sol = solve_ivp(rhs, (0.0, 1.0), [1.0], method="DOP853", rtol=1e-13, atol=1e-15, events=reach)
    return sol.t_events[0][0] * t_scale


def entropy_change_of_transfer(dE: float, T_body: float, M: float) -> float:
    """Total entropy change when heat dE leaves a body at T_body and enters the hole."""

    return dE * (1.0 / hawking_temperature(M) - 1.0 / T_body)
