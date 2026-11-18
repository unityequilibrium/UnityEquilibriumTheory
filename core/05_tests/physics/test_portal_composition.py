"""Equivalence-principle signal of the portal (module uet_portal_composition.py).

1. Known limit: equal charge-per-mass bodies give eta = 0 exactly (composition-independent force).
2. Two code paths: the closed-form uniform-sphere Yukawa field equals a direct volume integral.
3. Known limits of the geometry: point source (R << lambda) and exponential screening (r - R >> lambda).
"""

from __future__ import annotations

import importlib.util
import sys
from math import exp, pi
from pathlib import Path

import pytest
from scipy.integrate import dblquad

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "scalar_tensor" / "uet_portal_composition.py"
_SPEC = importlib.util.spec_from_file_location("uet_portal_composition", _PATH)
pc = sys.modules.setdefault("uet_portal_composition", importlib.util.module_from_spec(_SPEC))
_SPEC.loader.exec_module(pc)


def test_equal_composition_gives_zero():
    assert pc.eotvos(0.7, 1.0, 1.0008, 1.0008, 2.0, 1.0, 3.0) == 0.0
    assert pc.eotvos(0.7, 1.0, 1.0010, 1.0002, 2.0, 1.0, 3.0) > 0.0


def _numeric_field(r, radius, lam):
    """Radial Yukawa acceleration of a uniform unit-mass sphere at distance r, by direct integration,
    normalised to the Newtonian 1/r^2 of the same mass."""
    rho = 3.0 / (4.0 * pi * radius**3)

    def integrand(cos_t, s):
        d2 = r * r + s * s - 2.0 * r * s * cos_t
        d = d2 ** 0.5
        radial = (r - s * cos_t) / d
        return rho * 2.0 * pi * s * s * exp(-d / lam) * (1.0 + d / lam) / d2 * radial

    val, _ = dblquad(integrand, 0.0, radius, -1.0, 1.0, epsabs=1e-12, epsrel=1e-10)
    return val * r * r


@pytest.mark.parametrize("lam", [0.3, 1.0, 5.0])
def test_sphere_closed_form_matches_volume_integral(lam):
    r, radius = 1.7, 1.0
    assert pc.yukawa_geometry(r, radius, lam) == pytest.approx(_numeric_field(r, radius, lam), rel=1e-6)


def test_geometry_limits():
    assert pc.yukawa_geometry(1e3, 1.0, 1e9) == pytest.approx(1.0, rel=1e-6)
    r, radius, lam = 2.0, 1.0, 0.01
    expected = pc.sphere_form_factor(radius, lam) * exp(-r / lam) * (1.0 + r / lam)
    assert pc.yukawa_geometry(r, radius, lam) == pytest.approx(expected, rel=1e-12)
    assert pc.yukawa_geometry(r, radius, lam) < 1e-30
