"""Layer 3 against the Lotka-Volterra model of Saavedra et al. (2025), term by term.

1. In the fast, weak-draw pool limit the full layer-3 consumer-resource dynamics and the derived
   Lotka-Volterra dynamics give the same populations; the gap shrinks as the draw/decay ratio eps
   shrinks (first order in eps, as the expansion predicts).
2. The derived interaction matrix is a_ij = (a_j F_j)/(a_i F_i), with a_ii = 1, and has rank 1.
3. Rank 1 means one pool supports one winner: the LV equilibrium for two types is not feasible
   (one density negative or the system singular), and the full model keeps the lowest-R* type.
4. Under metabolic scaling (F ~ M, P ~ M^3/4, a ~ M^-1/4): tau ~ M^1/4, and the biomass interaction
   matrix equals Saavedra's Eq. (14), a_ij = (M_j/M_i)^-1/4.
5. Negative control: with F independent of mass (no store-to-mass link) Eq. (14) is not reproduced.
"""

from __future__ import annotations

import importlib
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

lv = importlib.import_module("core.03_lanes.persistence.uet_layer3_lv_map")
ps = importlib.import_module("core.03_lanes.persistence.uet_persistence_selection")


def _run_both(eps: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = random.Random(seed)
    a = np.array([rng.uniform(0.8, 1.2), rng.uniform(0.8, 1.2)])
    F = np.array([rng.uniform(0.8, 1.2), rng.uniform(0.8, 1.2)])
    P = np.array([rng.uniform(0.3, 0.5), rng.uniform(0.3, 0.5)])
    decay = 50.0  # fast pool
    supply = decay * 3.0 / float(np.mean(a))  # R ~ 3 / a: well above R* = P/(aF)
    # initial densities chosen so the draw sum a F n is eps * decay
    n0 = np.full(2, eps * decay / (2 * float(np.mean(a * F))))
    p = lv.lv_parameters(a, F, P, supply, decay)
    R0 = supply / (decay + float(np.sum(a * F * n0)))

    def full(y):
        dn, dR = lv.layer3_rhs(y[:2], y[2], a, F, P, supply, decay)
        return np.array([dn[0], dn[1], dR])

    horizon = 0.05
    y_full = lv.integrate(full, np.array([*n0, R0]), horizon, 1e-4)[:2]
    y_lv = lv.integrate(lambda n: lv.lv_rhs(n, p["r"], p["K"], p["A"]), n0, horizon, 1e-4)
    return y_full, y_lv


@pytest.mark.parametrize("seed", range(5))
def test_layer3_reduces_to_lotka_volterra_with_gap_of_order_eps(seed: int) -> None:
    gaps = []
    for eps in (0.04, 0.02, 0.01):
        y_full, y_lv = _run_both(eps, seed)
        gaps.append(float(np.max(np.abs(y_full - y_lv) / y_full)))
    assert gaps[0] < 0.05
    # halving eps roughly halves (or better) the relative gap: first-order expansion
    assert gaps[1] < 0.65 * gaps[0]
    assert gaps[2] < 0.65 * gaps[1]


@pytest.mark.parametrize("seed", range(10))
def test_interaction_matrix_is_ratio_of_draws_with_rank_one(seed: int) -> None:
    rng = random.Random(10 + seed)
    k = 4
    a = np.array([rng.uniform(0.1, 3) for _ in range(k)])
    F = np.array([rng.uniform(0.1, 3) for _ in range(k)])
    P = np.array([rng.uniform(0.1, 3) for _ in range(k)])
    p = lv.lv_parameters(a, F, P, supply=5.0, decay=2.0)
    draw = a * F
    assert np.allclose(np.diag(p["A"]), 1.0, rtol=1e-14)
    assert np.allclose(p["A"], draw[None, :] / draw[:, None], rtol=1e-12)
    assert np.linalg.matrix_rank(p["A"]) == 1


def test_one_pool_supports_one_winner() -> None:
    types = [ps.SystemType(capture=1.0, free_energy_store=1.0, burn_power=0.5),
             ps.SystemType(capture=1.0, free_energy_store=1.0, burn_power=0.3)]
    p = lv.lv_parameters([1.0, 1.0], [1.0, 1.0], [0.5, 0.3], supply=10.0, decay=1.0)
    with pytest.raises(np.linalg.LinAlgError):
        np.linalg.solve(p["A"], p["K"])  # rank 1: no interior equilibrium
    N, _ = ps.simulate_competition([1.0, 1.0], 1.0, types, supply=10.0, decay=1.0, horizon=400.0, dt=0.01)
    assert ps.predicted_winner(types) == 1
    assert N[0] < 1e-6 * N[1]


@pytest.mark.parametrize("seed", range(10))
def test_metabolic_scaling_reproduces_saavedra_eq14(seed: int) -> None:
    rng = random.Random(30 + seed)
    M = np.exp([rng.gauss(0.0, 2.0) for _ in range(6)])
    a, F, P = lv.metabolic_types(M)
    p = lv.lv_parameters(a, F, P, supply=1.0, decay=1.0)
    assert np.allclose(p["tau"], M**0.25, rtol=1e-12)
    A_bio = lv.to_biomass_interaction(p["A"], M)
    assert np.allclose(A_bio, (M[None, :] / M[:, None]) ** -0.25, rtol=1e-12)


def test_negative_control_store_not_proportional_to_mass() -> None:
    M = np.array([0.1, 1.0, 10.0, 100.0])
    a = M**-0.25
    F = np.ones_like(M)  # store independent of mass
    P = M**0.75
    p = lv.lv_parameters(a, F, P, supply=1.0, decay=1.0)
    A_bio = lv.to_biomass_interaction(p["A"], M)
    assert not np.allclose(A_bio, (M[None, :] / M[:, None]) ** -0.25, rtol=1e-3)
