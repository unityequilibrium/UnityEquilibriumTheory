import numpy as np
import pytest

from docs.core.uet_matter_space_finite_cone import (
    FINITE_CONE_C_OPERATOR_MODE,
    FiniteConeCConfig,
    FiniteConeCState,
    finite_cone_c_free_energy,
    finite_cone_c_step,
)
from docs.core.uet_master_equation import UETMasterEquation


def make_state(n=24):
    x = np.arange(n, dtype=float)
    return FiniteConeCState(
        C=0.1 + 0.03 * np.sin(2.0 * np.pi * x / n),
        C_rate=0.02 * np.cos(2.0 * np.pi * x / n),
        space_response=0.01 * np.sin(2.0 * np.pi * x / n),
        space_rate=np.zeros(n),
    )


def make_config():
    return FiniteConeCConfig(
        a_C=1.0,
        b_C=1.0,
        kappa_C=0.2,
        mobility_C=1.0,
        tau_C=1.0,
        a_space=1.0,
        b_space=1.0,
        kappa_space=0.2,
        mobility_space=1.0,
        tau_space=1.0,
        coupling_g=0.1,
        c_limit=1.0,
    )


def test_finite_cone_lane_has_distinct_nonconserved_contract():
    config = make_config()
    assert config.matter_speed == pytest.approx(np.sqrt(0.2))
    state = make_state()
    result = finite_cone_c_step(state, 1.0e-4, 1.0, config)
    assert result.diagnostics["operator_mode"] == FINITE_CONE_C_OPERATOR_MODE
    assert result.energy_ledger["mass_conservation"].startswith("NOT_APPLICABLE")
    assert result.diagnostics["C_lane"] == "C_telegraph_candidate"


def test_finite_cone_step_closes_local_ledger_without_trace():
    state = make_state()
    config = make_config()
    result = finite_cone_c_step(state, 1.0e-4, 1.0, config)
    assert result.trace_observable is None
    assert result.diagnostics["trace_backreaction"] is False
    assert result.energy_ledger["ledger_gate"] == "PASS"
    assert result.diagnostics["field_clipping_applied"] is False
    assert result.diagnostics["parameter_fitting_applied"] is False


def test_trace_is_optional_and_does_not_change_physical_step():
    state = make_state()
    config = make_config()
    plain = finite_cone_c_step(state, 1.0e-4, 1.0, config)
    traced = finite_cone_c_step(
        state,
        1.0e-4,
        1.0,
        config,
        trace_history=[],
        trace_config=__import__("docs.core.uet_trace", fromlist=["TraceKernelConfig"]).TraceKernelConfig(
            D_trace=0.1,
            tau_trace=0.1,
            source_normalization="normalized",
            boundary_condition="periodic",
        ),
    )
    np.testing.assert_allclose(plain.C, traced.C, atol=1.0e-14, rtol=0.0)
    np.testing.assert_allclose(plain.V, traced.V, atol=1.0e-14, rtol=0.0)
    np.testing.assert_allclose(plain.space_response, traced.space_response, atol=1.0e-14, rtol=0.0)
    assert traced.trace_observable is not None


def test_master_equation_compatibility_adapter_preserves_mode_boundary():
    engine = UETMasterEquation()
    config = make_config()
    result = engine.step(
        np.zeros(24),
        dt=1.0e-4,
        dx=1.0,
        operator_mode=FINITE_CONE_C_OPERATOR_MODE,
        finite_cone_c_config=config,
    )
    assert result.diagnostics["operator_mode"] == FINITE_CONE_C_OPERATOR_MODE
    with pytest.raises(ValueError, match="ambiguous legacy inputs"):
        engine.step(
            result.C,
            dt=1.0e-4,
            dx=1.0,
            I=np.zeros(24),
            operator_mode=FINITE_CONE_C_OPERATOR_MODE,
            finite_cone_c_config=config,
        )


def test_config_rejects_s_i_and_superluminal_declared_limit():
    with pytest.raises(NotImplementedError):
        FiniteConeCConfig(unit_lane="SI")
    with pytest.raises(ValueError, match="speed exceeds"):
        FiniteConeCConfig(kappa_C=4.0, c_limit=1.0)