from __future__ import annotations

import numpy as np

from docs.core.uet_matter_space_characteristic import characteristic_cone_dt, characteristic_cone_step
from docs.core.uet_matter_space_finite_cone import FiniteConeCConfig, FiniteConeCState
from docs.core.uet_matter_space_observable import (
    MATTER_SPACE_OBSERVABLE_OPERATOR_MODE,
    normalized_matter_space_observable,
)


def _config() -> FiniteConeCConfig:
    return FiniteConeCConfig(
        a_C=0.0, b_C=0.1, kappa_C=1.0, mobility_C=1.0, tau_C=1.0,
        a_space=0.0, b_space=0.1, kappa_space=1.0, mobility_space=1.0,
        tau_space=1.0, coupling_g=0.1, boundary_condition="periodic",
        unit_lane="normalized", ledger_tolerance=1e-4,
    )


def test_normalized_observable_has_explicit_nonphysical_boundary() -> None:
    n = 41
    center = n // 2
    state = FiniteConeCState(
        np.eye(1, n, center, dtype=float).reshape(-1) * 0.1,
        np.zeros(n), np.zeros(n), np.zeros(n),
    )
    result = characteristic_cone_step(state, characteristic_cone_dt(0.1, _config()), 0.1, _config())
    observed = normalized_matter_space_observable(result, dx=0.1, center_index=center)
    assert observed["operator_mode"] == MATTER_SPACE_OBSERVABLE_OPERATOR_MODE
    assert observed["unit_lane"] == "normalized"
    assert observed["mass_density_mapping"] == "NOT_DEFINED"
    assert observed["physical_energy_mapping"] == "NOT_DEFINED"
    assert observed["trace_backreaction"] is False
    assert np.all(np.isfinite(observed["C_profile"]))


def test_observable_does_not_change_step_inputs() -> None:
    config = _config()
    n = 41
    center = n // 2
    state = FiniteConeCState(
        np.eye(1, n, center, dtype=float).reshape(-1) * 0.1,
        np.zeros(n), np.zeros(n), np.zeros(n),
    )
    dt = characteristic_cone_dt(0.1, config)
    before = state.C.copy()
    result = characteristic_cone_step(state, dt, 0.1, config)
    _ = normalized_matter_space_observable(result, dx=0.1, center_index=center)
    np.testing.assert_array_equal(state.C, before)
