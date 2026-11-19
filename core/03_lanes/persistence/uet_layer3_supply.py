"""Layer 3 pool supply S and loss delta from the parent action (stage 3, wave L3-2).

Question: layer 3 has a pool equation dR/dt = S - delta R - R sum_i a_i F_i n_i, and wave L3-1
(uet_layer3_from_action.py) derived a_i, tau_i and F_i for a chi stream that feeds phi modes. Do S and delta
follow from the action too?

Answer [AI derivation, tree level in the chi self-coupling, natural units]:
1. delta follows. The action's matter potential W = 1/2 m^2 |C|^2 + 1/4 lambda |C|^4 with kinetic factor Z
   gives the canonical O(2) contact vertex -2 i lam (d_ab d_cd + d_ac d_bd + d_ad d_bc), lam = lambda/Z^2.
   A stream particle of component a meets the resting sink (both components, density n per component) with
       |M(aa->aa)|^2 = 36 lam^2,  |M(aa->bb)|^2 = 4 lam^2 (identical pairs, factor 1/2),  |M(ab->ab)|^2 = 4 lam^2,
   so the total cross section summed over sink components is sigma_tot(s) = 3 lam^2 / (2 pi s), and the stream
   loses its particles (each contact collision is isotropic in the centre of mass) at
       delta = n_sink < sigma_tot v_Moller >,
   which for M >> T is delta = n_sink * 3 lam^2/(8 pi M^2) * <|v_rel|> with v_rel Gaussian of variance
   (T + T_s)/M per axis shifted by the stream speed v.
2. S does not follow. In a region that holds only the action's fields, the stream has no source: S = 0, R decays
   as e^{-delta t} at best, and every phi mode dies once R < R*_i. A steady structure needs S > S* = delta R*_min,
   and S has to be a flux through the region's boundary, i.e. set by an enclosing system.
   With a stream entering a region of length L at density n_in and speed v: S = n_in v / L (in units of R).
3. Persistence threshold, everything except the boundary flux from the action:
       S* = delta * R*_min = n_sink <sigma_tot v> * min_i [rho_sink,i / (-rho_stream,i)].

Approximations: tree level in lam; the collision rate uses Boltzmann momenta and no Bose enhancement of final
states (good for M >~ 3 T); "a collision removes a particle from the stream" holds when the stream is fast
compared with its thermal spread (beam attenuation).

[AI interpretation] This is the author's nesting: the supply of one level is the throughput of the level that
contains it; the action fixes how fast a pool leaks and how cheaply a structure lives, not how much is sent in.
Nearest known theory: beam attenuation (mean free path), chemostat dilution, laser pump threshold. Not UET-distinct.
"""

from __future__ import annotations

import importlib
from math import erf, exp, pi, sqrt

import numpy as np
from scipy.integrate import quad

l2 = importlib.import_module("core.03_lanes.open_system.uet_layer2_from_action")
cov = importlib.import_module("core.02_equations.covariant.uet_covariant_matter")


def canonical_quartic(mc) -> float:
    """lam = lambda/Z^2, read from the action's matter potential and kinetic factor."""
    x = 0.7
    W = cov.matter_potential(np.array([x, 0.0]), mc)
    lam_raw = 4.0 * (W - 0.5 * mc.matter_mass_sq * x * x) / x**4
    return lam_raw / mc.matter_kinetic**2


def squared_amplitudes(lam: float) -> dict[str, float]:
    """Tree-level |M|^2 of the O(2) contact vertex, V = lam/4 (chi_a chi_a)^2 with canonical fields."""
    def vertex(a: int, b: int, c: int, d: int) -> float:
        dd = lambda i, j: 1.0 if i == j else 0.0
        return -2.0 * lam * (dd(a, b) * dd(c, d) + dd(a, c) * dd(b, d) + dd(a, d) * dd(b, c))
    return {"aa->aa": vertex(0, 0, 0, 0) ** 2, "aa->bb": vertex(0, 0, 1, 1) ** 2, "ab->ab": vertex(0, 1, 0, 1) ** 2}


def sigma_total(s: float, lam: float) -> float:
    """Total cross section of a stream particle on the sink, summed over both sink components."""
    m2 = squared_amplitudes(lam)
    per = lambda msq, identical: msq / (16.0 * pi * s) * (0.5 if identical else 1.0)
    return per(m2["aa->aa"], True) + per(m2["aa->bb"], True) + per(m2["ab->ab"], False)


def sink_density(T: float, M: float) -> float:
    """Number density of one chi component in a resting thermal bath (Bose)."""
    val, _ = quad(lambda k: k * k * l2.bose(sqrt(k * k + M * M), T), 0.0, np.inf, limit=400, epsrel=1e-11)
    return val / (2.0 * pi * pi)


def mean_relative_speed(T: float, T_s: float, v: float, M: float) -> float:
    """<|v_rel|> for two Maxwellians of mass M (temperatures T, T_s) with relative drift v (M >> T)."""
    s = sqrt((T + T_s) / M)
    if v == 0.0:
        return sqrt(8.0 / pi) * s
    x = v / (s * sqrt(2.0))
    return s * sqrt(2.0) * (exp(-x * x) / sqrt(pi) + (x + 1.0 / (2.0 * x)) * erf(x))


def rate_coefficient(T: float, T_s: float, v: float, M: float, lam: float) -> float:
    """<sigma_tot v> for M >> T: sigma_tot(4 M^2) <|v_rel|>."""
    return sigma_total(4.0 * M * M, lam) * mean_relative_speed(T, T_s, v, M)


def stream_loss_rate(T: float, T_s: float, v: float, M: float, lam: float) -> float:
    """delta = n_sink <sigma_tot v> (M >> T)."""
    return sink_density(T, M) * rate_coefficient(T, T_s, v, M, lam)


def _sample_juttner(rng: np.random.Generator, T: float, M: float, n: int) -> np.ndarray:
    """Momenta from the Maxwell-Juttner (Boltzmann) distribution at rest, by rejection in |p|."""
    out = np.empty((0, 3))
    kmax = sqrt((M + 40.0 * T) ** 2 - M * M)
    kpk = sqrt(2.0 * M * T + T * T)  # near the peak of k^2 exp(-E/T)
    fmax = 1.2 * kpk * kpk * exp(-(sqrt(kpk * kpk + M * M) - M) / T)
    while len(out) < n:
        k = rng.uniform(0.0, kmax, 4 * n)
        acc = rng.uniform(0.0, fmax, 4 * n) < k * k * np.exp(-(np.sqrt(k * k + M * M) - M) / T)
        k = k[acc]
        c = rng.uniform(-1.0, 1.0, len(k))
        ph = rng.uniform(0.0, 2.0 * pi, len(k))
        sn = np.sqrt(1.0 - c * c)
        out = np.vstack([out, np.column_stack([k * sn * np.cos(ph), k * sn * np.sin(ph), k * c])])
    return out[:n]


def rate_coefficient_mc(T: float, T_s: float, v: float, M: float, lam: float, n: int = 200_000,
                        seed: int = 0) -> tuple[float, float]:
    """<sigma_tot(s) v_Moller> with exact relativistic kinematics (Monte Carlo); returns (value, s.e.)."""
    rng = np.random.default_rng(seed)
    p1 = _sample_juttner(rng, T_s, M, n)
    E1 = np.sqrt(np.sum(p1 * p1, axis=1) + M * M)
    g = 1.0 / sqrt(1.0 - v * v)
    pz, E1 = g * (p1[:, 2] + v * E1), g * (E1 + v * p1[:, 2])   # boost the stream along z
    p1[:, 2] = pz
    p2 = _sample_juttner(rng, T, M, n)
    E2 = np.sqrt(np.sum(p2 * p2, axis=1) + M * M)
    dot = E1 * E2 - np.sum(p1 * p2, axis=1)
    s = 2.0 * M * M + 2.0 * dot
    v_moller = np.sqrt(dot * dot - M**4) / (E1 * E2)
    sig = sigma_total(s, lam)  # amplitude table summed per channel, evaluated at each sampled s
    vals = sig * v_moller
    return float(vals.mean()), float(vals.std(ddof=1) / sqrt(n))


def persistence_threshold(loss_rate: float, r_star: np.ndarray) -> float:
    """S* = delta R*_min: the smallest boundary supply that keeps any phi mode alive in steady state."""
    finite = r_star[np.isfinite(r_star)]
    return float("inf") if finite.size == 0 else loss_rate * float(finite.min())
