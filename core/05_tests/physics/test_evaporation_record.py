"""Wave D9: one black hole evaporates completely in Lambda-only space - where is the record?

(a) Derivation check: closed-form lifetime with the horizon bath equals the numerical integral of
    dM / (dM/dt) built from the general D5 power and sigma A T_dS^4, at 20 random masses up to
    0.9 M_eq, rel < 1e-10; for small masses it is F0/(3 P0) of wave D5.
(b) Second route: integrating u = M^3 in time gives int M dt equal to the closed form
    -(M_eq^4/(4a)) ln(1 - x0^4), rel < 1e-9; for small x0 it is (3/4) M0 tau.
(c) Photon distance in de Sitter from the comoving integral equals (c/H)(e^{H dt} - 1); it reaches
    the horizon c/H at dt = ln2/H.
(d) Memory identity: isotropic emission leaves zero wave memory; a two-sided jet does not; a narrow
    beam converges to the beam formula at first order in the beam width.
"""

from __future__ import annotations

import importlib
from math import log

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_evaporation_record")


@pytest.mark.parametrize("seed", range(20))
def test_lifetime_closed_form_matches_numeric(seed: int) -> None:
    x0 = 10 ** np.random.default_rng(20000 + seed).uniform(-25, log(0.9, 10))
    M0 = x0 * m.M_EQ
    assert abs(m.lifetime_closed_form(M0) / m.lifetime_numeric(M0) - 1.0) < 1e-10


def test_small_mass_limit_is_d5_lifetime() -> None:
    for M0 in (1e12, m.bh.M_SUN):
        assert abs(m.lifetime_closed_form(M0) / m.bh.evaporation_time_closed_form(M0) - 1.0) < 1e-10


@pytest.mark.parametrize("x0", [1e-20, 1e-3, 0.3, 0.8])
def test_mass_time_integral_two_routes(x0: float) -> None:
    M0 = x0 * m.M_EQ
    a = m.mass_time_integral_ode(M0)
    b = m.mass_time_integral_closed_form(M0)
    assert abs(a / b - 1.0) < 1e-9
    if x0 < 1e-2:
        assert abs(b / (0.75 * M0 * m.lifetime_closed_form(M0)) - 1.0) < 1e-9


@pytest.mark.parametrize("H_dt", [1e-3, 0.3, log(2.0), 3.0])
def test_photon_distance_and_leaving_time(H_dt: float) -> None:
    dt = H_dt / m.H_L
    assert abs(m.photon_proper_distance_numeric(dt) / m.photon_proper_distance(dt) - 1.0) < 1e-11
    leave = m.record_leaves_after()
    assert abs(m.photon_proper_distance(leave) / (m.C_LIGHT / m.H_L) - 1.0) < 1e-12


def test_isotropic_emission_leaves_no_memory_jets_do() -> None:
    iso = m.memory_tensor(lambda n: 1.0 / (4 * np.pi))
    assert np.max(np.abs(iso)) < 1e-12
    jets = m.memory_tensor(lambda n: np.exp(30.0 * (n[0] ** 2 - 1.0)))
    assert jets[0, 0] > 0.05 and abs(jets[0, 0] + jets[1, 1]) < 1e-10


def test_narrow_beam_converges_to_beam_formula_first_order() -> None:
    n0 = m.unit((1.0, 0.3, 1.0))
    ref = m.beam_memory(n0)[0, 0]
    ks, errs = [100.0, 200.0, 400.0], []
    for k in ks:
        norm = 2 * np.pi * (1 - np.exp(-2 * k)) / k
        t = m.memory_tensor(lambda n, k=k, norm=norm: np.exp(k * (n @ n0 - 1.0)) / norm)
        errs.append(abs(t[0, 0] / ref - 1.0))
    orders = [log(errs[i] / errs[i + 1]) / log(ks[i + 1] / ks[i]) for i in range(2)]
    for p in orders:
        assert abs(p - 1.0) < 0.02
    assert errs[-1] < 0.02
