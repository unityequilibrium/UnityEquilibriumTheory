"""Field equations of the DRAFT Theory Card UET_PARENT v2 (wave V2-W4; the card is not approved, v1 stays in force).

Question: do the field equations written in core/THEORY_CARD_V2_DRAFT.md follow from its action, and which exact
identity does the scale symmetry of that action impose on them?

Action (draft card, natural units, signature -+++, X = chi_1^2 + chi_2^2):
    S = int sqrt(-g) [ F R / 2 - (grad phi)^2 / 2 - (grad chi_A)^2 / 2 - V ],
    F = xi_phi phi^2 + xi_chi X,
    V = (lambda_chi / 4)(X - (alpha / lambda_chi) phi^2)^2 + (beta / 4) phi^4.

Results [AI derivation; checked in core/05_tests/physics/test_card_v2_field_equations.py against an independent
sympy Euler-Lagrange variation of the action text].
1. The four equations of the draft card are the Euler-Lagrange equations of its action:
       E_phi   = box phi + xi_phi phi R - dV/dphi                     = 0,
       E_A     = box chi_A + xi_chi R chi_A - 2 (dV/dX) chi_A         = 0,
       E_mn    = F G_mn - T_mn - (nabla_m nabla_n - g_mn box) F       = 0,
   with T_mn = sum_fields [d_m f d_n f] - g_mn [ (grad phi)^2 / 2 + (grad chi)^2 / 2 + V ] and
   delta S / delta g^mn = sqrt(-g) E_mn / 2.
2. Dilatation identity (off shell, for every field configuration and metric):
       phi E_phi + chi_A E_A + g^mn E_mn = (1/2) box J,   J = (1 + 6 xi_phi) phi^2 + (1 + 6 xi_chi) X.
   It holds because V is homogeneous of degree 4 and F of degree 2. On shell box J = 0: the current
   j_m = d_m J / 2 is conserved. This is the Noether current of the scale symmetry g -> s^-2 g, phi -> s phi,
   chi -> s chi, and J is the quantity the Einstein-frame dilaton is built from (wave V2-EF).
3. Exact solution through the general code path: X = 0, phi = phi0 and de Sitter with
       H^2 = beta_eff phi0^2 / (12 xi_phi),  beta_eff = beta + alpha^2 / lambda_chi,
   for every phi0 (the flat direction of S1, now with the portal).
Nearest known theory: induced gravity with two non-minimally coupled scalars (Higgs-dilaton class, Shaposhnikov &
Zenhausern 2009; Garcia-Bellido et al. 2011). Not UET-distinct: these are the textbook equations of that class.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CardV2:
    xi_phi: float
    xi_chi: float
    lam_chi: float
    alpha: float
    beta: float

    # potential and its derivatives -------------------------------------------------
    def F(self, phi: float, X: float) -> float:
        return self.xi_phi * phi * phi + self.xi_chi * X

    def V(self, phi: float, X: float) -> float:
        return 0.25 * self.lam_chi * (X - self.alpha / self.lam_chi * phi * phi) ** 2 + 0.25 * self.beta * phi**4

    def dV_dphi(self, phi: float, X: float) -> float:
        return -self.alpha * phi * (X - self.alpha / self.lam_chi * phi * phi) + self.beta * phi**3

    def dV_dX(self, phi: float, X: float) -> float:
        return 0.5 * self.lam_chi * (X - self.alpha / self.lam_chi * phi * phi)

    def J(self, phi: float, X: float) -> float:
        """Dilatation charge density: J = (1 + 6 xi_phi) phi^2 + (1 + 6 xi_chi) X."""
        return (1.0 + 6.0 * self.xi_phi) * phi * phi + (1.0 + 6.0 * self.xi_chi) * X


def dilaton_residual(card: CardV2, R: float, box_phi: float, phi: float, chi) -> float:
    X = float(np.dot(chi, chi))
    return box_phi + card.xi_phi * phi * R - card.dV_dphi(phi, X)


def matter_residual(card: CardV2, R: float, box_chi, chi, phi: float) -> np.ndarray:
    chi = np.asarray(chi, dtype=float)
    X = float(np.dot(chi, chi))
    return np.asarray(box_chi, dtype=float) + card.xi_chi * R * chi - 2.0 * card.dV_dX(phi, X) * chi


def stress_tensor(card: CardV2, metric, phi: float, grad_phi, chi, grad_chi) -> np.ndarray:
    """T_mn of the two scalars; gradients are covariant (lower-index) components."""
    g = np.asarray(metric, dtype=float)
    ginv = np.linalg.inv(g)
    dphi = np.asarray(grad_phi, dtype=float)
    dchi = np.asarray(grad_chi, dtype=float)          # shape (2, 4)
    chi = np.asarray(chi, dtype=float)
    kin = 0.5 * dphi @ ginv @ dphi + 0.5 * sum(d @ ginv @ d for d in dchi)
    T = np.outer(dphi, dphi) + sum(np.outer(d, d) for d in dchi)
    return T - g * (kin + card.V(phi, float(chi @ chi)))


def metric_residual(card: CardV2, metric, einstein, phi: float, grad_phi, chi, grad_chi, hess_F) -> np.ndarray:
    """E_mn = F G_mn - T_mn - (nabla_m nabla_n F - g_mn box F); hess_F is nabla_m nabla_n F."""
    g = np.asarray(metric, dtype=float)
    H = np.asarray(hess_F, dtype=float)
    chi = np.asarray(chi, dtype=float)
    box_F = float(np.trace(np.linalg.inv(g) @ H))
    F = card.F(phi, float(chi @ chi))
    return F * np.asarray(einstein, dtype=float) - stress_tensor(card, g, phi, grad_phi, chi, grad_chi) - (H - g * box_F)


def dilatation_combination(card: CardV2, metric, E_phi: float, E_chi, E_mn, phi: float, chi) -> float:
    """phi E_phi + chi_A E_A + g^mn E_mn; equals box J / 2 off shell (result 2)."""
    ginv = np.linalg.inv(np.asarray(metric, dtype=float))
    return phi * E_phi + float(np.dot(chi, E_chi)) + float(np.sum(ginv * np.asarray(E_mn, dtype=float)))


def de_sitter_H2(card: CardV2, phi0: float) -> float:
    """H^2 of the X = 0, phi = phi0 de Sitter solution (result 3)."""
    beta_eff = card.beta + card.alpha**2 / card.lam_chi
    return beta_eff * phi0 * phi0 / (12.0 * card.xi_phi)
