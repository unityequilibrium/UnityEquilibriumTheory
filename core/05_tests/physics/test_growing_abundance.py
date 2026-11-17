"""Layer 3 with a growing formation rate (module uet_growing_abundance.py).

1. Known limit: growth rate -> 0 recovers the steady abundance law N = b tau.
2. Identity: the phase fractions of one full cycle sum to 1.
3. Independent dynamics: an agent model of dividing cells reaches the analytic phase fractions
   (asynchronous exponential growth), and differs clearly from the steady Little's-law value.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "persistence" / "uet_growing_abundance.py"
_SPEC = importlib.util.spec_from_file_location("uet_growing_abundance", _PATH)
ga = sys.modules.setdefault("uet_growing_abundance", importlib.util.module_from_spec(_SPEC))
_SPEC.loader.exec_module(ga)


def test_zero_growth_limit():
    for lam in (1e-3, 1e-5, 1e-7):
        assert ga.abundance_growing(2.0, lam, 0.3, 1.5) == pytest.approx(3.0, rel=2 * lam)
    assert ga.abundance_growing(2.0, 0.0, 0.3, 1.5) == 3.0


def test_full_cycle_fractions_sum_to_one():
    edges = [0.0, 0.4, 0.75, 0.95, 1.0]
    total = sum(ga.phase_fraction_dividing(a, b, 1.0) for a, b in zip(edges[:-1], edges[1:]))
    assert total == pytest.approx(1.0, abs=1e-14)


@pytest.mark.parametrize("a1,a2", [(0.0, 0.3), (0.5, 0.8), (0.95, 1.0)])
def test_agent_model_matches_age_distribution(a1, a2):
    # 10 percent cycle-time spread lets the population mix (a fixed cycle never relaxes); the
    # fixed-cycle formula then holds to O(cv^2), about 0.005 here.
    rng = np.random.default_rng(22022)
    sim = ga.simulate_dividing_population(1.0, a1, a2, 40000, 25.0, 0.01, rng, cv=0.1)
    exact = ga.phase_fraction_dividing(a1, a2, 1.0)
    steady = a2 - a1
    assert sim == pytest.approx(exact, abs=0.008)
    assert abs(sim - steady) > 2.0 * abs(sim - exact)  # the simulation resolves the growth correction
