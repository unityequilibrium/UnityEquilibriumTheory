"""Vacuum structure and stability attacks on the UET parent action (wave B1).

Canonical potential of Theory Card UET_PARENT v1 on a flat vacuum (Lambda_eff = 0,
R = 0), with X = |chi~|^2 >= 0:

    V(psi, X) = m2_psi psi^2/2 + lam_psi psi^4/4 + m2_chi X/2 + lam_chi X^2/4 - g_c psi X/2

``m2_psi`` is the effective Jordan-frame mass at the flat vacuum; it absorbs the
Lambda and rho_star curvature terms (Theory Card section 6). The portal sign follows
the action term +1/2 g_c psi |chi~|^2.

Questions answered here:
* where is the true vacuum (psi0, X0)?  If psi0 != 0, the DEF coupling alpha0 is
  nonzero and gamma_PPN - 1 != 0, so solar-system tests can rule the theory out;
* is the potential bounded below, and is the origin only metastable?
* is there a ghost (F <= 0) at the vacuum?
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from math import isfinite, sqrt

import numpy as np

_mapping = importlib.import_module("docs.core.02_equations.covariant.uet_scalar_tensor_mapping")
uet_def_parameters = _mapping.uet_def_parameters


@dataclass(frozen=True)
class CanonicalPotential:
    m2_psi: float
    lam_psi: float
    m2_chi: float
    lam_chi: float
    g_c: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.m2_psi, self.lam_psi, self.m2_chi, self.lam_chi, self.g_c)):
            raise ValueError("potential parameters must be finite")

    def value(self, psi, X):
        return (0.5 * self.m2_psi * psi**2 + 0.25 * self.lam_psi * psi**4
                + 0.5 * self.m2_chi * X + 0.25 * self.lam_chi * X**2 - 0.5 * self.g_c * psi * X)

    def grad(self, psi: float, X: float) -> tuple[float, float]:
        dpsi = self.m2_psi * psi + self.lam_psi * psi**3 - 0.5 * self.g_c * X
        dX = 0.5 * self.m2_chi + 0.5 * self.lam_chi * X - 0.5 * self.g_c * psi
        return dpsi, dX


def bounded_below(p: CanonicalPotential) -> bool:
    """Quartic terms dominate at large field iff both quartic couplings are positive."""

    return p.lam_psi > 0.0 and p.lam_chi > 0.0


def x_star(p: CanonicalPotential, psi):
    """Minimizing X >= 0 at fixed psi."""

    return np.maximum(0.0, (p.g_c * np.asarray(psi, dtype=float) - p.m2_chi) / p.lam_chi)


def reduced_potential(p: CanonicalPotential, psi):
    return p.value(np.asarray(psi, dtype=float), x_star(p, psi))


def global_vacuum(p: CanonicalPotential, psi_max: float = 50.0, n: int = 200001) -> dict[str, float]:
    """Global minimum of V by exact elimination of X and a refined 1-D search in psi."""

    if not bounded_below(p):
        raise ValueError("potential is unbounded below: no vacuum")
    grid = np.linspace(-psi_max, psi_max, n)
    vals = reduced_potential(p, grid)
    i = int(np.argmin(vals))
    lo, hi = grid[max(i - 1, 0)], grid[min(i + 1, n - 1)]
    for _ in range(200):  # golden-section refinement of the bracketing cell
        a = hi - 0.6180339887498949 * (hi - lo)
        b = lo + 0.6180339887498949 * (hi - lo)
        if reduced_potential(p, a) < reduced_potential(p, b):
            hi = b
        else:
            lo = a
    psi0 = 0.5 * (lo + hi)
    for _ in range(20):  # Newton on dV/dpsi along X = X*(psi) (envelope theorem), to machine precision
        X = float(x_star(p, psi0))
        h = p.m2_psi * psi0 + p.lam_psi * psi0**3 - 0.5 * p.g_c * X
        dh = p.m2_psi + 3.0 * p.lam_psi * psi0**2 - (0.5 * p.g_c**2 / p.lam_chi if X > 0.0 else 0.0)
        if dh <= 0.0:
            break
        step = h / dh
        psi0 -= step
        if abs(step) < 1e-15 * max(1.0, abs(psi0)):
            break
    X0 = float(x_star(p, psi0))
    return {"psi0": float(psi0), "X0": X0, "V0": float(p.value(psi0, X0))}


def origin_is_global_vacuum(p: CanonicalPotential, tol: float = 1e-12) -> bool:
    vac = global_vacuum(p)
    return vac["V0"] >= -tol


def linear_response_psi0(p: CanonicalPotential) -> float:
    """Small-g_c limit with a chi condensate (m2_chi < 0): psi0 = g_c X_c/(2 m2_psi), X_c = -m2_chi/lam_chi."""

    return p.g_c * (-p.m2_chi / p.lam_chi) / (2.0 * p.m2_psi)


def ghost_free(psi: float, xi_c: float, kappa: float) -> bool:
    """F = 1 + kappa xi_c psi^2 > 0 (with K = 1 this also makes the Einstein-frame kinetic term positive)."""

    return 1.0 + kappa * xi_c * psi * psi > 0.0


def strong_coupling_field(xi_c: float, kappa: float) -> float:
    """|psi| at which F = 0 for xi_c < 0; infinite when xi_c >= 0."""

    return float("inf") if xi_c >= 0.0 else 1.0 / sqrt(kappa * -xi_c)


def vacuum_ppn(psi0: float, xi_c: float, kappa: float) -> dict[str, float]:
    """DEF alpha0 and gamma_PPN - 1 around the true vacuum (massless-scalar formula)."""

    return uet_def_parameters(xi_c, kappa, psi0)


def cassini_max_psi0(xi_c: float, kappa: float, gamma_bound: float = 2.3e-5) -> float:
    """Largest |psi0| allowed by |gamma - 1| < gamma_bound, small-alpha limit alpha0 = -sqrt(2 kappa) xi_c psi0.

    Applies only when the scalar is light on solar-system scales (Cassini domain).
    """

    alpha_max = sqrt(gamma_bound / (2.0 - gamma_bound))
    return alpha_max / (sqrt(2.0 * kappa) * abs(xi_c))
