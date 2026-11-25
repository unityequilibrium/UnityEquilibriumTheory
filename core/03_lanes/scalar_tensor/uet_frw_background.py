"""Late-time expansion of a flat FRW universe in the parent action, and the dark-energy w(a) it allows (wave C1).

Question: the Theory Card (section 6) lists w(z) as a candidate observable that was never computed. If psi is
displaced from its minimum, what equation of state w(a) can the action give for the apparent dark energy, and can
the non-minimal coupling xi_c psi^2 R make w < -1 (phantom) once solar-system bounds are applied?

Setting [AI derivation; checked in core/05_tests/physics/test_frw_background.py]. Canonical Jordan-frame action of the
Theory Card with kappa = 8 pi G = 1, a flat FRW metric -dt^2 + a^2 dx^2, pressureless matter rho_m ~ a^-3 coupled
minimally to the metric (chi as ordinary matter, author decision), radiation neglected (late times only):
    L = F(psi) R / 2 - (d psi)^2 / 2 - W(psi),     F = 1 + xi psi^2,
    W = F Lambda + eps rho* + m_psi^2 psi^2/2 + lam psi^4/4 = Lambda_eff + m2 psi^2 / 2 + lam psi^4 / 4,
with Lambda_eff = Lambda + eps rho* and m2 = m_psi^2 + 2 xi Lambda (so how Lambda_eff is split does not matter).
Field equations (Boisseau, Esposito-Farese, Polarski, Starobinsky 2000, eqs. 2.4-2.6):
    3 F H^2 = rho_m + pi^2/2 + W - 3 H F' pi                      (constraint; pi = d psi/dt)
    -2 F dH/dt = rho_m + pi^2 + F'' pi^2 + F' psi'' - H F' pi
    psi'' + 3 H pi = F' (3 dH/dt + 6 H^2) - W'
Apparent dark energy, as an observer who assumes GR with today's G = 1/(8 pi F0) infers it:
    rho_DE = 3 F0 H^2 - rho_m,   p_DE = -2 F0 dH/dt - rho_m - rho_DE,   w = p_DE / rho_DE.
Portal: the force g_c psi n_baryon on cosmological psi is below 1e-24 of the potential force for g_c within the
MICROSCOPE bound (T016), so it is dropped [AI estimate in the result note].

Results (numbers in docs/standard/results/R_C1_FRW_DARK_ENERGY.json):
1. psi = 0 is an exact solution with w = -1: the action contains LambdaCDM.
2. xi = 0: rho_DE + p_DE = pi^2 >= 0, so w >= -1 at all times (thawing quintessence, no phantom crossing).
3. xi = 0, field released at rest (thawing) on the quadratic potential: CPL fit over 0.4 <= a <= 1 (AI window) gives
   wa/(1 + w0) = -1.50 (m/H0 = 0.5), -1.45 (1), -1.23 to -1.30 (2), -0.58 to -0.98 (3, the field starts to oscillate).
4. xi != 0, AI scan grid (xi = +-0.003 to 0.05, psi_i = 0.1 to 1, m/H0 = 1 to 3; 135 runs, 61 allowed today by
   Cassini, lunar laser ranging and T001): no allowed run has w0 < -1, but xi > 0 gives a past phantom phase,
   1 + w down to -0.086 within 0.25 <= a <= 1 (xi = 0.02, psi_i = 0.4, m/H0 = 3), crossing back above -1 at
   z = 1.5 to 2.2 while rho_DE stays positive. xi < 0 gives no phantom phase on the grid. The grid value is a lower
   bound on the allowed depth, not a maximum.
Here m = sqrt(W''(0)) includes 2 xi Lambda; the de Sitter effective mass is m*^2 = m^2 - 4 xi Lambda_eff, so a large
positive xi makes psi tachyonic (excluded by the same bounds).
Nearest known theory: thawing quintessence (Scherrer & Sen 2008; Dutta & Scherrer 2008) and extended quintessence
(Perrotta, Baccigalupi, Matarrese 1999). Not UET-distinct; it is the w(a) family the action allows, which a Test
Card can confront with BAO and supernova data. Natural units, kappa = 1, H in units of today's H0.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

CASSINI_GAMMA = 2.3e-5     # |gamma - 1| bound (Bertotti, Iess, Tortora 2003)
LLR_GDOT_H0 = 2.2e-3       # |dG/dt / G| / H0 bound (Hofmann & Mueller 2018, 2 sigma; H0 = 67.7 km/s/Mpc)
T001_XI_EXCLUDED = (2.0, 2.4)  # xi_c interval excluded for light psi (T001)


@dataclass(frozen=True)
class Background:
    """Parameters in units of today's matter density rho_m0 = 1 (kappa = 1)."""
    lambda_eff: float
    m2: float
    lam: float
    xi: float

    def F(self, psi):
        return 1.0 + self.xi * psi * psi

    def dF(self, psi):
        return 2.0 * self.xi * psi

    def ddF(self, psi):
        return 2.0 * self.xi + 0.0 * psi

    def W(self, psi):
        return self.lambda_eff + 0.5 * self.m2 * psi * psi + 0.25 * self.lam * psi**4

    def dW(self, psi):
        return self.m2 * psi + self.lam * psi**3


def hubble(bg: Background, psi, pi, rho_m):
    """Positive root of the constraint 3 F H^2 + 3 F' pi H - (rho_m + pi^2/2 + W) = 0."""
    F, dF = bg.F(psi), bg.dF(psi)
    S = rho_m + 0.5 * pi * pi + bg.W(psi)
    return (-3.0 * dF * pi + np.sqrt(9.0 * dF * dF * pi * pi + 12.0 * F * S)) / (6.0 * F)


def accelerations(bg: Background, psi, pi, rho_m, H):
    """Solve the two dynamical equations for (dH/dt, psi'')."""
    F, dF, ddF = bg.F(psi), bg.dF(psi), bg.ddF(psi)
    A0 = -3.0 * H * pi + 6.0 * dF * H * H - bg.dW(psi)          # psi'' - 3 F' dH = A0
    B0 = -rho_m - pi * pi - ddF * pi * pi + H * dF * pi           # F' psi'' + 2 F dH = B0
    Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
    return Hdot, A0 + 3.0 * dF * Hdot


def _rhs(bg: Background, N: float, psi: float, pi: float) -> tuple[float, float]:
    """d(psi, pi)/dN with plain floats (the hot loop)."""
    rho_m = math.exp(-3.0 * N)
    F = 1.0 + bg.xi * psi * psi
    dF = 2.0 * bg.xi * psi
    S = rho_m + 0.5 * pi * pi + bg.lambda_eff + 0.5 * bg.m2 * psi * psi + 0.25 * bg.lam * psi**4
    H = (-3.0 * dF * pi + math.sqrt(9.0 * dF * dF * pi * pi + 12.0 * F * S)) / (6.0 * F)
    A0 = -3.0 * H * pi + 6.0 * dF * H * H - (bg.m2 * psi + bg.lam * psi**3)
    B0 = -rho_m - pi * pi - 2.0 * bg.xi * pi * pi + H * dF * pi
    Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
    return pi / H, (A0 + 3.0 * dF * Hdot) / H


def integrate(bg: Background, psi_i: float, z_i: float = 99.0, steps: int = 4000):
    """Fixed-step RK4 in N = ln a from a_i = 1/(1 + z_i) to a = 1, starting at rest (thawing)."""
    N = np.linspace(-math.log1p(z_i), 0.0, steps + 1)
    h = N[1] - N[0]
    y = np.empty((steps + 1, 2))
    y[0] = (psi_i, 0.0)
    psi, pi = psi_i, 0.0
    for k in range(steps):
        n = N[k]
        a1, b1 = _rhs(bg, n, psi, pi)
        a2, b2 = _rhs(bg, n + h / 2, psi + h / 2 * a1, pi + h / 2 * b1)
        a3, b3 = _rhs(bg, n + h / 2, psi + h / 2 * a2, pi + h / 2 * b2)
        a4, b4 = _rhs(bg, n + h, psi + h * a3, pi + h * b3)
        psi += h / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        pi += h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        y[k + 1] = (psi, pi)
    return N, y


@dataclass(frozen=True)
class History:
    a: np.ndarray
    w: np.ndarray
    omega_m0: float
    H0: float
    gamma_minus_1: float
    gdot_over_G_H0: float


def history(bg: Background, psi_i: float, z_i: float = 99.0, steps: int = 4000) -> History:
    N, y = integrate(bg, psi_i, z_i, steps)
    psi, pi = y[:, 0], y[:, 1]
    rho_m = np.exp(-3.0 * N)
    H = hubble(bg, psi, pi, rho_m)
    Hdot, _ = accelerations(bg, psi, pi, rho_m, H)
    F0, dF0 = float(bg.F(psi[-1])), float(bg.dF(psi[-1]))
    rho_de = 3.0 * F0 * H * H - rho_m
    p_de = -2.0 * F0 * Hdot - rho_m - rho_de
    H0 = float(H[-1])
    gamma_m1 = -dF0 * dF0 / (F0 + 2.0 * dF0 * dF0)
    gdot = -dF0 * float(pi[-1]) / F0 / H0  # d ln G_eff / dt at leading order, in units of H0
    return History(np.exp(N), p_de / rho_de, float(rho_m[-1] / (3.0 * F0 * H0 * H0)), H0, gamma_m1, gdot)


def calibrated(m_over_H0: float, xi: float, psi_i: float, omega_m0: float = 0.315, lam: float = 0.0,
               steps: int = 4000) -> tuple[Background, History]:
    """Choose Lambda_eff and m2 so that today Omega_m = omega_m0 and m_psi / H0 = m_over_H0 (m2 includes 2 xi Lambda)."""
    H0 = math.sqrt(1.0 / (3.0 * omega_m0))
    lam_eff = 3.0 * H0 * H0 * (1.0 - omega_m0)
    for _ in range(60):
        bg = Background(lam_eff, (m_over_H0 * H0) ** 2, lam, xi)
        h = history(bg, psi_i, steps=steps)
        if abs(h.omega_m0 - omega_m0) < 1e-10 and abs(h.H0 - H0) < 1e-10 * H0:
            break
        H0 = h.H0 * math.sqrt(h.omega_m0 / omega_m0)
        lam_eff *= (1.0 - omega_m0) / (1.0 - h.omega_m0)
    return bg, h


def cpl_fit(h: History, a_min: float = 0.4) -> tuple[float, float]:
    """Least-squares w0, wa of w(a) = w0 + wa (1 - a) on a_min <= a <= 1 (AI fit window)."""
    sel = h.a >= a_min
    A = np.column_stack([np.ones(sel.sum()), 1.0 - h.a[sel]])
    (w0, wa), *_ = np.linalg.lstsq(A, h.w[sel], rcond=None)
    return float(w0), float(wa)


def allowed_today(h: History, xi: float) -> bool:
    """Cassini, lunar laser ranging and the T001 interval."""
    lo, hi = T001_XI_EXCLUDED
    return abs(h.gamma_minus_1) < CASSINI_GAMMA and abs(h.gdot_over_G_H0) < LLR_GDOT_H0 and not (lo <= xi <= hi)


SCAN_XI = (-0.05, -0.03, -0.01, -0.003, 0.003, 0.01, 0.02, 0.03, 0.05)
SCAN_PSI = (0.1, 0.2, 0.4, 0.7, 1.0)
SCAN_M = (1.0, 2.0, 3.0)


def report(steps: int = 1500) -> dict:
    """Numbers of the result record (AI scan grid; minutes of run time)."""
    out: dict = {"thawing_xi0": [], "scan": []}
    for m_h in (0.5, 1.0, 2.0, 3.0):
        for psi_i in (0.2, 0.6):
            _, h = calibrated(m_h, 0.0, psi_i, steps=steps)
            w0, wa = cpl_fit(h)
            out["thawing_xi0"].append({"m_over_H0": m_h, "psi_i": psi_i, "w0": w0, "wa": wa,
                                       "ratio": wa / (1.0 + w0), "min_1_plus_w": float(np.min(h.w + 1.0))})
    for xi in SCAN_XI:
        for psi_i in SCAN_PSI:
            for m_h in SCAN_M:
                if 1.0 + xi * psi_i * psi_i <= 0.3:
                    continue
                _, h = calibrated(m_h, xi, psi_i, steps=steps)
                w0, wa = cpl_fit(h)
                sel = h.a >= 0.25
                out["scan"].append({"xi": xi, "psi_i": psi_i, "m_over_H0": m_h, "w0": w0, "wa": wa,
                                    "min_1_plus_w": float(np.min(h.w[sel] + 1.0)),
                                    "gamma_minus_1": h.gamma_minus_1, "gdot_over_G_H0": h.gdot_over_G_H0,
                                    "allowed": bool(allowed_today(h, xi))})
    allowed = [r for r in out["scan"] if r["allowed"]]
    out["deepest_allowed_phantom"] = min(allowed, key=lambda r: r["min_1_plus_w"])
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
