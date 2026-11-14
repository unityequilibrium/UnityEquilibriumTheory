"""Tests for the declared retarded/advanced mixed current triangle."""
import numpy as np
import pytest
from docs.scripts.audit import audit_topic13_retarded_ra_mixed_current_vertex as a


@pytest.mark.parametrize("q",[-1,1])
def test_frozen_thermal_weights_reduce_to_matsubara_triangle(q):
    assert a.matsubara_reduction_witness(q=q)<1e-13


@pytest.mark.parametrize("q",[-1,1])
@pytest.mark.parametrize("eta",[.04,.02,.01])
def test_ra_mixed_vertex_satisfies_continued_ward(q,eta):
    row=a.ra_vertex(q=q,eta=eta)
    assert row["Ward_relative_error"]<2e-8
    assert np.linalg.norm(row["mixed_thermal"])>0
    assert np.isfinite(row["transverse_coefficient"])


def test_finite_transfer_eta_convergence():
    rows=[a.ra_vertex(eta=x) for x in (.04,.02,.01)]
    last=np.linalg.norm(rows[-1]["total"]-rows[-2]["total"])/np.linalg.norm(rows[-1]["total"])
    assert last<.02


def test_proper_zero_transfer_triangle_has_finite_limit_not_ra_pair_pinch():
    rows=a.zero_transfer_1pi_scan()
    assert rows[-1]["norm"]<2*rows[0]["norm"]
    assert abs(rows[-1]["norm"]/rows[-2]["norm"]-1)<1e-3


@pytest.mark.parametrize("kwargs",[{"T":0.},{"q":0},{"eta":0.},{"mu":1.}])
def test_invalid_ra_domains(kwargs):
    with pytest.raises(ValueError):
        a.ra_vertex(**kwargs)
