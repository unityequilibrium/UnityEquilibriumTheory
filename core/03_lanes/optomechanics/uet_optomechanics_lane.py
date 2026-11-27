"""Optomechanics as a laboratory lane for the layer 1 -> 2 -> 3 chain of the parent action (wave O8, STRESS_13 item 2.3).

Question: STRESS_13 found that the real synthesis content of UET is the chain action -> layer 2 (friction of a psi
mode in a chi bath, C_L2_FROM_ACTION) -> layer 3 (growth a R - 1/tau and threshold R* = 1/(a tau),
C_L3_FROM_ACTION), with one coupling setting every rate, and that it can be tested only where the coupling is
measured. Is there a laboratory system whose interaction has the form of the portal psi |chi|^2?

Lane [AI choice, conditional]. Cavity optomechanics: H = hbar Omega b^dag b - hbar Delta a^dag a - hbar g0 x a^dag a,
x = b + b^dag (Aspelmeyer, Kippenberg & Marquardt 2014, Rev. Mod. Phys. 86, 1391). The interaction x |a|^2 is the
portal (1/2) g_c psi |chi|^2 with psi -> mechanical displacement x, chi -> the complex optical mode a (an O(2)
doublet), g_c -> g0 (up to normalisation). In the classical limit used here the equations are
    da/dt = (i Delta - kappa/2) a + i g0 x a + E,     x'' + Gamma_m x' + Omega^2 x = 2 Omega g0 |a|^2.
Map of the UET quantities [AI derivation; checked in core/05_tests/physics/test_optomechanics_lane.py]:
- layer 2: the light is the bath of the mode x; its friction is the dynamical backaction
      Gamma_opt(Delta) = g^2 [kappa / (kappa^2/4 + (Delta + Omega)^2) - kappa / (kappa^2/4 + (Delta - Omega)^2)],
  g = g0 sqrt(n), n = |a_bar|^2 (RMP eq. 87; Delta is the static-shift-corrected detuning). Red detuning
  (Delta < 0) gives Gamma_opt > 0 (cooling, the layer-2 sink).
- layer 3: with blue detuning the light is a stream that feeds the mode: capture a_i = -Gamma_opt / n per intracavity
  photon, death rate 1/tau = Gamma_m, and the mode persists (self-oscillates) when n > R* = 1/(a_i tau) =
  Gamma_m n / (-Gamma_opt). This is the parametric-instability threshold.
- cross-layer identity forced by the single coupling: Gamma_opt(-Delta) = -Gamma_opt(+Delta) at the same n, so the
  layer-2 cooling rate measured at -Delta fixes the layer-3 threshold at +Delta with no free parameter:
      n*_(+Delta) = Gamma_m n_red / Gamma_cool(-Delta).
Nearest known theory: standard cavity optomechanics and its laser-rate-equation form (Khurgin et al. 2012, PRL 108,
223904). Not UET-distinct: the value of the lane is that the UET chain, composed from separate fields, reproduces
the field's own relation with one coupling.
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OM:
    Omega: float
    kappa: float
    Gamma_m: float
    g0: float


def gamma_opt(om: OM, n: float, Delta: float) -> float:
    g2 = om.g0 * om.g0 * n
    k = om.kappa
    return g2 * (k / (k * k / 4 + (Delta + om.Omega) ** 2) - k / (k * k / 4 + (Delta - om.Omega) ** 2))


def threshold_photons(om: OM, Delta: float) -> float:
    """Layer-3 threshold R* = 1/(a tau) with a = -Gamma_opt/n (blue side only)."""
    per_photon = -gamma_opt(om, 1.0, Delta)
    if per_photon <= 0:
        return math.inf
    return om.Gamma_m / per_photon


def threshold_from_cooling(om: OM, Delta: float, n_red: float) -> float:
    """Cross-layer identity: threshold at +Delta from the cooling rate measured at -Delta."""
    return om.Gamma_m * n_red / gamma_opt(om, n_red, -abs(Delta))


def steady_state(om: OM, Delta0: float, E: float, iters: int = 200) -> tuple[complex, float]:
    """Self-consistent a_bar, x_bar (static radiation-pressure shift)."""
    x = 0.0
    for _ in range(iters):
        a = E / (om.kappa / 2 - 1j * (Delta0 + om.g0 * x))
        x = 2.0 * om.g0 * abs(a) ** 2 / om.Omega
    return a, x


def linear_rates(om: OM, Delta0: float, E: float) -> tuple[float, float, float]:
    """Exact linear stability around the steady state (independent of the weak-coupling formula).
    Returns (mechanical energy decay rate = -2 Re lambda_mech, effective detuning, n)."""
    a, x = steady_state(om, Delta0, E)
    D = Delta0 + om.g0 * x
    ar, ai = a.real, a.imag
    k2, g0, W = om.kappa / 2, om.g0, om.Omega
    # state (Re da, Im da, dx, dv); d(da)/dt = (iD - k/2) da + i g0 a dx
    J = np.array([
        [-k2, -D, -g0 * ai, 0.0],
        [D, -k2, g0 * ar, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [2 * W * g0 * 2 * ar, 2 * W * g0 * 2 * ai, -W * W, -om.Gamma_m],
    ])
    lam = np.linalg.eigvals(J)
    mech = lam[np.argmin(np.abs(np.abs(lam.imag) - W))]
    return -2.0 * mech.real, D, abs(a) ** 2


def time_domain_rate(om: OM, Delta0: float, E: float, t_end: float, dt: float = 0.01, kick: float = 1e-4) -> float:
    """Integrate the full nonlinear classical equations after a small kick and measure the decay rate of the
    mechanical energy (independent route, no linearisation)."""
    a0, x0 = steady_state(om, Delta0, E)
    y = np.array([a0.real, a0.imag, x0 + kick, 0.0])

    def f(s):
        a = complex(s[0], s[1])
        da = (1j * Delta0 - om.kappa / 2) * a + 1j * om.g0 * s[2] * a + E
        acc = -om.Omega**2 * s[2] - om.Gamma_m * s[3] + 2 * om.Omega * om.g0 * abs(a) ** 2
        return np.array([da.real, da.imag, s[3], acc])

    def energy(s):
        return 0.5 * (s[3] ** 2 + om.Omega**2 * (s[2] - x0) ** 2)

    steps = int(t_end / dt)
    t1, t2 = 0.2 * t_end, t_end
    e1 = None
    for k in range(steps):
        k1 = f(y); k2 = f(y + dt / 2 * k1); k3 = f(y + dt / 2 * k2); k4 = f(y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t = (k + 1) * dt
        if e1 is None and t >= t1:
            # average energy over one period to remove the oscillation
            e1, t1 = energy(y), t
    e2 = energy(y)
    return -math.log(e2 / e1) / (t2 - t1)


def report() -> dict:
    om = OM(Omega=1.0, kappa=0.5, Gamma_m=1e-3, g0=1e-3)
    E = 5.0
    rows = {}
    for D0 in (-1.0, 1.0):
        rate, D, n = linear_rates(om, D0, E)
        rows[f"Delta0={D0}"] = {"exact_linear_rate": rate, "Gamma_m_plus_Gamma_opt": om.Gamma_m + gamma_opt(om, n, D), "n": n}
    return {"example_parameters": "Omega = 1, kappa = 0.5, Gamma_m = 1e-3, g0 = 1e-3 (dimensionless)", **rows,
            "threshold_blue_Delta1": threshold_photons(om, 1.0),
            "threshold_from_cooling": threshold_from_cooling(om, 1.0, 100.0)}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
