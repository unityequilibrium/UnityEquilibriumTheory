"""Wave D21: layer-3 persistence selection as survival optimisation (fuel order in a fast).

(a) Derivation check: under the optimal rule (burn the most fat allowed), the integrated survival time equals the
    closed form (phase II, phase III with F^(1/3) linear, protein alone) at 20 random systems, rel < 1e-8.
(b) Second route: a backward dynamic programme on a (F, P) grid (Clark-Mangel style) converges to the same survival
    time as the grid is refined, and its maximising choice is the largest allowed fat use almost everywhere.
(c) Identities: no rule that burns a fixed fraction s < 1 of the allowed fat outlives the optimal rule; rules that
    die with fat left die strictly sooner, rules that use all fat in time tie (energy conservation);
    the protein share of energy equals q0 exactly above F* and rises below it.
(d) Known limit: with no fat (F0 = 0) survival is rho_P (P0 - Pc)/e exactly.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_fuel_order")
RHO_F, RHO_P = 9.44, 4.7


def draw(seed: int):
    rng = np.random.default_rng(31000 + seed)
    e = rng.uniform(1000, 2500)
    q0 = rng.uniform(0.05, 0.3)
    k = 140.0 * 3.8 / (10 ** rng.uniform(3.5, 4.5)) ** (2 / 3)
    F0 = 10 ** rng.uniform(3, 4.7)
    P0 = rng.uniform(6000, 14000)
    return e, q0, k, F0, P0, 0.5 * P0


@pytest.mark.parametrize("seed", range(20))
def test_optimal_rule_survival_matches_closed_form(seed: int) -> None:
    e, q0, k, F0, P0, Pc = draw(seed)
    g = lambda F: m.greedy_fat_use(F, e, q0, k, RHO_F)
    num = m.survival_numeric(g, F0, P0, Pc, e, RHO_F, RHO_P)
    assert abs(num / m.survival_closed(F0, P0, Pc, e, q0, k, RHO_F, RHO_P) - 1.0) < 1e-8


def test_dynamic_programme_converges_to_closed_form() -> None:
    e, q0, rF, rP = 1400.0, 0.17, RHO_F, RHO_P
    k = 140.0 * 3.8 / 10000.0 ** (2 / 3)
    F0, P0, Pc = 9000.0, 10000.0, 5000.0
    exact = m.survival_closed(F0, P0, Pc, e, q0, k, rF, rP)
    errs, shares = [], []
    for n in (11, 21):
        v, share = m.survival_dp(F0, P0, Pc, e, q0, k, rF, rP, nF=n, nP=n)
        errs.append(abs(v / exact - 1.0))
        shares.append(share)
    assert errs[1] < errs[0] < 0.05
    order = log(errs[0] / errs[1]) / log(20 / 10)
    assert 1.0 < order < 2.5
    assert min(shares) > 0.9


@pytest.mark.parametrize("seed", range(10))
def test_selection_keeps_the_most_fat_rule(seed: int) -> None:
    e, q0, k, F0, P0, Pc = draw(seed)
    g = lambda F: m.greedy_fat_use(F, e, q0, k, RHO_F)
    best = m.survival_numeric(g, F0, P0, Pc, e, RHO_F, RHO_P)
    all_energy = (RHO_F * F0 + RHO_P * (P0 - Pc)) / e      # survival if every gram of fat is used before death
    for s in (0.5, 0.9, 0.99):
        t = m.survival_numeric(lambda F, s=s: s * g(F), F0, P0, Pc, e, RHO_F, RHO_P)
        assert t <= best * (1 + 1e-9)
        assert t <= all_energy * (1 + 1e-9)
        if t < all_energy * (1 - 1e-6):          # died with fat left
            assert t < best * (1 - 1e-9)


def test_protein_share_is_q0_above_threshold_and_rises_below() -> None:
    e, q0 = 1400.0, 0.17
    k = 140.0 * 3.8 / 10000.0 ** (2 / 3)
    Fs = m.phase3_threshold(e, q0, k, RHO_F)
    share = lambda F: (e - RHO_F * m.greedy_fat_use(F, e, q0, k, RHO_F)) / e
    for F in (1.5 * Fs, 3 * Fs, 10 * Fs):
        assert abs(share(F) - q0) < 1e-12
    below = [share(f * Fs) for f in (0.9, 0.5, 0.1)]
    assert below[0] > q0 and np.all(np.diff(below) > 0)
    assert abs(m.fat_ceiling(Fs, k) * RHO_F / ((1 - q0) * e) - 1.0) < 1e-12


def test_no_fat_limit() -> None:
    e, q0 = 1500.0, 0.2
    k = 140.0 * 3.8 / 10000.0 ** (2 / 3)
    t = m.survival_closed(0.0, 9000.0, 4500.0, e, q0, k, RHO_F, RHO_P)
    assert abs(t / (RHO_P * 4500.0 / e) - 1.0) < 1e-10


def test_illustration() -> None:
    out = m.illustration()
    assert 1000 < out["phase3_fat_g"] < 1200
    assert 70 < out["survival_days"] < 80
