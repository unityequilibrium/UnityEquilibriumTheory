"""Wave D18: tidal settling as motion that stops resisting.

(a) Derivation check: the general path (Kepler orbit, spectral body-frame derivative of the tidal tensor)
    gives F = 18 (G M/a^3)^2 (n - omega)^2 on circular orbits at 20 random systems, rel < 1e-10.
(b) Known limit with convergence order: a locked body on an ellipse has F -> 63 (G M/a^3)^2 n^2 e^2, with
    relative deviation of order 2 in e; F = 0 exactly at e = 0, omega = n.
(c) Identity and second route: at fixed angular momentum the synchronous circular states are stationary
    points of the energy (numerical derivative), with e = 0 preferred; they are minima exactly when
    mu a^2 > 3 I (Darwin-Hut), checked by numerical second derivatives on both sides.
"""

from __future__ import annotations

import importlib
from math import log, sqrt

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_tidal_settling")


@pytest.mark.parametrize("seed", range(20))
def test_circular_flex_rate_general_path(seed: int) -> None:
    rng = np.random.default_rng(28000 + seed)
    M = 10 ** rng.uniform(22, 31)
    mm = M * 10 ** rng.uniform(-6, 0)
    a = 10 ** rng.uniform(7, 12)
    n = m.mean_motion(a, M + mm)
    omega = n * rng.uniform(-3, 3)
    assert abs(m.flex_rate(a, 0.0, omega, M, mm) / m.flex_rate_circular(a, omega, M, mm) - 1.0) < 1e-10


def test_locked_ellipse_limit_order_two() -> None:
    M, mm, a = 6e24, 7e22, 3.8e8
    n = m.mean_motion(a, M + mm)
    A2n2 = (m.G * M / a ** 3) ** 2 * n ** 2
    es = [1e-2, 1e-3, 1e-4]
    devs = [abs(m.flex_rate(a, e, n, M, mm) / (63.0 * A2n2 * e * e) - 1.0) for e in es]
    orders = [log(devs[i] / devs[i + 1]) / log(es[i] / es[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 2.0) < 0.02
    assert m.flex_rate(a, 0.0, n, M, mm) < 1e-25 * A2n2


@pytest.mark.parametrize("seed", range(10))
def test_settled_state_is_the_energy_minimum_iff_darwin_hut(seed: int) -> None:
    rng = np.random.default_rng(28100 + seed)
    M = 10 ** rng.uniform(28, 31)
    mm = M * 10 ** rng.uniform(-4, -1)
    R = 10 ** rng.uniform(6, 8)
    I = 0.4 * mm * R ** 2
    mu = M * mm / (M + mm)
    a_crit = sqrt(3 * I / mu)
    a0 = a_crit * 10 ** rng.uniform(0.3, 1.5)  # a stable synchronous state exists here
    L = m.angular_momentum(I, m.mean_motion(a0, M + mm), a0, 0.0, M, mm)
    roots = m.synchronous_states(L, I, M, mm, 1e-3 * a_crit, 1e4 * a0)
    assert len(roots) == 2 and any(abs(r / a0 - 1) < 1e-9 for r in roots)
    for a in roots:
        h = 1e-4 * a
        E = lambda x: m.energy_at_fixed_L(x, 0.0, L, I, M, mm)
        d1 = (E(a + h) - E(a - h)) / (2 * h)
        d2 = (E(a + h) - 2 * E(a) + E(a - h)) / h ** 2
        scale = abs(E(a)) / a
        assert abs(d1) < 1e-4 * scale  # finite-difference cancellation limits this check
        assert (d2 > 0) == m.is_stable_synchronous(a, I, M, mm)
        if m.is_stable_synchronous(a, I, M, mm):
            assert m.energy_at_fixed_L(a, 1e-2, L, I, M, mm) > E(a)  # an ellipse costs energy
    assert sum(m.is_stable_synchronous(a, I, M, mm) for a in roots) == 1


def test_earth_moon_illustration() -> None:
    out = m.illustration_earth_moon()
    assert 1.2e4 < out["earth_flex_in_units_A2n2"] < 1.3e4
    assert abs(out["moon_flex_in_units_A2n2"] / (63 * 0.0549 ** 2) - 1.0) < 0.1  # O(e^2) correction at e = 0.055
