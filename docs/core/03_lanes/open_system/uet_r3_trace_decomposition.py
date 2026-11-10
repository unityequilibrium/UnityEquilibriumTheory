"""R3: what is the "trace" that energy use leaves? (author points 7-9, clarified 2026-11-10)

Author: the trace is not a new thing in the universe; it may be just a number, a
potential difference or a value of some change. This module makes that precise for
the closed system of A3 (one mode + a Caldeira-Leggett environment).

Exact identity for a system S and reservoir R that start uncorrelated, with R in
equilibrium at temperature T, under any total Hamiltonian evolution
(Esposito, Lindenberg & Van den Broeck, New J. Phys. 12, 013013, 2010,
doi:10.1088/1367-2630/12/1/013013):

    Sigma = dS_S + Q/T = I(S:R) + D(rho_R || rho_R^eq)

  Sigma  total entropy production (k_B = 1); Q = energy that entered the bare reservoir
  I      mutual information between system and environment: the READABLE RECORD
         (what the environment now "knows" about the system)
  D      relative entropy of the environment from equilibrium; T*D is the free energy
         left in the environment: a POTENTIAL DIFFERENCE (the author's "number")

So the trace has two parts, both numbers: a correlation and a free-energy difference.
For linear dynamics with Gaussian states every term is computed exactly from covariance
matrices (classical differential entropies, natural units: nats; bits = nats / ln 2).
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from math import log, pi

import numpy as np

_l2 = importlib.import_module("docs.core.03_lanes.open_system.uet_layer2_dissipation")
OhmicBath = _l2.OhmicBath


def _entropy(cov: np.ndarray) -> float:
    """Differential entropy of a zero-mean Gaussian: 1/2 ln det(2 pi e C)."""

    sign, logdet = np.linalg.slogdet(2.0 * pi * np.e * cov)
    if sign <= 0:
        raise ValueError("covariance is not positive definite")
    return 0.5 * logdet


@dataclass(frozen=True)
class TraceBudget:
    time: float
    sigma: float          # total entropy production
    record: float         # I(S:R)
    potential: float      # D(rho_R || rho_eq)
    delta_s_system: float
    heat_to_environment: float
    total_entropy_drift: float  # S_SR(t) - S_SR(0); 0 for Hamiltonian evolution


def initial_covariance(w0: float, bath: "OhmicBath", t_sys: float, t_bath: float) -> np.ndarray:
    """Product state: system thermal at t_sys (in its bare Hamiltonian), bath thermal at t_bath."""

    n = bath.n_modes + 1
    var_q = np.concatenate([[t_sys / w0**2], t_bath / bath.omegas**2])
    var_p = np.concatenate([[t_sys], np.full(bath.n_modes, t_bath)])
    return np.diag(np.concatenate([var_q, var_p]))


def bare_bath_energy(cov: np.ndarray, bath: "OhmicBath") -> float:
    n = bath.n_modes + 1
    w2 = bath.omegas**2
    return 0.5 * float(np.sum(np.diag(cov)[n + 1:] + w2 * np.diag(cov)[1:n]))


def trace_budget(w0: float, bath: "OhmicBath", t_sys: float, t_bath: float,
                 times: np.ndarray) -> list[TraceBudget]:
    """Exact Sigma = I + D bookkeeping along the closed evolution.

    The system is coupled through the full Caldeira-Leggett Hamiltonian; the reservoir
    energy Q is that of the bare oscillators, as in the cited identity.
    """

    from scipy.linalg import expm

    a, _ = _l2.generator(w0, bath)
    n = bath.n_modes + 1
    sys_idx = [0, n]
    res_idx = [i for i in range(2 * n) if i not in sys_idx]
    c0 = initial_covariance(w0, bath, t_sys, t_bath)
    s_tot0 = _entropy(c0)
    s_sys0 = _entropy(c0[np.ix_(sys_idx, sys_idx)])
    s_res0 = _entropy(c0[np.ix_(res_idx, res_idx)])
    e_res0 = bare_bath_energy(c0, bath)
    out = []
    for t in times:
        m = expm(a * float(t))
        c = m @ c0 @ m.T
        s_sys = _entropy(c[np.ix_(sys_idx, sys_idx)])
        s_res = _entropy(c[np.ix_(res_idx, res_idx)])
        q = bare_bath_energy(c, bath) - e_res0
        record = s_sys + s_res - _entropy(c)
        potential = -(s_res - s_res0) + q / t_bath
        sigma = (s_sys - s_sys0) + q / t_bath
        out.append(TraceBudget(float(t), sigma, record, potential, s_sys - s_sys0, q, _entropy(c) - s_tot0))
    return out


def relaxation_entropy_production(t_sys: float, t_bath: float) -> float:
    """Weak-coupling long-time limit for one oscillator relaxing from t_sys to t_bath: x - 1 - ln x, x = t_sys/t_bath."""

    x = t_sys / t_bath
    return x - 1.0 - log(x)
