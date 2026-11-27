"""The portal inside cosmology: what one psi in two lanes forces (wave J1, topic 0.23 STRESS_13).

Question: waves C1-C3, T040 and T041 treat psi as dark energy with the portal switched off (g_c = 0); the portal
lane (T005, T016, T019) treats the same psi as the mediator of a force between nucleons. If psi is one field, both
hold at once: the cosmological psi has m_psi ~ 3 H0, so its portal range is the Hubble radius and the MICROSCOPE
bound g_c <= 1.16e-15 eV (T016) applies; and the baryons of the universe push psi through the portal. How large is
that push, and how much does it change w(a)?

Setting [AI derivation; checked in core/05_tests/physics/test_portal_cosmology.py]. With chi = nucleon the trilinear
portal (1/2) g_c psi |chi|^2 shifts the nucleon mass, m_eff^2 = m_chi^2 - g_c psi, so pressureless baryons have
rho_b(a, psi) = f_b a^-3 sqrt(1 - c psi) / sqrt(1 - c psi_ref) with c = g_c M_Pl / m_chi^2 (psi in units of the
reduced Planck mass, code units of uet_frw_cmb.py, rho_m0 = 1, f_b = omega_b / omega_m). This is coupled
quintessence (Amendola 2000) with a field-dependent baryon mass. The field equation gains -d rho_b / d psi, baryon
energy obeys d rho_b/dt = -3 H rho_b + (d rho_b / d psi) psi', and the Friedmann equations are unchanged in form, so
the constraint is preserved (checked). Dark matter is left uncoupled (AI choice: the portal lane is for nucleons).
Numbers (T041 best point; g_c at the T016 bound):
    c = 3.2e-6, force ratio |d rho_b / d psi| / W'(psi_i) = 2.5e-7 today (larger in the past, as rho_b ~ a^-3),
    1 + w0 (instantaneous, a = 1) changes from 0.020912 to 0.020913, a relative change of 5.1e-5.
Combining the two lanes therefore forces a coupled-quintessence term, but the lab bound makes its effect on w0
about 5e-5 of the thawing signal, far below what BAO, supernovae or the CMB resolve: the matter-space exchange
cannot be seen in cosmology if one psi serves both lanes.
Nearest known theory: coupled quintessence / varying-mass baryons. Not UET-distinct.
"""

from __future__ import annotations

import importlib
import math
from dataclasses import dataclass

import numpy as np

cmbm = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_cmb")

G_C_T016_EV = 1.16e-15
M_NUCLEON_EV = 0.938e9
M_PL_REDUCED_EV = 2.435e27
H0_REF = 1.0 / math.sqrt(3.0 * 0.30)


def c_portal(g_c_eV: float = G_C_T016_EV) -> float:
    return g_c_eV * M_PL_REDUCED_EV / M_NUCLEON_EV**2


@dataclass(frozen=True)
class Coupled:
    md: object          # cmbm.Model (radiation, Lambda_eff, m2, lam, xi)
    f_b: float          # baryon share of rho_m0
    c: float            # portal strength in Planck units
    psi_ref: float      # normalisation: rho_b(a = 1, psi_ref) = f_b

    def rho_b(self, a, psi):
        return self.f_b * a**-3 * np.sqrt(1.0 - self.c * psi) / math.sqrt(1.0 - self.c * self.psi_ref)

    def drho_b(self, a, psi):
        return -0.5 * self.c * self.rho_b(a, psi) / (1.0 - self.c * psi)


def hubble(cp: Coupled, psi, pi, a):
    md = cp.md
    F, dF = md.F(psi), md.dF(psi)
    S = (1.0 - cp.f_b) * a**-3 + cp.rho_b(a, psi) + md.r * a**-4 + 0.5 * pi * pi + md.W(psi)
    return (-3.0 * dF * pi + np.sqrt(9.0 * dF * dF * pi * pi + 12.0 * F * S)) / (6.0 * F)


def accelerations(cp: Coupled, psi, pi, a, H):
    md = cp.md
    F, dF = md.F(psi), md.dF(psi)
    rho_m = (1.0 - cp.f_b) * a**-3 + cp.rho_b(a, psi)
    A0 = -3.0 * H * pi + 6.0 * dF * H * H - md.dW(psi) - cp.drho_b(a, psi)
    B0 = -rho_m - 4.0 / 3.0 * md.r * a**-4 - pi * pi - 2.0 * md.xi * pi * pi + H * dF * pi
    Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
    return Hdot, A0 + 3.0 * dF * Hdot


def integrate(cp: Coupled, psi_i: float, steps: int = 3000, z_i: float = cmbm.Z_RELEASE):
    N = np.linspace(-math.log1p(z_i), 0.0, steps + 1)
    h = N[1] - N[0]

    def rhs(n, p, q):
        a = math.exp(n)
        H = float(hubble(cp, p, q, a))
        _, acc = accelerations(cp, p, q, a, H)
        return q / H, float(acc) / H

    psi, pi = psi_i, 0.0
    for k in range(steps):
        n = N[k]
        a1, b1 = rhs(n, psi, pi)
        a2, b2 = rhs(n + h / 2, psi + h / 2 * a1, pi + h / 2 * b1)
        a3, b3 = rhs(n + h / 2, psi + h / 2 * a2, pi + h / 2 * b2)
        a4, b4 = rhs(n + h, psi + h * a3, pi + h * b3)
        psi += h / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        pi += h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
    return psi, pi


def one_plus_w0(cp: Coupled, psi_i: float, steps: int = 3000) -> float:
    psi, pi = integrate(cp, psi_i, steps)
    md = cp.md
    H = float(hubble(cp, psi, pi, 1.0))
    Hdot, _ = accelerations(cp, psi, pi, 1.0, H)
    F0 = float(md.F(psi))
    rho_m = (1.0 - cp.f_b) + float(cp.rho_b(1.0, psi))
    rde = 3.0 * F0 * H * H - rho_m - md.r
    pde = -2.0 * F0 * float(Hdot) - rho_m - 4.0 / 3.0 * md.r - rde
    return 1.0 + pde / rde


T041_BEST = dict(lambda_eff=2.1770801724463746, omega_b=0.022466398489376642, omega_m=0.14342155069669388,
                 psi_i=0.1, m_label=3.0, xi=0.05)


def t041_coupled(c: float) -> tuple[Coupled, float]:
    p = T041_BEST
    md = cmbm.Model(p["lambda_eff"], (p["m_label"] * H0_REF) ** 2, 0.0, p["xi"], cmbm.r_ratio(p["omega_m"]))
    return Coupled(md, p["omega_b"] / p["omega_m"], c, p["psi_i"]), p["psi_i"]


def report(steps: int = 3000) -> dict:
    c = c_portal()
    cp0, psi_i = t041_coupled(0.0)
    cp1, _ = t041_coupled(c)
    w0, w1 = one_plus_w0(cp0, psi_i, steps), one_plus_w0(cp1, psi_i, steps)
    force_ratio = abs(float(cp1.drho_b(1.0, psi_i))) / float(cp1.md.dW(psi_i))
    return {"c_portal": c, "force_ratio_today": force_ratio, "one_plus_w0_uncoupled": w0,
            "one_plus_w0_coupled": w1, "relative_change": (w1 - w0) / w0}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
