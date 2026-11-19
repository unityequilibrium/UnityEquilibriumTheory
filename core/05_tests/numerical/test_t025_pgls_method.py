"""Method checks for the T025 PGLS code on synthetic trees only (no AnAge or TimeTree data is read)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location(
    "t025", ROOT / "core/03_lanes/persistence/t025_flight_lifetime_energy_pgls.py")
t025 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t025)


def _balanced_newick(depth: int, height: float, prefix: str = "T") -> str:
    """Ultrametric balanced tree with 2**depth leaves and total height `height`."""
    names = iter(f"{prefix}{i}" for i in range(2 ** depth))
    step = height / depth

    def build(level: int) -> str:
        if level == depth:
            return next(names)
        return f"({build(level + 1)}:{step},{build(level + 1)}:{step})"

    return build(0) + ";"


def test_covariance_of_a_known_tree():
    paths = t025.parse_newick("((A:1,B:1)'n1':2,C:3);")
    v = t025.covariance(paths, ["A", "B", "C"])
    assert np.allclose(v, [[3, 2, 0], [2, 3, 0], [0, 0, 3]])


def test_quoted_labels_polytomy_and_shared_paths():
    paths = t025.parse_newick("((A:1,B:1,C:1)'x':1,(D:0.5,E:0.5):1.5);")
    v = t025.covariance(paths, ["A", "C", "D", "E"])
    assert np.allclose(v, [[2, 1, 0, 0], [1, 2, 0, 0], [0, 0, 2, 1.5], [0, 0, 1.5, 2]])


def test_gls_with_identity_is_ordinary_least_squares():
    rng = np.random.default_rng(1)
    x = np.column_stack([np.ones(50), rng.normal(size=50), rng.integers(0, 2, 50), rng.integers(0, 2, 50)])
    y = x @ [0.3, -0.1, 0.4, 0.2] + rng.normal(scale=0.1, size=50)
    beta, _, _ = t025.gls(x, y, np.eye(50))
    assert np.allclose(beta, np.linalg.lstsq(x, y, rcond=None)[0], rtol=1e-12, atol=1e-12)


def test_gls_interval_coverage_under_brownian_motion():
    """95 percent t-intervals must cover the true coefficient about 95 percent of the time."""
    paths = t025.parse_newick(_balanced_newick(6, 100.0))
    leaves = sorted(paths)
    v = t025.covariance(paths, leaves)
    c = np.linalg.cholesky(v)
    rng = np.random.default_rng(20261119)
    n = len(leaves)
    x = np.column_stack([np.ones(n), rng.normal(size=n), (np.arange(n) < 16).astype(float), rng.integers(0, 2, n)])
    truth = np.array([1.0, -0.1, 0.4, 0.25])
    hits = 0
    trials = 1000
    for _ in range(trials):
        y = x @ truth + 0.02 * (c @ rng.normal(size=n))
        beta, cov, _ = t025.gls(x, y, v)
        lo, hi = t025.interval(float(beta[3]), float(np.sqrt(cov[3, 3])), n - 4)
        hits += lo <= truth[3] <= hi
    assert 0.93 <= hits / trials <= 0.97


def test_clade_indicator_interval_widens_under_phylogeny():
    """A dummy that marks one whole clade rests on one contrast: PGLS must widen its interval vs OLS."""
    paths = t025.parse_newick(_balanced_newick(6, 100.0))
    leaves = sorted(paths, key=lambda s: int(s[1:]))
    v = t025.covariance(paths, leaves)
    n = len(leaves)
    rng = np.random.default_rng(3)
    clade = (np.arange(n) < 16).astype(float)
    x = np.column_stack([np.ones(n), rng.normal(size=n), clade, rng.integers(0, 2, n)])
    y = x @ [1.0, -0.1, 0.4, 0.0] + 0.02 * (np.linalg.cholesky(v) @ rng.normal(size=n))
    _, cov_pgls, _ = t025.gls(x, y, v)
    _, cov_ols, _ = t025.gls(x, y, np.eye(n))
    assert np.sqrt(cov_pgls[2, 2]) > 2 * np.sqrt(cov_ols[2, 2])


def test_pagel_lambda_recovers_the_two_limits():
    paths = t025.parse_newick(_balanced_newick(7, 100.0))
    leaves = sorted(paths)
    v = t025.covariance(paths, leaves)
    n = len(leaves)
    rng = np.random.default_rng(5)
    x = np.column_stack([np.ones(n), rng.normal(size=n)])
    fit = lambda y: t025.optimize.minimize_scalar(t025.neg_log_likelihood, bounds=(0, 1), args=(x, y, v),
                                                  method="bounded").x
    y_bm = x @ [0.5, 0.2] + 0.05 * (np.linalg.cholesky(v) @ rng.normal(size=n))
    y_iid = x @ [0.5, 0.2] + 0.5 * rng.normal(size=n)
    assert fit(y_bm) > 0.8
    assert fit(y_iid) < 0.2


@pytest.mark.parametrize("name,leaf,rule", [
    ("Homo_sapiens", "Homo_sapiens", "exact"),
    ("Cervus_elaphus", "Cervus_elaphus_atlanticus", "subspecies"),
    ("Macropus_rufus", "Osphranter_rufus", "synonym"),
    ("Sylvia_curruca", "Curruca_curruca_blythi", "synonym"),
    ("Struthio_camelus", None, "dropped"),
])
def test_placement_rules(name, leaf, rule):
    leaves = {"Homo_sapiens", "Cervus_elaphus_atlanticus", "Cervus_elaphus_barbarus", "Osphranter_rufus",
              "Curruca_curruca_curruca", "Curruca_curruca_blythi", "Struthio"}
    assert t025.place(name, leaves) == (leaf, rule)


def test_outcome_rules_match_t023_and_add_the_coverage_rule():
    assert t025.outcome((0.2, 0.4), (-0.2, 0.1), 13, 23) == "PASS"
    assert t025.outcome((0.2, 0.4), (-0.2, 0.1), 31, 23) == "INCONCLUSIVE"
    assert t025.outcome((0.2, 0.4), (-0.2, 0.1), 13, 19) == "INCONCLUSIVE"
    assert t025.outcome((0.0, 0.17), (-0.2, 0.1), 13, 23) == "FAILED"
    assert t025.outcome((0.2, 0.4), (-0.6, -0.3), 13, 23) == "FAILED"
    assert t025.outcome((0.1, 0.4), (-0.3, 0.1), 13, 23) == "INCONCLUSIVE"
