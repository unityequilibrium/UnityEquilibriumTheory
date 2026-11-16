"""Wave B7: the burn power P of layer 3 computed from the closed system, not assumed.

Wave A4 (persistence/uet_layer2_to_3.py) showed that layer 3 follows from dF/dt = -P(F), so
tau = integral_{F_min}^{F0} dF / P(F), and tau = F/P only when P is held constant. It left P itself
as an input: FIDELITY_MATRIX point 4 notes that no P = T sigma had been computed from dynamics.

Here P is derived from the same closed system as wave A3 (Caldeira-Leggett: one mode of the
matter/response sector plus an ohmic bath, total energy exactly conserved, which is the layer-1
exchange ledger Q_m + Q_response = 0). For the system's phase-space density rho(x, p):

1. Free energy relative to the Gibbs state rho_eq ~ exp(-H_sys/T) of the bath temperature T is
       F = <H_sys> - T S - F_eq = T KL(rho || rho_eq)  >= 0,
   the work still extractable from the system against that bath.
2. In the Markov limit the reduced dynamics is the Kramers equation, and
       dF/dt = -P,     P = gamma < (p + T d_p ln rho)^2 > = T sigma  >= 0,
   with sigma the entropy production rate (system + bath). This is the second law for the subsystem
   and the reversed-Landauer write rate is P / (T ln 2) bits per unit time.
3. For a Gaussian rho with mean mu and covariance Sigma (exact for this linear model):
       F = (T/2)[tr(Sigma_eq^-1 Sigma) - 2 + mu^T Sigma_eq^-1 mu + ln det Sigma_eq - ln det Sigma]
       P = gamma [mu_p^2 + Sigma_pp - 2T + T^2 (Sigma^-1)_pp]
   A displaced thermal state gives F = mechanical energy of the mean and P = gamma mu_p^2, the A3
   burn power gamma x'^2.
4. Layer 3 then needs no extra assumption: tau = integral dF / P along the trajectory, with P from 2.

The check (05_tests/physics/test_free_energy_burn.py) propagates the exact mean and covariance of the
closed Hamiltonian system and compares -dF/dt with the formula for P, which is only an open-system
(Markov) statement. Units: dimensionless, w0 = 1, k_B = 1.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

_A3_PATH = Path(__file__).resolve().parent / "uet_layer2_dissipation.py"
_spec = importlib.util.spec_from_file_location("uet_layer2_dissipation", _A3_PATH)
a3 = sys.modules.setdefault("uet_layer2_dissipation", importlib.util.module_from_spec(_spec))
if not hasattr(a3, "OhmicBath"):
    _spec.loader.exec_module(a3)

OhmicBath = a3.OhmicBath


def equilibrium_covariance(w0: float, temperature: float) -> np.ndarray:
    return np.diag([temperature / w0**2, temperature])


def relative_free_energy(mu: np.ndarray, sigma: np.ndarray, w0: float, temperature: float) -> float:
    """F - F_eq = T KL(N(mu, Sigma) || Gibbs) for the system mode (x, p)."""
    seq = equilibrium_covariance(w0, temperature)
    inv = np.linalg.inv(seq)
    kl = 0.5 * (np.trace(inv @ sigma) - 2.0 + mu @ inv @ mu + np.log(np.linalg.det(seq) / np.linalg.det(sigma)))
    return float(temperature * kl)


def burn_power(mu: np.ndarray, sigma: np.ndarray, gamma: float, temperature: float) -> float:
    """P = gamma <(p + T d_p ln rho)^2> for a Gaussian density (Kramers, k_B = 1)."""
    return float(gamma * (mu[1] ** 2 + sigma[1, 1] - 2.0 * temperature + temperature**2 * np.linalg.inv(sigma)[1, 1]))


def initial_moments(bath, mu_sys: np.ndarray, sigma_sys: np.ndarray, temperature: float):
    """Full mean and covariance: system Gaussian, bath thermal around q_k = c_k x / w_k^2 (A3 convention)."""
    n = bath.n_modes + 1
    w, c = bath.omegas, bath.couplings
    lift = np.zeros((2 * n, 2))
    lift[0, 0] = 1.0
    lift[1:n, 0] = c / w**2
    lift[n, 1] = 1.0
    noise = np.zeros(2 * n)
    noise[1:n] = temperature / w**2
    noise[n + 1:] = temperature
    return lift @ mu_sys, lift @ sigma_sys @ lift.T + np.diag(noise)


def propagate_moments(w0: float, bath, mu0: np.ndarray, sigma0: np.ndarray, dt: float, steps: int):
    """Exact closed evolution of the mean and covariance; returns system (mu, Sigma) at each step."""
    a, _ = a3.generator(w0, bath)
    phi = expm(a * dt)
    n = bath.n_modes + 1
    idx = [0, n]
    rows = np.eye(2 * n)[idx]  # rows of Phi(t) for x and p; Phi(t + dt) rows = rows(t) @ phi
    mus, sigs = [], []
    for _ in range(steps + 1):
        mus.append(rows @ mu0)
        sigs.append(rows @ sigma0 @ rows.T)
        rows = rows @ phi
    return np.array(mus), np.array(sigs)


def lifetime_from_burn(f_values: np.ndarray, p_values: np.ndarray, f_min: float) -> float:
    """tau = integral_{F_min}^{F0} dF / P along a monotone trajectory (trapezoid in F)."""
    keep = f_values >= f_min
    f, p = f_values[keep], p_values[keep]
    return float(np.sum(0.5 * (1.0 / p[1:] + 1.0 / p[:-1]) * (f[:-1] - f[1:])))
