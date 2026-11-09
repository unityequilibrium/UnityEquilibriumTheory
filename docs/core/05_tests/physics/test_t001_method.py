"""Known-solution check for the T001 orbital-separation method (Kepler's third law).

Earth around the Sun: one sidereal year with M = 1 Msun (Earth mass ~3e-6 Msun
neglected) must give 1 au = 1.495978707e11 m to within 2e-5 relative.
The test does not run the T001 comparison itself.
"""

from __future__ import annotations

import importlib

import pytest

method = importlib.import_module("docs.core.03_lanes.scalar_tensor.t001_binary_pulsar_constraint")

pytestmark = pytest.mark.physics

AU_M = 1.495978707e11
SIDEREAL_YEAR_DAYS = 365.256363004


def test_kepler_separation_recovers_one_au() -> None:
    a = method.orbital_separation_m(SIDEREAL_YEAR_DAYS, 1.0)
    assert abs(a - AU_M) / AU_M < 2e-5


def test_light_domain_bound_scales_inversely_with_separation() -> None:
    a1 = method.orbital_separation_m(1.0, 2.0)
    a8 = method.orbital_separation_m(8.0, 2.0)  # P x8 -> a x4
    assert abs(a8 / a1 - 4.0) < 1e-12
