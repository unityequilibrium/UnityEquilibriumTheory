"""Wave SI-1: the parent action's matter sector in SI units for a Bose fluid, and what psi adds.

Canonical parent action (core/THEORY_CARD.md, section 3), natural units hbar = c = 1:
    L > -1/2 (d chi)^2 - 1/2 m^2 |chi|^2 - 1/4 lam |chi|^4 + 1/2 g_c psi |chi|^2 - 1/2 (d psi)^2 - 1/2 m_psi^2 psi^2

Every parameter has a mass dimension (m, m_psi, g_c in eV; lam dimensionless), so once chi is
identified with a particle the SI conversion needs only hbar, c (and k_B for temperature). No
free energy reference E_ref is left, unlike the normalized Topic 13 Phi lane.

1. Non-relativistic limit. With Phi = (chi_1 + i chi_2)/sqrt(2) = exp(-i m t) psi_NR / sqrt(2 m),
   W = lam |Phi|^4 becomes the Gross-Pitaevskii contact term with g = lam / (2 m^2) = 4 pi a / m,
   so lam = 8 pi a m. Relativistic sound speed at chemical potential mu:
       c_s^2 = (mu^2 - m^2) / (3 mu^2 - m^2),  n = mu (mu^2 - m^2) / lam,
   which tends to the Bogoliubov value g n / m when g n / m -> 0.
2. Portal. psi exchange between chi quanta is the Yukawa potential V = -alpha G m_chi^2 exp(-r/lambda)/r
   with alpha = g_c^2 / (16 pi G m_chi^4) (claim C_PORTAL_FIFTH_FORCE, same as T005). Its contact
   strength is int V d^3r = -4 pi alpha G m_chi^2 lambda^2; for an atom of mass M made of A
   nucleons (chi = nucleon lane, as in T005) the scattering-length shift is
       delta_a = -alpha G M^3 lambda^2.
3. Diluteness. Tree-level GP only describes a fluid with n a^3 << 1.
"""

from __future__ import annotations

from math import exp, pi, sqrt

from scipy.integrate import quad

HBAR_C_EV_M = 1.973269804e-7  # eV m (exact SI constants)
HBAR_J_S = 1.054571817e-34
EV_J = 1.602176634e-19
G_NAT_EV2 = 6.70883e-57  # G / (hbar c) in eV^-2 (CODATA 2018 G = 6.67430e-11)
U_EV = 931.49410242e6  # atomic mass unit in eV
M_NUCLEON_EV = 938.92e6  # mean nucleon mass, as in T005
BOHR_M = 5.29177210903e-11

MASS_EV = {"He4": 4.002603254 * U_EV, "Na23": 22.989769282 * U_EV, "Rb87": 86.909180531 * U_EV}

# T005 torsion-balance bound (claim C_T005_PORTAL_G_C): g_c < 5.1e-10 eV for m_psi <= 5.1e-3 eV
T005_G_C_MAX_EV = 5.1e-10
T005_M_PSI_EV = 5.1e-3


def lam_from_scattering_length(a_m: float, mass_ev: float) -> float:
    """lam = 8 pi a m (dimensionless), a converted from metres to eV^-1."""
    return 8.0 * pi * (a_m / HBAR_C_EV_M) * mass_ev


def gp_coupling(lam: float, mass_ev: float) -> float:
    """g = lam / (2 m^2) in eV^-2."""
    return lam / (2.0 * mass_ev**2)


def relativistic_state(mu_ev: float, mass_ev: float, lam: float) -> tuple[float, float]:
    """(number density in eV^3, sound speed in units of c) of the O(2) fluid at chemical potential mu."""
    d = mu_ev**2 - mass_ev**2
    return mu_ev * d / lam, sqrt(d / (3.0 * mu_ev**2 - mass_ev**2))


def bogoliubov_speed_natural(n_ev3: float, mass_ev: float, lam: float) -> float:
    return sqrt(gp_coupling(lam, mass_ev) * n_ev3 / mass_ev)


def bogoliubov_speed_si(n_m3: float, a_m: float, mass_kg: float) -> float:
    """c = hbar sqrt(4 pi a n) / m in m/s, computed directly in SI."""
    return HBAR_J_S * sqrt(4.0 * pi * a_m * n_m3) / mass_kg


def portal_alpha(g_c_ev: float, m_chi_ev: float = M_NUCLEON_EV) -> float:
    return g_c_ev**2 / (16.0 * pi * G_NAT_EV2 * m_chi_ev**4)


def yukawa_contact_strength(alpha: float, m_chi_ev: float, m_psi_ev: float) -> float:
    """int V d^3r for V = -alpha G m^2 exp(-m_psi r)/r, by quadrature (eV^-2)."""
    val, _ = quad(lambda r: 4.0 * pi * r**2 * exp(-m_psi_ev * r) / r, 0.0, float("inf"))
    return -alpha * G_NAT_EV2 * m_chi_ev**2 * val


def scattering_length_shift_m(alpha: float, atom_mass_ev: float, m_psi_ev: float) -> float:
    """delta_a = -alpha G M^3 / m_psi^2, returned in metres."""
    return -alpha * G_NAT_EV2 * atom_mass_ev**3 / m_psi_ev**2 * HBAR_C_EV_M


def diluteness(n_m3: float, a_m: float) -> float:
    return n_m3 * a_m**3


def compute() -> dict:
    alpha = portal_alpha(T005_G_C_MAX_EV)
    rb_a = 100.4 * BOHR_M  # AI-chosen representative Rb-87 value for scale only
    he_core = 2.6e-10  # He-He hard-core size, AI-chosen order of magnitude (lower bound on |a|)
    he_n = 2.1856480353841311e28  # He II at 1.7 K SVP, Topic 13 record T13_HE4_O2_SI_SCALE_AND_NORMALIZED_BETA
    return {
        "alpha_at_T005_bound": alpha,
        "delta_a_Rb87_m": scattering_length_shift_m(alpha, MASS_EV["Rb87"], T005_M_PSI_EV),
        "delta_a_over_a_Rb87": scattering_length_shift_m(alpha, MASS_EV["Rb87"], T005_M_PSI_EV) / rb_a,
        "delta_a_He4_m": scattering_length_shift_m(alpha, MASS_EV["He4"], T005_M_PSI_EV),
        "He_II_n_a3_with_hard_core": diluteness(he_n, he_core),
        "He_II_GP_sound_speed_hard_core_m_s": bogoliubov_speed_si(he_n, he_core, MASS_EV["He4"] * EV_J / 299792458.0**2),
    }


if __name__ == "__main__":
    for key, value in compute().items():
        print(f"{key}: {value:.3e}")
