import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_direction_moments import candidate14,moments,_DIRECTIONS


def test_six_axis_covers_second_not_fourth_moments():
    r=moments(_DIRECTIONS,np.full(6,1/6))
    np.testing.assert_allclose(r["second_moment"],np.eye(3)/3)
    assert r["quadrupole_rank"]==2
    assert r["shear_xy_source_norm"]==0
    assert r["x4"]==pytest.approx(1/3)


def test_candidate_covers_fourth_but_not_sixth():
    r=moments(*candidate14())
    assert r["quadrupole_rank"]==5
    assert r["x4"]==pytest.approx(1/5)
    assert r["x2y2"]==pytest.approx(1/15)
    assert r["fourth_order_gram_error"]<1.e-12
    assert r["x6"]!=pytest.approx(1/7)


def test_positive_weights_must_be_normalized():
    d,w=candidate14()
    with pytest.raises(ValueError):
        moments(d,w*2)
