import numpy as np
import pytest

from docs.scripts.audit.audit_topic13_phase_space_measure import audit_case, rule


def test_product_moments():
    row = audit_case(8, 6, 16)
    assert row["independent_radial_pairs"] == 64
    assert row["weights_positive"]
    for key, value in row["moments"].items():
        if key != "manufactured_exponential":
            assert value["absolute_error"] < 1e-13


def test_nonpolynomial_refinement():
    errors = [audit_case(n, 6, 16)["exponential_relative_error"] for n in (4, 8, 16)]
    assert errors[2] < errors[1] < errors[0]
    assert errors[2] < 1e-11


def test_independent_pairs_and_validation():
    x, w, c, a, phi = rule(8, 6, 16)
    assert len(set((float(p), float(q)) for p in x for q in x)) == 64
    assert np.any(c < 0) and np.any(c > 0)
    assert abs(a.sum()-1) < 1e-14
    with pytest.raises(ValueError):
        rule(True, 6, 16)
