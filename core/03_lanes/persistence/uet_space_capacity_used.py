"""Layer 2 -> 3, wave D12: how much of space's capacity to take disorder is already used?

Question (author, 2026-11-23): in the static (ideal) view space is open; in the dynamic view it takes
the disorder of mass, so it is not 100 % open. How far from full is it today?

Standard inputs. Flat Lambda-CDM of wave D6 (H0 = 67.4 km/s/Mpc, Om = 0.315, OL = 0.685), CMB
T0 = 2.7255 K, three neutrino species at T_nu = (4/11)^(1/3) T0. The capacity is the Gibbons-Hawking
entropy of the final de Sitter horizon, S_dS = pi k c^5/(G hbar H_L^2) (wave D6). The region that can
still send its disorder to that horizon is the inside of today's cosmic event horizon,
R_eh = c a0 int_{t0}^inf dt/a.

[AI derivation]
D12a Today's event horizon has proper radius R_eh = 16.7 Gly, 0.95 of the final c/H_L = 17.5 Gly; it
     approaches c/H_L as a^-3.
D12b Radiation inside it (photons and neutrinos, g_s = 2 + (7/8) 6 (4/11) = 3.909, entropy density
     s = (2 pi^2/45) g_s k (k T0 / hbar c)^3 = 2.9e9 k per m^3) carries 4.8e88 k: 1.4e-34 of S_dS (S_dS = 3.3e122 k).
D12c Supermassive black holes dominate today's entropy. Illustrative AI inputs from memory, not a
     data comparison: mass density 4.4e5 M_sun/Mpc^3 in holes of 1e8 M_sun gives 2.6e102 k inside the
     event horizon, 8e-21 of S_dS. The number scales with the typical hole mass (S ~ M^2).
D12d Ceiling from matter: even if all matter inside the event horizon fell into one black hole, its
     entropy would be S_dS (2 G M_in H_L / c^3)^2 = S_dS (Om/OL)^2 (R_eh H_L / c)^6 = 0.157 S_dS.
     Matter alone can never fill space; the horizon stays the larger reservoir.

Consequence [AI interpretation]: in the author's terms space is not 100 % open, but today it is
used to about one part in 10^20 of its capacity, and matter inside the horizon could use at most
about a sixth of it. The closing of space shows only as the horizon itself, which is slow (wave D7).

Nearest known theory: Gibbons-Hawking entropy, the generalised second law, the entropy budget of the
universe (Frampton et al. 2008; Egan and Lineweaver 2010). Not UET-distinct. Left out: stellar black
holes, dark-matter entropy, the measured black-hole mass function, quantum corrections.
"""

from __future__ import annotations

import importlib
from math import exp, pi

from scipy.integrate import quad

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")

G, C, HBAR, K_B, M_SUN, MPC = cd.G_NEWTON, cd.C_LIGHT, cd.HBAR, cd.K_B, cd.M_SUN, cd.MPC
H0, H_L, OM, OL = cd.H0, cd.H_L, cd.OMEGA_M, cd.OMEGA_L
T0 = cd.T_CMB0
GLY = 9.4607304725808e24
G_S = 2.0 + 7.0 / 8.0 * 6.0 * 4.0 / 11.0
RHO_BH_ILLUSTRATIVE = 4.4e5 * M_SUN / MPC ** 3
M_BH_ILLUSTRATIVE = 1e8 * M_SUN


def event_horizon_radius(a0: float = 1.0) -> float:
    """Proper radius c a0 int_{a0}^inf da/(a^2 H(a)) (general path, in a)."""

    val, _ = quad(lambda u: 1.0 / cd.hubble(1.0 / u), 0.0, 1.0 / a0, epsabs=0.0, epsrel=1e-13, limit=200)
    return C * a0 * val


def event_horizon_radius_time(a0: float = 1.0) -> float:
    """Second route: c a(t0) int_{t0}^inf dt / a(t) with the closed-form a(t)."""

    t0 = cd.time_of_a(a0)
    head, _ = quad(lambda t: 1.0 / cd.a_of_time(t), t0, t0 + 40.0 / H_L, epsabs=0.0, epsrel=1e-13, limit=400)
    tail = 1.0 / (H_L * cd.a_of_time(t0 + 40.0 / H_L))  # a ~ exp(H_L t) beyond; error ~ e^(-120)
    return C * a0 * (head + tail)


def boson_entropy_density_closed_form(T: float, g: float = 2.0) -> float:
    return 2.0 * pi ** 2 / 45.0 * g * K_B * (K_B * T / (HBAR * C)) ** 3


def entropy_density_numeric(T: float, g: float, fermion: bool) -> float:
    """s = (rho + p)/T = (4/3) rho/T from the Bose-Einstein or Fermi-Dirac energy integral."""

    sign = 1.0 if fermion else -1.0
    I, _ = quad(lambda x: x ** 3 / (exp(x) + sign), 0.0, 200.0, epsabs=0.0, epsrel=1e-13, limit=200)
    rho = g / (2.0 * pi ** 2) * (K_B * T) ** 4 / (HBAR * C) ** 3 * I
    return 4.0 / 3.0 * rho / T


def radiation_entropy_density() -> float:
    """Photons (g = 2, T0) plus three neutrino species (g = 6 fermionic, T_nu = (4/11)^(1/3) T0)."""

    return boson_entropy_density_closed_form(T0, G_S)


def horizon_volume() -> float:
    return 4.0 / 3.0 * pi * event_horizon_radius() ** 3


def hole_entropy(M: float) -> float:
    return 4.0 * pi * G * M * M * K_B / (HBAR * C)


def budget() -> dict:
    S_cap = cd.de_sitter_entropy()
    V = horizon_volume()
    S_rad = radiation_entropy_density() * V
    n_bh = RHO_BH_ILLUSTRATIVE / M_BH_ILLUSTRATIVE
    S_bh = n_bh * V * hole_entropy(M_BH_ILLUSTRATIVE)
    M_in = OM * 3.0 * H0 ** 2 / (8.0 * pi * G) * V
    S_all = hole_entropy(M_in)
    return {"R_eh_Gly": event_horizon_radius() / GLY, "c_over_H_L_Gly": C / H_L / GLY,
            "S_capacity_k": S_cap / K_B, "S_radiation_k": S_rad / K_B, "S_smbh_illustrative_k": S_bh / K_B,
            "S_all_matter_one_hole_k": S_all / K_B, "fraction_radiation": S_rad / S_cap,
            "fraction_smbh_illustrative": S_bh / S_cap, "fraction_all_matter_one_hole": S_all / S_cap}


def matter_ceiling_closed_form() -> float:
    x = event_horizon_radius() * H_L / C
    return (OM / OL) ** 2 * x ** 6
