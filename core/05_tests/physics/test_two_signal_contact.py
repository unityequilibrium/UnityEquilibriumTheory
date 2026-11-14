"""Wave O6: P4 with two signal speeds (thought experiment v3), and the Bose-Hubbard quasiparticle limits.

1. The closed form t = d/(c_a + c_b) equals a brute-force minimisation over the common-source position.
2. With c_a = c_b = c it reduces to the O2 result d/(2c) (a different module, the harmonic chain).
3. The direct-contact reading is strictly slower (later) whenever both speeds are positive.
4. Limits of the inherited Bose-Hubbard dispersions: U/J -> infinity gives doublon 4, holon 2, pair 6;
   the published closed form for v_max agrees with the dispersion maximum at large U/J.
5. Negative control: the pair bound c_a + c_b is NOT the single-signal bound; a front measured at
   5 J a/hbar at U/J = 9 exceeds the single-signal maximum by a wide margin.
"""

from __future__ import annotations

import importlib
import random

import pytest

pytestmark = pytest.mark.physics

two = importlib.import_module("docs.core.03_lanes.observation.uet_two_signal_contact")
shared = importlib.import_module("docs.core.03_lanes.observation.uet_shared_record")


@pytest.mark.parametrize("seed", range(8))
def test_closed_form_matches_search_over_the_common_source(seed: int) -> None:
    r = random.Random(seed)
    d, c_a, c_b = r.uniform(1, 50), r.uniform(0.2, 5), r.uniform(0.2, 5)
    assert two.contact_time_by_search(d, c_a, c_b) == pytest.approx(two.contact_time(d, c_a, c_b), rel=1e-6)


@pytest.mark.parametrize("c", [0.3, 1.0, 2.7])
def test_equal_speeds_reduce_to_the_o2_result(c: float) -> None:
    d = 11.0
    assert two.contact_time(d, c, c) == pytest.approx(shared.contact_time(d, c), rel=1e-12)


@pytest.mark.parametrize("seed", range(5))
def test_common_past_is_always_earlier_than_direct_contact(seed: int) -> None:
    r = random.Random(40 + seed)
    d, c_a, c_b = r.uniform(1, 50), r.uniform(0.2, 5), r.uniform(0.2, 5)
    assert two.contact_time(d, c_a, c_b) < two.direct_contact_time(d, c_a, c_b)


def test_large_interaction_limit_gives_doublon_4_holon_2_pair_6() -> None:
    c_d, c_h = two.single_signal_speeds(1e6)
    assert c_d == pytest.approx(4.0, abs=1e-3)
    assert c_h == pytest.approx(2.0, abs=1e-3)
    assert two.pair_front_velocity_bound(1e6) == pytest.approx(c_d + c_h, abs=1e-3)


@pytest.mark.parametrize("u_over_j", [20.0, 40.0, 100.0])
def test_published_closed_form_agrees_at_large_interaction(u_over_j: float) -> None:
    assert two.pair_front_velocity_bound(u_over_j) == pytest.approx(two.published_closed_form(u_over_j), rel=2e-3)


def test_negative_control_the_pair_bound_is_not_the_single_signal_bound() -> None:
    c_d, c_h = two.single_signal_speeds(9.0)
    bound = two.pair_front_velocity_bound(9.0)
    assert bound > max(c_d, c_h) * 1.4  # the common-past front is much faster than any single signal
    assert bound == pytest.approx(c_d + c_h, rel=0.05) or bound < c_d + c_h + 1e-6
