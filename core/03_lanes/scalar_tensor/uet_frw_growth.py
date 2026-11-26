"""Growth of matter perturbations in the parent action's expansion history (wave C3).

Question: T040 and T041 tested only the background (distances). The same action also fixes how fast matter clumps:
the coupling F(psi) R changes the gravitational constant that perturbations feel. At the best points of T040 and
T041, how much does the linear growth of structure differ from LambdaCDM with the same Omega_m, and is the change
large enough for growth data (f sigma8, S8) to see?

Setting [AI derivation from the literature; checked in core/05_tests/physics/test_frw_growth.py]. Action of wave C1
and C2 (kappa = 1): L = F(psi) R / 2 - (d psi)^2 / 2 - W(psi) + L_m, F = 1 + xi psi^2. Newtonian gauge
ds^2 = -(1 + 2 Phi) dt^2 + a^2 (1 - 2 Psi) dx^2, field perturbation dpsi, X = rho_m delta_m. On sub-horizon scales
in the quasi-static limit (time derivatives of perturbations dropped against k/a), and on scales well inside the
Compton length of psi (k/a >> m, so W'' and F'' R drop out), the field equations give the linear system
    F (Psi - Phi) = F' dpsi                                  (traceless ij part)
    2 F (k/a)^2 Psi = -X + (k/a)^2 F' dpsi                    (00 part)
    (2 F + 3 F'^2) (k/a)^2 dpsi = F' X                        (field equation with the trace for delta R)
whose solution is (Boisseau, Esposito-Farese, Polarski & Starobinsky 2000, eq. 2.10; Tsujikawa 2007)
    (k/a)^2 Phi = -(X / 2) g,   g(F, F') = (2 F + 4 F'^2) / (F (2 F + 3 F'^2)),
    Psi / Phi = (F + F'^2) / (F + 2 F'^2) = gamma_PPN  (the Cassini quantity of C1).
Matter (CDM and baryons together, AI simplification) obeys delta'' + 2 H delta' = -(k/a)^2 Phi, i.e. in N = ln a
    D_NN + (2 + dH/dt / H^2) D_N = g rho_m D / (2 H^2),        rho_m = a^-3 (code units, rho_m0 = 1).
The background (psi, pi, H, dH/dt) is that of wave C2 (uet_frw_cmb.py, radiation included); the growth equation is
integrated with it by the same RK4 in N from z = 1e6. Initial condition: the Meszaros growing mode
D = r + 1.5 a, D_N = 1.5 a (r = rho_r0 / rho_m0), exact for matter plus smooth radiation with constant G; with
F frozen at F(psi_i) early on, the error is a decaying mode of relative size about xi psi_i^2.
Observables (AI choice): mu(a) = g(a) / g(today) is G for clustering relative to the Newton constant measured today
in the lab (massless limit, valid since 1/m is Gpc-scale); D(today) / D_LCDM(today) with the same early amplitude
(a proxy for sigma8 and S8 when the CMB fixes the primordial amplitude); f = dln D / dN and f / f_LCDM at z = 0, 0.5,
1; growth index gamma0 = ln f / ln Omega_m(a) today. The LambdaCDM comparator is the same code with psi_i = 0.
Not computed: the transfer function, the k dependence near the Compton scale, baryon-CDM separation, massive
neutrinos, non-linear growth.
Results (numbers in docs/standard/results/R_C3_FRW_GROWTH.json; same Omega_m and early amplitude as LambdaCDM):
1. T041 best point (xi = 0.05, psi_i = 0.1, m/H0 = 3.06): D today 0.44% below LambdaCDM, f D at z = 0.5 (the
   f sigma8 proxy) 1.1% below, growth index gamma0 = 0.5555 against 0.5545; mu - 1 = -0.1% at z = 1.
2. The other C2 points allowed today: D today 1.5% to 4.3% below LambdaCDM, f D at z = 0.5 3.2% to 8.9% below.
   The suppression comes mostly from the background (xi = 0 gives nearly the same numbers); the coupling changes G
   for clustering by at most 0.32% on allowed points.
3. Every allowed point grows structure more slowly than LambdaCDM; the one point that grows faster (xi = 0.03,
   psi_i = 1, m/H0 = 1) fails Cassini today (gamma - 1 = -6.5e-3).
Nearest known theory: extended
quintessence (Perrotta, Baccigalupi & Matarrese 1999; Riazuelo & Uzan 2002); growth in scalar-tensor dark energy
(Boisseau et al. 2000; Esposito-Farese & Polarski 2001; Tsujikawa 2007). Not UET-distinct.
"""

from __future__ import annotations

import importlib
import math
from dataclasses import dataclass

import numpy as np

cmbm = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_cmb")

H0_REF = 1.0 / math.sqrt(3.0 * 0.30)   # H0 of Omega_m = 0.30 in code units; T040 and T041 measure m against it


def g_eff(F, dF):
    """G felt by matter in units of 1 / (8 pi) with kappa = 1: (2 F + 4 F'^2) / (F (2 F + 3 F'^2))."""
    return (2.0 * F + 4.0 * dF * dF) / (F * (2.0 * F + 3.0 * dF * dF))


def quasi_static(F: float, dF: float, X: float = 1.0, k2: float = 1.0) -> tuple[float, float, float]:
    """(Phi, Psi, dpsi) from the three sub-horizon equations solved as a linear system (independent route)."""
    A = np.array([[-F, F, -dF],
                  [0.0, 2.0 * F * k2, -k2 * dF],
                  [0.0, 0.0, (2.0 * F + 3.0 * dF * dF) * k2]])
    b = np.array([0.0, -X, dF * X])
    Phi, Psi, dpsi = np.linalg.solve(A, b)
    return float(Phi), float(Psi), float(dpsi)


def _rhs(md, N: float, y: np.ndarray) -> np.ndarray:
    psi, pi, D, DN = y
    a = math.exp(N)
    H = float(cmbm.hubble(md, psi, pi, a))
    Hdot, acc = cmbm.accelerations(md, psi, pi, a, H)
    g = g_eff(md.F(psi), md.dF(psi))
    return np.array([pi / H, float(acc) / H, DN,
                     -(2.0 + float(Hdot) / (H * H)) * DN + 0.5 * g * a**-3 * D / (H * H)])


@dataclass(frozen=True)
class Growth:
    N: np.ndarray
    psi: np.ndarray
    pi: np.ndarray
    D: np.ndarray
    DN: np.ndarray
    H: np.ndarray


def integrate(md, psi_i: float, steps: int = 6000, z_i: float = cmbm.Z_RELEASE) -> Growth:
    """RK4 in N for (psi, pi, D, D_N) from 1/(1 + z_i) to 1; psi at rest, D on the Meszaros growing mode."""
    N = np.linspace(-math.log1p(z_i), 0.0, steps + 1)
    h = N[1] - N[0]
    a_i = math.exp(N[0])
    y = np.array([psi_i, 0.0, md.r + 1.5 * a_i, 1.5 * a_i])
    out = np.empty((steps + 1, 4))
    out[0] = y
    for k in range(steps):
        n = N[k]
        k1 = _rhs(md, n, y)
        k2 = _rhs(md, n + h / 2, y + h / 2 * k1)
        k3 = _rhs(md, n + h / 2, y + h / 2 * k2)
        k4 = _rhs(md, n + h, y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[k + 1] = y
    H = cmbm.hubble(md, out[:, 0], out[:, 1], np.exp(N))
    return Growth(N, out[:, 0], out[:, 1], out[:, 2], out[:, 3], np.asarray(H))


def heath_lcdm(a: float, omega_m0: float) -> float:
    """Growing mode of LambdaCDM without radiation (Heath 1977): D = (5/2) Om E(a) int_0^a da' / (a' E)^3."""
    from scipy.integrate import quad
    E = lambda x: math.sqrt(omega_m0 * x**-3 + 1.0 - omega_m0)
    val, _ = quad(lambda x: (x * E(x)) ** -3, 0.0, a, epsabs=0.0, epsrel=1e-13, limit=200)
    return 2.5 * omega_m0 * E(a) * val


def _at(gr: Growth, z: float, arr: np.ndarray) -> float:
    zz = np.exp(-gr.N) - 1.0
    return float(np.interp(z, zz[::-1], arr[::-1]))


def summary(md, psi_i: float, steps: int = 6000) -> dict:
    """Growth numbers of one model against LambdaCDM with the same Omega_m today and the same r."""
    gr = integrate(md, psi_i, steps)
    F0, dF0 = float(md.F(gr.psi[-1])), float(md.dF(gr.psi[-1]))
    H0 = float(gr.H[-1])
    Om = 1.0 / (3.0 * F0 * H0 * H0)
    # LambdaCDM with the same Omega_m: rho_m0 = 1 fixes H0_ref^2 = 1 / (3 Om); Lambda from closure
    H0r2 = 1.0 / (3.0 * Om)
    ref_md = cmbm.Model(3.0 * H0r2 * (1.0 - Om) - md.r, 0.0, 0.0, 0.0, md.r)
    ref = integrate(ref_md, 0.0, steps)
    g = g_eff(md.F(gr.psi), md.dF(gr.psi))
    mu = g / g[-1]
    f = gr.DN / gr.D
    fr = ref.DN / ref.D
    a = np.exp(gr.N)
    Om_a = a**-3 / (3.0 * md.F(gr.psi) * gr.H**2)
    out = {"Omega_m": Om, "psi_today": float(gr.psi[-1]),
           "mu_z1e3_minus_1": _at(gr, 1.0e3, mu) - 1.0, "mu_z1_minus_1": _at(gr, 1.0, mu) - 1.0,
           "D0_over_D0_lcdm_minus_1": float(gr.D[-1] / ref.D[-1]) - 1.0,
           "gamma0": float(math.log(f[-1]) / math.log(Om_a[-1])),
           "gamma0_lcdm": float(math.log(fr[-1]) / math.log(1.0 / (3.0 * ref.H[-1] ** 2)))}
    for z in (0.0, 0.5, 1.0):
        out[f"f_z{z:g}"] = _at(gr, z, f)
        out[f"f_over_f_lcdm_minus_1_z{z:g}"] = _at(gr, z, f) / _at(ref, z, fr) - 1.0
        # f sigma8 ratio at fixed early amplitude: (f D) / (f D)_LCDM
        out[f"fD_over_lcdm_minus_1_z{z:g}"] = (_at(gr, z, f * gr.D) / _at(ref, z, fr * ref.D)) - 1.0
    gamma_m1 = -dF0 * dF0 / (F0 + 2.0 * dF0 * dF0)
    gdot = -dF0 * float(gr.pi[-1]) / F0 / H0
    out["gamma_ppn_minus_1"] = gamma_m1
    out["gdot_over_G_H0"] = gdot
    out["allowed_today"] = ("yes" if abs(gamma_m1) < 2.3e-5 and abs(gdot) < 2.2e-3 and not (2.0 <= md.xi <= 2.4)
                            else "no")   # Cassini, LLR and T001 bounds as in C1, C2, T040 and T041
    out["m_over_H0"] = math.sqrt(md.m2) / H0
    return out


def report(steps: int = 6000) -> dict:
    """Numbers of the result record: T041 and T040 best points and the C2 points (AI selection)."""
    pts = {
        # T041 best point (R_T041_W_OF_A_CMB_BAO_SN): Lambda_eff, omega_m, psi_i, m/H0 label, xi
        "T041_best": (2.1770801724463746, 0.14342155069669388, 0.1, 3.0, 0.05),
    }
    out: dict = {"points": {}}
    for name, (lam_eff, om, psi_i, m_h, xi) in pts.items():
        md = cmbm.Model(lam_eff, (m_h * H0_REF) ** 2, 0.0, xi, cmbm.r_ratio(om))
        out["points"][name] = {"xi": xi, "psi_i": psi_i, "m_label": m_h, **summary(md, psi_i, steps)}
    r = cmbm.r_ratio(cmbm.OMEGA_M_REF)
    for Om, psi_i, m_h, xi in [(0.30, 0.6, 2.0, -0.003), (0.30, 0.6, 2.0, 0.0), (0.30, 0.6, 2.0, 0.01),
                               (0.30, 1.0, 2.0, 0.0), (0.30, 0.4, 3.0, 0.02), (0.30, 1.0, 1.0, 0.03)]:
        md, _ = cmbm.calibrated(m_h, xi, psi_i, Om, r, steps=1500)
        out["points"][f"C2_xi{xi}_psi{psi_i}_m{m_h}"] = {"xi": xi, "psi_i": psi_i, "m_label": m_h,
                                                         **summary(md, psi_i, steps)}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
