from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_matter_space_characteristic import (
    CHARACTERISTIC_CONE_OPERATOR_MODE,
    CharacteristicConeStabilityError,
    characteristic_cone_dt,
    characteristic_cone_step,
)
from docs.core.uet_matter_space_finite_cone import FiniteConeCConfig, FiniteConeCState


def make_config() -> FiniteConeCConfig:
    return FiniteConeCConfig(
        a_C=0.0,
        b_C=0.1,
        kappa_C=1.0,
        mobility_C=1.0,
        tau_C=1.0,
        a_space=0.0,
        b_space=0.1,
        kappa_space=1.0,
        mobility_space=1.0,
        tau_space=1.0,
        coupling_g=0.1,
        boundary_condition="periodic",
        unit_lane="normalized",
        ledger_tolerance=1e-4,
    )


def test_strict_cfl_rejects_nonmatching_step() -> None:
    config = make_config()
    with pytest.raises(CharacteristicConeStabilityError):
        characteristic_cone_step(
            FiniteConeCState(
                np.zeros(41),
                np.zeros(41),
                np.zeros(41),
                np.zeros(41),
            ),
            dt=0.05,
            dx=0.1,
            config=config,
        )


def test_localized_pulse_has_no_prearrival_leakage() -> None:
    config = make_config()
    n = 101
    center = n // 2
    dx = 0.1
    dt = characteristic_cone_dt(dx, config)
    state = FiniteConeCState(
        C=np.eye(1, n, center, dtype=float).reshape(-1) * 0.1,
        C_rate=np.zeros(n),
        space_response=np.zeros(n),
        space_rate=np.zeros(n),
    )
    for step in range(1, 7):
        result = characteristic_cone_step(state, dt, dx, config)
        state = FiniteConeCState(
            result.C,
            result.V,
            result.space_response,
            result.space_rate,
        )
        distance = np.abs(np.arange(n) - center)
        outside = np.abs(state.C)[distance > step]
        outside_phi = np.abs(state.space_response)[distance > step]
        assert np.max(outside, initial=0.0) <= 1e-14
        assert np.max(outside_phi, initial=0.0) <= 1e-14


def test_ledger_and_mode_contract_are_reported() -> None:
    config = make_config()
    dx = 0.1
    dt = characteristic_cone_dt(dx, config)
    state = FiniteConeCState(
        np.zeros(41),
        np.zeros(41),
        np.zeros(41),
        np.zeros(41),
    )
    result = characteristic_cone_step(state, dt, dx, config)
    assert result.diagnostics["operator_mode"] == CHARACTERISTIC_CONE_OPERATOR_MODE
    assert result.diagnostics["field_clipping_applied"] is False
    assert result.diagnostics["cone_padding_applied"] is False
    assert result.energy_ledger["ledger_gate"] == "PASS"


def test_trace_toggle_does_not_change_physical_step() -> None:
    config = make_config()
    dx = 0.1
    dt = characteristic_cone_dt(dx, config)
    state = FiniteConeCState(
        np.zeros(41),
        np.zeros(41),
        np.zeros(41),
        np.zeros(41),
    )
    plain = characteristic_cone_step(state, dt, dx, config)
    assert plain.trace_observable is None
    with pytest.raises(ValueError):
        characteristic_cone_step(state, 0.05, dx, config)
