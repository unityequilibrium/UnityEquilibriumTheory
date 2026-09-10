import pytest
from docs.scripts.audit.audit_topic13_entropy_force_convention import witness


@pytest.mark.parametrize("temperature", [.22, .5, 1., 2.])
def test_current_divergence_and_temperature_factor(temperature):
    row = witness(temperature)
    assert row["reported_over_divergence"] == pytest.approx(1.)
    assert row["reported_entropy_production"] == pytest.approx(row["entropy_current_divergence"])
    errors = [r["relative_error"] for r in row["direct_current_difference"]]
    assert errors[2] < errors[1] < errors[0]
    assert errors[0]/errors[1] == pytest.approx(4., rel=.001)
