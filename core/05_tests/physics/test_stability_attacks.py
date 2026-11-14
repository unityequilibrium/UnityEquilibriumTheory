"""Wave B1: attempts to break the parent action from the inside (no data).

Each test either confirms a property by an independent route or exhibits a
parameter region where the theory fails a requirement. Failures found here are
recorded in docs/core/FIDELITY_MATRIX.md (section B1) as constraints or kill routes.
"""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest
from scipy.optimize import minimize

pytestmark = pytest.mark.physics

vac = importlib.import_module("docs.core.03_lanes.scalar_tensor.uet_vacuum_structure")
mapping = importlib.import_module("docs.core.02_equations.covariant.uet_scalar_tensor_mapping")


def _random_potential(rng: random.Random, condensate: bool | None = None) -> "vac.CanonicalPotential":
    lu = lambda a, b: 10 ** rng.uniform(math.log10(a), math.log10(b))  # noqa: E731
    m2_chi = lu(0.05, 2.0)
    if condensate or (condensate is None and rng.random() < 0.5):
        m2_chi = -m2_chi
    return vac.CanonicalPotential(m2_psi=lu(0.05, 2.0), lam_psi=lu(0.01, 2.0), m2_chi=m2_chi,
                                  lam_chi=lu(0.01, 2.0), g_c=rng.uniform(-2.0, 2.0))


def _brute_force_vacuum(p) -> tuple[float, float, float]:
    """Independent route: 2-D grid over (psi, X) without eliminating X, then a bounded local polish."""
    psi = np.linspace(-15, 15, 601)
    X = np.linspace(0, 120, 601)
    P, XX = np.meshgrid(psi, X, indexing="ij")
    V = p.value(P, XX)
    i, j = np.unravel_index(int(np.argmin(V)), V.shape)
    res = minimize(lambda z: float(p.value(z[0], z[1])), x0=[psi[i], X[j]],
                   bounds=[(None, None), (0.0, None)], method="L-BFGS-B", options={"ftol": 1e-15, "gtol": 1e-12})
    return float(res.x[0]), float(res.x[1]), float(res.fun)


@pytest.mark.parametrize("seed", range(15))
def test_global_vacuum_matches_independent_2d_minimization(seed: int) -> None:
    p = _random_potential(random.Random(6000 + seed))
    v = vac.global_vacuum(p)
    psi_b, X_b, V_b = _brute_force_vacuum(p)
    assert v["V0"] <= V_b + 1e-9
    assert abs(v["V0"] - V_b) < 1e-6 * max(1.0, abs(V_b))
    # stationarity (KKT) at the reported vacuum
    dpsi, dX = p.grad(v["psi0"], v["X0"])
    assert abs(dpsi) < 1e-6
    assert (abs(dX) < 1e-6) if v["X0"] > 0 else (dX >= -1e-9)


@pytest.mark.parametrize("seed", range(10))
def test_sufficient_condition_keeps_vacuum_at_origin(seed: int) -> None:
    """Derived bound: with m2_chi > 0 and g_c^2 <= 2 lam_chi m2_psi the origin is the global vacuum."""
    rng = random.Random(6100 + seed)
    p0 = _random_potential(rng, condensate=False)
    g_max = math.sqrt(2.0 * p0.lam_chi * p0.m2_psi)
    p = vac.CanonicalPotential(p0.m2_psi, p0.lam_psi, p0.m2_chi, p0.lam_chi, g_c=rng.uniform(-g_max, g_max))
    v = vac.global_vacuum(p)
    assert abs(v["psi0"]) < 1e-6 and v["X0"] == 0.0


def test_origin_can_be_metastable_with_all_masses_positive() -> None:
    """Attack found: positive masses do not guarantee psi0 = 0; a weak chi self-coupling shifts the vacuum."""
    p = vac.CanonicalPotential(m2_psi=1.0, lam_psi=1.0, m2_chi=0.1, lam_chi=0.01, g_c=1.0)
    hess_origin_positive = p.m2_psi > 0 and p.m2_chi > 0  # origin is a local minimum
    v = vac.global_vacuum(p)
    assert hess_origin_positive
    assert v["V0"] < -1.0 and abs(v["psi0"]) > 0.5
    assert not vac.origin_is_global_vacuum(p)


def test_condensate_shift_converges_to_linear_response() -> None:
    """Known limit: with a chi condensate, psi0 -> g_c X_c/(2 m2_psi) as g_c -> 0 (error O(g_c^2) relative)."""
    errors = []
    for g in (0.02, 0.01, 0.005):
        p = vac.CanonicalPotential(m2_psi=0.7, lam_psi=0.4, m2_chi=-0.6, lam_chi=0.9, g_c=g)
        errors.append(abs(vac.global_vacuum(p)["psi0"] / vac.linear_response_psi0(p) - 1.0))
    orders = [math.log2(errors[i] / errors[i + 1]) for i in range(2)]
    assert all(1.7 < o < 2.3 for o in orders), (errors, orders)


@pytest.mark.parametrize("xi_c", [0.3, 1.0, 2.5, -0.1])
def test_cassini_psi0_bound_reproduces_gamma_bound(xi_c: float) -> None:
    kappa = 1.0
    psi_max = vac.cassini_max_psi0(xi_c, kappa)
    gm1 = abs(vac.vacuum_ppn(psi_max, xi_c, kappa)["gamma_ppn_minus_1"])
    assert abs(gm1 / 2.3e-5 - 1.0) < 1e-3  # small-alpha formula agrees with the full DEF path


def test_ghost_boundary_for_negative_xi() -> None:
    xi_c, kappa = -0.4, 1.0
    psi_c = vac.strong_coupling_field(xi_c, kappa)
    assert vac.ghost_free(0.99 * psi_c, xi_c, kappa)
    assert not vac.ghost_free(1.01 * psi_c, xi_c, kappa)
    with pytest.raises(ValueError):
        mapping.uet_couplings(1.01 * psi_c, xi_c, kappa)
    assert math.isinf(vac.strong_coupling_field(0.5, kappa))
