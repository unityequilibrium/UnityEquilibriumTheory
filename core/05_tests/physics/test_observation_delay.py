"""Wave O1: delayed observation and gap = rate x record age (thought experiment v3, P1 and P2).

(a) The bracketed root search agrees with an independent closed form for uniform motion in 3-D
    (known solution through a different path).
(b) Known limits: a static source has zero gap; u -> infinity gives a ~ D/u -> 0.
(c) P2: for an accelerating source the first-order estimate Delta ~ Xdot(t_e) a has relative
    error proportional to a (first-order convergence), as the Taylor remainder 1/2 Xddot a^2 requires.
(d) Negative control: an observer who treats the record as the present is wrong by exactly Delta,
    and the error vanishes only when the source is static or the delay is zero.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest

pytestmark = pytest.mark.physics

obs = importlib.import_module("docs.core.03_lanes.observation.uet_observation_layer")
U = 1.0


@pytest.mark.parametrize("seed", range(10))
def test_retarded_time_matches_closed_form_for_uniform_motion(seed: int) -> None:
    rng = np.random.default_rng(seed)
    x_obs = rng.uniform(-3, 3, 3)
    x0 = rng.uniform(-10, 10, 3)
    v = rng.uniform(-0.6, 0.6, 3)
    vmax = float(np.linalg.norm(v))
    t_obs = rng.uniform(0.0, 5.0)
    numeric = obs.retarded_time(t_obs, x_obs, lambda t: x0 + v * t, U, vmax)
    exact = obs.retarded_time_uniform_motion(t_obs, x_obs, x0, v, U)
    assert abs(numeric - exact) < 1e-10
    # defining relation of the retarded time
    assert abs(numeric + np.linalg.norm(x_obs - (x0 + v * numeric)) / U - t_obs) < 1e-10


def test_static_source_has_zero_gap_and_delay_is_distance_over_speed() -> None:
    x_s = np.array([6.0, 0.0, 0.0])
    t_e = obs.retarded_time(10.0, np.zeros(3), lambda t: x_s, U, 0.0)
    assert t_e == pytest.approx(10.0 - 6.0 / U, abs=1e-12)
    assert np.all(obs.gap(10.0, t_e, lambda t: x_s) == 0.0)


def test_instantaneous_limit_u_to_infinity() -> None:
    d = 5.0
    ages = []
    for u in (1e2, 1e3, 1e4):
        t_e = obs.retarded_time(3.0, [0, 0, 0], lambda t: np.array([d + 0.2 * t, 0, 0]), u, 0.2)
        ages.append(obs.record_age(3.0, t_e))
    assert all(abs(a * u / (d + 0.6) - 1.0) < 2e-3 for a, u in zip(ages, (1e2, 1e3, 1e4)))
    assert ages[0] > ages[1] > ages[2]


def _x(t: float, g: float) -> np.ndarray:
    return np.array([2.0 + 0.3 * t + 0.5 * g * t * t, 0.0, 0.0])


def test_first_order_gap_has_first_order_convergence_in_the_record_age() -> None:
    g = 0.1  # acceleration; source speed stays below u (0.3 + 0.1 t_o = 0.6 at t_o = 3)
    rel = []
    for d in (4.0, 2.0, 1.0, 0.5):  # distance to the source at reception: halving it halves the age
        t_o = 3.0
        x_obs = _x(t_o, g) - np.array([d, 0.0, 0.0])
        t_e = obs.retarded_time(t_o, x_obs, lambda t: _x(t, g), U, 0.3 + g * t_o)
        a = obs.record_age(t_o, t_e)
        delta = obs.gap(t_o, t_e, lambda t: _x(t, g))
        rate_at_emission = np.array([0.3 + g * t_e, 0.0, 0.0])
        est = obs.first_order_gap(rate_at_emission, a)
        rel.append(abs(est[0] - delta[0]) / abs(delta[0]))
    ratios = [rel[i] / rel[i + 1] for i in range(len(rel) - 1)]
    # relative error ~ a: the ratio between successive halvings tends to 2 from above as a -> 0
    assert ratios[0] > ratios[1] > ratios[2] > 2.0 and abs(ratios[2] - 2.0) < 0.12, (rel, ratios)


@pytest.mark.parametrize("rate,age", [(0.5, 3.0), (0.2, 7.0), (0.9, 1.0)])
def test_ignoring_the_delay_costs_exactly_rate_times_age_for_uniform_motion(rate: float, age: float) -> None:
    x_s = lambda t: np.array([10.0 + rate * t, 0.0, 0.0])  # noqa: E731
    t_o = 20.0
    t_e = t_o - age
    naive_error = obs.gap(t_o, t_e, x_s)[0]
    assert naive_error == pytest.approx(rate * age, rel=1e-12)
    # negative controls: no motion or no age means no error
    assert obs.gap(t_o, t_e, lambda t: np.array([10.0, 0, 0]))[0] == 0.0
    assert obs.gap(t_o, t_o, x_s)[0] == 0.0
