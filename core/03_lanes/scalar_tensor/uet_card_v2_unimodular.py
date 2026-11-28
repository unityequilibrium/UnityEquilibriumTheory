"""DRAFT Card v2, option (b) unimodular gravity: which dark-energy w(a) does it give? (wave V2-UM; card not approved)

Question: under ordinary gravity (option (a)) the draft card's dark energy is a constant, U0 = V_E at the vacuum,
so w = -1 exactly. Under unimodular gravity (option (b), sqrt(-g) = 1 in the Jordan frame) the cosmological term
becomes an integration constant Lambda0 that is not scale invariant. Which w(a) family follows, how many free
parameters does it have, and how does it replace v1's thawing family (C1, C2, C3, T040, T041)?

Results [AI derivation; checked in core/05_tests/physics/test_card_v2_unimodular.py].
1. The unimodular constraint adds Lambda0 to the Jordan potential, so the Einstein-frame potential is
       U = (V + Lambda0) / F^2 = U0(ratio) + Lambda0 / F^2.
   With the heavy ratio mode at its vacuum (wave V2-EF) the dilaton orbit has F = F0 exp(2 sigma / sqrt(c0)),
   sigma canonical, c0 = J / F at the vacuum. Hence
       U(sigma) = U0 + A exp(-lam sigma),   lam = 4 / sqrt(c0) = 4 sqrt(F / J) -> 4 sqrt(xi_phi / (1 + 6 xi_phi))
   for X0 / phi0^2 = alpha / lambda_chi -> 0. lam < 4 / sqrt(6) = 1.633 for every xi_phi > 0.
   This is exponential quintessence, matching Garcia-Bellido et al. 2011 (their exp(-4 gamma rho), gamma^2 =
   xi / (1 + 6 xi)).
2. The shift symmetry of sigma means the initial value only rescales A, and A is fixed by Omega_DE today. With
   beta_eff = 0 (U0 = 0, the choice of Garcia-Bellido et al.) the whole w(a) is set by one number, xi_phi, against
   three for v1 (xi_c, psi_i, m/H0). With U0 > 0 a constant is added (two numbers).
3. Thawing: the field is frozen by Hubble friction early and starts to roll late. Numerically (matter + radiation,
   Omega_m0 = 0.31, CPL fit over 0.4 <= a <= 1, the same AI window as C1) 1 + w0 grows as lam^2; for small lam it
   follows the Scherrer & Sen (2008) thawing formula
       1 + w(a) = (lam^2 / 3) [ 1 / sqrt(Om) - (1 / Om - 1) artanh(sqrt(Om)) ]^2,  Om = Omega_DE(a),
   and wa / (1 + w0) is near -1.5, as v1's quadratic thawing at small mass (C1 result 3).
4. Matter stays decoupled (V2-EF result 2, degree-1 masses), so no extended-quintessence term: C3's growth shift
   from the coupling (|mu - 1| <= 0.32 %) becomes exactly zero and only the background changes growth.
Nearest known theory: exponential (thawing) quintessence; unimodular Higgs-dilaton cosmology. Not UET-distinct.
Not done here: confrontation with data (needs a Test Card); the n_s - w0 relation of the Higgs-dilaton model needs
chi to be the inflaton, which the UET lane does not assume.
"""

from __future__ import annotations

import math

import numpy as np

OMEGA_M0 = 0.31
OMEGA_R0 = 9.0e-5


def slope_from_card(card, phi0: float = 1.0) -> float:
    X0 = card.alpha / card.lam_chi * phi0 * phi0
    return 4.0 * math.sqrt(card.F(phi0, X0) / card.J(phi0, X0))


def slope_from_xi(xi: float) -> float:
    return 4.0 * math.sqrt(xi / (1.0 + 6.0 * xi))


def xi_from_slope(lam: float) -> float:
    g2 = (lam / 4.0) ** 2
    if g2 >= 1.0 / 6.0:
        raise ValueError("lam >= 4/sqrt(6) is not reachable for any xi_phi > 0")
    return g2 / (1.0 - 6.0 * g2)


def _rhs(N, y, lam, A, U0, om, orad):
    sig, v = y
    a = math.exp(N)
    rm, rr = 3 * om * a**-3, 3 * orad * a**-4
    U = U0 + A * math.exp(-lam * sig)
    dU = -lam * A * math.exp(-lam * sig)
    H2 = (rm + rr + U) / (3.0 - 0.5 * v * v)
    eps = (rm + 4.0 / 3.0 * rr) / (2 * H2) + 0.5 * v * v
    return np.array([v, (eps - 3.0) * v - dU / H2]), H2, U


def integrate(lam: float, A: float, U0: float = 0.0, om: float = OMEGA_M0, orad: float = OMEGA_R0,
              N0: float = math.log(1e-4), steps: int = 4000, sig0: float = 0.0):
    """RK4 in N = ln a from rest at sigma = sig0. Returns arrays (a, H2, w)."""
    h = -N0 / steps
    y = np.array([sig0, 0.0])
    out_a, out_H2, out_w = [], [], []
    N = N0
    for i in range(steps + 1):
        f, H2, U = _rhs(N, y, lam, A, U0, om, orad)
        kin = 0.5 * H2 * y[1] ** 2
        out_a.append(math.exp(N))
        out_H2.append(H2)
        out_w.append((kin - U) / (kin + U))
        if i == steps:
            break
        k1 = f
        k2 = _rhs(N + h / 2, y + h / 2 * k1, lam, A, U0, om, orad)[0]
        k3 = _rhs(N + h / 2, y + h / 2 * k2, lam, A, U0, om, orad)[0]
        k4 = _rhs(N + h, y + h * k3, lam, A, U0, om, orad)[0]
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        N += h
    return np.array(out_a), np.array(out_H2), np.array(out_w)


def solve_amplitude(lam: float, U0: float = 0.0, om: float = OMEGA_M0, orad: float = OMEGA_R0,
                    steps: int = 4000) -> float:
    """A such that H(a = 1) = H0 = 1 (flat universe with Omega_m0 = om)."""
    lo, hi = 1e-3, 30.0
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        H2 = integrate(lam, mid, U0, om, orad, steps=steps)[1][-1]
        if H2 > 1.0:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)


def w_of_a(lam: float, U0: float = 0.0, steps: int = 4000):
    A = solve_amplitude(lam, U0, steps=steps)
    a, H2, w = integrate(lam, A, U0, steps=steps)
    return a, w, H2


def cpl_fit(a, w, a_min: float = 0.4):
    m = a >= a_min
    M = np.vstack([np.ones(m.sum()), 1.0 - a[m]]).T
    (w0, wa), *_ = np.linalg.lstsq(M, w[m], rcond=None)
    return float(w0), float(wa)


def scherrer_sen(omega_de: float, lam: float) -> float:
    s = math.sqrt(omega_de)
    return lam * lam / 3.0 * (1.0 / s - (1.0 / omega_de - 1.0) * math.atanh(s)) ** 2


def omega_de_today(om: float = OMEGA_M0, orad: float = OMEGA_R0) -> float:
    return 1.0 - om - orad
