"""Wave O4: the parent-action scalar field propagates inside the light cone.

(a) The leapfrog solution of the PDE converges at second order to the exact retarded solution (J0 route).
(b) Known limit m -> 0: it also converges to the independent d'Alembert closed form (error functions).
(c) Causality: outside the cone (|x| > t + 8 sigma) the PDE solution and the exact solution vanish to 1e-10.
(d) Negative control: the quasi-static (instantaneous) screened response is not zero there, so the cone
    statement is not trivial; it also agrees with a direct quadrature of its defining convolution.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest
from scipy.integrate import quad

pytestmark = pytest.mark.physics

fc = importlib.import_module("docs.core.03_lanes.observation.uet_field_causality")
SIGMA, T_END, HALF = 0.5, 4.0, 14.0


def _errors(mass: float, dxs, reference):
    errs = []
    for dx in dxs:
        x, psi = fc.leapfrog_response(mass, SIGMA, dx, T_END, HALF)
        sel = np.abs(x) <= 6.0
        ref = reference(x[sel])
        errs.append(float(np.max(np.abs(psi[sel] - ref))) / float(np.max(np.abs(ref))))
    return errs


def test_pde_converges_at_second_order_to_exact_retarded_solution() -> None:
    errs = _errors(1.0, (0.1, 0.05, 0.025), lambda x: fc.exact_response(T_END, x, 1.0, SIGMA))
    orders = [math.log2(errs[i] / errs[i + 1]) for i in range(2)]
    assert errs[-1] < 1e-3, errs
    assert all(1.8 < o < 2.2 for o in orders), (errs, orders)


def test_massless_limit_matches_dalembert_closed_form() -> None:
    errs = _errors(0.0, (0.1, 0.05, 0.025), lambda x: fc.massless_dalembert(T_END, x, SIGMA))
    orders = [math.log2(errs[i] / errs[i + 1]) for i in range(2)]
    assert errs[-1] < 1e-3, errs
    assert all(1.8 < o < 2.2 for o in orders), (errs, orders)
    # and the J0 route reduces to the same function at m = 0
    x = np.linspace(-6, 6, 25)
    assert np.max(np.abs(fc.exact_response(T_END, x, 0.0, SIGMA) - fc.massless_dalembert(T_END, x, SIGMA))) < 1e-12


@pytest.mark.parametrize("mass", [0.0, 1.0])
def test_nothing_outside_the_light_cone(mass: float) -> None:
    x, psi = fc.leapfrog_response(mass, SIGMA, 0.05, T_END, HALF)
    outside = np.abs(x) > T_END + 8.0 * SIGMA
    peak = float(np.max(np.abs(psi)))
    assert float(np.max(np.abs(psi[outside]))) < 1e-10 * peak
    exact_outside = fc.exact_response(T_END, x[outside][::20], mass, SIGMA)
    assert float(np.max(np.abs(exact_outside))) < 1e-10 * peak


def test_negative_control_instantaneous_response_leaks_outside_the_cone() -> None:
    mass = 1.0
    t, x_far = 1.0, np.array([6.0])  # at t = 1 the cone ends near |x| = 1
    causal = fc.exact_response(t, x_far, mass, SIGMA)[0]
    acausal = fc.instantaneous_screened_response(x_far, mass, SIGMA)[0]
    assert abs(causal) < 1e-10 and acausal > 1e-3
    # the closed form equals the defining convolution with e^{-m|x|}/(2m)
    direct = quad(lambda y: math.exp(-mass * abs(6.0 - y)) / (2 * mass) * float(fc.gaussian(y, SIGMA)), -8, 8,
                  points=[0.0, 6.0], limit=200)[0]
    assert abs(direct / acausal - 1.0) < 1e-7
