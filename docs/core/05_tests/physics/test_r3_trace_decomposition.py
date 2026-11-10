"""R3: the trace left by energy use = readable record + potential difference (exact, closed system).

(a) Identity Sigma = I(S:R) + D(R||eq) and conservation of total entropy, for a hot and a
    cold system, at several times (Esposito, Lindenberg & Van den Broeck 2010).
(b) Positivity: I >= 0, D >= 0, Sigma >= 0. For a cold system the heat into the environment
    is negative while I > 0, so the naive bound "bits <= Q/(T ln 2)" fails; Sigma is the
    correct bound on the readable record.
(c) Known limit: the long-time Sigma converges, at first order in gamma*omega_max (the energy
    of switching the coupling on), to the weak-coupling value x - 1 - ln x, x = T_sys/T.
(d) At long times the trace is dominated by the potential difference D, not by the record I.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest

pytestmark = pytest.mark.physics

r3 = importlib.import_module("docs.core.03_lanes.open_system.uet_r3_trace_decomposition")
TIMES = np.array([1.0, 3.0, 8.0, 20.0])


@pytest.mark.parametrize("t_sys", [3.0, 0.3])
def test_entropy_production_is_record_plus_potential_exactly(t_sys: float) -> None:
    bath = r3.OhmicBath(n_modes=200, gamma=0.1, omega_max=8.0)
    for b in r3.trace_budget(1.0, bath, t_sys, 1.0, TIMES):
        assert abs(b.total_entropy_drift) < 1e-8
        assert abs(b.sigma - b.record - b.potential) < 1e-8
        assert b.record > 0.0 and b.potential > 0.0 and b.sigma > 0.0


def test_cold_system_breaks_the_naive_heat_bound_but_not_sigma() -> None:
    bath = r3.OhmicBath(n_modes=200, gamma=0.1, omega_max=8.0)
    b = r3.trace_budget(1.0, bath, 0.3, 1.0, np.array([20.0]))[0]
    assert b.heat_to_environment < 0.0 < b.record  # heat flows in, yet the environment holds a record
    assert b.record <= b.sigma


def test_long_time_sigma_converges_to_weak_coupling_limit() -> None:
    target = r3.relaxation_entropy_production(3.0, 1.0)
    excess = []
    for gamma in (0.1, 0.05, 0.025):
        bath = r3.OhmicBath(n_modes=400, gamma=gamma, omega_max=4.0)
        t = 6.0 / gamma
        assert t < 0.5 * bath.recurrence_time
        excess.append(r3.trace_budget(1.0, bath, 3.0, 1.0, np.array([t]))[0].sigma - target)
    orders = [math.log2(excess[i] / excess[i + 1]) for i in range(2)]
    assert all(0.9 < o < 1.1 for o in orders), (excess, orders)
    assert excess[-1] < 0.15


def test_trace_ends_up_mostly_as_potential_difference() -> None:
    bath = r3.OhmicBath(n_modes=400, gamma=0.025, omega_max=4.0)
    b = r3.trace_budget(1.0, bath, 3.0, 1.0, np.array([6.0 / 0.025]))[0]
    assert b.potential / b.sigma > 0.9
