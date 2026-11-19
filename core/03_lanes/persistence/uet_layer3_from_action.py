"""Layer 3 rates from the parent action: capture and death of phi modes in a chi pool (stage 3, wave L3-1).

Question: layer 3 (uet_layer3_lv_map.py) posits, for each type i,

    dn_i/dt = (a_i R - 1/tau_i) n_i,        dR/dt = S - delta R - R sum_i a_i F_i n_i.

Which of a_i, tau_i and F_i follow from the action, with the same one-loop spectral function that gave
layer 2 (uet_layer2_from_action.py)?

Derivation [AI derivation; one loop, portal L = 1/2 sigma phi chi_a chi_a, natural units]:
1. Occupation of a phi mode (w, q) in a chi medium with any occupation f(p):
       dn/dt = -(rho_f / 2w) n + Pi<_f / 2w,       rho_f = Pi>_f - Pi<_f.
   For a spacelike mode (w < |q|) only scattering chi(p) -> chi(p + q) contributes and
       rho_f(w, q z) = (N sigma^2 / 2)(2 / 8 pi q) int_{E1 >= a} dE1 [f(p1) - f(p1 + q z)],
   with |p1| = k(E1), cos(p1, z) = (2 E1 w + w^2 - q^2)/(2 k q). rho_f is linear in f (no vacuum part).
2. Isotropic pools cannot feed phi: if f depends on |p| only, the integral telescopes to
   int_a^{a+w} f(E) dE >= 0, so rho_f >= 0 for every isotropic f (thermal or not, inverted or not).
   This is the field-theory form of the plasma result that an isotropic distribution has a monotone
   reduced distribution and only damps waves.
3. A flowing pool can feed phi: a chi stream at temperature T_s moving with velocity v along z,
   f = R n(gamma (E - v p_z) / T_s), gives rho_stream(w, q) = rho_rest(w', q') with
   w' = gamma (w - v q), q' = |gamma (q - v w)| (Lorentz scalar). It is negative exactly when w < v q
   (Cherenkov condition), so the mode grows.
4. Layer 3 rates: with a resting sink at T (the layer 2 bath) and a stream of strength R,
       a_i = -rho_stream(w_i, q_i) / (2 w_i)    (capture per unit R, R = 1 is the reference stream)
       1/tau_i = rho_sink(w_i, q_i) / (2 w_i)    (the layer 2 damping rate)
       F_i = w_i / e_s                          (energy per created quantum over stream energy per unit R).
   The per-capita growth a_i R - 1/tau_i is exact at one loop because rho is linear in f; the only
   approximation is the large-n limit (spontaneous term Pi</2w dropped).
5. Selection follows as in layer 3: the mode with the lowest R*_i = 1/(a_i tau_i) = rho_sink/(-rho_stream)
   takes the pool; this is mode competition in a laser or a beam-plasma system (Lamb 1964).

What the action does not give: the supply S and loss delta of the stream (boundary conditions), and
which (w, q) modes exist (set by geometry). Nearest known theory: laser rate equations, beam-plasma
(Cherenkov) instability, consumer-resource ecology. Not UET-distinct.
"""

from __future__ import annotations

import importlib
from math import pi, sqrt
from typing import Callable, Sequence

import numpy as np
from scipy.integrate import quad, solve_ivp

l2 = importlib.import_module("core.03_lanes.open_system.uet_layer2_from_action")

Occupation = Callable[[float, float, float], float]  # f(E, p_z, |p|)


def _lower_energy(w: float, q: float, M: float) -> float:
    if not 0.0 < w < q:
        raise ValueError("spacelike scattering region needs 0 < w < q")
    return -w / 2.0 + (q / 2.0) * sqrt(1.0 + 4.0 * M * M / (q * q - w * w))


def spectral_scattering(w: float, q: float, occ: Occupation, M: float, sigma: float,
                        n_bath: int = l2.N_BATH) -> float:
    """rho_f(w, q z) for a spacelike mode and any occupation f(E, p_z, |p|) symmetric about the z axis."""
    a = _lower_energy(w, q, M)

    def integrand(E1: float) -> float:
        k = sqrt(max(E1 * E1 - M * M, 0.0))
        c = (2.0 * E1 * w + w * w - q * q) / (2.0 * k * q)
        c = min(1.0, max(-1.0, c))
        pz1 = k * c
        pz2 = pz1 + q
        E2 = E1 + w
        k2 = sqrt(k * k * (1.0 - c * c) + pz2 * pz2)
        return occ(E1, pz1, k) - occ(E2, pz2, k2)

    val, _ = quad(integrand, a, np.inf, limit=400, epsabs=0.0, epsrel=1e-10)
    return n_bath * sigma**2 / 2.0 * 2.0 / (8.0 * pi * q) * val


def thermal_stream(T: float, v: float, R: float = 1.0) -> Occupation:
    """Occupation of a chi stream at temperature T moving with velocity v along z, strength R."""
    g = 1.0 / sqrt(1.0 - v * v)
    return lambda E, pz, k: R * l2.bose(g * (E - v * pz), T)


def isotropic(fun: Callable[[float], float]) -> Occupation:
    return lambda E, pz, k: fun(E)


def rho_stream_boost(w: float, q: float, T: float, v: float, M: float, sigma: float,
                     n_bath: int = l2.N_BATH) -> float:
    """rho of a stream from the rest-frame closed form and a Lorentz transformation (q along v)."""
    g = 1.0 / sqrt(1.0 - v * v)
    w_r, q_r = g * (w - v * q), abs(g * (q - v * w))
    if w_r == 0.0:
        return 0.0
    sign = 1.0 if w_r > 0.0 else -1.0
    return sign * l2.rho_landau(abs(w_r), q_r, T, M, sigma, n_bath)


def layer3_rates(modes: Sequence[tuple[float, float]], T_sink: float, T_stream: float, v: float,
                 M: float, sigma: float, n_bath: int = l2.N_BATH) -> dict[str, np.ndarray]:
    """Capture a_i (per unit stream strength), death 1/tau_i and R*_i for spacelike modes (w_i, q_i)."""
    a, death = [], []
    for w, q in modes:
        a.append(-spectral_scattering(w, q, thermal_stream(T_stream, v), M, sigma, n_bath) / (2.0 * w))
        death.append(spectral_scattering(w, q, thermal_stream(T_sink, 0.0), M, sigma, n_bath) / (2.0 * w))
    a, death = np.array(a), np.array(death)
    with np.errstate(divide="ignore"):
        r_star = np.where(a > 0.0, death / a, np.inf)
    return {"capture": a, "death": death, "tau": 1.0 / death, "R_star": r_star}


def stream_energy_per_unit(T: float, v: float, M: float) -> float:
    """Energy density of the reference stream (R = 1) in the sink frame, per chi component."""
    g = 1.0 / sqrt(1.0 - v * v)

    def inner(k: float) -> float:
        E = sqrt(k * k + M * M)
        ang, _ = quad(lambda c: l2.bose(g * (E - v * k * c), T), -1.0, 1.0, epsrel=1e-10)
        return k * k * E * ang

    val, _ = quad(inner, 0.0, np.inf, limit=400, epsrel=1e-10)
    return val / (4.0 * pi * pi)


def simulate(capture: np.ndarray, death: np.ndarray, quantum: np.ndarray, supply: float, decay: float,
             n0: np.ndarray, R0: float, horizon: float) -> tuple[np.ndarray, float]:
    """Integrate the layer 3 equations with the action-derived rates; returns final (n, R)."""
    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        n, R = y[:-1], y[-1]
        dn = (capture * R - death) * n
        dR = supply - decay * R - R * float(np.sum(capture * quantum * n))
        return np.append(dn, dR)

    sol = solve_ivp(rhs, (0.0, horizon), np.append(n0, R0), method="LSODA", rtol=1e-9, atol=1e-12)
    return sol.y[:-1, -1], float(sol.y[-1, -1])
