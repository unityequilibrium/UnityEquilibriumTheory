"""Focused tests for the retarded non-closed constitutive kernel."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_nonclosed import (
    CausalInfluenceConfig,
    CausalSourceEvent,
    causal_exchange_from_events,
    causal_nonclosed_contract,
    covariant_retarded_kernel_value,
    rest_frame_separation,
    retarded_influence_from_events,
    retarded_telegraph_kernel_1p1,
    validate_rest_frame_slice,
)
from docs.core.uet_covariant_response import CovariantResponseConfig

METRIC = np.diag([-1.0, 1.0, 1.0, 1.0])
FRAME = np.array([1.0, 0.0, 0.0, 0.0])
AXIS = np.array([0.0, 1.0, 0.0, 0.0])


def _config() -> CausalInfluenceConfig:
    return CausalInfluenceConfig(
        tau_memory=1.25,
        diffusivity=.45,
        decay_rate=.35,
        source_coupling=.8,
    )


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"tau_memory": 0.0}, ValueError),
        ({"diffusivity": 0.0}, ValueError),
        ({"decay_rate": -1.0}, ValueError),
        ({"tau_memory": 1.0, "diffusivity": 1.01}, ValueError),
        ({"kernel_dimension": 3}, NotImplementedError),
        ({"unit_lane": "SI"}, NotImplementedError),
    ],
)
def test_config_rejects_unstable_or_unimplemented_lanes(
    kwargs: dict[str, object], error: type[Exception]
) -> None:
    with pytest.raises(error):
        CausalInfluenceConfig(**kwargs)


def test_rest_frame_slice_invariants_and_transverse_rejection() -> None:
    metric, frame, axis = validate_rest_frame_slice(METRIC, FRAME, AXIS)
    np.testing.assert_array_equal(metric, METRIC)
    np.testing.assert_array_equal(frame, FRAME)
    np.testing.assert_array_equal(axis, AXIS)
    time, distance, transverse = rest_frame_separation(
        np.array([2.0, -.4, 0.0, 0.0]), METRIC, FRAME, AXIS
    )
    assert time == 2.0
    assert distance == -.4
    assert transverse == 0.0
    with pytest.raises(ValueError, match="leaves"):
        rest_frame_separation(
            np.array([2.0, -.4, .1, 0.0]), METRIC, FRAME, AXIS
        )


def test_kernel_is_exactly_retarded_and_zero_outside_characteristic_cone() -> None:
    cfg = _config()
    distance = .75
    arrival = distance / cfg.propagation_speed
    assert retarded_telegraph_kernel_1p1(-1.0, 0.0, cfg) == 0.0
    assert retarded_telegraph_kernel_1p1(arrival * .999999, distance, cfg) == 0.0
    assert retarded_telegraph_kernel_1p1(arrival, distance, cfg) != 0.0
    assert retarded_telegraph_kernel_1p1(arrival * 1.01, distance, cfg) != 0.0


@pytest.mark.parametrize("decay", [0.0, .2, 1.5])
def test_under_and_overdamped_kernel_branches_are_finite(decay: float) -> None:
    cfg = CausalInfluenceConfig(
        tau_memory=1.0, diffusivity=.36, decay_rate=decay
    )
    value = retarded_telegraph_kernel_1p1(2.0, .3, cfg)
    assert np.isfinite(value)


def test_kernel_value_is_scalar_under_local_coordinate_change() -> None:
    cfg = _config()
    separation = np.array([2.1, .4, 0.0, 0.0])
    original = covariant_retarded_kernel_value(
        separation, METRIC, FRAME, AXIS, cfg
    )
    transform = np.array(
        [[1, .08, 0, 0], [.03, .97, 0, 0], [0, 0, 1.04, .02], [0, 0, .01, .96]],
        dtype=float,
    )
    inverse = np.linalg.inv(transform)
    transformed = covariant_retarded_kernel_value(
        inverse @ separation,
        transform.T @ METRIC @ transform,
        inverse @ FRAME,
        inverse @ AXIS,
        cfg,
    )
    assert transformed == pytest.approx(original, rel=1e-13, abs=1e-13)


def test_future_events_do_not_change_present_influence() -> None:
    cfg = _config()
    observation = np.array([2.0, .2, 0.0, 0.0])
    past = CausalSourceEvent(np.array([0.0, 0.0, 0.0, 0.0]), 1.0)
    future = CausalSourceEvent(np.array([3.0, 0.0, 0.0, 0.0]), 100.0)
    baseline = retarded_influence_from_events(
        observation, [past], METRIC, FRAME, AXIS, cfg
    )
    with_future = retarded_influence_from_events(
        observation, [past, future], METRIC, FRAME, AXIS, cfg
    )
    assert with_future == baseline


def test_causal_history_closes_exchange_and_switches_off_at_gr_limit() -> None:
    cfg = _config()
    events = [CausalSourceEvent(np.zeros(4), 1.0)]
    observation = np.array([2.0, .2, 0.0, 0.0])
    gradient = np.array([.1, -.03, .02, .04])
    open_ledger = causal_exchange_from_events(
        observation,
        events,
        METRIC,
        FRAME,
        AXIS,
        gradient,
        cfg,
        CovariantResponseConfig(epsilon_nc=.3),
    )
    assert open_ledger.full_scalar_source != 0.0
    assert open_ledger.closure_max_abs == 0.0
    closed_ledger = causal_exchange_from_events(
        observation,
        events,
        METRIC,
        FRAME,
        AXIS,
        gradient,
        cfg,
        CovariantResponseConfig(epsilon_nc=0.0),
    )
    assert closed_ledger.full_scalar_source == 0.0
    np.testing.assert_array_equal(closed_ledger.total_exchange, np.zeros(4))


def test_contract_separates_constitutive_source_from_derived_trace() -> None:
    contract = causal_nonclosed_contract()
    assert contract["source_role"] == "physical_constitutive_influence_j_phi"
    assert contract["derived_trace_role"] == "separate_observable_no_feedback"
    assert contract["derived_trace_imported"] is False
    assert contract["global_universe_closure"] == "UNRESOLVED"
    assert contract["closed_time_path_derivation"] is False
