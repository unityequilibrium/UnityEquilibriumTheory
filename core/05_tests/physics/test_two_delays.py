"""Wave O5: record delay (fixed by geometry) versus traveller ageing (bought with rest mass).

(a) Derivation check: the general worldline integration agrees with the closed forms for constant
    acceleration (fly-by, found by root search) and for the half-way flip (arrive at rest):
    tau_trip, t_trip and mass ratio at 24 random (d, alpha), rel < 1e-10.
(b) Known limit through the general path: alpha d << 1 gives the Newtonian trip sqrt(2 d/alpha),
    with no ageing difference at leading order.
(c) Physical bound and identity: for random accelerate-then-coast profiles the record age at
    arrival exceeds 2 d, the traveller ages less than the source clock, and the proper time equals
    int sqrt(1 - v^2) dt (metric identity).
(d) Second route: the rocket-equation mass ratio for exhaust speed c equals four-momentum
    conservation of photon emission, (gamma (1 + beta))^2 for start and stop.
(e) Resources remove ageing but not the record delay: as the mass ratio grows without bound,
    tau_trip -> 0 while the record age at arrival decreases only to 2 d.
"""

from __future__ import annotations

import importlib
from math import cosh, sinh, sqrt, tanh

import numpy as np
import pytest
from scipy.integrate import quad

pytestmark = pytest.mark.physics

td = importlib.import_module("docs.core.03_lanes.observation.uet_two_delays")


@pytest.mark.parametrize("seed", range(24))
def test_general_worldline_matches_closed_forms(seed: int) -> None:
    rng = np.random.default_rng(1000 + seed)
    d = 10 ** rng.uniform(-1.0, 2.5)
    alpha = 10 ** rng.uniform(-1.0, 1.0)

    # fly-by: arrival found by the root search of the general path
    exact = td.flyby_closed_form(alpha, d)
    got = td.arrival(lambda s: alpha, d, tau_max=1.5 * exact["tau_trip"] + 1.0)
    for key in ("tau_trip", "t_trip", "record_age_at_arrival"):
        assert abs(got[key] / exact[key] - 1.0) < 1e-10
    assert abs(td.mass_ratio_reaction_drive(lambda s: alpha, got["tau_trip"]) / exact["mass_ratio_photon"] - 1.0) < 1e-10

    # flip: x = d is reached at rest (a maximum), so integrate the general worldline to tau_trip
    profile, tau_half = td.flip_profile(alpha, d)
    flip = td.flip_closed_form(alpha, d)
    t_trip, x_end = td.worldline(profile, flip["tau_trip"], breakpoints=(tau_half,))
    assert abs(x_end / d - 1.0) < 1e-10
    assert abs(t_trip / flip["t_trip"] - 1.0) < 1e-10
    ratio = td.mass_ratio_reaction_drive(profile, flip["tau_trip"], 1.0, breakpoints=(tau_half,))
    assert abs(ratio / flip["mass_ratio_photon"] - 1.0) < 1e-10


@pytest.mark.parametrize("eps", [1e-4, 1e-5, 1e-6])
def test_newtonian_limit_through_general_path(eps: float) -> None:
    d, alpha = 1.0, eps  # alpha d = eps << 1
    got = td.arrival(lambda s: alpha, d, tau_max=10.0 / sqrt(alpha))
    newton = sqrt(2.0 * d / alpha)
    # relativistic corrections are O(alpha d)
    assert abs(got["t_trip"] / newton - 1.0) < eps
    assert abs(got["tau_trip"] / got["t_trip"] - 1.0) < eps


@pytest.mark.parametrize("seed", range(8))
def test_record_age_bound_and_metric_identity(seed: int) -> None:
    rng = np.random.default_rng(seed)
    d = rng.uniform(0.5, 50.0)
    a1, a2 = rng.uniform(0.05, 5.0, 2)
    tb = rng.uniform(0.1, 3.0)
    eta_peak = a1 * tb

    def coast_profile(s: float) -> float:
        """Accelerate for tb, then coast; this always reaches d (a brake could stop short)."""
        return a1 if s < tb else 0.0

    use = coast_profile
    got = td.arrival(use, d, tau_max=d / sinh(eta_peak) + tb + 10.0, breakpoints=(tb,))
    assert got["record_age_at_arrival"] > 2.0 * d
    assert got["tau_trip"] < got["t_trip"]

    # metric identity: tau = int sqrt(1 - v^2) dt along the same worldline (v as function of tau)
    def v_of_tau(s: float) -> float:
        return tanh(td.rapidity(use, s, (tb,)))

    def dt_dtau(s: float) -> float:
        return cosh(td.rapidity(use, s, (tb,)))

    tau_from_metric, _ = quad(lambda s: sqrt(1.0 - v_of_tau(s) ** 2) * dt_dtau(s), 0.0, got["tau_trip"],
                              points=[tb] if tb < got["tau_trip"] else None, epsabs=1e-14, epsrel=1e-13)
    assert abs(tau_from_metric / got["tau_trip"] - 1.0) < 1e-10


@pytest.mark.parametrize("beta", [0.1, 0.5, 0.9, 0.999, 0.999999])
def test_rocket_equation_equals_four_momentum_route(beta: float) -> None:
    eta = np.arctanh(beta)
    alpha = 1.0
    tau_burn = eta / alpha

    def start_stop(s: float) -> float:
        return alpha if s < tau_burn else -alpha

    rocket = td.mass_ratio_reaction_drive(start_stop, 2.0 * tau_burn, 1.0, breakpoints=(tau_burn,))
    momentum = td.photon_boost_mass_ratio(beta) ** 2
    assert abs(rocket / momentum - 1.0) < 1e-10
    # slower exhaust always needs more mass
    assert td.mass_ratio_reaction_drive(start_stop, 2.0 * tau_burn, 0.5, breakpoints=(tau_burn,)) > rocket


def test_resources_buy_ageing_not_record_delay() -> None:
    d = 1000.0
    previous = None
    for tau in [1000.0, 100.0, 10.0, 1.0, 0.1, 0.01]:
        c = td.cruise_for_proper_time(d, tau)
        # direct check of D2 through the boost: tau = gamma (t - beta x) at the arrival event;
        # t - beta x cancels ~log10(gamma^2) digits, so the tolerance follows float cancellation
        boost = c["gamma"] * (c["t_trip"] - c["beta"] * d)
        assert abs(boost / tau - 1.0) < 1e-13 * c["gamma"] ** 2 + 1e-12
        assert c["record_age_at_arrival"] > 2.0 * d
        if previous is not None:
            assert c["mass_ratio_photon"] > previous["mass_ratio_photon"]
            assert c["record_age_at_arrival"] < previous["record_age_at_arrival"]
        previous = c
    # tau -> 0 needs unbounded mass, while the record age only approaches 2 d (excess ~ tau^2 / 2d)
    excess = previous["record_age_at_arrival"] - 2.0 * d
    assert excess < 1e-6 and excess > 0.0
    assert abs(excess / (0.01 ** 2 / (2.0 * d)) - 1.0) < 1e-3
