"""Layer 2 -> 3, wave D10: where the record of a vanished mass goes in the real universe.

Question (follows D9, author 2026-11-22: compare the space-only model with the real universe and
keep space and record apart): in D9, with Lambda only, the radiation of an evaporating hole meets
nothing and isotropic emission leaves no wave memory, so space returns to what it was. In the real
universe there is matter (space of the second kind in the author's split) and events are not
symmetric. Does matter absorb the record? Does geometry keep a record of asymmetric events?

Standard inputs. Flat Lambda-CDM of wave D6 (H0 = 67.4 km/s/Mpc, Om = 0.315), baryon density
Omega_b h^2 = 0.02237 (Planck 2018 VI), helium mass fraction Y = 0.245, fully ionised gas with
n_e = rho_b (1 - Y/2)/m_p, Thomson cross-section sigma_T (an upper bound on Compton scattering at
any photon energy). Gravitational-wave memory from the Wiseman-Will / Thorne formula of wave D9,
with the quadrupole angular distribution of a circular binary, dE/dOmega ~ (1 + cos^2 i)^2/4 + cos^2 i.

[AI derivation]
D10a The record from now on mostly escapes all matter. The scattering optical depth for a photon
     emitted today, integrated over the whole future, is
         tau_future = n_e0 sigma_T c int_1^inf da / (a^4 H(a)) = 7.3e-4,
     so at least 99.93 % of the radiation is never scattered by intergalactic gas: the record
     travels free, as in the space-only model.
D10b The record from the far past was absorbed. For light emitted at redshift z towards us the
     same integral from 1/(1+z) to 1 gives tau = 0.0034 (z = 1), 0.057 (z = 7.7), 0.23 (z = 20),
     2.4 (z = 100) if the gas were ionised all the way. Before reionisation the gas was neutral and
     earlier than z ~ 1100 opaque: early records were taken up by matter and survive as its heat.
D10c Geometry keeps a record of asymmetric events. For a circular-binary merger radiating E the
     memory is
         Delta h = G E sin^2 i (17 + cos^2 i) / (24 c^4 r),
     derived here from the memory integral (coefficient 17/96 edge-on per 4GE/(c^4 r)). Illustrative
     AI choice: two 30 M_sun holes radiating 5 % of their mass, edge-on at 400 Mpc: Delta h = 2.5e-22,
     a permanent change of 5e-19 m in a 4 km arm.

Consequence [AI interpretation, in the author's 2026-11-22 split]: space of the first kind
(Lambda) keeps nothing, in either model. The geometry made by mass-energy (second kind, the author's
"information") keeps a record only of asymmetric events. Matter keeps the record of the early,
dense universe as heat. Today's universe is transparent, so present records mostly travel free.

Nearest known theory: Thomson optical depth (the reionisation optical depth is defined this way),
nonlinear gravitational-wave memory (Christodoulou 1991; Wiseman and Will 1991; Favata 2009).
Not UET-distinct. No external data are compared. Left out: neutral-gas and dust absorption inside
galaxies, Klein-Nishina suppression (which only lowers tau), spin and precession, memory detection.
"""

from __future__ import annotations

import importlib
from math import pi

import numpy as np
from scipy.integrate import quad

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")
er = importlib.import_module("docs.core.03_lanes.persistence.uet_evaporation_record")

G, C_LIGHT, M_SUN, MPC = cd.G_NEWTON, cd.C_LIGHT, cd.M_SUN, cd.MPC
H0 = cd.H0
LITTLE_H = 0.674
OMEGA_B = 0.02237 / LITTLE_H ** 2
Y_HE = 0.245
M_P = 1.67262192369e-27
SIGMA_T = 6.6524587321e-29


def electron_density_today() -> float:
    rho_crit = 3.0 * H0 ** 2 / (8.0 * pi * G)
    return rho_crit * OMEGA_B * (1.0 - Y_HE / 2.0) / M_P


def optical_depth(a_from: float, a_to: float) -> float:
    """tau = n_e0 sigma_T c int a^-3 dt = n_e0 sigma_T c int da / (a^4 H(a)), fully ionised.
    For a_to = inf the integral runs in u = 1/a to keep a finite interval."""

    k = electron_density_today() * SIGMA_T * C_LIGHT
    if np.isinf(a_to):
        head, _ = quad(lambda u: u ** 2 / cd.hubble(1.0 / u), 0.0, 1.0 / a_from, epsabs=0.0, epsrel=1e-12)
        return k * head
    val, _ = quad(lambda a: 1.0 / (a ** 4 * cd.hubble(a)), a_from, a_to, epsabs=0.0, epsrel=1e-12, limit=200)
    return k * val


def optical_depth_matter_era(a_from: float, a_to: float = 1.0) -> float:
    """Closed form when Lambda is negligible (a << (Om/OL)^(1/3)):
    (2/3) k / (H0 sqrt(Om)) (a_from^-3/2 - a_to^-3/2)."""

    k = electron_density_today() * SIGMA_T * C_LIGHT
    return 2.0 / 3.0 * k / (H0 * np.sqrt(cd.OMEGA_M)) * (a_from ** -1.5 - a_to ** -1.5)


def binary_flux(n) -> float:
    """Quadrupole angular distribution of GW energy from a circular binary (orbit normal = z)."""

    ct = n[2]
    return (1.0 + ct * ct) ** 2 / 4.0 + ct * ct


def binary_flux_norm() -> float:
    val, _ = quad(lambda ct: 2.0 * pi * ((1.0 + ct * ct) ** 2 / 4.0 + ct * ct), -1.0, 1.0)
    return val


def memory_coefficient_numeric(inclination: float) -> float:
    """|Delta h| per 4 G E / (c^4 r), from the memory integral, for line of sight at inclination i."""

    # integrate with the line of sight on the pole (where the TT kernel is smooth in theta, phi);
    # R turns the pole into the true line of sight (sin i, 0, cos i), so the source is rotated
    c, s = np.cos(inclination), np.sin(inclination)
    R = np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]])
    norm = binary_flux_norm()
    T = er.memory_tensor(lambda n: binary_flux(R @ n) / norm, N=(0.0, 0.0, 1.0))
    # plus polarisation: half the difference of the two transverse eigenvalues
    w = np.linalg.eigvalsh(T)
    return 0.5 * (w[-1] - w[0])


def memory_coefficient_closed_form(inclination: float) -> float:
    s2 = np.sin(inclination) ** 2
    return s2 * (17.0 + (1.0 - s2)) / 96.0


def memory_strain(E: float, r: float, inclination: float) -> float:
    return 4.0 * G * E / (C_LIGHT ** 4 * r) * memory_coefficient_closed_form(inclination)
