"""Layer 2 from the layer 1 action: the matter field chi as a thermal bath for the response field phi.

Question (stage 3, wave L2-1): the layer 2 model (uet_layer2_dissipation.py) is Caldeira-Leggett with an
assumed ohmic friction gamma. Does the parent action itself give phi an open-system law, friction and noise
that obey KMS (fluctuation-dissipation), and if so what is gamma in terms of the action's parameters?

Parent action (THEORY_CARD.md), flat space, R = Lambda = 0, around the equilibrium delta = phi - phi* = 0:

    L = -eps( 1/2 k (d phi)^2 + 1/2 mu^2 delta^2 ) - 1/2 Z (d chi_A)^2 - 1/2 m^2 |chi|^2 + 1/2 eps h delta |chi|^2 + ...

Canonical fields  varphi = sqrt(eps k) delta,  X_A = sqrt(Z) chi_A  give

    M_phi^2 = mu^2 / k,   M_chi^2 = m^2 / Z,   L_int = 1/2 sigma varphi |X|^2,   sigma = h sqrt(eps) / (Z sqrt(k)),

with N = 2 real bath fields (the O(2) doublet). The couplings are read from the action code itself by finite
differences (canonical_couplings), not typed in.

Bath in thermal equilibrium at temperature T (chi quartic dropped: leading order in sigma, free bath).
Integrating out chi at one loop (Feynman-Vernon / Schwinger-Keldysh) gives varphi the Wightman self-energy

    Pi>(w, q) = (N sigma^2 / 2) Int d^3k/(2pi)^3 1/(4 E1 E2) 2pi sum_{s1,s2} f(s1,E1) f(s2,E2) delta(w - s1 E1 - s2 E2),
    f(+,E) = 1 + n(E),  f(-,E) = n(E),  n = Bose occupation,  E2 = |q - k| energy,

Pi<(w, q) = Pi>(-w, q), spectral function rho = Pi> - Pi<, retarded Im Pi_R = -rho/2, and the open-system
(Langevin) law for a canonical mode of frequency w:

    damping rate Gamma(w) = rho(w)/(2w),   noise kernel Pi_sym = (Pi> + Pi<)/2 = coth(w/2T) rho/2   (KMS/FDT).

The angular delta is solved analytically, leaving one integral over E1 (Weldon 1983):

    Pi>(w,q) = (N sigma^2/2) / (8 pi q) sum_{s1,s2} Int dE1 f(s1,E1) f(s2,E2*),   E2* = s2 (w - s1 E1),

over the E1 where |k - q| <= sqrt(E2*^2 - M^2) <= k + q.

Closed forms (derived here, checked against the general integral in core/05_tests/physics/test_layer2_from_action.py):
  q = 0, w > 2M (decay into a chi pair):   rho = (N sigma^2/2) (1/8pi) sqrt(1 - 4M^2/w^2) (1 + 2 n(w/2))
  0 < w < q (Landau damping, scattering off thermal chi):
      rho = (N sigma^2/2) (2 / 8pi q) T ln[ (1 - exp(-(a+w)/T)) / (1 - exp(-a/T)) ],
      a = -w/2 + (q/2) sqrt(1 + 4 M^2/(q^2 - w^2))
  Ohmic limit w -> 0 at fixed q > 0:   rho / w -> (N sigma^2/2) (2 / 8pi q) n(E0),  E0 = sqrt(q^2/4 + M^2),
  so the Caldeira-Leggett friction of a mode with wavenumber q is  gamma(q, T) = rho/(2w) = N sigma^2 n(E0) / (16 pi q).

What follows (stated as derived relations, level L1):
  - friction and noise both come from the same Wightman functions, so KMS holds without being imposed;
  - a homogeneous mode (q = 0) below the pair threshold w < 2 M_chi does not dissipate at this order (consistent
    with the O(2) one-loop no-go, which is about chi's own tadpole);
  - long-wavelength inhomogeneous modes (q > 0, w < q) get an ohmic friction gamma(q, T) that vanishes as T -> 0;
  - gamma ~ sigma^2 ~ eps h^2 / (Z^2 k): the open-system strength is fixed by the portal, not a free parameter.

Natural units (hbar = c = k_B = 1).
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from math import exp, expm1, log, pi, sqrt

import numpy as np
from scipy.integrate import quad

_matter = importlib.import_module("core.02_equations.covariant.uet_covariant_matter")
_response = importlib.import_module("core.02_equations.covariant.uet_covariant_response")

N_BATH = 2  # the O(2) doublet: two real bath fields


@dataclass(frozen=True)
class CanonicalCouplings:
    M_phi: float
    M_chi: float
    sigma: float
    response_kinetic_coeff: float  # eps k
    matter_kinetic_coeff: float    # Z
    portal_coeff: float            # eps h


def _density(response_cfg, matter_cfg, phi_dot: float, delta: float, chi1: float, chi1_dot: float) -> float:
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    grad_phi = np.array([phi_dot, 0.0, 0.0, 0.0])
    chi = np.array([chi1, 0.0])
    chi_grad = np.zeros((2, 4))
    chi_grad[0, 0] = chi1_dot
    return _matter.coupled_conservative_action_density(
        eta, eta, 0.0, grad_phi, response_cfg.phi_equilibrium + delta, chi, chi_grad, response_cfg, matter_cfg)


def canonical_couplings(response_cfg, matter_cfg, h: float = 1e-3) -> CanonicalCouplings:
    """Read eps k, eps mu^2, Z, m^2 and eps h from the action density by finite differences."""
    L = lambda **kw: _density(response_cfg, matter_cfg, **{"phi_dot": 0.0, "delta": 0.0, "chi1": 0.0, "chi1_dot": 0.0, **kw})
    second = lambda name: (L(**{name: h}) - 2.0 * L() + L(**{name: -h})) / h**2
    eps_k = second("phi_dot")             # + 1/2 eps k phi_dot^2  (g^tt = -1)
    eps_mu2 = -second("delta")            # - 1/2 eps mu^2 delta^2
    Z = second("chi1_dot")
    m2 = -second("chi1")
    # d/d delta of d^2/d chi1^2 :  + eps h
    d2chi = lambda d: (L(delta=d, chi1=h) - 2.0 * L(delta=d) + L(delta=d, chi1=-h)) / h**2
    eps_h = (d2chi(h) - d2chi(-h)) / (2.0 * h)
    return CanonicalCouplings(M_phi=sqrt(eps_mu2 / eps_k), M_chi=sqrt(m2 / Z),
                              sigma=eps_h / (Z * sqrt(eps_k)), response_kinetic_coeff=eps_k,
                              matter_kinetic_coeff=Z, portal_coeff=eps_h)


def bose(E: float, T: float) -> float:
    if T <= 0.0:
        return 0.0
    x = E / T
    return exp(-x) / (-expm1(-x)) if x > 30.0 else 1.0 / expm1(x)


def _f(sign: int, E: float, T: float) -> float:
    return 1.0 + bose(E, T) if sign > 0 else bose(E, T)


def _e1_interval(w: float, q: float, M: float, s1: int, s2: int) -> tuple[float, float] | None:
    """E1 range where the angular delta has a root, for the channel (s1, s2)."""
    s = w * w - q * q

    def ok(E1: float) -> bool:
        E2 = s2 * (w - s1 * E1)
        if E2 < M or E1 < M:
            return False
        k, k2 = sqrt(max(E1 * E1 - M * M, 0.0)), sqrt(max(E2 * E2 - M * M, 0.0))
        return abs(k - q) - 1e-12 <= k2 <= k + q + 1e-12

    if s1 > 0 and s2 > 0:          # decay varphi -> chi chi, timelike, w > 0
        if w <= 0 or s <= 4 * M * M:
            return None
        r = (q / 2.0) * sqrt(1.0 - 4.0 * M * M / s)
        lo, hi = w / 2.0 - r, w / 2.0 + r
    elif s1 < 0 and s2 < 0:        # mirror of decay, w < 0
        if w >= 0 or s <= 4 * M * M:
            return None
        r = (q / 2.0) * sqrt(1.0 - 4.0 * M * M / s)
        lo, hi = -w / 2.0 - r, -w / 2.0 + r
    else:                          # scattering, spacelike
        if s >= 0:
            return None
        lo = s1 * w / 2.0 + (q / 2.0) * sqrt(1.0 - 4.0 * M * M / s)
        hi = float("inf")
    mid = lo + 1e-9 if hi == float("inf") else 0.5 * (lo + hi)
    if not ok(mid):
        raise AssertionError("kinematic interval check failed")
    return lo, hi


def wightman_greater(w: float, q: float, T: float, M: float, sigma: float, n_bath: int = N_BATH) -> float:
    """Pi>(w, q) at one loop, q > 0, by the general E1 integral."""
    if q <= 0.0:
        raise ValueError("use q > 0; the q = 0 value is the limit (see rho_q0)")
    total = 0.0
    for s1 in (1, -1):
        for s2 in (1, -1):
            iv = _e1_interval(w, q, M, s1, s2)
            if iv is None:
                continue
            g = lambda E1: _f(s1, E1, T) * _f(s2, s2 * (w - s1 * E1), T)
            val, _ = quad(g, iv[0], iv[1], limit=400, epsabs=0.0, epsrel=1e-11)
            total += val
    return n_bath * sigma**2 / 2.0 * total / (8.0 * pi * q)


def spectral(w: float, q: float, T: float, M: float, sigma: float, n_bath: int = N_BATH) -> float:
    """rho = Pi> - Pi<, with Pi<(w) = Pi>(-w)."""
    return wightman_greater(w, q, T, M, sigma, n_bath) - wightman_greater(-w, q, T, M, sigma, n_bath)


def rho_q0(w: float, T: float, M: float, sigma: float, n_bath: int = N_BATH) -> float:
    """Closed form at q = 0: pair decay above threshold, zero below."""
    if w <= 2.0 * M:
        return 0.0
    return n_bath * sigma**2 / 2.0 / (8.0 * pi) * sqrt(1.0 - 4.0 * M * M / (w * w)) * (1.0 + 2.0 * bose(w / 2.0, T))


def rho_landau(w: float, q: float, T: float, M: float, sigma: float, n_bath: int = N_BATH) -> float:
    """Closed form for 0 < w < q (scattering off thermal chi)."""
    if not 0.0 < w < q:
        raise ValueError("Landau region needs 0 < w < q")
    a = -w / 2.0 + (q / 2.0) * sqrt(1.0 + 4.0 * M * M / (q * q - w * w))
    num, den = -expm1(-(a + w) / T), -expm1(-a / T)
    return n_bath * sigma**2 / 2.0 * 2.0 / (8.0 * pi * q) * T * log(num / den)


def caldeira_leggett_gamma(q: float, T: float, M: float, sigma: float, n_bath: int = N_BATH) -> float:
    """Ohmic friction of a mode with wavenumber q > 0: gamma = lim_{w->0} rho/(2w)."""
    return n_bath * sigma**2 * bose(sqrt(q * q / 4.0 + M * M), T) / (16.0 * pi * q)


def damping_rate(w: float, q: float, T: float, M: float, sigma: float, n_bath: int = N_BATH) -> float:
    """Gamma = rho/(2w): amplitude^2 decay rate of a canonical mode at frequency w."""
    rho = rho_q0(w, T, M, sigma, n_bath) if q == 0.0 else spectral(w, q, T, M, sigma, n_bath)
    return rho / (2.0 * w)


def zero_temperature_decay_rate(M_phi: float, M_chi: float, sigma: float, n_bath: int = N_BATH) -> float:
    """Textbook tree-level width of varphi -> chi_a chi_a for L = 1/2 sigma varphi chi_a^2, summed over a."""
    if M_phi <= 2.0 * M_chi:
        return 0.0
    return n_bath * sigma**2 / (32.0 * pi * M_phi) * sqrt(1.0 - 4.0 * M_chi**2 / M_phi**2)


def burn_rates(gamma: float, velocity_sq: float, T: float) -> dict[str, float]:
    """Layer-2 quantities for a mode with friction gamma: power, entropy rate, bit-write rate (as in layer 2)."""
    P = gamma * velocity_sq
    return {"power": P, "entropy_rate": P / T, "bits_rate": P / (T * log(2.0))}
