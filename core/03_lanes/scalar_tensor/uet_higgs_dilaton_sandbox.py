"""Sandbox: the parent action extended to the Higgs-dilaton form (wave A2, STRESS_12 option A, not the Theory Card).

Question: wave S1 found that scale symmetry alone forbids the portal and all masses; wave B1 found that the card
generates xi_chi |chi|^2 R anyway. The Higgs-dilaton class (Shaposhnikov & Zenhausern 2009; Garcia-Bellido, Rubio,
Shaposhnikov & Zenhausern 2011, arXiv:1107.2163) adds exactly that term and a quartic portal. In this sandbox
(AI proposal; changing the card is the author's decision):
    L = (1/2)(xi_psi psi^2 + xi_chi |chi|^2) R - (1/2)(grad psi)^2 - (1/2)(grad chi)^2 - V,
    V = (lambda_chi / 4)(|chi|^2 - (alpha / lambda_chi) psi^2)^2 + (beta / 4) psi^4,
what is fixed, what stays free, and does the matter-space exchange come back?

Results [AI derivation; checked in core/05_tests/physics/test_higgs_dilaton_sandbox.py].
1. Parameters: 5 dimensionless (xi_psi, xi_chi, lambda_chi, alpha, beta) and one scale psi0, against 7 in the card.
   Every mass ratio is now a ratio of couplings. In the flat-space vacuum |chi0|^2 = (alpha / lambda_chi) psi0^2
   (beta = 0) the radial chi mass in the Jordan frame is m_chi^2 = 2 alpha psi0^2 and M_Pl^2 = psi0^2
   (xi_psi + xi_chi alpha / lambda_chi), so m_chi^2 / M_Pl^2 = 2 alpha / (xi_psi + xi_chi alpha / lambda_chi).
2. The hierarchy is moved, not explained: with chi = nucleon (the portal lane) m_chi = 0.938 GeV needs
   alpha = 7.4e-38 xi_psi (for xi_chi alpha / lambda_chi << xi_psi); with psi as dark energy beta / xi_psi^2 =
   2.9e-120 as in S1. Literature: small alpha is technically natural in this class because alpha = 0 enhances the
   symmetry (two decoupled sectors); that is an argument about stability, not a prediction of the value.
3. The matter-space exchange comes back through the dimensionless portal alpha psi^2 |chi|^2, and the
   Einstein-frame potential V / F^2 is homogeneous of degree 0 in (psi, chi): it depends only on the ratio
   chi / psi, so the overall scale is an exactly flat direction (the dilaton). In the literature this direction
   couples to matter only through derivatives, which removes the Cassini bound on xi_psi that S1 had
   (not derived here). The card's trilinear portal g_c psi |chi|^2 breaks the homogeneity.
Nearest known theory: the Higgs-dilaton model itself. Not UET-distinct: adopting it would make the parent action a
member of a published class whose cosmology (0 < 1 + w0 < 0.02 tied to n_s) is already worked out.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

M_NUCLEON_EV = 0.938e9
M_PL_REDUCED_EV = 2.435e27


@dataclass(frozen=True)
class Sandbox:
    xi_psi: float
    xi_chi: float
    lam_chi: float
    alpha: float
    beta: float = 0.0
    g_c: float = 0.0            # card's trilinear portal, for negative controls only

    def F(self, psi, X):
        return self.xi_psi * psi * psi + self.xi_chi * X

    def V(self, psi, X):
        """X = |chi|^2."""
        return (0.25 * self.lam_chi * (X - self.alpha / self.lam_chi * psi * psi) ** 2 + 0.25 * self.beta * psi**4
                - 0.5 * self.g_c * psi * X)

    def V_E(self, psi, X):
        return self.V(psi, X) / self.F(psi, X) ** 2


def vacuum_X(sb: Sandbox, psi0: float) -> float:
    return sb.alpha / sb.lam_chi * psi0 * psi0


def chi_mass2_numeric(sb: Sandbox, psi0: float, h: float = 1e-5) -> float:
    """Second derivative of V along one chi component at the vacuum (chi_2 = 0, chi_1 = sqrt(X0))."""
    c0 = math.sqrt(vacuum_X(sb, psi0))
    f = lambda c: sb.V(psi0, c * c)
    return (f(c0 + h) - 2.0 * f(c0) + f(c0 - h)) / (h * h)


def mass_ratio2(sb: Sandbox) -> float:
    return 2.0 * sb.alpha / (sb.xi_psi + sb.xi_chi * sb.alpha / sb.lam_chi)


def alpha_for_nucleon(xi_psi: float = 1.0) -> float:
    """alpha giving m_chi = nucleon mass when xi_chi alpha / lambda_chi << xi_psi."""
    return 0.5 * xi_psi * (M_NUCLEON_EV / M_PL_REDUCED_EV) ** 2


def report() -> dict:
    return {"dimensionless_parameters": 5, "scales": 1, "card_parameters": 7,
            "alpha_over_xi_psi_for_nucleon": alpha_for_nucleon(1.0),
            "beta_over_xi_psi2_for_dark_energy": 2.87e-120}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
