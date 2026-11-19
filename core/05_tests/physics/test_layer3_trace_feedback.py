"""Layer 3 with trace feedback (author 2026-11-19: the trace changes the environment of later systems).

1. Known limit through the general code path: with beta = 0 the feedback integrator reproduces the layer 3
   integrator without feedback (uet_layer3_from_action.simulate) at 20 random sets (rel < 1e-6).
2. Steady trace: the integrated E of one type alone equals the upper closed-form root at 20 random sets.
3. Derivation check at 20 random sets: the rate of type 2 entering type 1's steady state is zero at S_c,
   negative just below and positive just above.
4. Hysteresis in full dynamics (4 random sets with a window S_b < 0.95 S_c): lowering the supply from 1.4 S_c into
   the window keeps type 2; raising it from 0.7 S_b into the window keeps type 1; above S_c type 2 wins from
   either order.
5. Negative control: without feedback (beta_2 = 0) the same supply paths both end with type 1.
6. Obligate succession: if S_c < S < delta R*_2(0), type 2 alone dies out from an empty environment but replaces
   type 1 when type 1 came first (4 random sets).
"""

from __future__ import annotations

import importlib
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

tf = importlib.import_module("core.03_lanes.persistence.uet_layer3_trace_feedback")
l3 = importlib.import_module("core.03_lanes.persistence.uet_layer3_from_action")


def test_no_feedback_limit_reproduces_layer3():
    rng = random.Random(1)
    for _ in range(20):
        a0 = np.array([rng.uniform(0.5, 2.0), rng.uniform(0.5, 2.0)])
        d = np.array([rng.uniform(0.1, 0.5), rng.uniform(0.1, 0.5)])
        F = np.array([rng.uniform(0.5, 2.0), rng.uniform(0.5, 2.0)])
        delta = rng.uniform(0.1, 0.5)
        S = delta * max(d / a0) * rng.uniform(2.0, 5.0)
        n0, horizon = np.array([1e-2, 1e-2]), 400.0
        n_tf, R_tf, _ = tf.simulate(a0, [0.0, 0.0], d, F, S, delta, rng.uniform(0.1, 1.0), rng.uniform(0.1, 1.0),
                                    n0, S / delta, 0.0, horizon)
        n_l3, R_l3 = l3.simulate(a0, d, F, S, delta, n0, S / delta, horizon)
        scale = max(np.max(n_l3), 1e-3)
        assert np.max(np.abs(n_tf - n_l3)) / scale < 1e-6
        assert abs(R_tf - R_l3) / R_l3 < 1e-6


def test_steady_trace_matches_closed_form():
    rng = random.Random(2)
    for _ in range(20):
        a0, d, F = rng.uniform(0.5, 2.0), rng.uniform(0.1, 0.5), rng.uniform(0.5, 2.0)
        beta = rng.uniform(-0.3, 1.0)
        delta, w, kappa = rng.uniform(0.1, 0.5), rng.uniform(0.2, 1.0), rng.uniform(0.2, 1.0)
        S = delta * d / a0 * rng.uniform(2.0, 4.0)
        E_closed = tf.trace_steady_state(a0, beta, d, S, delta, w, kappa)
        n, R, E = tf.simulate([a0], [beta], [d], [F], S, delta, w, kappa, [1e-2], S / delta, 0.0, 3000.0)
        assert abs(E - E_closed) / E_closed < 1e-6
        assert abs(R - tf.r_star(a0, beta, d, E_closed)) / R < 1e-6


def _draw(rng):
    a0 = np.array([1.0, rng.uniform(0.6, 0.9)])
    d = np.array([rng.uniform(0.15, 0.3)] * 2)
    beta2 = rng.uniform(0.5, 8.0)
    delta, w, kappa = rng.uniform(0.1, 0.3), rng.uniform(0.5, 1.0), rng.uniform(0.05, 0.5)
    return a0, d, beta2, delta, w, kappa


def _winner(n) -> int:
    if max(n) < 1e-3:
        return -1
    return int(np.argmax(n)) if min(n) < 1e-4 * max(n) else -2


def _orders(a0, d, beta, S, delta, w, kappa):
    F = [1.0, 1.0]
    return tuple(_winner(tf.resident_then_invader(r, a0, beta, d, F, S, delta, w, kappa, 1500.0)) for r in (0, 1))


def test_invasion_rate_of_type2_switches_sign_at_critical_supply():
    rng = random.Random(5)
    for _ in range(20):
        a0, d, beta2, delta, w, kappa = _draw(rng)
        s_c = tf.critical_supply(d[0] / a0[0], d[1] / a0[1], beta2, delta, w, kappa)
        assert abs(tf.invasion_rates(a0, d, beta2, s_c, delta, w, kappa)[0]) < 1e-10
        assert tf.invasion_rates(a0, d, beta2, 0.99 * s_c, delta, w, kappa)[0] < 0.0
        assert tf.invasion_rates(a0, d, beta2, s_c / 0.99, delta, w, kappa)[0] > 0.0


def _window_sets(n: int):
    """Sets with a hysteresis window S_b < 0.95 S_c."""
    rng = random.Random(6)
    out = []
    while len(out) < n:
        a0, d, beta2, delta, w, kappa = _draw(rng)
        s_c = tf.critical_supply(d[0] / a0[0], d[1] / a0[1], beta2, delta, w, kappa)
        s_b = tf.lower_priority_supply(a0, d, beta2, delta, w, kappa)
        if s_b < 0.95 * s_c:
            out.append((a0, d, beta2, delta, w, kappa, s_b, s_c))
    return out


def _supply_path(a0, d, beta, s_start, s_end, delta, w, kappa):
    """Settle both types at s_start (type 1 first, then type 2), then move the supply to s_end and settle."""
    F = [1.0, 1.0]
    n, R, E = tf.resident_then_invader_state(0, a0, beta, d, F, s_start, delta, w, kappa, 1500.0)
    n2, _, _ = tf.simulate(a0, beta, d, F, s_end, delta, w, kappa, np.maximum(n, 1e-6), R, E, 1500.0)
    return _winner(n2)


def test_supply_history_sets_the_winner_in_the_window():
    for a0, d, beta2, delta, w, kappa, s_b, s_c in _window_sets(4):
        mid = 0.5 * (s_b + s_c)
        beta = [0.0, beta2]
        assert _orders(a0, d, beta, 1.4 * s_c, delta, w, kappa) == (1, 1)
        assert _supply_path(a0, d, beta, 1.4 * s_c, mid, delta, w, kappa) == 1
        assert _supply_path(a0, d, beta, 0.7 * s_b, mid, delta, w, kappa) == 0


def test_without_feedback_supply_history_does_not_matter():
    for a0, d, _beta2, delta, w, kappa, s_b, s_c in _window_sets(4):
        mid = 0.5 * (s_b + s_c)
        assert _supply_path(a0, d, [0.0, 0.0], 1.4 * s_c, mid, delta, w, kappa) == 0
        assert _supply_path(a0, d, [0.0, 0.0], 0.7 * s_b, mid, delta, w, kappa) == 0


def test_obligate_succession_needs_a_pioneer():
    rng = random.Random(7)
    done = 0
    while done < 4:
        a0, d, beta2, delta, w, kappa = _draw(rng)
        s_c = tf.critical_supply(d[0] / a0[0], d[1] / a0[1], beta2, delta, w, kappa)
        r2_0 = d[1] / a0[1]
        if not 1.25 * s_c < 0.8 * delta * r2_0:
            continue
        done += 1
        S = 0.5 * (1.25 * s_c + 0.8 * delta * r2_0)
        F = [1.0, 1.0]
        alone, _, _ = tf.simulate(a0, [0.0, beta2], d, F, S, delta, w, kappa, [0.0, 1e-2], S / delta, 0.0, 1500.0)
        assert alone[1] < 1e-6
        assert _winner(tf.resident_then_invader(0, a0, [0.0, beta2], d, F, S, delta, w, kappa, 1500.0)) == 1
