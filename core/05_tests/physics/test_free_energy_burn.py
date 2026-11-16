"""Wave B7: the layer-3 burn power from the closed system (module uet_free_energy_burn.py).

1. General code path: in the exact closed Hamiltonian evolution (A3 bath), the free energy the mode
   loses equals the time integral of the open-system formula P = T sigma, and the agreement improves
   as the bath cutoff grows (Markov limit, convergence).
2. Layer 3 from layers 1-2: the time the closed system takes to fall to F_min equals
   tau = integral dF / P with P from the formula.
3. Identities: the Gibbs state has F = 0 and P = 0; a displaced thermal state has F equal to the
   mechanical energy of the mean and P = gamma <p>^2, the A3 burn power.
4. Second law: F >= 0 and P >= 0 along the closed trajectory, so F never rises.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "open_system" / "uet_free_energy_burn.py"
_SPEC = importlib.util.spec_from_file_location("uet_free_energy_burn", _PATH)
fb = sys.modules.setdefault("uet_free_energy_burn", importlib.util.module_from_spec(_SPEC))
_SPEC.loader.exec_module(fb)

W0, GAMMA, T = 1.0, 0.2, 0.5
MU0, S0 = np.array([3.0, 0.0]), np.diag([0.05, 0.2])
DT, STEPS = 0.02, 1500


def _run(omega_max: float, n_modes: int):
    bath = fb.OhmicBath(n_modes=n_modes, gamma=GAMMA, omega_max=omega_max)
    assert bath.recurrence_time > DT * STEPS
    m, c = fb.initial_moments(bath, MU0, S0, T)
    mus, sigs = fb.propagate_moments(W0, bath, m, c, DT, STEPS)
    f = np.array([fb.relative_free_energy(a, b, W0, T) for a, b in zip(mus, sigs)])
    p = np.array([fb.burn_power(a, b, GAMMA, T) for a, b in zip(mus, sigs)])
    return f, p


@pytest.fixture(scope="module")
def runs():
    return {wmax: _run(wmax, int(40 * wmax)) for wmax in (5.0, 10.0)}


def _cumulative_error(f, p):
    burned = np.sum(0.5 * (p[1:] + p[:-1]) * DT)
    return abs((f[0] - f[-1]) - burned) / (f[0] - f[-1])


def test_closed_free_energy_loss_equals_integrated_burn(runs):
    assert _cumulative_error(*runs[10.0]) < 1e-2


def test_agreement_converges_with_bath_cutoff(runs):
    assert _cumulative_error(*runs[10.0]) < _cumulative_error(*runs[5.0])


def test_lifetime_equals_integral_of_df_over_p(runs):
    f, p = runs[10.0]
    f_min = 0.01 * f[0]
    i = int(np.argmax(f < f_min))
    t_closed = (i - 1 + (f[i - 1] - f_min) / (f[i - 1] - f[i])) * DT
    tau = fb.lifetime_from_burn(f[: i + 1], p[: i + 1], f[i]) - (f_min - f[i]) / p[i]
    assert tau == pytest.approx(t_closed, rel=2e-2)


def test_second_law_along_closed_trajectory(runs):
    f, p = runs[10.0]
    assert f.min() >= 0.0 and p.min() >= -1e-12


def test_gibbs_and_displaced_thermal_identities():
    seq = fb.equilibrium_covariance(W0, T)
    zero = np.zeros(2)
    assert fb.relative_free_energy(zero, seq, W0, T) == pytest.approx(0.0, abs=1e-14)
    assert fb.burn_power(zero, seq, GAMMA, T) == pytest.approx(0.0, abs=1e-14)
    mu = np.array([0.7, -1.3])
    assert fb.relative_free_energy(mu, seq, W0, T) == pytest.approx(0.5 * (W0**2 * mu[0] ** 2 + mu[1] ** 2))
    assert fb.burn_power(mu, seq, GAMMA, T) == pytest.approx(GAMMA * mu[1] ** 2)
