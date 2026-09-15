"""Diagnostic lane for relational organization and persistence cost.

This module separates a dimensionless relational trajectory ``C(t)`` from an
available-energy ledger.  The only constitutive assumption in this lane is a
Rayleigh-type path cost,

    P_C = eta_C * (dC/dt)**2 >= 0,

which is a phenomenological comparator, not a derivation from the UET master
equation.  It provides a precise place to test the idea that different patterns
of behaviour can consume available free energy at different rates.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import List, Optional, Sequence, Tuple


PERSISTENCE_ENERGY_STATUS = "DIAGNOSTIC_ONLY"
PATH_COST_ORIGIN = "RAYLEIGH_TYPE_CONSTITUTIVE_ANSATZ"
PERSISTENCE_PRINCIPLE_ID = "UET-PRINCIPLE-001"
PERSISTENCE_PRINCIPLE_NAME_TH = (
    "หลักการจัดสรรพลังงานร่วมเพื่อการดำรงอยู่ของระบบ"
)
PERSISTENCE_PRINCIPLE_NAME_EN = (
    "Cooperative Energy Allocation for System Persistence Principle"
)
PERSISTENCE_PRINCIPLE_STATUS = "CANDIDATE_PRINCIPLE"


@dataclass(frozen=True)
class PersistenceEnergyConfig:
    """Normalized ledger parameters for the diagnostic lane."""

    initial_available_energy: float = 1.0
    sustain_threshold: float = 0.2
    behavior_cost_coefficient: float = 0.1
    input_power: float = 0.0
    output_power: float = 0.0
    unit_lane: str = "normalized"

    def __post_init__(self) -> None:
        values = {
            "initial_available_energy": self.initial_available_energy,
            "sustain_threshold": self.sustain_threshold,
            "behavior_cost_coefficient": self.behavior_cost_coefficient,
            "input_power": self.input_power,
            "output_power": self.output_power,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("persistence-energy parameters must be finite")
        if self.initial_available_energy <= 0.0:
            raise ValueError("initial_available_energy must be positive")
        if self.sustain_threshold < 0.0:
            raise ValueError("sustain_threshold must be non-negative")
        if self.sustain_threshold >= self.initial_available_energy:
            raise ValueError("sustain_threshold must be below initial energy")
        if self.behavior_cost_coefficient <= 0.0:
            raise ValueError("behavior_cost_coefficient must be positive")
        if self.unit_lane != "normalized":
            raise NotImplementedError(
                "persistence-energy diagnostic supports only unit_lane='normalized'"
            )


@dataclass(frozen=True)
class PersistenceEnergyResult:
    """Ledger and path-cost outputs for one prescribed relational trajectory."""

    times: Tuple[float, ...]
    C: Tuple[float, ...]
    C_rate: Tuple[float, ...]
    behavior_power: Tuple[float, ...]
    available_energy: Tuple[float, ...]
    behavior_work: float
    external_net_work: float
    ledger_closure_residual: float
    persistence_time: Optional[float]
    post_threshold_steps: int
    status: str = PERSISTENCE_ENERGY_STATUS


def _validate_trajectory(C_values: Sequence[float], dt: float) -> Tuple[float, ...]:
    if not isfinite(float(dt)) or dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    values = tuple(float(value) for value in C_values)
    if len(values) < 2:
        raise ValueError("C trajectory requires at least two samples")
    if not all(isfinite(value) for value in values):
        raise ValueError("C trajectory must contain finite values")
    return values


def simulate_persistence_energy(
    C_values: Sequence[float],
    dt: float,
    config: PersistenceEnergyConfig | None = None,
) -> PersistenceEnergyResult:
    """Evaluate the available-energy ledger along a prescribed ``C(t)`` path.

    ``C`` is not converted to energy.  The ledger uses the path derivative of C
    only through the explicitly declared constitutive cost.  This makes the
    result suitable for a same-endpoint/different-activity diagnostic.
    """

    config = config or PersistenceEnergyConfig()
    values = _validate_trajectory(C_values, dt)
    step = float(dt)
    times = tuple(index * step for index in range(len(values)))
    rates = tuple(
        (values[index + 1] - values[index]) / step
        for index in range(len(values) - 1)
    )
    powers = tuple(
        config.behavior_cost_coefficient * rate * rate for rate in rates
    )
    available: List[float] = [config.initial_available_energy]
    behavior_work = 0.0
    external_net_work = 0.0
    for power in powers:
        behavior_work += power * step
        external_net_work += (config.input_power - config.output_power) * step
        available.append(
            available[-1]
            + (config.input_power - config.output_power - power) * step
        )

    persistence_time: Optional[float] = None
    post_threshold_steps = 0
    for index, energy in enumerate(available):
        if energy <= config.sustain_threshold:
            persistence_time = times[index]
            post_threshold_steps = len(available) - index - 1
            break

    expected_final = (
        config.initial_available_energy
        + external_net_work
        - behavior_work
    )
    closure_residual = available[-1] - expected_final
    return PersistenceEnergyResult(
        times=times,
        C=values,
        C_rate=rates,
        behavior_power=powers,
        available_energy=tuple(available),
        behavior_work=behavior_work,
        external_net_work=external_net_work,
        ledger_closure_residual=closure_residual,
        persistence_time=persistence_time,
        post_threshold_steps=post_threshold_steps,
    )


__all__ = [
    "PATH_COST_ORIGIN",
    "PERSISTENCE_ENERGY_STATUS",
    "PERSISTENCE_PRINCIPLE_ID",
    "PERSISTENCE_PRINCIPLE_NAME_EN",
    "PERSISTENCE_PRINCIPLE_NAME_TH",
    "PERSISTENCE_PRINCIPLE_STATUS",
    "PersistenceEnergyConfig",
    "PersistenceEnergyResult",
    "simulate_persistence_energy",
]
