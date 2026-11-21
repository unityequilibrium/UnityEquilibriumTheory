"""Layer 2 -> 3, wave D6: the expanding universe as the last divider.

Question (author, AUTHOR_PROPOSITION item 3: the vacuum always expands, Lambda_eff > 0, so nothing
is static; item 9: the universe is not empty because traces accumulate): after stars, planets and
black holes (waves D1-D5), what is the last place entropy can go, how cold is it, how much can it
hold, and when does it take over?

Standard inputs. Flat Lambda-CDM with matter and Lambda (radiation neglected, a 0.3 percent effect
on the age): H(a) = H0 sqrt(Om a^-3 + OL), Planck 2018 values H0 = 67.4 km/s/Mpc, Om = 0.315,
OL = 0.685; CMB T0 = 2.7255 K with T_CMB = T0/a. The cosmic event horizon of the Lambda era has the
Gibbons-Hawking temperature and entropy (1977)
    T_dS = hbar H_L / (2 pi k) ,   S_dS = pi k c^5 / (G hbar H_L^2) ,   H_L = H0 sqrt(OL).

[AI derivation]
D1  Expansion law: a(t) = (Om/OL)^(1/3) sinh^(2/3)(3 H_L t / 2), inverse
    t(a) = (2 / (3 H_L)) asinh( sqrt(OL/Om) a^(3/2) ). Age today 13.80 Gyr; late times a ~ e^(H_L t).
D2  The last divider is cold but not at zero: T_dS = 2.2e-30 K. No process can reach efficiency 1;
    1 - T_dS/T is the ceiling for anything at temperature T.
D3  Its capacity is finite: S_dS = 3.3e122 k. Every trace the author counts in item 9 (all entropy
    written into the universe) fits under this ceiling; the universe cannot keep writing forever.
D4  Hand-over times (from T_CMB(t) = T): the background becomes colder than a black hole of mass M
    when a = T0 / T_H(M): for one solar mass at t = 3.2e11 yr, for Sgr A* at 5.9e11 yr; after that
    holes start to evaporate (wave D5). The background falls below T_dS at t = 1.2e12 yr; from then
    the horizon is the last divider. Every black hole lighter than M_max = c^3 / (4 G H_L)
    = 5.6e52 kg, about 2.8e22 M_sun, is eventually hotter than T_dS and evaporates into it.

Nearest known theory: Lambda-CDM cosmology and de Sitter horizon thermodynamics (Gibbons and
Hawking 1977); the far-future sequence follows Adams and Laughlin (1997). Not UET-distinct; the
parent action does not fix H0, Om or OL. [AI interpretation] In the author's chain the expanding
vacuum is the divider that never fills up in practice but has a finite total size: the traces of
everything that used energy end up bounded by S_dS. For context only (AI memory, not computed
here): today's entropy is about 1e104 k, almost all in supermassive black holes (Egan and
Lineweaver 2010), so about 18 orders of magnitude of headroom remain.
Left out: radiation era, dark-energy evolution (w != -1), whether the horizon's heat capacity can
be treated like a body's, and quantum-gravity corrections.
"""

from __future__ import annotations

from math import asinh, log, pi, sinh, sqrt

from scipy.integrate import quad

HBAR = 1.054571817e-34
C_LIGHT = 299792458.0
G_NEWTON = 6.67430e-11
K_B = 1.380649e-23
M_SUN = 1.98847e30
YEAR = 3.15576e7
MPC = 3.0856775814913673e22  # m
T_CMB0 = 2.7255              # K, Fixsen 2009
H0 = 67.4e3 / MPC            # s^-1, Planck 2018 VI
OMEGA_M = 0.315
OMEGA_L = 0.685
H_L = H0 * sqrt(OMEGA_L)


def hubble(a: float) -> float:
    return H0 * sqrt(OMEGA_M * a ** -3 + OMEGA_L)


def time_of_a_numeric(a: float) -> float:
    """General path: t(a) = int_0^a da' / (a' H(a')), split at a = 1 for accuracy."""

    f = lambda x: 1.0 / (x * hubble(x))  # noqa: E731
    if a <= 1.0:
        value, _ = quad(f, 0.0, a, epsabs=0.0, epsrel=1e-13, limit=400)
        return value
    head, _ = quad(f, 0.0, 1.0, epsabs=0.0, epsrel=1e-13, limit=400)
    # beyond a = 1 integrate in ln a, where the integrand tends to the constant 1/H_L
    tail, _ = quad(lambda u: 1.0 / hubble(2.718281828459045 ** u), 0.0, log(a), epsabs=0.0, epsrel=1e-13, limit=400)
    return head + tail


def time_of_a(a: float) -> float:
    return 2.0 / (3.0 * H_L) * asinh(sqrt(OMEGA_L / OMEGA_M) * a ** 1.5)


def a_of_time(t: float) -> float:
    return (OMEGA_M / OMEGA_L) ** (1.0 / 3.0) * sinh(1.5 * H_L * t) ** (2.0 / 3.0)


def de_sitter_temperature(H: float = H_L) -> float:
    return HBAR * H / (2.0 * pi * K_B)


def de_sitter_entropy(H: float = H_L) -> float:
    return pi * K_B * C_LIGHT ** 5 / (G_NEWTON * HBAR * H * H)


def hawking_temperature(M: float) -> float:
    return HBAR * C_LIGHT ** 3 / (8.0 * pi * G_NEWTON * M * K_B)


def time_background_reaches(T: float) -> float:
    """Cosmic time at which T_CMB = T0/a falls to T."""

    return time_of_a(T_CMB0 / T)


def largest_mass_that_evaporates(H: float = H_L) -> float:
    """M with T_H(M) = T_dS: c^3 / (4 G H)."""

    return C_LIGHT ** 3 / (4.0 * G_NEWTON * H)
