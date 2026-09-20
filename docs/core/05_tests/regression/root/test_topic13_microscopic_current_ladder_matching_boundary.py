"""Independent tests for the microscopic current/ladder matching boundary."""
from dataclasses import replace
import numpy as np
import pytest

from docs.scripts.audit import audit_topic13_microscopic_current_ladder_matching_boundary as a


@pytest.mark.parametrize("momentum", [(0., 0., 0.), (.1, 0., 0.), (.3, -.2, .4), (1., .5, -.25)])
@pytest.mark.parametrize("q", [-1, 1])
def test_tree_vertex_has_exact_on_shell_kinetic_source(momentum, q):
    row = a.tree_on_shell_source(momentum, q)
    assert row["lsz_normalized_source"] == pytest.approx(row["kinetic_source"], abs=0.)
    assert row["relative_residual"] == 0


def test_tree_source_energy_covariance():
    p = np.array([.3, -.2, .4])
    base = a.tree_on_shell_source(p, mass=1.)
    scaled = a.tree_on_shell_source(3 * p, mass=3.)
    assert scaled["tree_spatial_vertex"] == pytest.approx(3 * base["tree_spatial_vertex"])
    assert scaled["lsz_normalized_source"] == pytest.approx(base["lsz_normalized_source"])


@pytest.mark.parametrize("coefficient", [-2., -.1, .1, 1., 3.])
def test_transverse_family_changes_vertex_without_changing_ward(coefficient):
    vertex = np.array([1.2 + .3j, -.4 + .2j])
    Q = np.array([.7, -.25])
    row = a.transverse_family(vertex, Q, coefficient)
    assert row["longitudinal_change"] == pytest.approx(0j, abs=1e-15)
    assert np.linalg.norm(row["vertex"] - vertex) > 0
    assert Q @ row["vertex"] == pytest.approx(Q @ vertex, abs=1e-15)


def test_bounded_transverse_family_vanishes_at_static_point():
    for coefficient in (-2., .1, 3.):
        row = a.transverse_family(np.array([1j, 0j]), np.zeros(2), coefficient)
        assert row["static_addition_norm"] == 0
        assert row["vertex"] == pytest.approx(np.array([1j, 0j]))


def test_default_action_drift_and_explicit_bridge():
    match = a.action_parameter_match()
    assert not match["default_matches"]
    assert match["default_residuals"]["matter_quartic"] != 0
    assert match["default_residuals"]["response_coupling"] != 0
    assert match["default_residuals"]["epsilon_nc"] != 0
    assert match["explicit_bridge_matches"]
    assert all(value == 0 for value in match["matched_residuals"].values())


def test_existing_ladders_disclose_the_microscopic_gap():
    assert all(a.contract_boundary().values())


@pytest.mark.parametrize("kwargs", [{"momentum": (1., 2.)}, {"q": 0}, {"mass": 0.}])
def test_invalid_tree_source_domains(kwargs):
    with pytest.raises(ValueError):
        a.tree_on_shell_source((.1, 0., 0.), **kwargs) if "momentum" not in kwargs else a.tree_on_shell_source(**kwargs)


def test_invalid_transverse_coefficient():
    with pytest.raises(ValueError):
        a.transverse_family(np.zeros(2), np.ones(2), float("nan"))
