"""Tests for the transition-operator dimensional no-go."""
import pytest
from docs.scripts.audit import audit_topic13_transition_kernel_rate_dimension_no_go as a

@pytest.mark.parametrize("scale",[1.5,2.,3.])
def test_existing_rate_scales_as_energy_squared(scale):
    row=a.scale_witness(scale)
    assert row["measured_energy_exponent"]==pytest.approx(2.,abs=1e-10)
    assert row["operator_trace_ratio"]==pytest.approx(scale**2,rel=1e-12)
    assert row["operator_trace_ratio"]!=pytest.approx(scale)

@pytest.mark.parametrize("scale",[-1.,0.,1.])
def test_invalid_scale(scale):
    with pytest.raises(ValueError): a.scale_witness(scale)
