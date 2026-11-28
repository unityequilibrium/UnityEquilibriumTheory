"""What is left of the parent action when scale symmetry is imposed (wave S1, topic 0.23 STRESS_12 option A).

Question: STRESS_12 found that no principle fixes the parent action's parameters. The closest mechanism in the
literature is scale (dilatation) symmetry broken spontaneously (Higgs-dilaton; Shaposhnikov & Zenhausern 2009;
Garcia-Bellido, Rubio, Shaposhnikov & Zenhausern 2011, arXiv:1107.2163). Without changing the action: which terms
of the parent action survive global scale symmetry, how many parameters are left, and what does the surviving
theory do?

Step 1 [AI derivation; checked in core/05_tests/physics/test_scale_symmetry.py]. A constant Weyl rescaling
g -> s^-2 g, phi -> s phi, chi -> s chi (equivalent to a global dilatation x -> x / s) multiplies sqrt(-g) by s^-4,
R by s^2 and each inverse-metric contraction g^{mu nu} by s^2, while every field brings one power of s. A term
c * phi^a |chi|^b * R^r with d contracted derivative pairs scales as s^(a + b + 2 r + 2 d - 4), so it survives iff
the mass dimension of its coefficient, 4 - a - b - 2 r - 2 d, is zero. Applied to UET_PARENT v1
(core/THEORY_CARD.md section 1, delta = phi - phi*):
    survive:   eps xi delta^2 R / (2 kappa) (only if phi* = 0), kinetic terms of phi and chi, lambda_phi phi^4,
               lambda_chi |chi|^4;
    forbidden: R / (2 kappa) (so the Planck mass must come from <phi>), every Lambda term, rho*, mu^2, m^2, and the
               portal (1/2) eps h delta |chi|^2, whose coefficient h has mass dimension 1.
In canonical variables (k, Z, eps absorbed as in THEORY_CARD section 5) the scale-invariant restriction is
    L_SI = (1/2) xi_c psi^2 R - (1/2) (grad psi)^2 - (lambda_psi / 4) psi^4 - (1/2) (grad chi)^2 - (lambda_chi / 4) |chi|^4,
three dimensionless constants (xi_c, lambda_psi, lambda_chi) and one scale <psi> that sets M_Pl^2 = xi_c <psi>^2.
Seven free parameters become three plus one scale; nothing in the action links chi to psi any more except gravity.

Step 2: consequences [AI derivation from standard results].
1. The psi sector is induced gravity, i.e. Brans-Dicke with Phi = xi_c psi^2 and omega_BD = 1 / (4 xi_c); with matter
   on the Jordan metric gamma_PPN - 1 = -1 / (omega_BD + 2) = -4 xi_c / (1 + 8 xi_c) (the C1 formula
   -F'^2 / (F + 2 F'^2) with F = xi_c psi^2). Cassini |gamma - 1| < 2.3e-5 gives xi_c <= 5.75e-6.
2. The Einstein-frame potential W / F^2 = lambda_psi / (4 xi_c^2) is flat: psi is the massless dilaton, every psi0
   is a static de Sitter solution, and dark energy is an exact cosmological constant (w = -1). The thawing dark
   energy of waves C1 to C3 needs m_psi, which is forbidden; it is not available in this restriction.
3. The observed dark energy fixes lambda_psi / xi_c^2 = 4 rho_Lambda / M_Pl^4 = 2.9e-120 (reduced Planck mass,
   h = 0.674, Omega_Lambda = 0.685), so lambda_psi <= 9.5e-131 at the Cassini bound: the hierarchy moves from
   m_psi / M_Pl = 1.8e-60 (STRESS_12) into a dimensionless coupling. Scale symmetry alone does not remove the
   tuning of the vacuum energy.
4. The portal is forbidden, so the author's matter-space exchange through h disappears; chi is massless. The
   Higgs-dilaton class restores both with a quartic portal zeta psi^2 |chi|^2 (and xi_chi |chi|^2 R), giving
   m_chi / M_Pl = sqrt(zeta / xi_c) from one scale, and in the Einstein frame the dilaton then couples to matter only
   through derivatives (Shaposhnikov & Zenhausern 2009; Ferreira, Hill & Ross 2016, literature, not derived here).
   Those terms are not in UET_PARENT v1: adding them changes the action, which is the author's decision
   (Theory Card v2, STANDARD section 3).
Nearest known theory: induced gravity (Zee 1979) and the Higgs-dilaton model. Not UET-distinct. Units kappa = 1 in
the FRW checks below (code F, W, rho in the units of uet_frw_cmb.py).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

CASSINI_GAMMA = 2.3e-5          # |gamma - 1| bound (Bertotti, Iess & Tortora 2003), as in C1
H0_EV = 2.1332e-33 * 0.674      # H0 in eV for h = 0.674
M_PL_REDUCED_EV = 2.435e27
OMEGA_LAMBDA = 0.685

# Terms of UET_PARENT v1 as (name, field power a + b, curvature power r, derivative pairs d)
PARENT_TERMS = (
    ("R / (2 kappa)", 0, 1, 0),
    ("eps xi phi^2 R / (2 kappa)  (phi* = 0)", 2, 1, 0),
    ("eps xi phi* phi R / kappa  (phi* != 0)", 1, 1, 0),
    ("F Lambda / kappa", 0, 0, 0),
    ("eps xi phi^2 Lambda / kappa", 2, 0, 0),
    ("eps k (grad phi)^2 / 2", 2, 0, 1),
    ("eps rho*", 0, 0, 0),
    ("eps mu^2 phi^2 / 2", 2, 0, 0),
    ("eps lambda_phi phi^4 / 4", 4, 0, 0),
    ("Z (grad chi)^2 / 2", 2, 0, 1),
    ("m^2 |chi|^2 / 2", 2, 0, 0),
    ("lambda_chi |chi|^4 / 4", 4, 0, 0),
    ("eps h phi |chi|^2 / 2  (portal)", 3, 0, 0),
)


def scaling_exponent(fields: int, curvature: int, derivative_pairs: int) -> int:
    """Power of s picked up by sqrt(-g) * term under g -> s^-2 g, fields -> s fields."""
    return fields + 2 * curvature + 2 * derivative_pairs - 4


def coefficient_mass_dimension(fields: int, curvature: int, derivative_pairs: int) -> int:
    return 4 - fields - 2 * curvature - 2 * derivative_pairs


def surviving_terms() -> tuple[list[str], list[str]]:
    keep, drop = [], []
    for name, a, r, d in PARENT_TERMS:
        (keep if scaling_exponent(a, r, d) == 0 else drop).append(name)
    return keep, drop


@dataclass(frozen=True)
class SIModel:
    """Scale-invariant restriction in code units: F = xi psi^2, W = lam psi^4 / 4, kappa absent."""
    xi: float
    lam: float
    m2: float = 0.0          # explicit breaking, for negative controls only

    def F(self, psi):
        return self.xi * psi * psi

    def dF(self, psi):
        return 2.0 * self.xi * psi

    def ddF(self, psi):
        return 2.0 * self.xi

    def W(self, psi):
        return 0.25 * self.lam * psi**4 + 0.5 * self.m2 * psi * psi

    def dW(self, psi):
        return self.lam * psi**3 + self.m2 * psi


def hubble(md, psi, pi, rho_m=0.0):
    """Root of 3 F H^2 + 3 F' pi H = rho_m + pi^2 / 2 + W (Boisseau et al. 2000, eq. 2.4, Z = 1)."""
    F, dF = md.F(psi), md.dF(psi)
    S = rho_m + 0.5 * pi * pi + md.W(psi)
    return (-3.0 * dF * pi + math.sqrt(9.0 * dF * dF * pi * pi + 12.0 * F * S)) / (6.0 * F)


def accelerations(md, psi, pi, H, rho_m=0.0):
    """(dH/dt, psi'') from Boisseau et al. eqs 2.5-2.6 with general F, as in uet_frw_cmb.accelerations."""
    F, dF, ddF = md.F(psi), md.dF(psi), md.ddF(psi)
    A0 = -3.0 * H * pi + 6.0 * dF * H * H - md.dW(psi)
    B0 = -rho_m - pi * pi - ddF * pi * pi + H * dF * pi
    Hdot = (B0 - dF * A0) / (2.0 * F + 3.0 * dF * dF)
    return Hdot, A0 + 3.0 * dF * Hdot


def static_de_sitter_residual(md, psi0: float) -> tuple[float, float]:
    """(dH/dt, psi'') / H^2 at psi = psi0, pi = 0, no matter; both vanish for a static de Sitter solution."""
    H = hubble(md, psi0, 0.0)
    Hdot, acc = accelerations(md, psi0, 0.0, H)
    return Hdot / (H * H), acc / (H * H * abs(psi0))


def gamma_minus_1(xi: float, psi: float = 1.0) -> float:
    F, dF = xi * psi * psi, 2.0 * xi * psi
    return -dF * dF / (F + 2.0 * dF * dF)


def cassini_xi_max(bound: float = CASSINI_GAMMA) -> float:
    """Largest xi with 4 xi / (1 + 8 xi) <= bound."""
    return bound / (4.0 - 8.0 * bound)


def rho_lambda_over_mpl4(h_eV: float = H0_EV, omega_l: float = OMEGA_LAMBDA) -> float:
    return 3.0 * omega_l * (h_eV / M_PL_REDUCED_EV) ** 2


def lambda_over_xi2_required() -> float:
    """Einstein-frame vacuum energy lambda / (4 xi^2) in reduced Planck units equals rho_Lambda / M_Pl^4."""
    return 4.0 * rho_lambda_over_mpl4()


def report() -> dict:
    keep, drop = surviving_terms()
    xi_max = cassini_xi_max()
    ratio = lambda_over_xi2_required()
    return {
        "terms_kept": keep, "terms_forbidden": drop,
        "free_parameters_parent": 7, "free_dimensionless_after": 3, "scales_after": 1,
        "cassini_xi_max": xi_max,
        "lambda_over_xi2": ratio,
        "lambda_max_at_cassini": ratio * xi_max**2,
        "rho_lambda_over_mpl4": rho_lambda_over_mpl4(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
