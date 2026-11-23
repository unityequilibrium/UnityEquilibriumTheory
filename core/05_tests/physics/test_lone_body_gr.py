"""Wave D11: one free-falling mass alone in a universe (GR, no Lambda) - does its fall emit anything?

(a) Derivation check: the general quadrupole path (spectral third derivative of Q from positions) gives
    the closed-form binary power (32/5) G^4 M^2 m^2 (M + m)/(c^5 d^5) at 20 random systems, rel < 1e-10.
(b) Second route: a spinning rigid body (z principal) through the same general path gives
    32 G (I1 - I2)^2 omega^6/(5 c^5), rel < 1e-10.
(c) Identities: a lone body in uniform motion has dddQ = 0 (exact finite difference of a quadratic);
    a spherical pulsation has Q_TF = 0 at all times, so P = 0 although its size changes.
(d) Known limit with convergence order: as the second body goes away (m -> 0) the binary power falls
    as m^2; (P / (m^2 K) - 1) shrinks with order 1 in m/M.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_lone_body_gr")


@pytest.mark.parametrize("seed", range(20))
def test_binary_general_path_matches_closed_form(seed: int) -> None:
    rng = np.random.default_rng(21000 + seed)
    M = 10 ** rng.uniform(-1, 2) * m.M_SUN
    mm = M * 10 ** rng.uniform(-6, 0)
    d = 10 ** rng.uniform(8, 12)
    traj, period = m.binary_trajectory(M, mm, d)
    p = m.power_from_dddq(m.dddq_spectral(traj, period))
    assert abs(p / m.binary_power_closed_form(M, mm, d) - 1.0) < 1e-10


@pytest.mark.parametrize("seed", range(10))
def test_spinning_body_second_route(seed: int) -> None:
    rng = np.random.default_rng(21100 + seed)
    k = rng.integers(2, 6)
    ms = rng.uniform(0.5, 2.0, k) * 1e20
    x = rng.normal(size=(k, 3)) * 1e3
    ms2, x2 = np.r_[ms, ms], np.vstack([x, x * [1.0, 1.0, -1.0]])  # z is a principal axis
    x2 = x2 - (ms2[:, None] * x2).sum(0) / ms2.sum()
    omega = 10 ** rng.uniform(-3, 1)
    traj, period = m.rotating_trajectory(ms2, x2, omega)
    p = m.power_from_dddq(m.dddq_spectral(traj, period))
    assert abs(p / m.rotating_power_closed_form(ms2, x2, omega) - 1.0) < 1e-10


@pytest.mark.parametrize("seed", range(10))
def test_lone_body_in_uniform_motion_emits_nothing(seed: int) -> None:
    rng = np.random.default_rng(21200 + seed)
    k = rng.integers(1, 6)
    ms = rng.uniform(0.5, 2.0, k)
    x = rng.normal(size=(k, 3))
    v = rng.normal(size=3)
    traj = m.translating_trajectory(ms, x, v)
    d = m.dddq_finite_difference(traj, rng.uniform(-5, 5), 0.25)
    scale = ms.sum() * np.linalg.norm(v) ** 3  # dddQ of a body of size 1 spinning at rate |v|
    assert np.max(np.abs(d)) < 1e-10 * scale
    # the same body spinning would radiate: the zero is not a property of the code path
    traj_s, period = m.rotating_trajectory(np.r_[ms, ms], np.vstack([x, -x]) + [0.3, 0.0, 0.0], 1.0)
    assert m.power_from_dddq(m.dddq_spectral(traj_s, period)) > 0.0


def test_spherical_pulsation_emits_nothing() -> None:
    traj, period = m.pulsating_octahedron(1e20, 1e3, 300.0, 0.7)
    Q = np.array([m.quadrupole_tf(*traj(t)) for t in np.linspace(0, period, 9)])
    sizes = [np.trace(np.einsum("a,ai,aj->ij", np.array(traj(t)[0]), traj(t)[1], traj(t)[1])) for t in (0.0, period / 4)]
    assert np.max(np.abs(Q)) < 1e-12 * max(sizes)
    assert sizes[1] / sizes[0] > 1.5
    scale = m.G / (5 * m.C_LIGHT ** 5) * (6 * 1e20 * 1e3 * 300.0 * 0.7 ** 3) ** 2  # an unbalanced pulsation
    assert m.power_from_dddq(m.dddq_spectral(traj, period)) < 1e-20 * scale


def test_second_body_going_away_power_falls_as_m_squared() -> None:
    M, d = m.M_SUN, m.AU
    K = 32.0 / 5.0 * m.G ** 4 * M ** 3 / (m.C_LIGHT ** 5 * d ** 5)
    qs = [1e-2, 1e-3, 1e-4]
    devs = []
    for q in qs:
        traj, period = m.binary_trajectory(M, q * M, d)
        p = m.power_from_dddq(m.dddq_spectral(traj, period))
        devs.append(p / ((q * M) ** 2 * K) - 1.0)
    orders = [log(devs[i] / devs[i + 1]) / log(qs[i] / qs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01
    assert abs(devs[-1] / qs[-1] - 1.0) < 1e-3


def test_sun_alone_and_with_earth() -> None:
    r = m.sun_alone_and_with_earth()
    assert r["sun_alone_W"] == 0.0
    assert 190.0 < r["sun_earth_W"] < 200.0
