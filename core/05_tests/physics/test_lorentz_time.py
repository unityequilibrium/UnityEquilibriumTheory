"""Wave O7: P3 (relativity of simultaneity) and the Ives-Stilwell observable (thought experiment v3).

1. Simultaneity offset from the boost matrix equals -gamma beta dx, and vanishes at beta = 0 or dx = 0.
2. The boost preserves the interval, and the retarded Green function of the parent-action response field
   (wave O4, uet_field_causality.retarded_green_1d) is invariant under a boost: its value at a point and at the
   boosted point agree, including the cone condition.
3. The Ives-Stilwell epsilon, found by root search on the boosted photon four-vector, is zero for all beta.
4. Negative control: the absolute-time (Galilean) Doppler shift gives epsilon = gamma - 1 ~ beta^2 / 2.
5. The same Galilean boost is NOT a symmetry of the massless Green function: the cone is not preserved.
"""

from __future__ import annotations

import importlib
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

lor = importlib.import_module("docs.core.03_lanes.observation.uet_lorentz_time")
fc = importlib.import_module("docs.core.03_lanes.observation.uet_field_causality")


@pytest.mark.parametrize("beta", [0.01, 0.1, 0.338, 0.9])
def test_simultaneity_offset_is_minus_gamma_beta_dx(beta: float) -> None:
    dx = 7.3
    assert lor.simultaneity_offset(beta, dx) == pytest.approx(-lor.gamma(beta) * beta * dx, rel=1e-12)
    assert lor.simultaneity_offset(0.0, dx) == 0.0
    assert lor.simultaneity_offset(beta, 0.0) == 0.0


@pytest.mark.parametrize("seed", range(5))
def test_boost_preserves_the_interval(seed: int) -> None:
    r = random.Random(seed)
    beta, t, x = r.uniform(-0.95, 0.95), r.uniform(-5, 5), r.uniform(-5, 5)
    t2, x2 = lor.boost_matrix(beta) @ np.array([t, x])
    assert t2 * t2 - x2 * x2 == pytest.approx(t * t - x * x, rel=1e-10, abs=1e-10)


@pytest.mark.parametrize("seed", range(8))
def test_response_green_function_is_boost_invariant(seed: int) -> None:
    r = random.Random(20 + seed)
    beta, mass = r.uniform(-0.9, 0.9), r.uniform(0.0, 2.0)
    t = r.uniform(0.5, 6.0)
    x = r.uniform(-0.95, 0.95) * t  # a point inside the cone
    t2, x2 = lor.boost_matrix(beta) @ np.array([t, x])
    assert t2 > 0 and abs(x2) < t2  # the cone is preserved
    assert float(fc.retarded_green_1d(t2, x2, mass)) == pytest.approx(float(fc.retarded_green_1d(t, x, mass)), rel=1e-9)


@pytest.mark.parametrize("beta", [0.001, 0.03, 0.064, 0.338, 0.8])
def test_ives_stilwell_epsilon_vanishes_for_the_lorentz_boost(beta: float) -> None:
    assert abs(lor.ives_stilwell_epsilon(beta)) < 1e-12


@pytest.mark.parametrize("beta", [0.03, 0.338, 0.8])
def test_negative_control_absolute_time_gives_gamma_minus_one(beta: float) -> None:
    eps = lor.ives_stilwell_epsilon(beta, shift=lor.galilean_rest_frame_frequency)
    assert eps == pytest.approx(lor.gamma(beta) - 1.0, rel=1e-9)
    assert eps > 0.4 * beta**2


def test_negative_control_galilean_boost_does_not_preserve_the_massless_cone() -> None:
    # A causal pair (inside the cone) is mapped by x' = x - beta t, t' = t to a spacelike pair, so the cone
    # structure that P4 and the Green function rely on is not invariant under the absolute-time transformation.
    beta, t, x = 0.5, 4.0, -3.9
    assert abs(x) < t
    assert abs(x - beta * t) > t
    # The Lorentz boost keeps the same pair inside the cone.
    t2, x2 = lor.boost_matrix(beta) @ np.array([t, x])
    assert abs(x2) < t2
