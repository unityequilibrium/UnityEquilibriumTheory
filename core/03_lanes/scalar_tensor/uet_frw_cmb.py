"""The parent action's expansion history back to recombination, and the CMB acoustic angle it gives (wave C2).

Question: T040 confronted the dark-energy w(a) of wave C1 with BAO and supernovae only (no CMB). C1 neglects radiation
and releases psi at z = 99, so it cannot give the angle theta* = r_s(z*) / D_M(z*) that the CMB measures. With
radiation added and psi released deep in the radiation era, (1) does the late-time w(a) of C1 survive, and (2) how far
does the thawing family move theta* away from LambdaCDM at fixed physical densities?

Setting [AI derivation; checked in core/05_tests/physics/test_frw_cmb.py]. The C1 equations (Boisseau et al. 2000,
eqs. 2.4-2.6; kappa = 1, rho_m0 = 1) with radiation rho_r = r a^-4 added as a second minimally coupled fluid:
    3 F H^2 = rho_m + rho_r + pi^2/2 + W - 3 H F' pi
    -2 F dH/dt = rho_m + (4/3) rho_r + pi^2 + F'' pi^2 + F' psi'' - H F' pi
    psi'' + 3 H pi = F' (3 dH/dt + 6 H^2) - W'        (R = 6 (dH/dt + 2 H^2); radiation is traceless)
r = omega_r / omega_m with omega_r = omega_gamma (1 + (7/8)(4/11)^(4/3) N_eff), omega_gamma = 2.4728e-5 (T_CMB =
2.7255 K), N_eff = 3.046; all neutrinos massless (AI simplification). psi is released at rest at z_i = 1e6; above z_i
it is frozen and H^2 = (rho_m + rho_r + W(psi_i)) / (3 F(psi_i)).
CMB angle (standard definitions, e.g. Hu & Sugiyama 1996): theta* = r_s(z*) / D_M(z*) with
    D_M = int_0^z* dz / H,   r_s = int_z*^inf c_s dz / H,   c_s = 1 / sqrt(3 (1 + R_b)),  R_b = (3 omega_b / 4 omega_gamma) a,
and z* from the Hu & Sugiyama (1996) fit in omega_b and omega_m. Both lengths are in the same code units, so theta*
needs no value of H0. Approximations [AI, stated in the result]: z* and the sound speed use the GR fit with the
physical densities an observer infers with today's G; the change of G between recombination and today, G*/G0 =
F0 / F(psi(z*)), is reported, not fed back into z*. No perturbations: this is the background angle only.
Results (numbers in docs/standard/results/R_C2_FRW_CMB_ANGLE.json; omega_b = 0.02237, omega_m = 0.14237, Omega_m =
0.30 as AI reference values, z* = 1091.85 from the fit):
1. xi = 0: releasing the field at z = 1e6 with radiation or at z = 99 without it gives the same w0, wa within 1e-4,
   so the C1 and T040 minimal-coupling family is unchanged.
2. xi != 0: the F' R drive during the matter era moves psi before z = 99, so w0 moves by up to 0.05 from C1
   (xi = 0.02, psi_i = 0.4, m/H0 = 3: w0 = -0.805 here against -0.854 in C1). The T040 best point (xi = -0.003)
   moves by 0.004 in w0.
3. At fixed omega_b, omega_m and Omega_m the thawing family moves theta* from LambdaCDM by +0.57% (T040 best point)
   up to +1.6% on the points computed; Planck measures theta* to about 0.03%, so the CMB will bind once the
   densities are fitted jointly. G at recombination differs from today by 0.08% at the T040 best point.
Nearest known theory: extended quintessence (Perrotta, Baccigalupi, Matarrese 1999; Pettorino & Baccigalupi 2008),
whose CMB analyses use the full Boltzmann code. Not UET-distinct. Natural units, kappa = 1, rho_m0 = 1.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

OMEGA_GAMMA = 2.4728e-5
N_EFF = 3.046
OMEGA_R_OVER_GAMMA = 1.0 + 7.0 / 8.0 * (4.0 / 11.0) ** (4.0 / 3.0) * N_EFF
Z_RELEASE = 1.0e6


@dataclass(frozen=True)
class Model:
    """Parent-action background in units rho_m0 = 1; r = rho_r0 / rho_m0."""
    lambda_eff: float
    m2: float
    lam: float
    xi: float
    r: float

    def F(self, psi):
        return 1.0 + self.xi * psi * psi

    def dF(self, psi):
        return 2.0 * self.xi * psi

    def W(self, psi):
        return self.lambda_eff + 0.5 * self.m2 * psi * psi + 0.25 * self.lam * psi**4

    def dW(self, psi):
        return self.m2 * psi + self.lam * psi**3


def hubble(md: Model, psi, pi, a):
    F, dF = md.F(psi), md.dF(psi)
    S = a**-3 + md.r * a**-4 + 0.5 * pi * pi + md.W(psi)
    return (-3.0 * dF * pi + np.sqrt(9.0 * dF * dF * pi * pi + 12.0 * F * S)) / (6.0 * F)


def accelerations(md: Model, psi, pi, a, H):
    """(dH/dt, psi'') from the two dynamical equations."""
    F, dF = md.F(psi), md.dF(psi)
    A0 = -3.0 * H * pi + 6.0 * dF * H * H - md.dW(psi)
    B0 = -a**-3 - 4.0 / 3.0 * md.r * a**-4 - pi * pi - 2.0 * md.xi * pi * pi + H * dF * pi
    Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
    return Hdot, A0 + 3.0 * dF * Hdot


def _rhs(md: Model, N: float, psi: float, pi: float) -> tuple[float, float]:
    a = math.exp(N)
    H = float(hubble(md, psi, pi, a))
    _, acc = accelerations(md, psi, pi, a, H)
    return pi / H, float(acc) / H


def integrate(md: Model, psi_i: float, steps: int = 6000, z_i: float = Z_RELEASE):
    """Fixed-step RK4 in N = ln a from 1/(1 + z_i) to 1, psi released at rest."""
    N = np.linspace(-math.log1p(z_i), 0.0, steps + 1)
    h = N[1] - N[0]
    y = np.empty((steps + 1, 2))
    psi, pi = psi_i, 0.0
    y[0] = (psi, pi)
    for k in range(steps):
        n = N[k]
        a1, b1 = _rhs(md, n, psi, pi)
        a2, b2 = _rhs(md, n + h / 2, psi + h / 2 * a1, pi + h / 2 * b1)
        a3, b3 = _rhs(md, n + h / 2, psi + h / 2 * a2, pi + h / 2 * b2)
        a4, b4 = _rhs(md, n + h, psi + h * a3, pi + h * b3)
        psi += h / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        pi += h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        y[k + 1] = (psi, pi)
    return N, y


@dataclass(frozen=True)
class Run:
    N: np.ndarray
    psi: np.ndarray
    pi: np.ndarray
    H: np.ndarray
    omega_m0: float
    H0: float


def run(md: Model, psi_i: float, steps: int = 6000) -> Run:
    N, y = integrate(md, psi_i, steps)
    a = np.exp(N)
    H = hubble(md, y[:, 0], y[:, 1], a)
    F0 = float(md.F(y[-1, 0]))
    H0 = float(H[-1])
    return Run(N, y[:, 0], y[:, 1], H, 1.0 / (3.0 * F0 * H0 * H0), H0)


def calibrated(m_over_H0: float, xi: float, psi_i: float, omega_m0: float, r: float, lam: float = 0.0,
               steps: int = 6000) -> tuple[Model, Run]:
    """Lambda_eff and m2 so that today Omega_m = omega_m0 (with today's G) and m / H0 = m_over_H0."""
    H0 = math.sqrt(1.0 / (3.0 * omega_m0))
    lam_eff = 3.0 * H0 * H0 * (1.0 - omega_m0) - r
    for _ in range(60):
        md = Model(lam_eff, (m_over_H0 * H0) ** 2, lam, xi, r)
        rn = run(md, psi_i, steps)
        if abs(rn.omega_m0 - omega_m0) < 1e-11 and abs(rn.H0 - H0) < 1e-11 * H0:
            break
        H0 = rn.H0 * math.sqrt(rn.omega_m0 / omega_m0)
        lam_eff += 3.0 * rn.H0 ** 2 * md.F(rn.psi[-1]) * (rn.omega_m0 - omega_m0)
    return md, rn


def z_star(omega_b: float, omega_m: float) -> float:
    """Hu & Sugiyama (1996) fit for the redshift of last scattering."""
    g1 = 0.0783 * omega_b ** -0.238 / (1.0 + 39.5 * omega_b ** 0.763)
    g2 = 0.560 / (1.0 + 21.1 * omega_b ** 1.81)
    return 1048.0 * (1.0 + 0.00124 * omega_b ** -0.738) * (1.0 + g1 * omega_m ** g2)


def _simpson(y: np.ndarray, h: float) -> float:
    if (len(y) - 1) % 2:
        return _simpson(y[:-1], h) + 0.5 * h * (y[-2] + y[-1])
    return h / 3.0 * (y[0] + y[-1] + 4.0 * y[1:-1:2].sum() + 2.0 * y[2:-1:2].sum())


@dataclass(frozen=True)
class Angle:
    theta_star: float
    z_star: float
    r_s: float
    D_M: float
    G_star_over_G0: float


def cmb_angle(md: Model, rn: Run, omega_b: float, omega_m: float) -> Angle:
    """theta* = r_s / D_M on the run's grid (Simpson), plus the frozen-field tail above z_i."""
    zs = z_star(omega_b, omega_m)
    Ns = -math.log1p(zs)
    h = rn.N[1] - rn.N[0]
    k = int(math.floor((Ns - rn.N[0]) / h))
    # split the grid at N*, interpolating the integrands linearly in the last cell
    a = np.exp(rn.N)
    inv = 1.0 / (a * rn.H)                              # dz/H = -(1/(a H)) dN
    cs = 1.0 / np.sqrt(3.0 * (1.0 + 0.75 * omega_b / OMEGA_GAMMA * a))
    t = (Ns - rn.N[k]) / h
    inv_s = inv[k] + t * (inv[k + 1] - inv[k])
    cs_s = cs[k] + t * (cs[k + 1] - cs[k])
    late = _simpson(inv[k + 1:], h) + 0.5 * (1.0 - t) * h * (inv_s + inv[k + 1])
    early = _simpson((cs * inv)[: k + 1], h) + 0.5 * t * h * (cs[k] * inv[k] + cs_s * inv_s)
    # above z_i: psi frozen, radiation dominated, c_s -> 1/sqrt(3); exact for H^2 = (rho_m + rho_r + W) / (3 F)
    a_i = a[0]
    F_i = float(md.F(rn.psi[0]))
    tail = _integral_tail(md, rn.psi[0], F_i, a_i, omega_b)
    psi_s = float(np.interp(Ns, rn.N, rn.psi))
    return Angle((early + tail) / late, zs, early + tail, late, float(md.F(rn.psi[-1]) / md.F(psi_s)))


def _integral_tail(md: Model, psi_i: float, F_i: float, a_i: float, omega_b: float, n: int = 400) -> float:
    """int_0^{a_i} c_s da / (a^2 H) with the frozen-field H, by Gauss-Legendre in a."""
    x, wts = np.polynomial.legendre.leggauss(n)
    aa = 0.5 * a_i * (x + 1.0)
    H = np.sqrt((aa**-3 + md.r * aa**-4 + md.W(psi_i)) / (3.0 * F_i))
    cs = 1.0 / np.sqrt(3.0 * (1.0 + 0.75 * omega_b / OMEGA_GAMMA * aa))
    return float(0.5 * a_i * np.sum(wts * cs / (aa * aa * H)))


def theta_lcdm(omega_b: float, omega_m: float, Om: float, n: int = 200000) -> float:
    """Independent route: LambdaCDM theta* by direct quadrature in a (no ODE)."""
    r = OMEGA_GAMMA * OMEGA_R_OVER_GAMMA / omega_m
    H0sq = 1.0 / (3.0 * Om)
    lam = 3.0 * H0sq - 1.0 - r

    def H(a):
        return np.sqrt((a**-3 + r * a**-4 + lam) / 3.0)

    a_s = 1.0 / (1.0 + z_star(omega_b, omega_m))
    x, w = np.polynomial.legendre.leggauss(2000)
    # D_M in u = ln a, r_s in a
    u = 0.5 * math.log(a_s) * (1.0 - x)
    au = np.exp(u)
    D = float(0.5 * -math.log(a_s) * np.sum(w / (au * H(au))))
    aa = 0.5 * a_s * (x + 1.0)
    cs = 1.0 / np.sqrt(3.0 * (1.0 + 0.75 * omega_b / OMEGA_GAMMA * aa))
    rs = float(0.5 * a_s * np.sum(w * cs / (aa * aa * H(aa))))
    return rs / D


def r_ratio(omega_m: float) -> float:
    return OMEGA_GAMMA * OMEGA_R_OVER_GAMMA / omega_m


# Reference densities for the scan (AI choice: Planck 2018 TT,TE,EE+lowE+lensing central values, used only to place
# the comparison, not as data being fitted): omega_b = 0.02237, omega_m = omega_b + omega_c = 0.14237.
OMEGA_B_REF, OMEGA_M_REF = 0.02237, 0.14237


def report(steps: int = 6000) -> dict:
    """Numbers of the result record."""
    from importlib import import_module
    c1 = import_module("core.03_lanes.scalar_tensor.uet_frw_background")
    out: dict = {"points": []}
    r = r_ratio(OMEGA_M_REF)
    # T040 best point and its neighbours on the T040 grid (AI selection)
    pts = [(0.30, 0.6, 2.0, -0.003), (0.30, 0.6, 2.0, 0.0), (0.30, 0.6, 2.0, 0.01), (0.30, 1.0, 2.0, 0.0),
           (0.30, 0.4, 3.0, 0.02), (0.30, 1.0, 1.0, 0.03)]
    for Om, psi_i, m_h, xi in pts:
        md, rn = calibrated(m_h, xi, psi_i, Om, r, steps=steps)
        ang = cmb_angle(md, rn, OMEGA_B_REF, OMEGA_M_REF)
        th0 = theta_lcdm(OMEGA_B_REF, OMEGA_M_REF, Om)
        # late-time w(a) as in C1 (radiation dropped, release at z = 99) for comparison
        bg, h = c1.calibrated(m_h, xi, psi_i, omega_m0=Om, steps=1500)
        w0_c1, wa_c1 = c1.cpl_fit(h)
        sel = rn.N >= math.log(0.4)                       # C1 CPL window (AI choice)
        a, psi, pi, H = np.exp(rn.N[sel]), rn.psi[sel], rn.pi[sel], rn.H[sel]
        F0, dF0 = float(md.F(rn.psi[-1])), float(md.dF(rn.psi[-1]))
        Hdot, _ = accelerations(md, psi, pi, a, H)
        rho_de = 3.0 * F0 * H**2 - a**-3 - r * a**-4
        p_de = -2.0 * F0 * Hdot - a**-3 - 4.0 / 3.0 * r * a**-4 - rho_de
        A = np.column_stack([np.ones(sel.sum()), 1.0 - a])
        (w0, wa), *_ = np.linalg.lstsq(A, p_de / rho_de, rcond=None)
        gamma_m1 = -dF0 * dF0 / (F0 + 2.0 * dF0 * dF0)
        gdot = -dF0 * float(rn.pi[-1]) / F0 / rn.H0
        lo, hi = c1.T001_XI_EXCLUDED
        allowed = abs(gamma_m1) < c1.CASSINI_GAMMA and abs(gdot) < c1.LLR_GDOT_H0 and not (lo <= xi <= hi)
        out["points"].append({"omega_m0": Om, "psi_i": psi_i, "m_over_H0": m_h, "xi": xi,
                              "100theta_star": 100 * ang.theta_star, "100theta_star_lcdm": 100 * th0,
                              "dtheta_over_theta": ang.theta_star / th0 - 1.0, "G_star_over_G0": ang.G_star_over_G0,
                              "w0": float(w0), "wa": float(wa), "w0_c1": w0_c1, "wa_c1": wa_c1,
                              "allowed_today": "yes" if allowed else "no"})
    out["z_star_ref"] = z_star(OMEGA_B_REF, OMEGA_M_REF)
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
