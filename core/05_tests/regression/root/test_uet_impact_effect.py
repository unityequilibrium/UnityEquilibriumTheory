"""Targeted tests for the carrier-neutral impact/effect relation."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_impact_effect import (
    COUPLED_RECEIVER_MODE,
    TRACE_ONLY_MODE,
    CarrierRecord,
    ImpactRecord,
    ReceiverDynamics,
    apply_receiver_effect,
    impact_to_effect,
)


def _impact(*, mass_transfer: float = 0.0) -> ImpactRecord:
    return ImpactRecord(
        source_id="source-A",
        receiver_id="receiver-B",
        interaction_type="emission",
        energy_transfer=0.5,
        mass_transfer=mass_transfer,
        impact_id="impact-1",
    )


def _carrier(*, payload: object = 2.0) -> CarrierRecord:
    return CarrierRecord(
        carrier_type="declared_signal",
        source_id="source-A",
        receiver_id="receiver-B",
        energy=0.5,
        propagation_speed=1.0,
        rest_mass_status="massless",
        carrier_id="carrier-1",
        payload=np.asarray(payload, dtype=float),
    )


def test_effect_can_exist_without_source_mass_transfer() -> None:
    effect = impact_to_effect(_impact(mass_transfer=0.0), _carrier())
    assert effect.active is True
    assert effect.carrier_id == "carrier-1"
    assert effect.physical_ledger["impact_mass_transfer"] == 0.0


def test_no_carrier_or_detector_interaction_does_not_change_receiver() -> None:
    state = np.array([1.0, 2.0])
    no_carrier = impact_to_effect(_impact(), None, generated_trace=np.zeros(2), mode=COUPLED_RECEIVER_MODE)
    no_signal_update = apply_receiver_effect(
        state,
        no_carrier,
        ReceiverDynamics(gain=3.0, feedback_enabled=True),
    )
    np.testing.assert_allclose(no_signal_update.state, state)
    assert no_carrier.reason == "no_carrier"

    no_detector = impact_to_effect(_impact(), _carrier(payload=[2.0, 3.0]), detector_interaction=False)
    detector_update = apply_receiver_effect(
        state,
        no_detector,
        ReceiverDynamics(gain=3.0, feedback_enabled=True),
    )
    np.testing.assert_allclose(detector_update.state, state)
    assert no_detector.reason == "no_detector_interaction"


def test_receiver_changes_only_with_explicit_feedback_mode() -> None:
    state = np.array([1.0, 2.0])
    effect = impact_to_effect(
        _impact(),
        _carrier(payload=[2.0, 3.0]),
        mode=COUPLED_RECEIVER_MODE,
    )
    disabled = apply_receiver_effect(state, effect, ReceiverDynamics(gain=0.5, feedback_enabled=False))
    np.testing.assert_allclose(disabled.state, state)

    enabled = apply_receiver_effect(state, effect, ReceiverDynamics(gain=0.5, feedback_enabled=True))
    np.testing.assert_allclose(enabled.state, [2.0, 3.5])
    assert enabled.ledger["feedback_applied"] is True
    assert enabled.ledger["trace_feedback"] is False


def test_observer_protocol_changes_record_not_generated_trace() -> None:
    trace = np.array([0.25, 0.5])
    first = impact_to_effect(_impact(), _carrier(payload=[2.0, 4.0]), generated_trace=trace, observer_gain=1.0)
    second = impact_to_effect(_impact(), _carrier(payload=[2.0, 4.0]), generated_trace=trace, observer_gain=0.25)
    np.testing.assert_allclose(first.generated_trace, second.generated_trace)
    np.testing.assert_allclose(first.observer_record, [2.0, 4.0])
    np.testing.assert_allclose(second.observer_record, [0.5, 1.0])
    assert first.physical_ledger["trace_feedback"] is False
    assert second.physical_ledger["trace_feedback"] is False


def test_trace_only_mode_never_applies_receiver_feedback() -> None:
    effect = impact_to_effect(_impact(), _carrier(payload=[1.0, 1.0]), mode=TRACE_ONLY_MODE)
    update = apply_receiver_effect(
        np.zeros(2), effect, ReceiverDynamics(gain=100.0, feedback_enabled=True)
    )
    np.testing.assert_allclose(update.state, 0.0)
    assert update.ledger["feedback_applied"] is False


def test_carrier_speed_and_unit_lane_are_checked() -> None:
    with pytest.raises(ValueError, match="causal limit"):
        CarrierRecord(
            carrier_type="superluminal",
            source_id="source-A",
            receiver_id="receiver-B",
            energy=1.0,
            propagation_speed=1.1,
        )
    with pytest.raises(ValueError, match="normalized unit lane"):
        CarrierRecord(
            carrier_type="si-without-contract",
            source_id="source-A",
            receiver_id="receiver-B",
            energy=1.0,
            unit_lane="si",
        )
