"""Independent tests for the static/confluent charged current vertex."""
from dataclasses import replace
import mpmath as mp
import numpy as np
import pytest

from docs.scripts.audit import audit_topic13_charged_static_confluent_vertex as a

CFG = a.CFG


@pytest.mark.parametrize("x,y", [(1., 1.), (1. + 1e-12, 1.), (.8, 1.), (2., .1)])
def test_confluent_divided_difference_derivative_high_precision(x, y):
    with mp.workdps(70):
        xx, yy, T = mp.mpf(x), mp.mpf(y), mp.mpf(".25")
        n = lambda z: 1 / mp.expm1(z / T)
        expected = mp.diff(n, xx, 2) / 2 if xx == yy else mp.diff(lambda z: (n(z) - n(yy)) / (z - yy), xx)
    assert float(a.divided_occupation_derivative(x, y, .25)) == pytest.approx(float(expected), rel=2e-13)


@pytest.mark.parametrize("T,mu,q", [(.1, .2, 1), (.25, .2, -1), (.5, .2, 1), (1., .2, -1)])
def test_explicit_static_vertex_matches_full_inverse_derivative(T, mu, q):
    for h in (1e-4, 5e-5, 2.5e-5):
        assert a.finite_difference_witness(T, mu, q, h=h)["relative_error"] < 2e-7


def test_each_self_energy_component_has_the_declared_vertex_sign():
    T, mu, q, h = .25, .2, 1, 2.5e-5
    row = a.static_vertex(T, mu, q, order=160)
    def components(x):
        s = a.charged.charged_self_energy(q * x, T, x, q, order=160, static=True)
        return s
    lo, hi = components(mu - h), components(mu + h)
    pairs = (("mean_mass_shift", "bath_and_response_mean"),
             ("quartic_tadpole", "bath_and_response_mean"))
    combined_fd = -1j * ((hi[pairs[0][0]] + hi[pairs[1][0]])
                         - (lo[pairs[0][0]] + lo[pairs[1][0]])) / (2 * h)
    assert row["bath_and_response_mean"] == pytest.approx(combined_fd, rel=2e-8, abs=1e-13)
    for self_key, vertex_key in (("mixed_thermal_bubble", "mixed_thermal_confluent"),
                                 ("vacuum_subtracted", "vacuum_and_counterterm")):
        fd = -1j * (hi[self_key] - lo[self_key]) / (2 * h)
        assert row[vertex_key] == pytest.approx(fd, rel=2e-7, abs=1e-13)


@pytest.mark.parametrize("T", [.1, .25, .5, 1.])
def test_static_charge_conjugation_and_zero_density(T):
    plus = a.static_vertex(T, .2, 1)
    minus = a.static_vertex(T, .2, -1)
    assert plus["total"] == pytest.approx(minus["total"], rel=1e-13)
    for q in (-1, 1):
        zero = a.static_vertex(T, 0., q)
        assert zero["total"] == pytest.approx(0j, abs=1e-14)
        assert zero["spatial_vertex_by_isotropy"] == 0


def test_zero_response_coupling_leaves_quartic_bath_only():
    cfg = replace(CFG, response_coupling=0.)
    row = a.static_vertex(cfg=cfg)
    assert row["mixed_thermal_confluent"] == 0
    assert row["vacuum_and_counterterm"] == 0
    assert row["bath_and_response_mean"] != 0


def test_cold_and_energy_scaling_limits():
    cold = a.static_vertex(T=0.)
    assert cold["bath_and_response_mean"] == 0
    assert cold["mixed_thermal_confluent"] == 0
    scale = 2.
    cfg = replace(CFG, mass_squared=CFG.mass_squared * scale**2,
                  response_mass_squared=CFG.response_mass_squared * scale**2,
                  response_coupling=CFG.response_coupling * scale)
    new = a.static_vertex(T=.25 * scale, mu=.2 * scale, cfg=cfg)
    base = a.static_vertex()
    for key in ("bare", "bath_and_response_mean", "mixed_thermal_confluent", "vacuum_and_counterterm", "total"):
        assert new[key] == pytest.approx(base[key] * scale, rel=2e-9, abs=1e-13)


def test_canonical_field_covariance():
    z, k, eps = .25, 4., .5
    cfg = replace(CFG, z=z, mass_squared=z, quartic=CFG.coupling * z * z,
                  epsilon=eps, response_kinetic=k, response_mass_squared=CFG.response_mass_sq * k,
                  response_coupling=CFG.cubic * z * np.sqrt(k / eps),
                  response_quartic=CFG.neutral_quartic * eps * k * k)
    assert a.static_vertex(cfg=cfg)["total"] == pytest.approx(a.static_vertex()["total"], rel=2e-12)


@pytest.mark.parametrize("kwargs", [{"T": -.1}, {"mu": 1.}, {"q": 0}, {"order": True}, {"order": 16}])
def test_invalid_static_domains(kwargs):
    with pytest.raises(ValueError):
        a.static_vertex(**kwargs)


def test_invalid_finite_difference_step():
    with pytest.raises(ValueError):
        a.finite_difference_witness(h=0.)
