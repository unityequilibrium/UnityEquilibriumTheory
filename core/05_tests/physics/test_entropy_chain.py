"""Wave D2: dividing entropy along a chain of structures.

(a) Derivation check: the numerically maximised total power of chains with N = 1 ... 4 stages
    equals K_chain (sqrt(T0) - sqrt(T_N))^2 at 24 random chains, rel < 1e-10; N = 1 agrees with the
    single-engine result of wave D1 (uet_entropy_divider).
(b) Known limit through the general path: as the entropy flux goes to zero the chain efficiency
    tends to the Carnot value 1 - T_N/T0 for every N (the reversible chain telescopes).
(c) Conservation and second law: the shares add to J_0 - J_N, and the entropy produced in the
    contacts (from temperatures only) adds to J_N/T_N - J_0/T0 >= 0.
(d) Second route: a two-stage chain built directly from the working temperatures (no entropy
    flux variables) gives the same heats and total as the flux route.
(e) Zero-sum sharing: at a fixed flux, random splits leave the total unchanged; one stage can take
    everything or nothing.
(f) Each hand-off costs: with 2N equal contacts the maximum falls as 1/N, and a chain persists
    exactly when the sum of its needs is below the maximum.
"""

from __future__ import annotations

import importlib

import numpy as np
import pytest

pytestmark = pytest.mark.physics

ch = importlib.import_module("docs.core.03_lanes.persistence.uet_entropy_chain")
dv = importlib.import_module("docs.core.03_lanes.persistence.uet_entropy_divider")


def _random_chain(rng: np.random.Generator, n_stages: int):
    T0 = 10 ** rng.uniform(2, 4)
    TN = T0 * rng.uniform(0.001, 0.8)
    K_0, K_N = 10 ** rng.uniform(-1, 1, 2)
    K_mid = list(10 ** rng.uniform(-1, 1, n_stages - 1))
    return T0, TN, K_0, K_mid, K_N


@pytest.mark.parametrize("seed", range(24))
def test_chain_maximum_matches_series_closed_form(seed: int) -> None:
    rng = np.random.default_rng(4000 + seed)
    n = 1 + seed % 4
    T0, TN, K_0, K_mid, K_N = _random_chain(rng, n)
    p_num, _ = ch.max_total_numeric(T0, TN, K_0, K_mid, K_N)
    p_exact = ch.max_total_closed_form(T0, TN, K_0, K_mid, K_N)
    assert abs(p_num / p_exact - 1.0) < 1e-10
    if n == 1:
        assert abs(p_exact / dv.max_power_closed_form(T0, TN, K_0, K_N) - 1.0) < 1e-12


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_reversible_limit_gives_carnot_for_any_length(n: int) -> None:
    rng = np.random.default_rng(n)
    T0, TN, K_0, K_mid, K_N = _random_chain(rng, n)
    cap = ch.flux_cap(K_0, K_mid, K_N)
    gaps = []
    for frac in [1e-3, 1e-4, 1e-5]:
        J0, JN, _ = ch.end_heats(frac * cap, T0, TN, K_0, K_mid, K_N)
        gaps.append(abs((J0 - JN) / J0 - (1.0 - TN / T0)))
    # the gap to Carnot closes linearly in the flux (so it vanishes in the reversible limit)
    assert all(abs(gaps[i] / gaps[i + 1] - 10.0) < 0.1 for i in range(len(gaps) - 1))


@pytest.mark.parametrize("seed", range(8))
def test_energy_and_entropy_balance(seed: int) -> None:
    rng = np.random.default_rng(5000 + seed)
    n = 2 + seed % 3
    T0, TN, K_0, K_mid, K_N = _random_chain(rng, n)
    s_opt = ch.max_total_numeric(T0, TN, K_0, K_mid, K_N)[1]
    s1 = rng.uniform(0.05, 1.0) * s_opt  # below the optimum the chain always delivers work
    J0, JN, _ = ch.end_heats(s1, T0, TN, K_0, K_mid, K_N)
    assert J0 > JN
    J_mid = sorted(rng.uniform(JN, J0, n - 1), reverse=True)
    st = ch.chain_state(s1, J_mid, T0, TN, K_0, K_mid, K_N)
    assert abs(sum(st["shares"]) / st["total"] - 1.0) < 1e-12
    produced = sum(st["contact_entropy_production"])
    assert all(x >= -1e-15 for x in st["contact_entropy_production"])
    assert abs(produced / (JN / TN - J0 / T0) - 1.0) < 1e-10


@pytest.mark.parametrize("seed", range(6))
def test_two_stage_chain_from_temperatures_matches_flux_route(seed: int) -> None:
    rng = np.random.default_rng(6000 + seed)
    T0, TN, K_0, K_mid, K_N = _random_chain(rng, 2)
    K23 = K_mid[0]
    s1 = rng.uniform(0.1, 0.6) * ch.flux_cap(K_0, K_mid, K_N)
    J0f, JNf, _ = ch.end_heats(s1, T0, TN, K_0, K_mid, K_N)
    # independent route: pick the working temperatures of stage 1, march heat down the contacts
    a1 = K_0 * T0 / (K_0 + s1)              # from J0 = K_0 (T0 - a1) = s1 a1
    J0 = K_0 * (T0 - a1)
    J1 = rng.uniform(0.3, 0.7) * J0          # stage 1 keeps the rest
    b1 = J1 * a1 / J0                        # reversible stage: J0/a1 = J1/b1
    a2 = b1 - J1 / K23                       # middle contact
    s2 = J1 / a2
    b2 = K_N * TN / (K_N - s2)               # last contact: s2 b2 = K_N (b2 - TN)
    J2 = s2 * b2
    assert abs(J0 / J0f - 1.0) < 1e-12
    assert abs(J2 / JNf - 1.0) < 1e-10


def test_sharing_is_zero_sum_at_fixed_flux() -> None:
    T0, TN, K_0, K_mid, K_N = 1000.0, 50.0, 1.0, [1.5, 0.7], 2.0
    s1 = 0.4 * ch.flux_cap(K_0, K_mid, K_N)
    J0, JN, _ = ch.end_heats(s1, T0, TN, K_0, K_mid, K_N)
    rng = np.random.default_rng(0)
    totals, firsts = [], []
    for _ in range(50):
        J_mid = sorted(rng.uniform(JN, J0, 2), reverse=True)
        st = ch.chain_state(s1, J_mid, T0, TN, K_0, K_mid, K_N)
        totals.append(st["total"])
        firsts.append(st["shares"][0])
    assert max(totals) - min(totals) < 1e-12 * abs(totals[0])
    # extremes: the first stage takes everything, or nothing
    all_first = ch.chain_state(s1, [JN, JN], T0, TN, K_0, K_mid, K_N)
    none_first = ch.chain_state(s1, [J0, J0], T0, TN, K_0, K_mid, K_N)
    assert abs(all_first["shares"][0] / all_first["total"] - 1.0) < 1e-12
    assert abs(none_first["shares"][0]) < 1e-12 * abs(none_first["total"])
    assert min(firsts) >= 0.0


def test_each_hand_off_costs_and_chain_persistence() -> None:
    T0, TN, k = 5000.0, 3.0, 1.0
    one = ch.max_total_closed_form(T0, TN, k, [], k)
    for n in [2, 3, 5, 10]:
        K_mid = [ch.series(k, k)] * (n - 1)     # each middle reservoir has two contacts of conductance k
        p = ch.max_total_numeric(T0, TN, k, K_mid, k)[0]
        assert abs(p / (one / n) - 1.0) < 1e-10
    needs = [10.0, 20.0, 30.0]
    K_mid = [ch.series(k, k)] * 2
    p3 = ch.max_total_closed_form(T0, TN, k, K_mid, k)
    scale_ok = 0.999 * p3 / sum(needs)
    scale_bad = 1.001 * p3 / sum(needs)
    assert ch.chain_can_persist([x * scale_ok for x in needs], T0, TN, k, K_mid, k)
    assert not ch.chain_can_persist([x * scale_bad for x in needs], T0, TN, k, K_mid, k)
