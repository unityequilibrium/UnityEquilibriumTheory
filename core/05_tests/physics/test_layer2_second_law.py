"""Layer 2 second law and burn chain from the parent action (stage 3, wave L2-2).

1. Positivity: the action-derived spectral function rho(w, q) >= 0 for w > 0 (random decay and scattering points).
2. Heat flows from hot to cold: J has the sign of T_phi - T.
3. Second law: entropy production J (1/T - 1/T_phi) >= 0, zero only at T_phi = T.
4. Burn chain: a coherent phi mode with the action-derived damping rate, coupled to a closed Caldeira-Leggett bath
   (uet_layer2_dissipation), loses energy at P = Gamma E; bits written = P/(T ln 2).
"""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest

pytestmark = pytest.mark.physics

l2 = importlib.import_module("core.03_lanes.open_system.uet_layer2_from_action")
sl = importlib.import_module("core.03_lanes.open_system.uet_layer2_second_law")
cl = importlib.import_module("core.03_lanes.open_system.uet_layer2_dissipation")


def _point(rng: random.Random, M: float) -> tuple[float, float]:
    while True:
        w, q = rng.uniform(0.01, 4.0), rng.uniform(0.05, 3.0)
        s = w * w - q * q
        if s > 4 * M * M * 1.02 or s < -0.01:
            return w, q


@pytest.mark.parametrize("seed", range(12))
def test_spectral_function_is_positive(seed: int) -> None:
    rng = random.Random(400 + seed)
    M, sigma, T = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.1, 2.0)
    w, q = _point(rng, M)
    assert l2.spectral(w, q, T, M, sigma) > 0.0


@pytest.mark.parametrize("seed", range(8))
def test_heat_flows_from_hot_to_cold_and_entropy_production_is_nonnegative(seed: int) -> None:
    rng = random.Random(500 + seed)
    M, sigma, T = rng.uniform(0.2, 1.0), rng.uniform(0.1, 1.0), rng.uniform(0.2, 2.0)
    w, q = _point(rng, M)
    for T_phi in (0.5 * T, 0.9 * T, 1.1 * T, 3.0 * T):
        J = sl.heat_current(w, q, T_phi, T, M, sigma)
        assert math.copysign(1.0, J) == math.copysign(1.0, T_phi - T)
        assert sl.entropy_production(w, q, T_phi, T, M, sigma) > 0.0
    assert sl.heat_current(w, q, T, T, M, sigma) == pytest.approx(0.0, abs=1e-15)
    assert sl.entropy_production(w, q, T, T, M, sigma) == pytest.approx(0.0, abs=1e-15)


def test_entropy_production_is_quadratic_near_equilibrium() -> None:
    M, sigma, T, w, q = 0.5, 0.7, 0.8, 0.3, 1.0
    s1 = sl.entropy_production(w, q, T * 1.01, T, M, sigma)
    s2 = sl.entropy_production(w, q, T * 1.02, T, M, sigma)
    assert s2 / s1 == pytest.approx(4.0, rel=0.03)  # sigma ~ (dT)^2: no first-order entropy production


def test_coherent_mode_burns_at_the_action_rate_in_a_closed_bath() -> None:
    # action-derived damping of a long-wavelength mode, then a closed Caldeira-Leggett bath with that friction
    M, sigma, T, q = 0.5, 0.7, 0.8, 1.0
    w0 = 1.0
    gamma = l2.caldeira_leggett_gamma(q, T, M, sigma) * 5.0  # scale up for a short run; same law at any gamma
    bath = cl.OhmicBath(n_modes=1200, gamma=gamma, omega_max=12.0)
    z0 = np.zeros(2 + 2 * bath.n_modes)
    z0[0] = 1.0
    dt, steps = 0.05, 400
    z = cl.evolve(w0, bath, z0, dt, steps)
    E = cl.system_energy(w0, z)
    t = np.arange(steps + 1) * dt
    rate = -np.polyfit(t[40:], np.log(E[40:]), 1)[0]
    assert rate == pytest.approx(gamma, rel=0.08)
    burn = sl.coherent_burn(1.0, w0, q, T, M, sigma)
    assert burn["bits_rate"] == pytest.approx(burn["power"] / (T * math.log(2.0)), rel=1e-14)
    assert burn["entropy_rate"] == pytest.approx(burn["power"] / T, rel=1e-14)
