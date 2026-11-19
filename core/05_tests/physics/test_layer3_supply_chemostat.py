"""Layer 3 supply in a chemostat (stage 3, wave L3-3).

1. Threshold: with saturating (Monod) uptake a consumer invades an empty vessel iff S > S* = delta R*,
   checked by integrating the full equations at 20 random parameter sets on both sides of the threshold.
2. Steady abundance n* = Y (S0 - R*) at 20 random sets (rel < 1e-6).
3. Linear limit through the general code path: the chemostat integrator with mu = a R reproduces the
   action-derived layer 3 integrator (uet_layer3_from_action.simulate) with S = D S0, delta = D,
   1/tau = D, F = 1/Y (rel < 1e-6), and both equal the closed form n* = (S - delta R*)/(a F R*).
4. Competitive exclusion: with two consumers the one with the lower R* is left (Tilman's rule).
5. R* from the general root finder equals Tilman's closed form used by Test Card T007.
"""

from __future__ import annotations

import importlib
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

ch = importlib.import_module("core.03_lanes.persistence.uet_layer3_supply_chemostat")
l3 = importlib.import_module("core.03_lanes.persistence.uet_layer3_from_action")


def _draws(seed: int, n: int = 20):
    rng = random.Random(seed)
    for _ in range(n):
        mu_max = rng.uniform(0.5, 2.0)
        k = rng.uniform(0.1, 5.0)
        d = rng.uniform(0.1, 0.4) * mu_max
        y = rng.uniform(0.5, 5.0)
        yield mu_max, k, d, y


def test_threshold_holds_for_saturating_uptake():
    for mu_max, k, d, y in _draws(1):
        mu = ch.monod(mu_max, k)
        rs = ch.r_star(mu, d)
        for factor, alive in ((1.3, True), (0.7, False)):
            s0 = factor * rs
            m = ch.layer3_map(d, s0, [y])
            assert bool(m["S"] > m["delta"] * rs) == alive
            n, _ = ch.simulate([mu], [y], d, s0, [1e-3], s0, horizon=400.0 / d)
            assert bool(n[0] > 1e-6) == alive, (mu_max, k, d, y, factor, n)


def test_steady_abundance_matches_yield_times_excess_supply():
    for mu_max, k, d, y in _draws(2):
        mu = ch.monod(mu_max, k)
        rs = ch.r_star(mu, d)
        s0 = rs + random.Random(int(1e6 * k)).uniform(0.5, 5.0)
        n, r = ch.simulate([mu], [y], d, s0, [1e-2], s0, horizon=600.0 / d)
        assert abs(r - rs) / rs < 1e-6
        assert abs(n[0] - ch.steady_abundance(y, s0, rs)) / ch.steady_abundance(y, s0, rs) < 1e-6


def test_linear_uptake_reproduces_the_action_derived_layer3_integrator():
    rng = random.Random(3)
    for _ in range(20):
        a = rng.uniform(0.2, 2.0)
        d = rng.uniform(0.05, 0.5)
        y = rng.uniform(0.5, 4.0)
        rs = d / a
        s0 = rs * rng.uniform(1.5, 6.0)
        m = ch.layer3_map(d, s0, [y])
        n_ch, r_ch = ch.simulate([lambda r, a=a: a * r], [y], d, s0, [1e-2], s0, horizon=500.0 / d)
        n_l3, r_l3 = l3.simulate(np.array([a]), np.array([m["death"]]), np.array(m["quantum"]), m["S"],
                                 m["delta"], np.array([1e-2]), s0, 500.0 / d)
        closed = (m["S"] - m["delta"] * rs) / (a * m["quantum"][0] * rs)
        assert abs(n_ch[0] - n_l3[0]) / closed < 1e-6
        assert abs(r_ch - r_l3) / rs < 1e-6
        assert abs(n_l3[0] - closed) / closed < 1e-6


def test_lowest_r_star_excludes_the_other():
    rng = random.Random(4)
    for _ in range(20):
        d = rng.uniform(0.1, 0.3)
        mus = [ch.monod(rng.uniform(0.8, 2.0), rng.uniform(0.2, 3.0)) for _ in range(2)]
        rs = [ch.r_star(m, d) for m in mus]
        if abs(rs[0] - rs[1]) / min(rs) < 0.2:
            rs[1] = rs[0] * 2.0
            mus[1] = ch.monod(d * (1 + 1.0 / rs[1]), 1.0)  # mu(R) = D at R = rs[1] with K = 1
            rs[1] = ch.r_star(mus[1], d)
        s0 = 3.0 * max(rs)
        n, r = ch.simulate(mus, [1.0, 1.0], d, s0, [1e-2, 1e-2], s0, horizon=3000.0 / d)
        winner = int(np.argmin(rs))
        assert n[winner] > 1e-3
        assert n[1 - winner] < 1e-6 * n[winner]
        assert abs(r - rs[winner]) / rs[winner] < 1e-4


def test_root_finder_matches_tilman_closed_form_on_registered_data():
    out = ch.thresholds_tilman(0.25)
    assert len(out) == 4
    for v in out.values():
        assert abs(v["R_star_uM"] - v["R_star_t007_uM"]) / v["R_star_t007_uM"] < 1e-12
        assert abs(v["S_star_uM_per_day"] - 0.25 * v["R_star_uM"]) < 1e-15
