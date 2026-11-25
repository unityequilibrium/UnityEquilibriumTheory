"""Wave D3: a chain of entropy dividers with power-law (radiative) contacts.

(a) Derivation check: every contact of the computed chain state obeys J = G (T_h^n - T_c^n)/n and
    every stage is reversible (J_{k-1}/a_k = J_k/b_k), at 24 random chains, rel < 1e-10.
(b) Known limit through the general path: n = 1 reproduces the linear chain of wave D2 (same total
    for any split) and gives marginal cost exactly 1 (zero-sum).
(c) Second law: each contact produces entropy >= 0 and the sum is J_N/T_N - J_0/T0.
(d) Second route: the marginal cost from implicit differentiation of the two-stage chain equals
    the Richardson finite difference of the general path.
(e) Sign: c > 1 for n > 1 (radiation: taking work upstream costs the rest more than one for one),
    c < 1 for n < 1.
(f) Reversible limit: as s_1 -> 0 the chain efficiency tends to 1 - T_N/T0 for n = 4 and n = -1.
"""

from __future__ import annotations

import importlib

import numpy as np
import pytest

pytestmark = pytest.mark.physics

rc = importlib.import_module("docs.core.03_lanes.persistence.uet_entropy_chain_radiative")
ch = importlib.import_module("docs.core.03_lanes.persistence.uet_entropy_chain")


def _flux_scale(T0, TN, G0, G_mid, GN, n):
    """Entropy flux a contact G carries with a small temperature drop at T is about G T^(n-1); the
    chain is limited by its weakest contact, at the coldest temperature for n > 1 and the hottest for n < 1."""

    T_lim = TN if n > 1.0 else T0
    return min([G0 * T0 ** (n - 1.0), GN * TN ** (n - 1.0)] + [g * T_lim ** (n - 1.0) for g in G_mid])


def _feasible_state(rng: np.random.Generator, n: float, n_stages: int, frac_range=(0.6, 0.95)):
    """Random chain and a valid (s1, J_mid); returns parameters and state."""

    for _ in range(200):
        T0 = 10 ** rng.uniform(2.5, 4)
        TN = T0 * rng.uniform(0.001, 0.3)
        G0, GN = 10 ** rng.uniform(-1, 1, 2)
        G_mid = list(10 ** rng.uniform(-1, 1, n_stages - 1))
        s1 = _flux_scale(T0, TN, G0, G_mid, GN, n) * 10 ** rng.uniform(-2, 0)
        try:
            a1 = rc._source_side(s1, T0, G0, n)
            J0 = s1 * a1
            fr = sorted(rng.uniform(*frac_range, n_stages - 1), reverse=True)
            J_mid = [J0 * np.prod(fr[: k + 1]) for k in range(n_stages - 1)]
            st = rc.chain_state(s1, J_mid, T0, TN, G0, G_mid, GN, n)
        except ValueError:
            continue
        if st["total"] > 0.0:
            return (T0, TN, G0, G_mid, GN), s1, J_mid, st
    raise RuntimeError("no feasible chain found")


@pytest.mark.parametrize("seed", range(24))
def test_contact_laws_and_reversible_stages(seed: int) -> None:
    rng = np.random.default_rng(7000 + seed)
    n = [4.0, 2.0, 0.5, -1.0][seed % 4]
    (T0, TN, G0, G_mid, GN), s1, J_mid, st = _feasible_state(rng, n, 2 + seed % 3)
    J, a, b = st["J"], st["a"], st["b"]

    def law_ok(G: float, T_h: float, T_c: float, J_k: float) -> bool:
        # T_h^n - T_c^n cancels digits when the drop is small: allow eps * T_h^n / |T_h^n - T_c^n|
        cancel = max(abs(T_h ** n), abs(T_c ** n)) / abs(T_h ** n - T_c ** n)
        return abs(rc.transfer(G, T_h, T_c, n) / J_k - 1.0) < 1e-10 + 1e-14 * cancel

    assert law_ok(G0, T0, a[0], J[0])
    for k, G in enumerate(G_mid):
        assert law_ok(G, b[k], a[k + 1], J[k + 1])
    assert law_ok(GN, b[-1], TN, J[-1])
    for k in range(len(a)):
        assert abs((J[k] / a[k]) / (J[k + 1] / b[k]) - 1.0) < 1e-12


@pytest.mark.parametrize("seed", range(6))
def test_linear_limit_reproduces_wave_d2(seed: int) -> None:
    rng = np.random.default_rng(8000 + seed)
    (T0, TN, G0, G_mid, GN), s1, J_mid, st = _feasible_state(rng, 1.0, 3)
    linear = ch.total_power(s1, T0, TN, G0, G_mid, GN)
    assert abs(st["total"] / linear - 1.0) < 1e-10
    for k in (1, 2):
        assert abs(rc.marginal_cost(k, s1, J_mid, T0, TN, G0, G_mid, GN, 1.0) - 1.0) < 1e-8


@pytest.mark.parametrize("seed", range(8))
def test_second_law_per_contact(seed: int) -> None:
    rng = np.random.default_rng(9000 + seed)
    n = [4.0, 0.5][seed % 2]
    (T0, TN, *_), s1, J_mid, st = _feasible_state(rng, n, 3)
    sigma = st["contact_entropy_production"]
    assert all(x > 0.0 for x in sigma)
    J = st["J"]
    assert abs(sum(sigma) / (J[-1] / TN - J[0] / T0) - 1.0) < 1e-10


def _analytic_marginal_cost_two_stage(s1, J1, TN, G_mid, GN, n):
    s2 = (s1 ** (-n) - n * J1 ** (1.0 - n) / G_mid) ** (-1.0 / n)
    ds2_dJ1 = (1.0 - n) * J1 ** (-n) * s2 ** (n + 1.0) / G_mid
    b = rc._sink_side(s2, TN, GN, n)
    dJN_ds2 = b * GN * b ** (n - 1.0) / (GN * b ** (n - 1.0) - s2)
    return 1.0 - dJN_ds2 * ds2_dJ1


@pytest.mark.parametrize("seed", range(10))
def test_marginal_cost_two_routes(seed: int) -> None:
    rng = np.random.default_rng(10000 + seed)
    n = [4.0, 2.0, 0.5, -1.0, 3.0][seed % 5]
    (T0, TN, G0, G_mid, GN), s1, J_mid, st = _feasible_state(rng, n, 2)
    numeric = rc.marginal_cost(1, s1, J_mid, T0, TN, G0, G_mid, GN, n)
    analytic = _analytic_marginal_cost_two_stage(s1, J_mid[0], TN, G_mid[0], GN, n)
    assert abs(numeric / analytic - 1.0) < 1e-7


@pytest.mark.parametrize("n,above_one", [(4.0, True), (2.0, True), (0.5, False), (-1.0, False)])
def test_sign_of_the_marginal_cost(n: float, above_one: bool) -> None:
    rng = np.random.default_rng(int(10 * n) + 50)
    for _ in range(6):
        (T0, TN, G0, G_mid, GN), s1, J_mid, st = _feasible_state(rng, n, 3)
        for k in (1, 2):
            c = rc.marginal_cost(k, s1, J_mid, T0, TN, G0, G_mid, GN, n)
            assert (c > 1.0) == above_one


@pytest.mark.parametrize("n", [4.0, -1.0])
def test_reversible_limit_is_carnot(n: float) -> None:
    T0, TN, G0, G_mid, GN = 5778.0, 2.725, 1.0, [0.5], 2.0
    scale = _flux_scale(T0, TN, G0, G_mid, GN, n)
    gaps = []
    for frac in [1e-3, 1e-4, 1e-5]:
        s1 = frac * scale
        J0 = s1 * rc._source_side(s1, T0, G0, n)
        st = rc.chain_state(s1, [0.8 * J0], T0, TN, G0, G_mid, GN, n)
        gaps.append(abs(st["total"] / J0 - (1.0 - TN / T0)))
    # the gap to Carnot closes linearly in the flux
    assert all(abs(gaps[i] / gaps[i + 1] - 10.0) < 0.2 for i in range(len(gaps) - 1))
