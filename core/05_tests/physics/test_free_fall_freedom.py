"""Wave D16: how free is a freely falling frame?

(a) Derivation check: the tidal tensor from complex-step differentiation of the point-mass acceleration has
    eigenvalues (2, -1, -1) G M/d^3 at 20 random configurations, rel < 1e-12; for Lambda it is H_L^2 delta_ij.
(b) Known limit with convergence order: the inner Lagrange distance of a circular two-body orbit, found by
    root finding, tends to the Hill radius d (q/3)^(1/3) as q = m/M -> 0, relative deviation of order q^(1/3).
(c) Identities: Newton plus Lambda gives zero acceleration at r_ZG = (G m/H_L^2)^(1/3), where the Lambda
    tide equals the binding tide; the tidal radius makes epsilon = 1 exactly.
(d) Table: compact bodies are nearly free (Earth: largest leftover from the Moon ~1e-7); bound systems of
    galaxies are not (Local Group: Lambda ~0.24, Virgo ~0.18).
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_free_fall_freedom")


@pytest.mark.parametrize("seed", range(20))
def test_point_mass_tidal_tensor(seed: int) -> None:
    rng = np.random.default_rng(26000 + seed)
    M = 10 ** rng.uniform(20, 45)
    X = rng.normal(size=3) * 10 ** rng.uniform(6, 22)
    x = X + rng.normal(size=3) * 10 ** rng.uniform(6, 22)
    d = np.linalg.norm(x - X)
    T = m.tidal_tensor_complex_step(lambda y: m.acceleration_point(y, M, X), x)
    ev = np.sort(np.linalg.eigvalsh(0.5 * (T + T.T)))
    k = m.G * M / d ** 3
    assert np.allclose(ev / k, [-1.0, -1.0, 2.0], rtol=0, atol=1e-12)
    assert abs(ev[-1] / m.point_tide(M, d) - 1.0) < 1e-12
    assert abs(np.trace(T)) < 1e-12 * k  # vacuum: no isotropic part


def test_lambda_tidal_tensor_is_isotropic() -> None:
    x = np.array([3.1, -2.0, 0.7]) * m.MPC
    T = m.tidal_tensor_complex_step(m.acceleration_lambda, x)
    assert np.allclose(T / m.lambda_tide(), np.eye(3), rtol=0, atol=1e-12)


def test_l1_tends_to_hill_radius_order_one_third() -> None:
    M, d = m.M_SUN, m.AU
    qs = [1e-6, 1e-9, 1e-12]
    devs = [abs(m.l1_distance(q * M, M, d) / (d * (q / 3.0) ** (1.0 / 3.0)) - 1.0) for q in qs]
    orders = [log(devs[i] / devs[i + 1]) / log(qs[i] / qs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0 / 3.0) < 0.01


@pytest.mark.parametrize("seed", range(10))
def test_zero_gravity_and_tidal_radius_identities(seed: int) -> None:
    rng = np.random.default_rng(26100 + seed)
    mass = 10 ** rng.uniform(40, 46)
    r = m.zero_gravity_radius(mass)
    assert abs(m.H_L ** 2 * r / (m.G * mass / r ** 2) - 1.0) < 1e-12
    assert abs(m.lambda_tide() / m.binding_tide(mass, r) - 1.0) < 1e-12
    M, d = mass * 10 ** rng.uniform(0, 4), r * 10 ** rng.uniform(1, 3)
    rt = m.tidal_radius(mass, M, d)
    assert abs(m.point_tide(M, d) / m.binding_tide(mass, rt) - 1.0) < 1e-12


def test_background_and_lambda_today() -> None:
    q0 = m.OM / 2.0 - m.OL
    assert abs(m.background_tide_today() / (-q0 * m.H0 ** 2) - 1.0) < 1e-12
    assert m.background_tide_today() < m.lambda_tide()


def test_freedom_table() -> None:
    t = m.freedom_table()
    assert t["Earth"]["largest"] == "Moon" and 1e-7 < t["Earth"]["epsilon_largest"] < 1.3e-7
    assert t["Solar_system_to_Neptune"]["epsilon_largest"] < 1e-10
    assert t["Local_Group"]["largest"] == "Lambda" and 0.2 < t["Local_Group"]["epsilon_largest"] < 0.3
    assert 1.5 < t["Local_Group"]["zero_gravity_radius_over_size"] < 1.7
    assert t["Milky_Way_halo"]["largest"] == "Andromeda" and 0.09 < t["Milky_Way_halo"]["epsilon_largest"] < 0.12
    for row in t.values():
        assert row["epsilon_lambda"] > 0.0  # no falling frame is free of Lambda
