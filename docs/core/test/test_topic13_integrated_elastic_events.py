import numpy as np
import pytest
from docs.scripts.audit.audit_topic13_integrated_elastic_events import integrate


def test_event_count_and_charge_conjugation():
    plus = integrate(4, 4, mu=.2, cutoff=8.)
    minus = integrate(4, 4, mu=-.2, cutoff=8.)
    a = np.array(plus["ordered_tag_density"])
    b = np.array(minus["ordered_tag_density"])
    assert np.all(a > 0)
    assert plus["event_density"] == pytest.approx(a.sum()/2)
    np.testing.assert_allclose(a, b[::-1,::-1], rtol=1e-12)
    assert plus["detailed_balance_relative_error"] < 1e-10


def test_radial_order_validation():
    with pytest.raises(ValueError):
        integrate(True, 4)
