"""Layer 2 of the author proposition: open-system thermodynamics from a closed system (wave A3).

Author logic (AUTHOR_PROPOSITION.md points 1, 2, 4, 8): counted together, matter and
the structure it interacts with form a closed system; matter alone is open, burns
free energy, and writes entropy (bits) into its environment.

Model (standard, Caldeira-Leggett 1983): one mode x of the matter/response sector with
frequency w0, coupled to N environment oscillators q_k. The total Hamiltonian is closed:

    H = p^2/2 + w0^2 x^2/2 + sum_k [ p_k^2/2 + w_k^2/2 (q_k - c_k x / w_k^2)^2 ]

With an ohmic spectral density J(w) = gamma w up to w_max (w_k = (k - 1/2) dw,
c_k^2 = (2/pi) gamma w_k^2 dw), the reduced dynamics of x tends to the open-system law

    x'' + gamma x' + w0^2 x = xi(t),   <xi(t) xi(t')> = 2 gamma T delta(t - t')

Nothing in the open law is assumed here: friction, noise and the KMS/fluctuation-
dissipation relation must emerge from the closed evolution (checked in
05_tests/physics/test_layer2_dissipation.py).

Layer-2 quantities for the mode:
    P(t)      = gamma x'(t)^2          power burned into the environment
    sigma(t)  = P / T                  entropy production rate (k_B = 1)
    bits(t)   = P / (T ln 2)           reversed-Landauer write rate (entropy in bits)

Units: dimensionless (w0 = 1 sets the scale), k_B = 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log, pi

import numpy as np
from scipy.linalg import expm


@dataclass(frozen=True)
class OhmicBath:
    n_modes: int
    gamma: float
    omega_max: float

    def __post_init__(self) -> None:
        if self.n_modes < 1 or self.gamma < 0.0 or self.omega_max <= 0.0:
            raise ValueError("need n_modes >= 1, gamma >= 0, omega_max > 0")

    @property
    def d_omega(self) -> float:
        return self.omega_max / self.n_modes

    @property
    def omegas(self) -> np.ndarray:
        return (np.arange(1, self.n_modes + 1) - 0.5) * self.d_omega

    @property
    def couplings(self) -> np.ndarray:
        w = self.omegas
        return np.sqrt(2.0 / pi * self.gamma * w**2 * self.d_omega)

    @property
    def recurrence_time(self) -> float:
        return 2.0 * pi / self.d_omega


def generator(w0: float, bath: OhmicBath) -> np.ndarray:
    """Linear generator A of z' = A z with z = (x, q_1..q_N, p, p_1..p_N)."""

    n = bath.n_modes + 1
    w, c = bath.omegas, bath.couplings
    k = np.zeros((n, n))  # potential Hessian: H = p.p/2 + z.K.z/2
    k[0, 0] = w0**2 + float(np.sum(c**2 / w**2))  # counterterm keeps w0 the physical frequency
    k[0, 1:] = k[1:, 0] = -c
    k[1:, 1:] = np.diag(w**2)
    a = np.zeros((2 * n, 2 * n))
    a[:n, n:] = np.eye(n)
    a[n:, :n] = -k
    return a, k


def evolve(w0: float, bath: OhmicBath, z0: np.ndarray, dt: float, steps: int) -> np.ndarray:
    """Exact closed evolution (matrix exponential), returns z at t = 0, dt, ..., steps*dt.

    ``z0`` may be one state (2n,) or an ensemble (2n, M).
    """

    a, _ = generator(w0, bath)
    step = expm(a * dt)
    z = np.array(z0, dtype=float)
    out = [z.copy()]
    for _ in range(steps):
        z = step @ z
        out.append(z.copy())
    return np.stack(out)


def total_energy(w0: float, bath: OhmicBath, z: np.ndarray) -> np.ndarray:
    _, k = generator(w0, bath)
    n = bath.n_modes + 1
    q, p = z[..., :n], z[..., n:]
    return 0.5 * np.einsum("...i,...i->...", p, p) + 0.5 * np.einsum("...i,ij,...j->...", q, k, q)


def system_energy(w0: float, z: np.ndarray) -> np.ndarray:
    n = (z.shape[-1]) // 2
    return 0.5 * z[..., n] ** 2 + 0.5 * w0**2 * z[..., 0] ** 2


def damped_oscillator(w0: float, gamma: float, x0: float, v0: float, t: np.ndarray) -> np.ndarray:
    """Open-system (Markov) prediction for x(t) with no noise, underdamped gamma < 2 w0."""

    wd = np.sqrt(w0**2 - gamma**2 / 4.0)
    b = (v0 + 0.5 * gamma * x0) / wd
    return np.exp(-0.5 * gamma * t) * (x0 * np.cos(wd * t) + b * np.sin(wd * t))


def thermal_bath_ensemble(bath: OhmicBath, temperature: float, samples: int, rng: np.random.Generator,
                          x0: float = 0.0, v0: float = 0.0) -> np.ndarray:
    """Classical Boltzmann bath around the displaced equilibrium q_k = c_k x0 / w_k^2."""

    n = bath.n_modes + 1
    w, c = bath.omegas, bath.couplings
    z = np.zeros((2 * n, samples))
    z[0, :], z[n, :] = x0, v0
    z[1:n, :] = (c * x0 / w**2)[:, None] + rng.normal(size=(bath.n_modes, samples)) * (np.sqrt(temperature) / w)[:, None]
    z[n + 1:, :] = rng.normal(size=(bath.n_modes, samples)) * np.sqrt(temperature)
    return z


def burn_power(gamma: float, velocity) -> np.ndarray:
    return gamma * np.asarray(velocity, dtype=float) ** 2


def entropy_production_rate(gamma: float, velocity, temperature: float) -> np.ndarray:
    return burn_power(gamma, velocity) / temperature


def bits_write_rate(gamma: float, velocity, temperature: float) -> np.ndarray:
    return burn_power(gamma, velocity) / (temperature * log(2.0))


def exhaustion_time_linear_friction(gamma: float, f0: float, f_min: float) -> float:
    """Time for free energy to fall from f0 to f_min when P = gamma <x'^2> = gamma F (F decays as exp(-gamma t))."""

    if not (f0 > f_min > 0.0):
        raise ValueError("need f0 > f_min > 0")
    return log(f0 / f_min) / gamma
