"""What an RG fixed point could fix in the parent action, and is the card closed under renormalization? (wave B1)

Question (topic 0.23 STRESS_12, option B): in asymptotic safety the couplings that are irrelevant at the fixed
point are predicted (Shaposhnikov & Wetterich 2010, arXiv:0912.0208: the Higgs mass), the relevant ones stay free.
Which parent-action parameters could a fixed point fix, and does the one-loop running of the card generate terms
that the card does not contain?

Results [AI derivation from standard one-loop results; checked in core/05_tests/physics/test_rg_closure.py].
1. Relevant versus irrelevant. Near any fixed point a coupling with positive mass dimension is relevant (it grows
   towards the infrared) unless an anomalous dimension of order one flips it. In the card these are Lambda_eff,
   m_psi^2, m_chi^2 and g_c (and kappa, which sets the units): a fixed point leaves them free, so it cannot touch the
   hierarchy m_psi / M_Pl = 1.8e-60 of STRESS_12. Only the dimensionless couplings lambda_psi, lambda_chi, xi_c
   (and xi_chi below) can be predicted. Scale symmetry (wave S1) removes the dimensionful ones but leaves the
   dimensionless ones free, so the two are complementary; together they are the dilaton quantum gravity scenario
   of Wetterich (2013, arXiv:1304.7743), which the literature proposes but has not established.
2. One-loop flow of the matter sector in a mass-independent scheme (O(N) scalar with V = (lambda / 4) (phi^2)^2 and
   coupling xi phi^2 R / 2 on a curved background; e.g. Buchbinder, Odintsov & Shapiro 1992; dimensionful couplings
   such as g_c do not enter the running of dimensionless ones):
       beta_lambda = (N + 8) lambda^2 / (8 pi^2),   beta_xi = (N + 2) lambda (xi - 1/6) / (8 pi^2).
   For psi (N = 1) lambda_psi = 0 is a fixed point of the matter flow, so the AI choice lambda_psi = 0 of C1-C3 is
   stable. For chi (O(2), N = 2) the card has no chi^2 R term, but beta_xi_chi at xi_chi = 0 is
   -lambda_chi / (12 pi^2) != 0: the card is not closed under renormalization. A term xi_chi |chi|^2 R is generated,
   which is one of the two terms the Higgs-dilaton class adds (wave S1, item 4).
3. xi = 1/6 is special because it makes the massless scalar equation Weyl covariant:
   (box - R/6) acting on Omega^-1 phi in the metric Omega^2 g equals Omega^-3 (box - R/6) phi. This is checked
   with sympy geometry; any other xi breaks it.
Nearest known theory: renormalization of scalar fields in curved space; asymptotic safety. Not UET-distinct.
"""

from __future__ import annotations

import math

PI2 = math.pi**2


def beta_lambda(lam: float, N: int) -> float:
    return (N + 8) * lam * lam / (8.0 * PI2)


def beta_xi(lam: float, xi: float, N: int) -> float:
    return (N + 2) * lam * (xi - 1.0 / 6.0) / (8.0 * PI2)


PARENT_COUPLINGS = {
    # name: mass dimension in canonical variables (THEORY_CARD section 2)
    "kappa": -2, "Lambda_eff": 2, "m_psi^2": 2, "m_chi^2": 2, "g_c": 1,
    "lambda_psi": 0, "lambda_chi": 0, "xi_c": 0,
}


def classify() -> dict[str, list[str]]:
    relevant = [k for k, d in PARENT_COUPLINGS.items() if d > 0]
    marginal = [k for k, d in PARENT_COUPLINGS.items() if d == 0]
    return {"relevant_free_at_fixed_point": relevant, "dimensionless_predictable": marginal + ["xi_chi (generated)"]}


def generated_xi_chi_rate(lam_chi: float) -> float:
    """beta of xi_chi at xi_chi = 0 for the O(2) chi of the card."""
    return beta_xi(lam_chi, 0.0, 2)


def report() -> dict:
    c = classify()
    return {**c, "beta_xi_chi_at_0_over_lambda_chi": generated_xi_chi_rate(1.0),
            "minus_one_over_12_pi2": -1.0 / (12.0 * PI2)}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
