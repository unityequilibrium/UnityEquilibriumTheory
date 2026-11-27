"""Can an attractor remove the parent action's dependence on initial conditions? (wave D1, STRESS_12 option D)

Question: the T041 fit needs the initial field value psi_i (best point on the grid edge, psi_i = 0.1). Tracker and
attractor solutions (Steinhardt, Wang & Zlatev 1999; Copeland, Liddle & Wands 1998) make late-time dark energy
independent of initial conditions. Does the parent action have one, and what does it fix?

Results [AI derivation; checked in core/05_tests/physics/test_attractor.py].
1. Parent action as it stands (thawing class, Caldwell & Linder 2005): with m_psi << H early the field is frozen,
   so the late-time displacement is linear in psi_i and 1 + w0 = C(m/H0, Omega_m) psi_i^2 for small psi_i.
   Measured with the C2 code (xi_c = 0, m/H0 = 2, Omega_m = 0.30): C = 0.2556, exponent 2.0000 between
   psi_i = 0.01 and 0.08. Data on w(a) therefore fix only C psi_i^2: psi_i is not removed, it is degenerate with m.
   The tracker condition Gamma = W W'' / W'^2 > 1 with a rolling field (Steinhardt et al.) needs a potential steep
   at small field (inverse power or exponential); the polynomial W = Lambda_eff + m^2 psi^2 / 2 + lambda psi^4 / 4
   of the card has none.
2. An exponential potential does appear one step away from the card. Keep the scale-invariant restriction of wave S1
   (F = xi psi^2) and break it only with the card's own mass term m^2 psi^2 / 2. In the Einstein frame
   (M_Pl = 1) the canonical field is sigma = sqrt((1 + 6 xi) / xi) ln psi and
       V_E = W / F^2 = (m^2 / (2 xi^2)) exp(-lambda_E sigma),   lambda_E = 2 sqrt(xi / (1 + 6 xi)),
   the cosmon of Wetterich (1988). Its late-time attractor (Copeland, Liddle & Wands 1998) has w = -1 + lambda_E^2 / 3
   whatever the initial conditions, for lambda_E^2 < 2.
3. With matter on the Jordan metric, Cassini (xi <= 5.75e-6, wave S1) gives lambda_E <= 4.8e-3 and
   1 + w <= 7.7e-6: the attractor is indistinguishable from a cosmological constant. Its height is still set by
   m^2 / (xi^2 psi0^2) ~ rho_Lambda / M_Pl^4 = 7.2e-121, so the attractor removes psi_i but not the vacuum-energy
   tuning.
Nearest known theory: thawing quintessence (item 1), the cosmon / exponential quintessence (items 2-3).
Not UET-distinct. The S1-plus-mass hybrid of item 2 is an AI choice, not the Theory Card.
"""

from __future__ import annotations

import math

import numpy as np

CASSINI_XI_MAX = 2.3e-5 / (4.0 - 8.0 * 2.3e-5)     # wave S1


def lambda_E(xi: float) -> float:
    return 2.0 * math.sqrt(xi / (1.0 + 6.0 * xi))


def sigma_of_psi(xi: float, psi: float) -> float:
    """Einstein-frame canonical field for L = xi psi^2 R / 2 - (grad psi)^2 / 2 (M_Pl = 1 in the Einstein frame)."""
    return math.sqrt((1.0 + 6.0 * xi) / xi) * math.log(psi)


def dsigma_dpsi_general(F, dF, psi: float) -> float:
    """sqrt((F + 3 F'^2 / 2) / F^2) for any F (standard frame change, e.g. Faraoni 2004)."""
    f, d = F(psi), dF(psi)
    return math.sqrt((f + 1.5 * d * d) / (f * f))


def V_E(xi: float, m2: float, psi: float) -> float:
    F = xi * psi * psi
    return 0.5 * m2 * psi * psi / (F * F)


def w_attractor(lam: float) -> float:
    return -1.0 + lam * lam / 3.0


def exponential_quintessence(lam: float, x0: float, y0: float, N: float = 40.0, steps: int = 8000) -> tuple[float, float]:
    """Copeland-Liddle-Wands autonomous system without matter is trivial; with dust:
    x' = -3x + lam sqrt(3/2) y^2 + (3/2) x (2x^2 + (1 - x^2 - y^2)),  y' = -lam sqrt(3/2) x y + (3/2) y (2x^2 + 1 - x^2 - y^2).
    Returns (w_phi, Omega_phi) after N e-folds (RK4)."""
    c = lam * math.sqrt(1.5)

    def f(v):
        x, y = v
        g = 1.5 * (2.0 * x * x + (1.0 - x * x - y * y))
        return np.array([-3.0 * x + c * y * y + x * g, -c * x * y + y * g])

    v = np.array([x0, y0])
    h = N / steps
    for _ in range(steps):
        k1 = f(v); k2 = f(v + h / 2 * k1); k3 = f(v + h / 2 * k2); k4 = f(v + h * k3)
        v = v + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    x, y = v
    om = x * x + y * y
    return (x * x - y * y) / om, om


def thawing_one_plus_w0(psi_i: float, m_over_H0: float = 2.0, omega_m0: float = 0.30, steps: int = 3000) -> float:
    """1 + w today of the card's thawing field (xi_c = 0) from the C2 background code."""
    import importlib
    c = importlib.import_module("core.03_lanes.scalar_tensor.uet_frw_cmb")
    r = c.r_ratio(c.OMEGA_M_REF)
    md, rn = c.calibrated(m_over_H0, 0.0, psi_i, omega_m0, r, steps=steps)
    a, H = math.exp(rn.N[-1]), float(rn.H[-1])
    Hdot, _ = c.accelerations(md, rn.psi[-1], rn.pi[-1], a, H)
    F0 = float(md.F(rn.psi[-1]))
    rde = 3.0 * F0 * H * H - a**-3 - r * a**-4
    pde = -2.0 * F0 * float(Hdot) - a**-3 - 4.0 / 3.0 * r * a**-4 - rde
    return 1.0 + pde / rde


def report() -> dict:
    lam_max = lambda_E(CASSINI_XI_MAX)
    w1, w8 = thawing_one_plus_w0(0.01), thawing_one_plus_w0(0.08)
    return {"thawing_C_m2_Om030": w1 / 0.01**2, "thawing_exponent": math.log(w8 / w1) / math.log(8.0),
            "lambda_E_at_cassini": lam_max, "one_plus_w_attractor_at_cassini": lam_max**2 / 3.0,
            "rho_lambda_over_mpl4": 7.16e-121}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
