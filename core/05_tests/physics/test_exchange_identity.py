"""Wave A2: derive the matter <-> structure exchange of the parent action (author point 2).

The Theory Card claims that matter alone does not conserve energy-momentum; it
exchanges with the response field. Here the exchange covector is derived, not set
by bookkeeping (uet_covariant_balance.exchange_completed_ledger sets
Q_response = -Q_m by construction).

Off-shell identity (flat space, Hilbert stress of matter plus portal, sympy):

    d^mu T_mu_nu = sum_A E_A d_nu chi_A + (1/2) eps h |chi|^2 d_nu phi

with E_A the matter Euler-Lagrange residual. On the matter shell the matter sector
therefore receives Q_nu = (1/2) eps h |chi|^2 d_nu phi from the response field.
The curvature coupling xi does not appear: matter talks to the response field only
through the portal h, and to geometry only through the standard metric coupling.
"""

from __future__ import annotations

import random

import numpy as np
import pytest
import sympy as sp

from docs.core.uet_covariant_matter import coupled_matter_stress_tensor, matter_eom_residual

from ._symbolic_geometry import COORDS, T, X, Y, ZC
from .test_parent_derivation import configs, random_params, rel_diff

pytestmark = pytest.mark.physics

ETA = sp.diag(-1, 1, 1, 1)
TOL = 1e-10


def _poly(rng: random.Random, c0: float, s: float):
    c = [rng.uniform(-s, s) for _ in range(6)]
    return c0 + c[0] * T + c[1] * X + c[2] * Y * ZC + c[3] * X * T + c[4] * Y**2 + c[5] * T**2 * ZC


def _fields(rng: random.Random, p: dict):
    return _poly(rng, p["phi_star"] + 0.2, 0.4), _poly(rng, 0.3, 0.4), _poly(rng, -0.2, 0.4)


@pytest.mark.parametrize("seed", range(10))
def test_matter_stress_divergence_equals_portal_exchange(seed: int) -> None:
    rng = random.Random(5000 + seed)
    p = random_params(rng)
    response, matter = configs(p)
    phi, c1, c2 = _fields(rng, p)
    eps, h, Z, m2, lam, ps = (p[k] for k in ("epsilon", "h", "Z", "m2", "lambda_chi", "phi_star"))

    chi_sq = c1**2 + c2**2
    grad = lambda f: [sp.diff(f, x) for x in COORDS]  # noqa: E731
    kin = sum(ETA[m, m] * (sp.diff(c1, COORDS[m]) ** 2 + sp.diff(c2, COORDS[m]) ** 2) for m in range(4))
    lag = -Z * kin / 2 - (m2 * chi_sq / 2 + lam * chi_sq**2 / 4) + eps * h * (phi - ps) * chi_sq / 2
    g1, g2 = grad(c1), grad(c2)
    Tmn = sp.Matrix(4, 4, lambda a, b: Z * (g1[a] * g1[b] + g2[a] * g2[b]) + ETA[a, b] * lag)
    div = [sum(ETA[m, m] * sp.diff(Tmn[m, n], COORDS[m]) for m in range(4)) for n in range(4)]
    box = lambda f: sum(ETA[m, m] * sp.diff(f, COORDS[m], 2) for m in range(4))  # noqa: E731

    for _ in range(3):
        pt = {T: rng.uniform(0, .4), X: rng.uniform(-.4, .4), Y: rng.uniform(-.4, .4), ZC: rng.uniform(-.4, .4)}
        ev = lambda e: float(sp.sympify(e).evalf(30, subs=pt))  # noqa: E731
        doublet = np.array([ev(c1), ev(c2)])
        grads = np.array([[ev(d) for d in g1], [ev(d) for d in g2]])
        # implementation agreement for the stress tensor itself
        code_T = coupled_matter_stress_tensor(np.diag([-1., 1, 1, 1]), None, doublet, grads, ev(phi), response, matter)
        assert np.max(np.abs(code_T - np.array([[ev(Tmn[a, b]) for b in range(4)] for a in range(4)]))) < TOL
        e_res = matter_eom_residual(np.array([ev(box(c1)), ev(box(c2))]), doublet, ev(phi), response, matter)
        exchange = 0.5 * eps * h * float(doublet @ doublet)
        for n in range(4):
            lhs = ev(div[n])
            rhs = e_res[0] * grads[0, n] + e_res[1] * grads[1, n] + exchange * ev(sp.diff(phi, COORDS[n]))
            assert rel_diff(lhs, rhs) < TOL, (n, lhs, rhs)
            # negative control: the opposite exchange sign must be detected
            wrong = rhs - 2 * exchange * ev(sp.diff(phi, COORDS[n]))
            if abs(exchange * ev(sp.diff(phi, COORDS[n]))) > 1e-4:
                assert rel_diff(lhs, wrong) > 1e-6
