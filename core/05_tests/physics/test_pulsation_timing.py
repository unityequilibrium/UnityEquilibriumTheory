"""Wave O5: P1/P2 for a pulsating star on a Kepler orbit (thought experiment v3).

1. Identity between the two observables: d tau/dt = -v_r / c (finite differences, random orbits).
2. Closed-form half range of tau matches a dense numerical scan.
3. General code path: the retarded-time solver of the observation layer, applied to the moving
   pulsator, gives a received phase gap equal to nu * (D/c + tau(t_e)) (P2: rate x record age).
4. Negative control: with an effectively instantaneous signal the phase modulation vanishes.
"""

from __future__ import annotations

import importlib
import random
from math import pi

import numpy as np
import pytest

pytestmark = pytest.mark.physics

pt = importlib.import_module("docs.core.03_lanes.observation.uet_pulsation_timing")
obs = importlib.import_module("docs.core.03_lanes.observation.uet_observation_layer")


def _orbit(seed: int):
    r = random.Random(seed)
    return dict(period=r.uniform(5, 50), t_peri=r.uniform(0, 5), e=r.uniform(0.0, 0.8), varpi=r.uniform(0, 2 * pi))


@pytest.mark.parametrize("seed", range(6))
def test_delay_derivative_is_minus_radial_velocity_over_c(seed: int) -> None:
    o, c, a_sini = _orbit(seed), 3.0, 0.7
    r = random.Random(50 + seed)
    for _ in range(10):
        t, h = r.uniform(0, 3 * o["period"]), 1e-5 * o["period"]
        dtau = (pt.time_delay(t + h, a_sini_over_c=a_sini / c, **o) - pt.time_delay(t - h, a_sini_over_c=a_sini / c, **o)) / (2 * h)
        assert dtau == pytest.approx(-pt.radial_velocity(t, a_sini=a_sini, **o) / c, rel=1e-6, abs=1e-9)


@pytest.mark.parametrize("seed", range(4))
def test_closed_form_half_range_matches_scan(seed: int) -> None:
    o = _orbit(seed)
    taus = [pt.time_delay(t, a_sini_over_c=1.0, **o) for t in np.linspace(0, o["period"], 20001)]
    assert (max(taus) - min(taus)) / 2 == pytest.approx(pt.delay_half_range(o["e"], o["varpi"], 1.0), rel=1e-5)


def test_rv_amplitude_converts_to_delay_amplitude() -> None:
    # K1 from an orbit of known a sin i, converted back with the RV-only formula.
    o, c, a_sini = _orbit(9), 3.0, 0.7
    k1 = 2 * pi * a_sini / (o["period"] * np.sqrt(1 - o["e"] ** 2))
    assert pt.a_sini_over_c_from_rv(k1, o["period"], o["e"], c) == pytest.approx(a_sini / c, rel=1e-12)


def _received_phase_gap(signal_speed: float, nu: float, distance: float, o: dict, a_sini: float, t_obs: float) -> tuple[float, float]:
    def source(t: float) -> np.ndarray:
        return np.array([distance + pt.line_of_sight_position(t, a_sini=a_sini, **o)])

    v_max = 2 * pi * a_sini / o["period"] * np.sqrt((1 + o["e"]) / (1 - o["e"])) * 1.01
    t_e = obs.retarded_time(t_obs, np.array([0.0]), source, signal_speed, v_max)
    return nu * (t_obs - t_e), t_e


@pytest.mark.parametrize("seed", range(4))
def test_retarded_phase_gap_is_rate_times_record_age(seed: int) -> None:
    o, c, nu, distance, a_sini = _orbit(seed), 1.0, 7.3, 40.0, 0.05
    r = random.Random(200 + seed)
    for _ in range(5):
        t_obs = distance / c + r.uniform(0, 2 * o["period"])
        gap, t_e = _received_phase_gap(c, nu, distance, o, a_sini, t_obs)
        assert gap == pytest.approx(nu * (distance / c - pt.time_delay(t_e, a_sini_over_c=a_sini / c, **o)), rel=1e-10)


def test_negative_control_instant_signal_shows_no_modulation() -> None:
    o, nu, distance, a_sini = _orbit(1), 7.3, 40.0, 0.05
    gaps = [_received_phase_gap(1e9, nu, distance, o, a_sini, t)[0] for t in np.linspace(0, o["period"], 40)]
    finite = [_received_phase_gap(1.0, nu, distance, o, a_sini, distance + t)[0] for t in np.linspace(0, o["period"], 40)]
    assert np.ptp(gaps) < 1e-6
    assert np.ptp(finite) > 0.5 * 2 * nu * pt.delay_half_range(o["e"], o["varpi"], a_sini)
