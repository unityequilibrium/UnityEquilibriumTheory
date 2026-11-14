"""Wave A3: layer-2 open-system laws emerge from a closed Hamiltonian (author points 1, 2, 4, 8).

The total system (mode + environment) is closed and conserves energy exactly. Viewed
alone, the mode must show (checked here, not assumed):
(a) friction: x(t) converges to the damped-oscillator law as the bath becomes dense;
(b) burn power: the energy the mode loses equals the integral of P = gamma x'^2;
(c) noise + KMS: from rest, the mode heats up to equipartition <x'^2> = T, <x^2> = T/w0^2;
(d) second law: mean heat flows from the hotter to the colder side;
(e) depletion law: free energy decays as exp(-gamma t), so P is proportional to F.
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest

pytestmark = pytest.mark.physics

l2 = importlib.import_module("docs.core.03_lanes.open_system.uet_layer2_dissipation")

W0 = 1.0


def _single_run(gamma: float, omega_max: float, n_modes: int, t_max: float, dt: float = 0.05):
    bath = l2.OhmicBath(n_modes=n_modes, gamma=gamma, omega_max=omega_max)
    assert t_max < 0.5 * bath.recurrence_time
    n = n_modes + 1
    z0 = np.zeros(2 * n)
    z0[0] = 1.0  # displaced mode, bath at rest at its displaced equilibrium
    z0[1:n] = bath.couplings / bath.omegas**2
    steps = int(round(t_max / dt))
    z = l2.evolve(W0, bath, z0, dt, steps)
    t = np.arange(steps + 1) * dt
    return bath, t, z


def test_friction_emerges_from_closed_dynamics_and_converges() -> None:
    gamma, t_max = 0.2, 15.0
    errors = []
    for omega_max, n_modes in ((5.0, 150), (10.0, 300), (20.0, 600)):
        _, t, z = _single_run(gamma, omega_max, n_modes, t_max)
        errors.append(float(np.max(np.abs(z[:, 0] - l2.damped_oscillator(W0, gamma, 1.0, 0.0, t)))))
    assert errors[0] > errors[1] > errors[2], errors
    assert errors[-1] < 0.02, errors


def test_total_energy_conserved_while_mode_loses_energy() -> None:
    gamma = 0.2
    bath, t, z = _single_run(gamma, 20.0, 600, 15.0)
    total = l2.total_energy(W0, bath, z)
    assert np.max(np.abs(total - total[0])) < 1e-9 * abs(total[0])
    e_sys = l2.system_energy(W0, z)
    assert e_sys[-1] < 0.1 * e_sys[0]  # the open mode alone is not conserved


def test_lost_energy_equals_integrated_burn_power() -> None:
    gamma = 0.2
    bath, t, z = _single_run(gamma, 20.0, 600, 15.0, dt=0.01)
    n = bath.n_modes + 1
    e_sys = l2.system_energy(W0, z)
    p = l2.burn_power(gamma, z[:, n])
    burned = float(np.sum(0.5 * (p[1:] + p[:-1])) * (t[1] - t[0]))
    lost = float(e_sys[0] - e_sys[-1])
    assert abs(burned / lost - 1.0) < 0.02, (burned, lost)


def _thermal_ensemble(gamma: float, t_sys: float | None, t_bath: float, samples: int = 400, seed: int = 7):
    bath = l2.OhmicBath(n_modes=300, gamma=gamma, omega_max=10.0)
    rng = np.random.default_rng(seed)
    z0 = l2.thermal_bath_ensemble(bath, t_bath, samples, rng)
    n = bath.n_modes + 1
    if t_sys is not None:
        x0 = rng.normal(size=samples) * math.sqrt(t_sys) / W0
        v0 = rng.normal(size=samples) * math.sqrt(t_sys)
        z0[0, :], z0[n, :] = x0, v0
        z0[1:n, :] += (bath.couplings / bath.omegas**2)[:, None] * x0[None, :]
    dt, steps = 0.1, 120
    z = l2.evolve(W0, bath, z0, dt, steps)  # shape (steps+1, 2n, M)
    return bath, z


def test_noise_and_kms_emerge_equipartition_from_rest() -> None:
    temperature, gamma = 1.0, 0.5
    bath, z = _thermal_ensemble(gamma, None, temperature)
    n = bath.n_modes + 1
    assert abs(float(np.mean(z[0, n, :] ** 2))) < 1e-12  # starts at rest: no noise put in by hand
    late = slice(80, 121)  # t in [8, 12] = 4-6 relaxation times
    v2 = float(np.mean(z[late, n, :] ** 2))
    x2 = float(np.mean(z[late, 0, :] ** 2))
    assert abs(v2 / temperature - 1.0) < 0.15, v2
    assert abs(x2 * W0**2 / temperature - 1.0) < 0.15, x2


@pytest.mark.parametrize("t_sys,sign", [(3.0, 1.0), (0.2, -1.0)])
def test_second_law_heat_flows_from_hot_to_cold(t_sys: float, sign: float) -> None:
    t_bath, gamma = 1.0, 0.5
    bath, z = _thermal_ensemble(gamma, t_sys, t_bath, seed=11)
    e_sys = l2.system_energy(W0, np.moveaxis(z, 1, -1))  # (steps+1, M)
    heat_to_env = float(np.mean(e_sys[0] - e_sys[-1]))
    assert sign * heat_to_env > 0.0
    assert abs(heat_to_env / (t_sys - t_bath) - 1.0) < 0.25  # relaxes to <E_sys> = T_bath


def test_free_energy_decays_exponentially_so_power_tracks_free_energy() -> None:
    """Depletion law of linear friction: F(t) ~ F0 exp(-gamma t), P ~ gamma F (not constant P)."""
    gamma = 0.2
    _, t, z = _single_run(gamma, 20.0, 600, 20.0)  # three full periods (18.85) inside the run
    e = l2.system_energy(W0, z)
    # cycle-averaged log-slope over the run
    period = 2.0 * math.pi / W0
    idx = [int(round(k * period / (t[1] - t[0]))) for k in range(0, 3)]
    means = [float(np.mean(e[i:i + idx[1]])) for i in idx]
    rates = [math.log(means[k] / means[k + 1]) / period for k in range(2)]
    assert all(abs(r / gamma - 1.0) < 0.05 for r in rates), rates
    # consequence for layer 3: lifetime to a threshold F_min is ln(F0/F_min)/gamma, not F0/P0 = 1/gamma
    assert abs(l2.exhaustion_time_linear_friction(gamma, 1.0, math.exp(-3.0)) * gamma - 3.0) < 1e-12


def test_bits_rate_is_entropy_production_in_bits() -> None:
    v, gamma, temperature = np.array([0.3, -1.2, 2.0]), 0.4, 1.7
    sigma = l2.entropy_production_rate(gamma, v, temperature)
    assert np.all(sigma >= 0.0)
    assert np.allclose(l2.bits_write_rate(gamma, v, temperature) * math.log(2.0), sigma)
