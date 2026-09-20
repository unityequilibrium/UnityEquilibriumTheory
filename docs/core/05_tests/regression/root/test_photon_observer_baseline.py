"""Tests for the normalized standard-photon comparator."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.photon_observer_baseline import (
    PhotonBaselineConfig,
    PhotonEmissionEvent,
    detect_photon,
    photon_energy_momentum,
    propagate_photon,
)


def _event() -> PhotonEmissionEvent:
    return PhotonEmissionEvent(
        source_id="s",
        receiver_id="d",
        emission_time=2.0,
        path_length=5.0,
        photon_energy=2.0,
        direction=(1.0, 0.0, 0.0),
        source_energy_before=10.0,
        source_energy_after=8.0,
        source_momentum_before=(3.0, 1.0, 0.0),
        source_momentum_after=(1.0, 1.0, 0.0),
    )


def test_massless_energy_momentum_and_arrival_relations() -> None:
    event = _event()
    momentum = photon_energy_momentum(event.photon_energy, event.direction)
    result = propagate_photon(event)
    assert np.allclose(momentum, (2.0, 0.0, 0.0))
    assert np.isclose(np.linalg.norm(momentum), event.photon_energy)
    assert result.ledger_closed
    assert result.arrival_time == 7.0
    assert result.causal_ok


def test_detector_protocol_changes_record_not_propagation() -> None:
    event = _event()
    config = PhotonBaselineConfig(detector_gain=1.5, detector_threshold=0.5)
    result = propagate_photon(event, config)
    active = detect_photon(result, config)
    inactive = detect_photon(result, config, detector_interaction=False)
    assert active.detected
    assert not inactive.detected
    assert active.propagation.arrival_time == inactive.propagation.arrival_time
    assert active.observer_record != inactive.observer_record


def test_invalid_source_ledger_is_rejected() -> None:
    with pytest.raises(ValueError, match="source energy decrease"):
        PhotonEmissionEvent(
            source_id="s",
            receiver_id="d",
            emission_time=0.0,
            path_length=1.0,
            photon_energy=2.0,
            direction=(1.0, 0.0),
            source_energy_before=10.0,
            source_energy_after=9.0,
            source_momentum_before=(2.0, 0.0),
            source_momentum_after=(0.0, 0.0),
        )
