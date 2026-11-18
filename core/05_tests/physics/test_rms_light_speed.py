"""Wave O8: Michelson-Morley and Kennedy-Thorndike combinations from the parent action's local boost.

1. With a, b, d read off the boost matrix of the parent action's local frame, the two-way speed of light
   is exactly 1 for every laboratory speed and rod angle (not only to order v^2).
2. The boost used here is the one uet_lorentz_time.boost_matrix gives: a = 1/gamma, b = gamma, d = 1.
3. The fitted Robertson-Mansouri-Sexl parameters of the boost are alpha = -1/2, beta = 1/2, delta = 0,
   and both combinations P_MM = beta - delta - 1/2 and P_KT = alpha - beta + 1 vanish.
4. Precision: the model's P_MM and P_KT are below 1e-20, far under the 8e-12 and 3.7e-8 uncertainties of
   the T022 data. (The first T022 run used 64-bit floats and got -1.3e-10, which failed this check.)
5. The light-travel solver reproduces the O(v^2) test-theory formula for arbitrary alpha, beta, delta
   (a check that the solver is not tuned to the Lorentz case), with the sin^2 theta form checked at pi/4.
6. Negative controls: Galilean kinematics gives P_MM = -1/2, P_KT = 1; contraction without time
   dilation gives P_MM = 0 but P_KT = 1/2.
"""

from __future__ import annotations

import importlib
import random
from math import pi, sqrt

import numpy as np
import pytest

pytestmark = pytest.mark.physics

rms = importlib.import_module("core.03_lanes.observation.uet_rms_light_speed")
lor = importlib.import_module("core.03_lanes.observation.uet_lorentz_time")


@pytest.mark.parametrize("seed", range(25))
def test_lorentz_two_way_speed_is_exactly_one(seed: int) -> None:
    r = random.Random(seed)
    v, theta, length = r.uniform(0.0, 0.95), r.uniform(0.0, 2 * pi), r.uniform(0.1, 10.0)
    c = rms.two_way_light_speed(v, theta, rms.lorentz_from_boost, length)
    assert abs(c - 1) < 1e-40  # 60-digit arithmetic


@pytest.mark.parametrize("v", [0.01, 0.338, 0.9])
def test_boost_is_the_observation_layer_boost(v: float) -> None:
    ours = rms.boost_matrix(v)
    theirs = lor.boost_matrix(v)
    for i in range(2):
        for j in range(2):
            assert float(ours[i, j]) == pytest.approx(theirs[i, j], rel=1e-14)
    a, b, d = rms.lorentz_from_boost(v)
    assert float(a) == pytest.approx(1.0 / lor.gamma(v), rel=1e-14)
    assert float(b) == pytest.approx(lor.gamma(v), rel=1e-14)
    assert d == 1


def test_boost_rms_parameters_and_combinations() -> None:
    p = rms.rms_combinations(rms.lorentz_from_boost)
    assert p["alpha"] == pytest.approx(-0.5, abs=1e-9)
    assert p["beta"] == pytest.approx(0.5, abs=1e-9)
    assert p["delta"] == 0.0


def test_model_error_is_far_below_the_data_precision() -> None:
    p = rms.rms_combinations(rms.lorentz_from_boost)
    assert abs(p["P_MM"]) < 1e-20  # Herrmann et al. 2009: sigma = 8e-12
    assert abs(p["P_KT"]) < 1e-20  # Tobar et al. 2010: sigma = 3.7e-8
    assert abs(p["residual_quarter"]) < 1e-20


@pytest.mark.parametrize("seed", range(20))
def test_solver_reproduces_the_order_v2_test_theory(seed: int) -> None:
    r = random.Random(100 + seed)
    al, be, de = r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)

    def kin(v):
        return 1 + al * v * v, 1 + be * v * v, 1 + de * v * v

    p = rms.rms_combinations(kin)
    assert p["P_MM"] == pytest.approx(be - de - 0.5, abs=1e-9)
    assert p["P_KT"] == pytest.approx(al - be + 1.0, abs=1e-9)
    assert abs(p["residual_quarter"]) < 1e-9


def test_galilean_control_fails_both() -> None:
    p = rms.rms_combinations(rms.galilean)
    assert p["P_MM"] == pytest.approx(-0.5, abs=1e-9)
    assert p["P_KT"] == pytest.approx(1.0, abs=1e-9)


def test_contraction_only_passes_mm_and_fails_kt() -> None:
    p = rms.rms_combinations(rms.contraction_only)
    assert abs(p["P_MM"]) < 1e-20
    assert p["P_KT"] == pytest.approx(0.5, abs=1e-9)
    # no anisotropy at finite speed, but the two-way speed depends on v: slower by 1/gamma
    c1 = float(rms.two_way_light_speed(0.3, 0.0, rms.contraction_only))
    c2 = float(rms.two_way_light_speed(0.3, pi / 2, rms.contraction_only))
    assert c1 == pytest.approx(c2, rel=1e-14)
    assert c1 == pytest.approx(sqrt(1 - 0.09), rel=1e-14)
