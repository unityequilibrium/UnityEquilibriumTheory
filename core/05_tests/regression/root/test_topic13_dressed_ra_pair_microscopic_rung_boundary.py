"""Tests for dressed RA-pair normalization and microscopic rung boundary."""
import pytest
from docs.scripts.audit import audit_topic13_dressed_ra_pair_microscopic_rung_boundary as a

@pytest.mark.parametrize("E",[.7,1.,2.])
@pytest.mark.parametrize("width",[.01,.05,.2])
def test_ra_pair_integral(E,width):
    assert a.ra_pair_energy_integral(E,width)["relative_error"]<1e-10

@pytest.mark.parametrize("q",[-1,1])
@pytest.mark.parametrize("width",[.02,.1])
def test_dressed_current_source_matches_kinetic(q,width):
    assert a.dressed_current_source_match(.3,.5,.25,.2,q,width)["relative_error"]<1e-13

def test_legacy_rung_is_not_production_action_rung():
    rows=a.rung_comparison()
    assert sorted(r["contact_to_legacy_ratio"] for r in rows)==[8.,16.]
    assert all(r["full_to_legacy_ratio"]!=r["contact_to_legacy_ratio"] for r in rows)

@pytest.mark.parametrize("args",[(0.,.1), (1.,0.)])
def test_invalid_pair(args):
    with pytest.raises(ValueError): a.ra_pair_energy_integral(*args)
