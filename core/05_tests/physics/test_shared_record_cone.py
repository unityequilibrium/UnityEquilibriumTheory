"""Wave O2: a shared record exists only after causal contact (thought experiment v3, P4).

(a) Derivation: the group velocity of the chain never exceeds c = sqrt(kappa) (numerical sup over q).
(b) Product initial state: I(A:B) = 0 exactly at t = 0.
(c) Before contact (t = 0.6 t_contact, t_contact = d / 2c) the shared record is below 1e-6 and shrinks
    by orders of magnitude as the distance grows; after contact (t = 1.2 t_contact) it exceeds 1e-4.
(d) Contact is by overlapping past cones (a common source), at d/2c, not only direct contact at d/c:
    at t = 0.75 d/c, before any direct signal can arrive, the record is already positive.
(e) Negative control: if the signal speed were assumed smaller than the true one (c/2), the 'before contact'
    prediction fails, so the claim is not vacuous.
"""

from __future__ import annotations

import importlib
import math

import pytest

pytestmark = pytest.mark.physics

sr = importlib.import_module("docs.core.03_lanes.observation.uet_shared_record")
N, KAPPA, W0, TEMP = 121, 1.0, 0.5, 1.0
CENTRE = N // 2
C = sr.signal_speed_bound(KAPPA)
A = sr.chain_generator(N, KAPPA, W0)
C0 = sr.product_thermal_covariance(N, W0, TEMP)
# a hotter source site in the middle gives the state some structure; still a product state
C0[CENTRE, CENTRE] *= 4.0
C0[N + CENTRE, N + CENTRE] *= 4.0


def info(distance: int, time: float) -> float:
    cov = sr.evolve_covariance(A, C0, time)
    return sr.mutual_information(cov, CENTRE, CENTRE + distance, N)


def test_group_velocity_never_exceeds_c() -> None:
    for w0 in (0.0, 0.2, 0.5, 2.0):
        assert sr.max_group_velocity(KAPPA, w0) <= C + 1e-12
    assert sr.max_group_velocity(KAPPA, 0.0) > 0.99 * C  # sharp: the bound is nearly attained


def test_product_state_shares_no_record_at_t0() -> None:
    assert abs(sr.mutual_information(C0, CENTRE, CENTRE + 10, N)) < 1e-12


def test_no_record_before_contact_and_a_record_after_it() -> None:
    before, after = [], []
    for d in (10, 20, 30):
        tc = sr.contact_time(d, C)
        before.append(info(d, 0.6 * tc))
        after.append(info(d, 1.2 * tc))
    assert all(abs(b) < 1e-6 for b in before), before
    assert all(a > 1e-4 for a in after), after
    assert abs(before[1]) < 1e-3 * abs(before[0]) and abs(before[2]) < 1e-9  # super-exponential suppression in d


def test_contact_is_by_common_past_not_only_direct_signal() -> None:
    d = 20
    t = 0.75 * d / C  # a direct signal needs d/C: it cannot have arrived yet
    assert t < d / C
    assert info(d, t) > 1e-4


def test_negative_control_wrong_signal_speed_breaks_the_prediction() -> None:
    d = 20
    t_wrong = 0.6 * sr.contact_time(d, C / 2.0)  # "before contact" if signals were half as fast
    assert info(d, t_wrong) > 1e-3
