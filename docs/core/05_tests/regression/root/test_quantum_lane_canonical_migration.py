"""Compatibility checks for the migrated operational quantum lane."""

from __future__ import annotations

import importlib

from docs.core import uet_quantum_interpretations as legacy_interpretations
from docs.core import uet_quantum_measurement as legacy_measurement


def test_quantum_root_modules_forward_to_one_canonical_lane() -> None:
    measurement_name = (
        "docs.core.03_lanes.carrier_observer.uet_quantum_measurement"
    )
    interpretations_name = (
        "docs.core.03_lanes.carrier_observer.uet_quantum_interpretations"
    )
    measurement = importlib.import_module(measurement_name)
    interpretations = importlib.import_module(interpretations_name)
    package = importlib.import_module("docs.core.03_lanes.carrier_observer")

    assert legacy_measurement.__canonical_module__ == measurement_name
    assert legacy_interpretations.__canonical_module__ == interpretations_name
    assert legacy_measurement.DensityOperator is measurement.DensityOperator
    assert legacy_interpretations.qbist_view is interpretations.qbist_view
    assert package.DensityOperator is measurement.DensityOperator
    assert package.interpretation_contract is interpretations.interpretation_contract
