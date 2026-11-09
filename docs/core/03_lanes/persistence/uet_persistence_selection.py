"""Layer 3 of the Author Proposition: persistence selection by resource exhaustion.

docs/core/AUTHOR_PROPOSITION.md, layer 3. A system that burns its free-energy
store disappears; what remains observable is what lasts. This module makes
that logic explicit without hand-set payoffs.

Definitions (SI where given; the lane itself is unit-agnostic):

- Lifetime of one system with free-energy store F burned at power P:
      tau = F / P                                          [derived, layer 2 -> 3]
  tau is computed from F and P BEFORE any survival is observed, which keeps the
  selection argument non-circular.
- Steady-state abundance of a type formed at rate b with lifetime tau:
      N* = b * tau                                         [Little's law, 1961]
- Bits written to the environment over one lifetime at temperature T:
      bits = F / (k_B T ln 2)                               [reversed Landauer]
  independent of the burn rate P.
- Competition for a shared free-energy pool R (consumer-resource form):
      dN_i/dt = (a_i R - 1/tau_i) N_i
      dR/dt   = S - delta R - R * sum_i a_i F_i N_i
  New systems of type i form at per-capita rate a_i R and each draws F_i from
  the pool. Each system disappears when its store runs out (rate 1/tau_i).
  The per-capita growth g_i = a_i R - 1/tau_i is the fitness. Frequencies obey
  replicator dynamics dx_i/dt = x_i (g_i - g_bar) as an identity, derived here
  rather than imposed. With one shared resource the type with the lowest
      R*_i = 1 / (a_i tau_i)
  excludes the others (competitive exclusion; Tilman's R* rule). This is the
  stable end state (ESS) of the "burn fast vs burn slow" game.

Status: formal layer-3 model (L1 candidate). Not yet confronted with data and
not derived from the parent action. Parameters a_i, F_i, P_i, S and delta are
inputs, not fits.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from typing import Sequence

K_B = 1.380649e-23  # J/K, exact (SI 2019)


def _positive(value: float, name: str) -> float:
    v = float(value)
    if not isfinite(v) or v <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return v


def lifetime(free_energy_store: float, burn_power: float) -> float:
    """tau = F / P: time until the free-energy store is exhausted."""

    return _positive(free_energy_store, "free_energy_store") / _positive(burn_power, "burn_power")


def steady_abundance(formation_rate: float, tau: float) -> float:
    """Little's law: steady number present = formation rate x lifetime."""

    return _positive(formation_rate, "formation_rate") * _positive(tau, "tau")


def bits_written(free_energy_store: float, temperature: float) -> float:
    """Upper bound on bits written to the environment when F is dissipated at T."""

    return _positive(free_energy_store, "free_energy_store") / (K_B * _positive(temperature, "temperature") * log(2.0))


@dataclass(frozen=True)
class SystemType:
    """One kind of system: formation coefficient a, store F, burn power P."""

    capture: float          # a_i: formation per unit resource per existing system
    free_energy_store: float  # F_i
    burn_power: float       # P_i

    def __post_init__(self) -> None:
        _positive(self.capture, "capture")
        _positive(self.free_energy_store, "free_energy_store")
        _positive(self.burn_power, "burn_power")

    @property
    def tau(self) -> float:
        return lifetime(self.free_energy_store, self.burn_power)

    def r_star(self) -> float:
        """Resource level at which this type exactly replaces itself."""

        return 1.0 / (self.capture * self.tau)


def simulate_cohorts(formation_rates: Sequence[float], stores: Sequence[float], powers: Sequence[float],
                     horizon: float, dt: float) -> list[float]:
    """Age-structured exhaustion model: return final abundance per type.

    Each step, b_i*dt new systems of type i form with store F_i; every system
    burns P_i*dt per step and is removed when its store is exhausted. No payoff
    or survival rule is imposed beyond running out of free energy.
    """

    _positive(horizon, "horizon")
    _positive(dt, "dt")
    steps = int(round(horizon / dt))
    result = []
    for b, F, P in zip(formation_rates, stores, powers):
        _positive(b, "formation_rate")
        cohorts: list[list[float]] = []  # [count, remaining store]
        for _ in range(steps):
            cohorts.append([b * dt, F])
            for cohort in cohorts:
                cohort[1] -= P * dt
            cohorts = [c for c in cohorts if c[1] > 1e-15 * F]
        result.append(sum(c[0] for c in cohorts))
    return result


def competition_rhs(N: Sequence[float], R: float, types: Sequence[SystemType],
                    supply: float, decay: float) -> tuple[list[float], float]:
    """Right-hand side of the shared-resource competition model."""

    dN = [(t.capture * R - 1.0 / t.tau) * n for t, n in zip(types, N)]
    dR = supply - decay * R - R * sum(t.capture * t.free_energy_store * n for t, n in zip(types, N))
    return dN, dR


def simulate_competition(N0: Sequence[float], R0: float, types: Sequence[SystemType],
                         supply: float, decay: float, horizon: float, dt: float) -> tuple[list[float], float]:
    """Integrate the competition model with classical RK4; return final (N, R)."""

    N, R = [float(x) for x in N0], float(R0)
    steps = int(round(_positive(horizon, "horizon") / _positive(dt, "dt")))
    for _ in range(steps):
        k1N, k1R = competition_rhs(N, R, types, supply, decay)
        k2N, k2R = competition_rhs([n + 0.5 * dt * k for n, k in zip(N, k1N)], R + 0.5 * dt * k1R, types, supply, decay)
        k3N, k3R = competition_rhs([n + 0.5 * dt * k for n, k in zip(N, k2N)], R + 0.5 * dt * k2R, types, supply, decay)
        k4N, k4R = competition_rhs([n + dt * k for n, k in zip(N, k3N)], R + dt * k3R, types, supply, decay)
        N = [n + dt / 6.0 * (a + 2 * b + 2 * c + d) for n, a, b, c, d in zip(N, k1N, k2N, k3N, k4N)]
        R = R + dt / 6.0 * (k1R + 2 * k2R + 2 * k3R + k4R)
    return N, R


def single_type_equilibrium(t: SystemType, supply: float, decay: float) -> tuple[float, float]:
    """Analytic coexistence point of one type with the pool: (N*, R*).

    R* = 1/(a tau); N* = (S - delta R*) / (a F R*). Requires S > delta R*.
    """

    r = t.r_star()
    if supply <= decay * r:
        return 0.0, supply / decay if decay > 0 else float("inf")
    return (supply - decay * r) / (t.capture * t.free_energy_store * r), r


def predicted_winner(types: Sequence[SystemType]) -> int:
    """Index of the type with the lowest R* (competitive exclusion)."""

    return min(range(len(types)), key=lambda i: types[i].r_star())
