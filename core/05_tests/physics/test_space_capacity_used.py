"""Wave D12: how much of space's capacity to take disorder is already used?

(a) Derivation check: entropy density from the Bose-Einstein and Fermi-Dirac energy integrals equals
    (2 pi^2/45) g k (kT/hbar c)^3 (times 7/8 for fermions) at 20 random temperatures, rel < 1e-10.
(b) Second route: today's event-horizon radius from the integral in a equals the integral in t with
    the closed-form a(t) of wave D6, rel < 1e-10.
(c) Known limit with convergence order: R_eh(a) H_L / c -> 1 as a grows, with deviation ~ a^-3.
(d) Identity: the entropy of one hole holding mass M, over S_dS, is (2 G M H_L / c^3)^2 at random
    masses; with all matter inside the horizon it equals (Om/OL)^2 (R_eh H_L/c)^6.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_space_capacity_used")


@pytest.mark.parametrize("seed", range(20))
def test_entropy_density_integrals_match_closed_form(seed: int) -> None:
    T = 10 ** np.random.default_rng(22000 + seed).uniform(-1, 4)
    boson = m.entropy_density_numeric(T, 2.0, fermion=False)
    fermion = m.entropy_density_numeric(T, 6.0, fermion=True)
    assert abs(boson / m.boson_entropy_density_closed_form(T, 2.0) - 1.0) < 1e-10
    assert abs(fermion / (7.0 / 8.0 * m.boson_entropy_density_closed_form(T, 6.0)) - 1.0) < 1e-10


def test_neutrino_counting_in_g_s() -> None:
    T_nu = (4.0 / 11.0) ** (1.0 / 3.0) * m.T0
    total = m.entropy_density_numeric(m.T0, 2.0, False) + m.entropy_density_numeric(T_nu, 6.0, True)
    assert abs(total / m.radiation_entropy_density() - 1.0) < 1e-10
    assert abs(m.G_S - 3.909090909) < 1e-8


@pytest.mark.parametrize("a0", [0.5, 1.0, 2.0, 5.0])
def test_event_horizon_two_routes(a0: float) -> None:
    assert abs(m.event_horizon_radius(a0) / m.event_horizon_radius_time(a0) - 1.0) < 1e-10


def test_event_horizon_tends_to_de_sitter_radius_order_three() -> None:
    a_s = [4.0, 8.0, 16.0]
    devs = [1.0 - m.event_horizon_radius(a) * m.H_L / m.C for a in a_s]
    orders = [log(devs[i] / devs[i + 1]) / log(a_s[i + 1] / a_s[i]) for i in range(2)]
    for o in orders:
        assert abs(o - 3.0) < 0.05
    assert 0.94 < m.event_horizon_radius() * m.H_L / m.C < 0.96


@pytest.mark.parametrize("seed", range(10))
def test_one_hole_over_capacity_identity(seed: int) -> None:
    M = 10 ** np.random.default_rng(22100 + seed).uniform(30, 53)
    ratio = m.hole_entropy(M) / m.cd.de_sitter_entropy()
    assert abs(ratio / (2 * m.G * M * m.H_L / m.C ** 3) ** 2 - 1.0) < 1e-12


def test_budget_numbers() -> None:
    b = m.budget()
    assert abs(b["fraction_all_matter_one_hole"] / m.matter_ceiling_closed_form() - 1.0) < 1e-12
    assert 0.15 < b["fraction_all_matter_one_hole"] < 0.17
    assert 1e-35 < b["fraction_radiation"] < 1e-33
    assert 1e-21 < b["fraction_smbh_illustrative"] < 1e-19
