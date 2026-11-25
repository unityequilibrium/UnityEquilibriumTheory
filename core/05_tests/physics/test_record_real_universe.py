"""Wave D10: the record of a vanished mass in the real universe.

(a) Derivation check: the memory coefficient from the memory integral with the quadrupole
    distribution of a circular binary equals sin^2 i (17 + cos^2 i)/96 at 20 random inclinations,
    rel < 1e-9; face-on it vanishes.
(b) Known limit with convergence: at early times (Lambda negligible) the optical depth of a segment
    [a, 2a] tends to the matter-era closed form with error of order a^3 (three grids).
(c) Identity: the optical depth is additive along the path, tau(a1, a3) = tau(a1, a2) + tau(a2, a3),
    and the future integral equals the past-style integral split at a = 1 in the u = 1/a form.
(d) Numbers: today's future optical depth is below 1e-3, so at least 99.9 % of the record escapes.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_record_real_universe")


@pytest.mark.parametrize("seed", range(20))
def test_memory_coefficient_matches_closed_form(seed: int) -> None:
    i = np.random.default_rng(21100 + seed).uniform(0.02, np.pi - 0.02)
    a = m.memory_coefficient_numeric(i)
    b = m.memory_coefficient_closed_form(i)
    assert abs(a / b - 1.0) < 1e-9


def test_face_on_memory_vanishes() -> None:
    assert abs(m.memory_coefficient_numeric(0.0)) < 1e-12


def test_early_time_segment_tends_to_matter_era_at_third_order() -> None:
    aa = [0.04, 0.02, 0.01]
    errs = [abs(m.optical_depth(a, 2 * a) / m.optical_depth_matter_era(a, 2 * a) - 1.0) for a in aa]
    orders = [log(errs[i] / errs[i + 1]) / log(aa[i] / aa[i + 1]) for i in range(2)]
    for p in orders:
        assert abs(p - 3.0) < 0.05


@pytest.mark.parametrize("seed", range(6))
def test_optical_depth_is_additive(seed: int) -> None:
    a1, a2, a3 = np.sort(10 ** np.random.default_rng(21000 + seed).uniform(-2.5, 0.8, size=3))
    whole = m.optical_depth(a1, a3)
    parts = m.optical_depth(a1, a2) + m.optical_depth(a2, a3)
    assert abs(whole / parts - 1.0) < 1e-10


def test_future_optical_depth_two_forms_and_bound() -> None:
    fut = m.optical_depth(1.0, np.inf)
    split = m.optical_depth(1.0, 3.0) + m.optical_depth(3.0, np.inf)
    assert abs(fut / split - 1.0) < 1e-10
    assert fut < 1e-3
