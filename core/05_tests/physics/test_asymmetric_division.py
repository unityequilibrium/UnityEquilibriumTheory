"""Layer 3 for unequal division (module uet_asymmetric_division.py).

1. Known limit: equal cycles (P = D) give T = P and the equal-division budded fraction.
2. Independent dynamics: an agent model of budding cells reaches the predicted doubling time,
   fraction of unbudded cells that are daughters, and budded fraction.
3. Reproduction of the published calculation: Hartwell and Unger (1977) report T_calc = 165 min
   for P = 132 min, D = 203 min, and u_d = 82 percent with the budded period from their regression.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "persistence" / "uet_asymmetric_division.py"
_SPEC = importlib.util.spec_from_file_location("uet_asymmetric_division", _PATH)
ad = sys.modules.setdefault("uet_asymmetric_division", importlib.util.module_from_spec(_SPEC))
_SPEC.loader.exec_module(ad)


def test_equal_division_limit():
    assert ad.doubling_time(100.0, 100.0) == pytest.approx(100.0, rel=1e-12)
    assert ad.doubling_time(100.0, 100.0 + 1e-6) == pytest.approx(100.0, rel=1e-7)
    assert ad.budded_fraction(30.0, 100.0) == pytest.approx(2.0 ** 0.3 - 1.0, rel=1e-14)


def test_agent_model_matches_formulas():
    p, d, b = 1.0, 1.6, 0.8
    sim = ad.simulate(p, d, b, 0.1, 40000, 25.0, 0.01, np.random.default_rng(1977))
    t = ad.doubling_time(p, d)
    assert sim["doubling"] == pytest.approx(t, rel=0.01)
    assert sim["unbudded_daughter_fraction"] == pytest.approx(ad.unbudded_daughter_fraction(p, d, b, t), abs=0.015)
    assert sim["budded_fraction"] == pytest.approx(ad.budded_fraction(b, t), abs=0.01)


def test_reproduces_published_calculation():
    t = ad.doubling_time(132.0, 203.0)
    assert t == pytest.approx(165.0, abs=1.0)
    b = 0.17 * t + 87.4  # the authors' regression for the budded interval
    assert ad.unbudded_daughter_fraction(132.0, 203.0, b, t) == pytest.approx(0.82, abs=0.005)
