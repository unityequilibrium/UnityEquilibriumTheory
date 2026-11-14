"""Normalized standard-photon comparator for the carrier/observer lane.

This module is deliberately a standard-physics comparator. It provides a
small, deterministic source -> propagation -> detector chain in normalized
units; it does not identify a UET trace with a photon and does not derive
electromagnetism from the UET core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


PHOTON_OBSERVER_BASELINE_MODE = "standard_photon_observer_baseline_v1"
_UNIT_LANES = {"normalized"}


def _vector(value: Any, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a finite non-empty vector")
    return array.copy()


def _residual(value: np.ndarray, expected: np.ndarray) -> float:
    return float(np.max(np.abs(value - expected))) if value.size else 0.0


@dataclass(frozen=True)
class PhotonBaselineConfig:
    """Configuration for the normalized comparator and explicit detector."""

    unit_lane: str = "normalized"
    causal_speed: float = 1.0
    detector_gain: float = 1.0
    detector_threshold: float = 0.0
    tolerance: float = 1e-12

    def __post_init__(self) -> None:
        if self.unit_lane not in _UNIT_LANES:
            raise ValueError("photon comparator v1 accepts only normalized units")
        for name in ("causal_speed", "detector_gain", "detector_threshold", "tolerance"):
            value = float(getattr(self, name))
            if not np.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.causal_speed <= 0:
            raise ValueError("causal_speed must be positive")
        if self.detector_gain < 0 or self.detector_threshold < 0 or self.tolerance <= 0:
            raise ValueError("detector_gain, detector_threshold, and tolerance must be non-negative/positive")


@dataclass(frozen=True)
class PhotonEmissionEvent:
    """A source event with an explicit energy-momentum emission ledger."""

    source_id: str
    receiver_id: str
    emission_time: float
    path_length: float
    photon_energy: float
    direction: tuple[float, ...]
    source_energy_before: float
    source_energy_after: float
    source_momentum_before: tuple[float, ...]
    source_momentum_after: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.source_id or not self.receiver_id:
            raise ValueError("source_id and receiver_id are required")
        scalar_names = (
            "emission_time", "path_length", "photon_energy",
            "source_energy_before", "source_energy_after",
        )
        for name in scalar_names:
            value = float(getattr(self, name))
            if not np.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.path_length < 0 or self.photon_energy <= 0:
            raise ValueError("path_length must be non-negative and photon_energy must be positive")
        if self.source_energy_before < 0 or self.source_energy_after < 0:
            raise ValueError("source energies must be non-negative")
        direction = _vector(self.direction, "direction")
        before = _vector(self.source_momentum_before, "source_momentum_before")
        after = _vector(self.source_momentum_after, "source_momentum_after")
        if before.shape != direction.shape or after.shape != direction.shape:
            raise ValueError("direction and source momentum vectors must have equal shape")
        if not np.isclose(np.linalg.norm(direction), 1.0, atol=1e-12, rtol=0.0):
            raise ValueError("direction must be a unit vector")
        if not np.isclose(
            self.source_energy_before - self.source_energy_after,
            self.photon_energy,
            atol=1e-12,
            rtol=0.0,
        ):
            raise ValueError("source energy decrease must equal photon energy")
        object.__setattr__(self, "direction", tuple(float(x) for x in direction))
        object.__setattr__(self, "source_momentum_before", tuple(float(x) for x in before))
        object.__setattr__(self, "source_momentum_after", tuple(float(x) for x in after))


@dataclass(frozen=True)
class PhotonPropagationResult:
    emission: PhotonEmissionEvent
    photon_momentum: tuple[float, ...]
    propagation_speed: float
    travel_time: float
    arrival_time: float
    energy_residual: float
    momentum_residual: float
    causal_ok: bool
    ledger_closed: bool


@dataclass(frozen=True)
class PhotonDetectorRecord:
    propagation: PhotonPropagationResult
    detector_interaction: bool
    detected: bool
    measured_energy: float
    measured_momentum: tuple[float, ...]
    observer_record: tuple[float, ...]
    detector_gain: float
    detector_threshold: float


def photon_energy_momentum(
    photon_energy: float,
    direction: Any,
) -> tuple[float, ...]:
    """Return the standard normalized massless relation ``p = E * n``."""

    energy = float(photon_energy)
    if not np.isfinite(energy) or energy <= 0:
        raise ValueError("photon_energy must be finite and positive")
    unit_direction = _vector(direction, "direction")
    if not np.isclose(np.linalg.norm(unit_direction), 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("direction must be a unit vector")
    return tuple(float(value) for value in energy * unit_direction)


def propagate_photon(
    event: PhotonEmissionEvent,
    config: PhotonBaselineConfig | None = None,
) -> PhotonPropagationResult:
    """Propagate one standard comparator photon at the declared causal speed."""

    cfg = config or PhotonBaselineConfig()
    momentum = np.asarray(photon_energy_momentum(event.photon_energy, event.direction), dtype=float)
    source_before = np.asarray(event.source_momentum_before, dtype=float)
    source_after = np.asarray(event.source_momentum_after, dtype=float)
    energy_residual = abs(event.source_energy_before - event.source_energy_after - event.photon_energy)
    momentum_residual = _residual(source_before - source_after, momentum)
    travel_time = event.path_length / cfg.causal_speed
    arrival_time = event.emission_time + travel_time
    causal_ok = cfg.causal_speed <= cfg.causal_speed * (1.0 + cfg.tolerance)
    ledger_closed = energy_residual <= cfg.tolerance and momentum_residual <= cfg.tolerance
    return PhotonPropagationResult(
        emission=event,
        photon_momentum=tuple(float(value) for value in momentum),
        propagation_speed=float(cfg.causal_speed),
        travel_time=float(travel_time),
        arrival_time=float(arrival_time),
        energy_residual=float(energy_residual),
        momentum_residual=float(momentum_residual),
        causal_ok=bool(causal_ok),
        ledger_closed=bool(ledger_closed),
    )


def detect_photon(
    propagation: PhotonPropagationResult,
    config: PhotonBaselineConfig | None = None,
    *,
    detector_interaction: bool = True,
) -> PhotonDetectorRecord:
    """Create an explicit detector record without changing source dynamics."""

    cfg = config or PhotonBaselineConfig()
    raw_energy = propagation.emission.photon_energy * cfg.detector_gain if detector_interaction else 0.0
    detected = bool(
        detector_interaction
        and propagation.causal_ok
        and propagation.ledger_closed
        and raw_energy >= cfg.detector_threshold
    )
    measured_energy = raw_energy if detected else 0.0
    measured_momentum = (
        tuple(cfg.detector_gain * value for value in propagation.photon_momentum)
        if detected else tuple(0.0 for _ in propagation.photon_momentum)
    )
    observer_record = (
        (propagation.arrival_time, measured_energy, *measured_momentum)
        if detected else ()
    )
    return PhotonDetectorRecord(
        propagation=propagation,
        detector_interaction=bool(detector_interaction),
        detected=detected,
        measured_energy=float(measured_energy),
        measured_momentum=measured_momentum,
        observer_record=tuple(float(value) for value in observer_record),
        detector_gain=float(cfg.detector_gain),
        detector_threshold=float(cfg.detector_threshold),
    )


def photon_observer_contract() -> dict[str, Any]:
    """Return the semantic and claim boundary for this comparator."""

    return {
        "operator_mode": PHOTON_OBSERVER_BASELINE_MODE,
        "unit_lane": "normalized_natural_units_v1",
        "relations": [
            "p = E * n for unit direction n",
            "t_arrival = t_emit + distance / c",
            "source_energy_before - source_energy_after = E_photon",
            "source_momentum_before - source_momentum_after = p_photon",
        ],
        "physical_layers": ["source_event", "emission", "propagation", "detector_record"],
        "observer_record_is_physical_feedback": False,
        "trace_feedback": False,
        "parameter_fitting": False,
        "external_validation": False,
        "uet_photon_derivation": False,
        "claim_boundary": "standard normalized photon comparator only; no UET particle identity or massless-transition derivation",
        "open_items": [
            "SI source and detector units",
            "instrument response and uncertainty",
            "external source package",
            "UET source-to-carrier transition law",
        ],
    }


__all__ = [
    "PHOTON_OBSERVER_BASELINE_MODE",
    "PhotonBaselineConfig",
    "PhotonEmissionEvent",
    "PhotonPropagationResult",
    "PhotonDetectorRecord",
    "photon_energy_momentum",
    "propagate_photon",
    "detect_photon",
    "photon_observer_contract",
]
