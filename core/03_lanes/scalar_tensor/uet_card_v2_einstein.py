"""DRAFT Card v2 in the Einstein frame: does the dilaton couple to matter? (wave V2-EF; card not approved)

Question: v1 couples psi to matter through F = 1 + xi_c psi^2, so the solar system bounds xi_c (Cassini,
xi <= 5.75e-6, wave S1) and binary pulsars bound it through the Damour-Esposito-Farese (DEF) map (T001).
Does the same hold for the draft card v2, whose F = xi_phi phi^2 + xi_chi X has no constant?

Setup [AI derivation; checked in core/05_tests/physics/test_card_v2_einstein_frame.py].
Units M = 1 (8 pi G_E = 1). Einstein metric g_E = F g. Fields q^a = (phi, chi_1, chi_2). Then
    L_E = R_E / 2 - (1/2) K_ab d q^a d q^b - U,   K_ab = delta_ab / F + (3/2) F_a F_b / F^2,   U = V / F^2.
A body whose Jordan-frame mass is m_J(q) has Einstein-frame mass m_E = m_J / sqrt(F).

Results.
1. Dilatation Killing vector: k^a = q^a (q -> s q). Its one-form is exact up to a factor of the ratio only:
       K_ab k^b = d_a J / (2 F),   K_ab k^a k^b = J / F,   J = (1 + 6 xi_phi) phi^2 + (1 + 6 xi_chi) X.
   With s = (1/2) ln J the field-space metric splits as (J / F)(ds)^2 + h(ratio), and U depends on the ratio only
   (degree 0). The dilaton s has an exact shift symmetry: it is massless and enters only through derivatives.
2. Matter coupling. If every matter mass comes from the fields through dimensionless couplings (m_J homogeneous of
   degree 1 in q, e.g. m_J = y phi or y |chi|), then m_E has degree 0 and does not depend on s: the dilaton's
   scalar charge is exactly zero,  alpha_s = 0,  so PPN gamma - 1 = 0 and there is no long-range fifth force and
   no DEF scalarisation from it, for every xi_phi. The solar-system and binary-pulsar bounds on v1's xi_c have no
   counterpart: they no longer bound xi_phi.
   If instead matter keeps a fixed mass (m_J of degree 0: the action then has a dimensionful parameter after all),
   the dilaton is a Brans-Dicke field with alpha_DEF^2 = 2 F / J -> 2 xi_phi / (1 + 6 xi_phi) at X -> 0 and
   Cassini needs xi_phi <= 5.75e-6, as for v1. So the card's "no dimensionful parameter" decides Cassini.
3. The orthogonal (ratio) mode is heavy. At the vacuum X0 = (alpha / lambda_chi) phi0^2 (beta = 0) the canonical
   mass matrix K^-1 Hess(U) has eigenvalues {0, 0, m_r^2}: the dilaton and the O(2) phase are massless, and in the
   decoupling limit xi -> 0 the Jordan-frame mass of the radial mode is m_r^2 F = 2 alpha phi0^2 (1 + alpha /
   lambda_chi). Its Yukawa range is 1 / m_r: for the nucleon lane (m_r ~ 0.94 GeV) 0.2 fm, for a Higgs-like chi
   1.6e-18 m. The quartic portal therefore gives no macroscopic force; the g_c bounds of T005, T016 and T019
   (Yukawa range 1 / m_psi up to astronomical) have no v2 counterpart unless the dilaton gets a mass.
4. With beta > 0 the Einstein-frame potential at the vacuum is a constant U0 > 0 (w = -1 exactly, option (a));
   the dilaton stays exactly flat.
Caveat (literature, not derived here): result 2 is classical. Quantum corrections keep it only if the
regularisation is scale invariant (Shaposhnikov & Zenhausern 2009, "Quantum scale invariance, cosmological constant
and hierarchy problem"); with a fixed renormalisation scale the trace anomaly couples the dilaton to matter.
Nearest known theory: the Higgs-dilaton model (Garcia-Bellido, Rubio, Shaposhnikov & Zenhausern 2011, sec. 3,
which states the same decoupling). Not UET-distinct.
"""

from __future__ import annotations

import math

import numpy as np

M_PL_REDUCED_GEV = 2.435e18
HBARC_GEV_M = 1.97327e-16
CASSINI_GAMMA = 2.3e-5          # |gamma - 1| bound used in S1 (Bertotti et al. 2003, 1 sigma width)


def field_metric(card, q) -> np.ndarray:
    phi, c1, c2 = q
    X = c1 * c1 + c2 * c2
    F = card.F(phi, X)
    Fa = np.array([2 * card.xi_phi * phi, 2 * card.xi_chi * c1, 2 * card.xi_chi * c2])
    return np.eye(3) / F + 1.5 * np.outer(Fa, Fa) / F**2


def U(card, q) -> float:
    phi, c1, c2 = q
    X = c1 * c1 + c2 * c2
    return card.V(phi, X) / card.F(phi, X) ** 2


def J_of(card, q) -> float:
    phi, c1, c2 = q
    return card.J(phi, c1 * c1 + c2 * c2)


def killing_one_form(card, q) -> np.ndarray:
    return field_metric(card, q) @ np.asarray(q, dtype=float)


def grad_J_over_2F(card, q) -> np.ndarray:
    phi, c1, c2 = q
    F = card.F(phi, c1 * c1 + c2 * c2)
    dJ = np.array([2 * (1 + 6 * card.xi_phi) * phi, 2 * (1 + 6 * card.xi_chi) * c1, 2 * (1 + 6 * card.xi_chi) * c2])
    return dJ / (2 * F)


def einstein_mass(card, m_jordan, q) -> float:
    phi, c1, c2 = q
    return m_jordan(q) / math.sqrt(card.F(phi, c1 * c1 + c2 * c2))


def dilaton_charge_def(card, m_jordan, q, h: float = 1e-6) -> float:
    """alpha_DEF of the dilaton: sqrt(2) d ln m_E / d sigma along the Killing orbit, sigma the canonical length.

    The orbit q(s) = e^s q has |dq/ds|_K = sqrt(J / F); DEF normalise the scalar with 2 (d phi_D)^2, hence sqrt(2).
    Computed by a symmetric finite difference along the orbit (independent of result 2's homogeneity argument).
    """
    q = np.asarray(q, dtype=float)
    lp = math.log(einstein_mass(card, m_jordan, q * math.exp(h)))
    lm = math.log(einstein_mass(card, m_jordan, q * math.exp(-h)))
    norm = math.sqrt(J_of(card, q) / card.F(q[0], q[1] ** 2 + q[2] ** 2))
    return math.sqrt(2.0) * (lp - lm) / (2 * h) / norm


def gamma_minus_1(alpha_def: float) -> float:
    return -2.0 * alpha_def**2 / (1.0 + alpha_def**2)


def brans_dicke_xi_bound(gamma_bound: float = CASSINI_GAMMA) -> float:
    """xi_phi bound when matter keeps a fixed Jordan mass: 2 xi / (1 + 6 xi) <= a2, a2 from |gamma - 1|."""
    a2 = gamma_bound / (2.0 - gamma_bound)
    return a2 / (2.0 - 6.0 * a2)


def vacuum(card, phi0: float) -> np.ndarray:
    return np.array([phi0, math.sqrt(card.alpha / card.lam_chi) * phi0, 0.0])


def hessian(fun, q, h: float = 1e-4) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    n = len(q)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ei, ej = np.eye(n)[i] * h, np.eye(n)[j] * h
            H[i, j] = (fun(q + ei + ej) - fun(q + ei - ej) - fun(q - ei + ej) + fun(q - ei - ej)) / (4 * h * h)
    return H


def canonical_masses(card, phi0: float) -> np.ndarray:
    """Eigenvalues of K^-1 Hess(U) at the vacuum (Einstein units); at a minimum the connection terms drop out."""
    q = vacuum(card, phi0)
    M2 = np.linalg.solve(field_metric(card, q), hessian(lambda x: U(card, x), q))
    return np.sort(np.linalg.eigvals(M2).real)


def jordan_radial_mass2_decoupled(card, phi0: float) -> float:
    return 2.0 * card.alpha * phi0 * phi0 * (1.0 + card.alpha / card.lam_chi)


def yukawa_range_m(mass_gev: float) -> float:
    return HBARC_GEV_M / mass_gev
