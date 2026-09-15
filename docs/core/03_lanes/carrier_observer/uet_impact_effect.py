"""Carrier-neutral impact/effect relation for the foundation research lane.

This module deliberately models relations and records, not a new information
field.  A physical impact may generate a carrier.  A detector/receiver may
then construct an effect or observer record from that carrier.  Receiver
feedback is disabled unless a caller explicitly selects ``coupled_receiver_v1``
and supplies a declared ``ReceiverDynamics`` object.

The v1 lane is normalized and finite-dimensional.  It is a research interface,
not a derivation of a photon, neutrino, positron, or massless transition.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

import numpy as np


IMPACT_EFFECT_OPERATOR_MODE = "carrier_neutral_impact_effect_v1"
TRACE_ONLY_MODE = "observation_only"
COUPLED_RECEIVER_MODE = "coupled_receiver_v1"
SUPPORTED_EFFECT_MODES = {TRACE_ONLY_MODE, COUPLED_RECEIVER_MODE}
_UNIT_LANES = {"normalized"}
_REST_MASS_STATUSES = {"massless", "massive", "unspecified"}


def _finite_array(value: Any, name: str, *, allow_none: bool = False) -> Optional[np.ndarray]:
    if value is None and allow_none:
        return None
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array.copy()


def _validate_unit_lane(unit_lane: str) -> None:
    if unit_lane not in _UNIT_LANES:
        raise ValueError("carrier-neutral v1 accepts only the normalized unit lane")


@dataclass(frozen=True)
class ImpactRecord:
    """A physical coupling record; it is not an observer interpretation."""

    source_id: str
    receiver_id: str
    interaction_type: str
    energy_transfer: float = 0.0
    momentum_transfer: tuple[float, ...] = ()
    mass_transfer: float = 0.0
    unit_lane: str = "normalized"
    impact_id: str = "impact-0"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_id or not self.receiver_id or not self.interaction_type:
            raise ValueError("source_id, receiver_id, and interaction_type are required")
        _validate_unit_lane(self.unit_lane)
        if not np.isfinite(self.energy_transfer) or not np.isfinite(self.mass_transfer):
            raise ValueError("impact transfers must be finite")
        momentum = _finite_array(self.momentum_transfer, "momentum_transfer")
        object.__setattr__(self, "momentum_transfer", tuple(float(x) for x in momentum))


@dataclass(frozen=True)
class CarrierRecord:
    """A declared propagating channel between a source and receiver."""

    carrier_type: str
    source_id: str
    receiver_id: str
    energy: float
    momentum: tuple[float, ...] = ()
    propagation_speed: float = 1.0
    causal_speed_limit: float = 1.0
    rest_mass_status: str = "unspecified"
    unit_lane: str = "normalized"
    carrier_id: str = "carrier-0"
    payload: Optional[np.ndarray] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.carrier_type or not self.source_id or not self.receiver_id:
            raise ValueError("carrier_type, source_id, and receiver_id are required")
        _validate_unit_lane(self.unit_lane)
        if self.rest_mass_status not in _REST_MASS_STATUSES:
            raise ValueError(f"rest_mass_status must be one of {sorted(_REST_MASS_STATUSES)}")
        if not np.isfinite(self.energy) or self.energy < 0:
            raise ValueError("carrier energy must be finite and non-negative")
        if not np.isfinite(self.propagation_speed) or self.propagation_speed <= 0:
            raise ValueError("carrier propagation_speed must be finite and positive")
        if not np.isfinite(self.causal_speed_limit) or self.causal_speed_limit <= 0:
            raise ValueError("causal_speed_limit must be finite and positive")
        if self.propagation_speed > self.causal_speed_limit * (1.0 + 1e-12):
            raise ValueError("carrier propagation_speed exceeds the declared causal limit")
        momentum = _finite_array(self.momentum, "momentum")
        payload = _finite_array(self.payload, "payload", allow_none=True)
        object.__setattr__(self, "momentum", tuple(float(x) for x in momentum))
        object.__setattr__(self, "payload", payload)


@dataclass(frozen=True)
class EffectRecord:
    """A derived receiver/observer record, never an independent physical field."""

    impact_id: str
    carrier_id: Optional[str]
    mode: str
    active: bool
    reason: str
    input_value: np.ndarray
    output_value: np.ndarray
    receiver_delta: np.ndarray
    observer_record: np.ndarray
    generated_trace: np.ndarray
    carrier_energy: float
    physical_ledger: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.mode not in SUPPORTED_EFFECT_MODES:
            raise ValueError(f"mode must be one of {sorted(SUPPORTED_EFFECT_MODES)}")
        for name in ("input_value", "output_value", "receiver_delta", "observer_record", "generated_trace"):
            object.__setattr__(self, name, _finite_array(getattr(self, name), name))
        if not np.isfinite(self.carrier_energy) or self.carrier_energy < 0:
            raise ValueError("carrier_energy must be finite and non-negative")


@dataclass(frozen=True)
class ReceiverDynamics:
    """Explicit normalized receiver law used only when feedback is requested."""

    gain: float = 1.0
    feedback_enabled: bool = False
    unit_lane: str = "normalized"
    law_id: str = "explicit_linear_receiver_v1"

    def __post_init__(self) -> None:
        _validate_unit_lane(self.unit_lane)
        if not np.isfinite(self.gain):
            raise ValueError("receiver gain must be finite")
        if not self.law_id:
            raise ValueError("receiver law_id is required")


@dataclass(frozen=True)
class ReceiverUpdate:
    """Result of applying an explicit receiver law and its local ledger."""

    state: np.ndarray
    delta: np.ndarray
    ledger: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", _finite_array(self.state, "state"))
        object.__setattr__(self, "delta", _finite_array(self.delta, "delta"))


def _zero_like(value: Any) -> np.ndarray:
    array = _finite_array(value, "receiver_state")
    return np.zeros_like(array, dtype=float)


def _payload(carrier: CarrierRecord) -> np.ndarray:
    if carrier.payload is not None:
        return carrier.payload.copy()
    return np.asarray(carrier.energy, dtype=float)


def impact_to_effect(
    impact: ImpactRecord,
    carrier: Optional[CarrierRecord],
    *,
    generated_trace: Any = 0.0,
    detector_interaction: bool = True,
    observer_gain: float = 1.0,
    mode: str = TRACE_ONLY_MODE,
) -> EffectRecord:
    """Construct a derived effect record without mutating physical state.

    ``carrier=None`` or ``detector_interaction=False`` produces an inactive
    record with zero receiver/observer response.  This makes the no-signal
    control case explicit instead of treating absent data as a force.
    """

    if mode not in SUPPORTED_EFFECT_MODES:
        raise ValueError(f"mode must be one of {sorted(SUPPORTED_EFFECT_MODES)}")
    if not np.isfinite(observer_gain):
        raise ValueError("observer_gain must be finite")
    trace = _finite_array(generated_trace, "generated_trace")
    if carrier is None:
        zero = _zero_like(trace)
        return EffectRecord(
            impact_id=impact.impact_id,
            carrier_id=None,
            mode=mode,
            active=False,
            reason="no_carrier",
            input_value=zero,
            output_value=zero,
            receiver_delta=zero,
            observer_record=zero,
            generated_trace=trace,
            carrier_energy=0.0,
            physical_ledger={"carrier_present": False, "trace_feedback": False},
        )
    if impact.source_id != carrier.source_id or impact.receiver_id != carrier.receiver_id:
        raise ValueError("impact and carrier source/receiver ids must match")
    input_value = _payload(carrier)
    zero = np.zeros_like(input_value, dtype=float)
    if not detector_interaction:
        return EffectRecord(
            impact_id=impact.impact_id,
            carrier_id=carrier.carrier_id,
            mode=mode,
            active=False,
            reason="no_detector_interaction",
            input_value=input_value,
            output_value=zero,
            receiver_delta=zero,
            observer_record=zero,
            generated_trace=trace,
            carrier_energy=float(carrier.energy),
            physical_ledger={"carrier_present": True, "detector_interaction": False, "trace_feedback": False},
        )
    output_value = input_value * float(observer_gain)
    return EffectRecord(
        impact_id=impact.impact_id,
        carrier_id=carrier.carrier_id,
        mode=mode,
        active=True,
        reason="detector_interaction",
        input_value=input_value,
        output_value=output_value,
        receiver_delta=zero,
        observer_record=output_value.copy(),
        generated_trace=trace,
        carrier_energy=float(carrier.energy),
        physical_ledger={
            "carrier_present": True,
            "detector_interaction": True,
            "impact_energy_transfer": float(impact.energy_transfer),
            "impact_mass_transfer": float(impact.mass_transfer),
            "trace_feedback": False,
            "units_lane": impact.unit_lane,
        },
    )


def apply_receiver_effect(
    receiver_state: Any,
    effect: EffectRecord,
    dynamics: ReceiverDynamics,
) -> ReceiverUpdate:
    """Apply feedback only through an explicit receiver-dynamics law."""

    state = _finite_array(receiver_state, "receiver_state")
    if not effect.active or not dynamics.feedback_enabled or effect.mode != COUPLED_RECEIVER_MODE:
        delta = np.zeros_like(state, dtype=float)
        return ReceiverUpdate(
            state=state,
            delta=delta,
            ledger={
                "feedback_applied": False,
                "reason": "inactive_or_feedback_disabled",
                "trace_feedback": False,
                "law_id": dynamics.law_id,
                "units_lane": dynamics.unit_lane,
            },
        )
    try:
        delta = np.broadcast_to(dynamics.gain * effect.output_value, state.shape).astype(float, copy=True)
    except ValueError as exc:
        raise ValueError("effect output cannot be broadcast to receiver_state") from exc
    updated = state + delta
    return ReceiverUpdate(
        state=updated,
        delta=delta,
        ledger={
            "feedback_applied": True,
            "reason": "explicit_receiver_dynamics",
            "trace_feedback": False,
            "law_id": dynamics.law_id,
            "input_carrier_energy": float(effect.carrier_energy),
            "receiver_change_proxy": float(np.sum(np.abs(delta))),
            "units_lane": dynamics.unit_lane,
        },
    )


def impact_effect_contract() -> dict[str, Any]:
    """Return the machine-readable semantic contract used by audits/tests."""

    return {
        "operator_mode": IMPACT_EFFECT_OPERATOR_MODE,
        "chain": ["impact", "R_gen", "carrier", "detector_interaction", "effect", "R_obs"],
        "effect_is_independent_field": False,
        "trace_feedback_into_core": False,
        "receiver_feedback_requires": ["explicit mode", "receiver dynamics", "unit lane", "input/ledger"],
        "unit_lane": "normalized_only_v1",
        "candidate_carriers": ["photon", "neutrino", "gravitational_wave", "matter_antimatter_products"],
        "claim_boundary": "carrier-neutral candidate relation; no particle identity or transition law derived",
    }
