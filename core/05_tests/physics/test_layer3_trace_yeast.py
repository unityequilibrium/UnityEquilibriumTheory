"""Trace feedback in yeast on sucrose: shared glucose at the cooperative-growth switch.

1. Closed form G = (1 - eps) h (N - N0)/gamma against direct integration of dN/dt = gamma N,
   dG/dt = (1 - eps) h N at 20 random sets (rel < 1e-8), through the general integrator with uptake = 0.
2. Known limits of the writing rate: h -> Vmax for S >> Km, h -> Vmax S/Km for S << Km (rel < 1e-3).
3. With uptake switched on, free glucose stays below the closed form (it is an upper estimate).
4. Unit chain: 2 percent w/v sucrose is 58.4 mM; the switch level from the registered values lies between
   0.1 and 10 mM (reported, not a comparison with data).
"""

from __future__ import annotations

import importlib
import random

import pytest

pytestmark = pytest.mark.physics

ty = importlib.import_module("core.03_lanes.persistence.uet_layer3_trace_yeast")


def test_closed_form_matches_integration():
    rng = random.Random(1)
    for _ in range(20):
        n0 = rng.uniform(1.0, 50.0)
        h = rng.uniform(1e7, 5e8)
        g = rng.uniform(0.1, 0.6) / 3600.0
        t = rng.uniform(2.0, 12.0) * 3600.0
        n, G = ty.simulate(n0, h, g, t)
        closed = ty.trace_at_density(n, n0, h, g)
        assert abs(G - closed) / closed < 1e-8


def test_writing_rate_limits():
    vmax, km = 3.6e8, 11.0
    assert abs(ty.hydrolysis_rate(vmax, km, 1e4 * km) / vmax - 1.0) < 1e-3
    s = 1e-3 * km
    assert abs(ty.hydrolysis_rate(vmax, km, s) / (vmax * s / km) - 1.0) < 1e-3


def test_uptake_lowers_free_glucose():
    rng = random.Random(2)
    for _ in range(20):
        n0, h, g, t = rng.uniform(1.0, 50.0), rng.uniform(1e7, 5e8), rng.uniform(0.1, 0.6) / 3600.0, 8 * 3600.0
        n, G0 = ty.simulate(n0, h, g, t)
        _, G1 = ty.simulate(n0, h, g, t, uptake=1e-12)
        assert G1 < G0


def test_unit_chain_and_registered_switch_level():
    assert abs(ty.sucrose_mM(2.0) - 58.43) < 0.01
    out = ty.switch_glucose()
    assert 0.1 < out["G_star_mM"] < 10.0
