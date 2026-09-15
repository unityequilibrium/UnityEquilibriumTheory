"""Deterministic relational two-body baseline for the UET foundation lane.

This module is deliberately a standard-physics comparator, not a new UET law.  It
provides the smallest executable mapping needed to keep four layers separate:

    C_relational -> normalized interaction potential -> force -> acceleration
    source event -> finite-signal observer record

The masses are parameters in the standard Newtonian counterpart.  They are not
the definition of ``C``.  The comparator therefore also exposes a mass-scale
diagnostic: the geometry-only ``C`` coordinate can remain unchanged while the
potential and force amplitudes change with the masses.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, List, Tuple


Vector2 = Tuple[float, float]


def _add(a: Vector2, b: Vector2) -> Vector2:
    return a[0] + b[0], a[1] + b[1]


def _sub(a: Vector2, b: Vector2) -> Vector2:
    return a[0] - b[0], a[1] - b[1]


def _scale(a: Vector2, factor: float) -> Vector2:
    return factor * a[0], factor * a[1]


def _norm(a: Vector2) -> float:
    return sqrt(a[0] * a[0] + a[1] * a[1])


@dataclass(frozen=True)
class RelationalBaselineConfig:
    """Normalized comparator configuration.

    ``G``, masses, distances, time, and signal speed are code-unit quantities.
    They are not SI constants.  A dimensional lane must provide a separate unit
    and provenance contract before any physical claim is made.
    """

    G: float = 1.0
    mass_a: float = 1.0
    mass_b: float = 1.0
    separation_reference: float = 2.0
    dt: float = 0.001
    steps: int = 2000
    signal_speed: float = 10.0


@dataclass(frozen=True)
class TwoBodyState:
    time: float
    position_a: Vector2
    position_b: Vector2
    velocity_a: Vector2
    velocity_b: Vector2


def circular_initial_state(config: RelationalBaselineConfig) -> TwoBodyState:
    """Return a center-of-mass circular initial condition for the comparator."""

    total_mass = config.mass_a + config.mass_b
    radius = config.separation_reference
    omega = sqrt(config.G * total_mass / radius**3)
    radius_a = radius * config.mass_b / total_mass
    radius_b = radius * config.mass_a / total_mass
    return TwoBodyState(
        time=0.0,
        position_a=(radius_a, 0.0),
        position_b=(-radius_b, 0.0),
        velocity_a=(0.0, omega * radius_a),
        velocity_b=(0.0, -omega * radius_b),
    )


def separation_vector(state: TwoBodyState) -> Vector2:
    return _sub(state.position_a, state.position_b)


def separation(state: TwoBodyState) -> float:
    return _norm(separation_vector(state))


def interaction_coordinate(
    state: TwoBodyState, separation_reference: float
) -> float:
    """Dimensionless geometry-only relational coordinate ``C = -r_ref / r``."""

    return -separation_reference / separation(state)


def interaction_energy(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> float:
    """Standard Newtonian pair potential used as the comparator counterpart."""

    return -config.G * config.mass_a * config.mass_b / separation(state)


def interaction_energy_from_coordinate(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> float:
    """Recover the Newtonian pair potential from the normalized ``C`` map."""

    energy_scale = (
        config.G
        * config.mass_a
        * config.mass_b
        / config.separation_reference
    )
    return energy_scale * interaction_coordinate(
        state, config.separation_reference
    )


def force_on_a(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> Vector2:
    """Return the standard Newtonian force on body A."""

    r_vec = separation_vector(state)
    r = _norm(r_vec)
    return _scale(
        r_vec,
        -config.G * config.mass_a * config.mass_b / r**3,
    )


def force_on_a_from_coordinate(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> Vector2:
    """Return force from ``U(C)`` and the exact radial derivative of ``C``."""

    r_vec = separation_vector(state)
    r = _norm(r_vec)
    energy_scale = (
        config.G
        * config.mass_a
        * config.mass_b
        / config.separation_reference
    )
    d_coordinate_dr = config.separation_reference / r**2
    return _scale(
        r_vec,
        -energy_scale * d_coordinate_dr / r,
    )


def accelerations(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> Tuple[Vector2, Vector2]:
    force = force_on_a(state, config)
    return _scale(force, 1.0 / config.mass_a), _scale(
        force, -1.0 / config.mass_b
    )


def velocity_verlet_step(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> TwoBodyState:
    """Advance the standard comparator with a time-reversible Verlet step."""

    dt = config.dt
    acceleration_a, acceleration_b = accelerations(state, config)
    next_position_a = _add(
        _add(state.position_a, _scale(state.velocity_a, dt)),
        _scale(acceleration_a, 0.5 * dt * dt),
    )
    next_position_b = _add(
        _add(state.position_b, _scale(state.velocity_b, dt)),
        _scale(acceleration_b, 0.5 * dt * dt),
    )
    position_state = TwoBodyState(
        time=state.time + dt,
        position_a=next_position_a,
        position_b=next_position_b,
        velocity_a=state.velocity_a,
        velocity_b=state.velocity_b,
    )
    next_acceleration_a, next_acceleration_b = accelerations(
        position_state, config
    )
    next_velocity_a = _add(
        state.velocity_a,
        _scale(_add(acceleration_a, next_acceleration_a), 0.5 * dt),
    )
    next_velocity_b = _add(
        state.velocity_b,
        _scale(_add(acceleration_b, next_acceleration_b), 0.5 * dt),
    )
    return TwoBodyState(
        time=position_state.time,
        position_a=position_state.position_a,
        position_b=position_state.position_b,
        velocity_a=next_velocity_a,
        velocity_b=next_velocity_b,
    )


def trajectory(
    initial_state: TwoBodyState, config: RelationalBaselineConfig
) -> List[TwoBodyState]:
    states = [initial_state]
    for _ in range(config.steps):
        states.append(velocity_verlet_step(states[-1], config))
    return states


def total_energy(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> float:
    kinetic = 0.5 * config.mass_a * _norm(state.velocity_a) ** 2
    kinetic += 0.5 * config.mass_b * _norm(state.velocity_b) ** 2
    return kinetic + interaction_energy(state, config)


def total_momentum(
    state: TwoBodyState, config: RelationalBaselineConfig
) -> Vector2:
    return _add(
        _scale(state.velocity_a, config.mass_a),
        _scale(state.velocity_b, config.mass_b),
    )


def galilean_boost(state: TwoBodyState, boost: Vector2) -> TwoBodyState:
    return TwoBodyState(
        time=state.time,
        position_a=state.position_a,
        position_b=state.position_b,
        velocity_a=_add(state.velocity_a, boost),
        velocity_b=_add(state.velocity_b, boost),
    )


def delayed_observation(
    states: Iterable[TwoBodyState],
    event_index: int,
    observer_position: Vector2,
    signal_speed: float,
) -> dict:
    """Return a received source record and the source's later state.

    The observer is fixed in this Newtonian comparator.  The record is indexed by
    the source event; it is not silently replaced with the source state at the
    observer's arrival time.
    """

    history = list(states)
    event = history[event_index]
    distance = _norm(_sub(event.position_a, observer_position))
    arrival_time = event.time + distance / signal_speed
    current_index = min(
        range(len(history)), key=lambda index: abs(history[index].time - arrival_time)
    )
    current = history[current_index]
    return {
        "event_time": event.time,
        "arrival_time": arrival_time,
        "delay": arrival_time - event.time,
        "event_position_a": event.position_a,
        "received_position_a": event.position_a,
        "source_position_at_arrival": current.position_a,
        "arrival_index": current_index,
        "past_state_separation": _norm(
            _sub(event.position_a, current.position_a)
        ),
    }


__all__ = [
    "RelationalBaselineConfig",
    "TwoBodyState",
    "accelerations",
    "circular_initial_state",
    "delayed_observation",
    "force_on_a",
    "force_on_a_from_coordinate",
    "galilean_boost",
    "interaction_coordinate",
    "interaction_energy",
    "interaction_energy_from_coordinate",
    "separation",
    "total_energy",
    "total_momentum",
    "trajectory",
]
