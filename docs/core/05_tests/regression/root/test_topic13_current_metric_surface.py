import pytest
from docs.scripts.audit.audit_topic13_current_metric_surface import witness


@pytest.mark.parametrize("cutoff",[2.,4.,8.,24.])
def test_finite_cutoff_identity(cutoff):
    r=witness(cutoff)
    assert r["corrected_charge_residual"]<1e-12
    assert r["corrected_enthalpy_residual"]<1e-12


def test_charge_symmetry_and_boundary_not_zero():
    a=witness(2.,mu=.2); b=witness(2.,mu=-.2); zero=witness(2.,mu=0.)
    assert a["charge_surface"]==pytest.approx(-b["charge_surface"])
    assert zero["charge_density"]==0.
    assert zero["momentum_projection_ratio"]==0.
    assert a["omitted_enthalpy_surface_fraction"]>.01
