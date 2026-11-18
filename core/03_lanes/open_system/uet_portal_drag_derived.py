"""Wave B6: derive the psi friction Gamma from the parent action instead of choosing it.

Wave B4 put a friction term Gamma u.d psi into the psi equation by hand and found a portal drag
F = Gamma v q^2/(12 pi R); wave B5 bounded Gamma g_c^2. Here Gamma is not a parameter. It follows
from the closed system "psi + ordinary matter" through the same open-from-closed step as wave A3
(Caldeira-Leggett): integrating out a bath that couples linearly to psi gives a retarded self-energy
Sigma_R(omega, k), and the friction is its dissipative part.

1. Coupling. The parent action has + (1/2) g_c psi |chi|^2 with chi = ordinary matter (author
   decision 2026-11-10). For non-relativistic matter each particle feels the potential
   U = -alpha_c psi with alpha_c = g_c / (2 m_chi), which reproduces the source g_c rho/(2 m_chi^2)
   used in waves B1b-B5. The bath operator is the matter number density n.
2. Vacuum. With chi = nucleons and m_psi << 2 m_chi, psi cannot decay into the bath, and a Lorentz
   invariant action cannot produce a term Gamma u.d psi with a preferred u in vacuum. So the
   vacuum friction is zero. The only preferred frame is the rest frame of the ambient matter.
3. Medium. In a medium Sigma_R = -alpha_c^2 chi_nn(omega, k), with chi_nn the density response.
   Number conservation gives Im chi_nn(omega, k = 0) = 0, so a uniform psi does not dissipate.
   For a classical ideal gas (Maxwellian, dispersion sigma, temperature T = m sigma^2)
       Im chi_nn(omega, k) = (n/T) sqrt(pi/2) (omega/(k sigma)) exp(-omega^2/(2 k^2 sigma^2)),
   so the B4 friction is Gamma(k) = alpha_c^2 n sqrt(pi/2) / (T k sigma): it depends on k, it is
   fixed by g_c and the medium, and it is not a free constant.
4. Drag. A source moving at v through the medium loses momentum at the linear-response rate
       F = integral d^3k/(2 pi)^3 (k . v_hat) |U_k|^2 Im chi_nn(k . v, k),
   with U_k = alpha_c q / (k^2 + m_psi^2) and q = g_c M / (2 m_chi^2). Putting in gravity instead,
   U_k = 4 pi G M m / k^2, the same formula is Chandrasekhar's dynamical friction (checked in the
   test). For m_psi -> 0 the portal potential is alpha times the gravitational one, with
   alpha = g_c^2 / (16 pi G m_chi^4) the T005 strength, so the portal drag is alpha^2 times the
   gravitational dynamical friction of the same medium.

Consequence: the cross-layer drag is ordinary momentum exchange with ambient matter through the
fifth force. It is not UET-distinct, and its size is fixed once g_c is bounded.

Units: SI for the medium and the body; the portal enters only through alpha (dimensionless).
"""

from __future__ import annotations

from math import erf, exp, log, pi, sqrt

from scipy.integrate import quad

G_SI = 6.67430e-11
PROTON_MASS_KG = 1.67262192e-27
K_BOLTZMANN = 1.380649e-23
HBAR_C_EV_M = 1.973269804e-7
PLANCK_MASS_EV = 1.220890e28  # 1/sqrt(G) in eV
NUCLEON_MASS_EV = 0.9389e9


def portal_alpha(g_c_ev: float, m_chi_ev: float = NUCLEON_MASS_EV) -> float:
    """Fifth-force strength relative to gravity, alpha = g_c^2 / (16 pi G m_chi^4) (natural units)."""
    return g_c_ev**2 * PLANCK_MASS_EV**2 / (16.0 * pi * m_chi_ev**4)


def im_density_response(omega: float, k: float, n: float, temperature_j: float, sigma: float) -> float:
    """Im chi_nn of a classical ideal gas (free-particle Maxwellian response), SI: s.t. units m^-3 J^-1."""
    x = omega / (k * sigma)
    return (n / temperature_j) * sqrt(pi / 2.0) * x * exp(-0.5 * x * x)


def friction_coefficient(k: float, alpha_c: float, n: float, temperature_j: float, sigma: float) -> float:
    """Gamma(k) = lim_{omega -> 0} alpha_c^2 Im chi_nn(omega, k) / omega (B4 friction, derived)."""
    return alpha_c**2 * (n / temperature_j) * sqrt(pi / 2.0) / (k * sigma)


def linear_response_drag(potential_k2, v: float, n: float, particle_mass: float, sigma: float,
                         k_min: float, k_max: float) -> float:
    """F = int d^3k/(2pi)^3 (k cos th) |U_k|^2 Im chi(k v cos th, k), done as a k and mu = cos th integral.

    ``potential_k2(k)`` returns |U_k|^2 in J^2 m^6 (Fourier transform of the particle potential energy).
    The mu integral is done in closed form: int_{-1}^{1} mu * (k v mu/(k sigma)) e^{-(v mu)^2/(2 sigma^2)} dmu.
    """
    temperature = particle_mass * sigma * sigma
    s = v / sigma

    def mu_integral() -> float:
        # int_{-1}^{1} s mu^2 exp(-s^2 mu^2 / 2) dmu
        value, _ = quad(lambda mu: s * mu * mu * exp(-0.5 * s * s * mu * mu), -1.0, 1.0)
        return value

    angular = mu_integral()

    def integrand(lnk: float) -> float:
        k = exp(lnk)
        # d^3k/(2pi)^3 = k^2 dk dmu dphi / (2pi)^3 -> k^2 dk dmu / (4 pi^2); dk = k dlnk; extra factor k from k cos th
        return k**4 * potential_k2(k) / (4.0 * pi**2)

    radial, _ = quad(integrand, log(k_min), log(k_max), limit=400)
    return (n / temperature) * sqrt(pi / 2.0) * angular * radial


def chandrasekhar_drag(mass: float, rho: float, v: float, sigma: float, coulomb_log: float) -> float:
    """Chandrasekhar dynamical friction F = 4 pi G^2 M^2 rho lnL / v^2 [erf X - 2X e^{-X^2}/sqrt(pi)]."""
    x = v / (sqrt(2.0) * sigma)
    return 4.0 * pi * G_SI**2 * mass**2 * rho * coulomb_log / v**2 * (erf(x) - 2.0 * x * exp(-x * x) / sqrt(pi))


def gravity_potential_k2(mass: float, particle_mass: float):
    return lambda k: (4.0 * pi * G_SI * mass * particle_mass / (k * k)) ** 2


def portal_potential_k2(mass: float, particle_mass: float, alpha: float, m_psi_inv_m: float):
    """|U_k|^2 for the portal force: alpha times gravity, Yukawa-cut at k ~ m_psi (in 1/m)."""
    return lambda k: (alpha * 4.0 * pi * G_SI * mass * particle_mass / (k * k + m_psi_inv_m**2)) ** 2


def orbital_decay_rate(force: float, mass: float, v_orbit: float) -> float:
    """|d ln a/dt| = 2 F / (M v) for a tangential drag on a circular orbit (as in wave B5)."""
    return 2.0 * force / (mass * v_orbit)
