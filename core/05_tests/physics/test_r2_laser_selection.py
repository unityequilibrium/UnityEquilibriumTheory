"""R2: a physical (non-biological) autocatalytic system that obeys layer 3 exactly — laser modes.

Multimode laser rate equations (Statz-deMars form, spontaneous emission into the modes
neglected), photon number q_i of mode i, inversion N shared by all modes:

    dq_i/dt = q_i (B_i N - 1/tau_i)              stimulated emission is autocatalytic
    dN/dt   = W - N/tau_sp - N sum_i B_i q_i      pump W, spontaneous decay, one inversion per photon

This is layer 3 (uet_persistence_selection.competition_rhs) term for term with
a_i = B_i, tau_i = cavity photon lifetime (stored energy / loss power), F_i = 1,
S = W, delta = 1/tau_sp. Consequences checked here:
(a) symbolic identity of the two models;
(b) the layer-3 R* = 1/(a tau) is the laser threshold inversion N_th = 1/(B tau);
(c) with one shared inversion only the lowest-threshold mode survives (single-mode
    lasing of a homogeneously broadened laser), and the inversion clamps at N_th;
(d) with two inversion pools (spatial hole burning) two modes coexist, as in A4.
"""

from __future__ import annotations

import importlib

import numpy as np
import pytest
import sympy as sp

pytestmark = pytest.mark.physics

l3 = importlib.import_module("docs.core.03_lanes.persistence.uet_persistence_selection")
l23 = importlib.import_module("docs.core.03_lanes.persistence.uet_layer2_to_3")


def test_laser_rate_equations_are_layer3_term_for_term() -> None:
    B1, B2, t1, t2, W, tsp, q1, q2, N = sp.symbols("B1 B2 tau1 tau2 W tau_sp q1 q2 N", positive=True)

    class Mode:  # attributes read by competition_rhs
        def __init__(self, b, tau):
            self.capture, self.tau, self.free_energy_store = b, tau, 1

    dq, dN = l3.competition_rhs([q1, q2], N, [Mode(B1, t1), Mode(B2, t2)], W, 1 / tsp)
    laser_dq = [q1 * (B1 * N - 1 / t1), q2 * (B2 * N - 1 / t2)]
    laser_dN = W - N / tsp - N * (B1 * q1 + B2 * q2)
    assert all(sp.simplify(a - b) == 0 for a, b in zip(dq, laser_dq))
    assert sp.simplify(dN - laser_dN) == 0
    # steady state of dq_1/dt = 0 with q_1 > 0 gives the textbook threshold inversion, i.e. layer-3 R*
    assert sp.solve(sp.Eq(dq[0] / q1, 0), N) == [1 / (B1 * t1)]


def _laser_rk4(gain, tau, pump, decay, q0, horizon, dt):
    """Photons leak exponentially (rate 1/tau), as in a real cavity. gain[i][j] couples mode i to pool j."""
    g = np.asarray(gain, dtype=float)
    tau, pump, decay = (np.asarray(x, dtype=float) for x in (tau, pump, decay))
    q, n = np.array(q0, dtype=float), np.zeros(g.shape[1])

    def rhs(q, n):
        return q * (g @ n - 1.0 / tau), pump - decay * n - n * (g * q[:, None]).sum(axis=0)

    for _ in range(int(round(horizon / dt))):
        k1 = rhs(q, n)
        k2 = rhs(q + 0.5 * dt * k1[0], n + 0.5 * dt * k1[1])
        k3 = rhs(q + 0.5 * dt * k2[0], n + 0.5 * dt * k2[1])
        k4 = rhs(q + dt * k3[0], n + dt * k3[1])
        q = q + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        n = n + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    return q, n


def test_single_inversion_pool_lases_in_the_lowest_threshold_mode_only() -> None:
    gains, lifetimes = [1.0, 1.1, 0.9], [2.0, 1.7, 2.4]
    n_th = [1.0 / (b * t) for b, t in zip(gains, lifetimes)]
    winner = int(np.argmin(n_th))
    q, n = _laser_rk4([[b] for b in gains], lifetimes, [2.0], [0.2], [1e-3] * 3, 600.0, 0.02)
    assert all(q[i] < 1e-6 for i in range(3) if i != winner)
    assert q[winner] > 1.0
    assert abs(n[0] / n_th[winner] - 1.0) < 1e-6  # gain clamping at threshold


def test_spatial_hole_burning_two_pools_allows_two_mode_lasing() -> None:
    capture = [[1.0, 0.3], [0.3, 1.0]]  # each mode overlaps mainly one inversion region
    taus = [2.0, 2.2]
    n_pred = l23.coexistence_resources(capture, taus)
    q, n = _laser_rk4(capture, taus, [1.5, 1.5], [0.2, 0.2], [1e-3, 1e-3], 600.0, 0.02)
    assert np.all(q > 0.5)
    assert np.max(np.abs(n / n_pred - 1.0)) < 1e-6
