"""Wave S3: alive fraction of the seen sources on the past light cone of Lambda-CDM.

(a) Derivation check: comoving distance from the cosmic-time integral equals the scale-factor
    integral int da / (a^2 H(a)) at 20 random emission times, rel < 1e-9; the closed-form age
    equals the numerical age of wave D6.
(b) Known limit through the general path, with convergence: for shallow surveys the alive fraction
    tends to the static result of S2, 1 - 3 lambda/4, with an error falling linearly in the depth
    (order 1.0 +- 0.15 over three depths).
(c) Identity: if tau >= t0 nobody born since t = 0 has died, so the fraction is 1 at every depth.
(d) Second route (seeded Monte Carlo on the light cone): the sampled alive fraction matches the
    shell integral within binomial errors, for the whole cone and for a z = 1 cut.
"""

from __future__ import annotations

import importlib
from math import asinh, log, sqrt

import numpy as np
import pytest
from scipy.integrate import quad

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_seen_but_gone_cosmic")
cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")


def _t_of_a(a: float) -> float:
    return 2.0 / (3.0 * m.H_L_GYR) * asinh(sqrt(1.0 / m.RATIO) * a ** 1.5)


@pytest.mark.parametrize("seed", range(20))
def test_comoving_distance_matches_scale_factor_integral(seed: int) -> None:
    rng = np.random.default_rng(17000 + seed)
    a_e = 10 ** rng.uniform(-3, -0.01)
    H_gyr = lambda a: cd.hubble(a) * m.GYR  # noqa: E731
    other, _ = quad(lambda a: 1.0 / (a * a * H_gyr(a)), a_e, 1.0, epsabs=0.0, epsrel=1e-12, limit=400)
    assert abs(m.comoving_distance(_t_of_a(a_e)) / other - 1.0) < 1e-9


def test_age_matches_numeric_integral() -> None:
    assert abs(m.T0 / (cd.time_of_a_numeric(1.0) / m.GYR) - 1.0) < 1e-10


def test_shallow_survey_tends_to_static_result_linearly() -> None:
    lam = 0.5
    errors, depths = [], [0.4, 0.2, 0.1]
    for dt in depths:
        t_min = m.T0 - dt
        tau = m.comoving_distance(t_min) / lam
        A = m.alive_fraction(t_min, tau)
        errors.append(abs(A - (1.0 - 3.0 * lam / 4.0)))
    orders = [log(errors[i] / errors[i + 1]) / log(depths[i] / depths[i + 1]) for i in range(2)]
    for p in orders:
        assert abs(p - 1.0) < 0.15
    assert errors[-1] < 0.01


@pytest.mark.parametrize("tau", [13.9, 20.0, 1000.0])
def test_no_ghosts_when_lifetime_exceeds_age(tau: float) -> None:
    for t_min in (0.0, 1.0, 6.0, 13.0):
        assert abs(m.alive_fraction(t_min, tau) - 1.0) < 1e-12


@pytest.mark.parametrize("tau,z_cut,seed", [(10.0, None, 21), (5.0, 1.0, 22)])
def test_light_cone_monte_carlo(tau: float, z_cut, seed: int) -> None:
    rng = np.random.default_rng(seed)
    t_min = 0.0 if z_cut is None else _t_of_a(1.0 / (1.0 + z_cut))
    seen, alive = m.simulate_light_cone(tau, t_min, 400_000, rng)
    A = m.alive_fraction(t_min, tau)
    p = alive / seen
    assert abs(p - A) < 5.0 * sqrt(A * (1.0 - A) / seen)
