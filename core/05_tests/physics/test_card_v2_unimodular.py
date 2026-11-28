"""Physics checks for wave V2-UM (core/03_lanes/scalar_tensor/uet_card_v2_unimodular.py), draft Card v2 option (b)."""

from __future__ import annotations

import importlib
import math
import random

import numpy as np
import pytest

v2 = importlib.import_module("core.03_lanes.scalar_tensor.uet_card_v2")
ef = importlib.import_module("core.03_lanes.scalar_tensor.uet_card_v2_einstein")
um = importlib.import_module("core.03_lanes.scalar_tensor.uet_card_v2_unimodular")

pytestmark = pytest.mark.physics

STEPS = 1000


@pytest.mark.parametrize("seed", range(20))
def test_slope_from_field_space_orbit(seed: int) -> None:
    """Independent route: lam = -d ln(Lambda0 / F^2) / d sigma along the Killing orbit, with the field-space metric
    of V2-EF, for cards with a non-zero chi vacuum."""
    rng = random.Random(7100 + seed)
    card = v2.CardV2(xi_phi=rng.uniform(1e-3, 2.0), xi_chi=rng.uniform(0.0, 1.0), lam_chi=rng.uniform(0.2, 1.5),
                     alpha=rng.uniform(0.01, 0.6), beta=0.0)
    q = ef.vacuum(card, 1.0)
    h = 1e-5
    lnU = lambda s: math.log(1.0 / card.F(*(lambda x: (x[0], x[1] ** 2 + x[2] ** 2))(q * math.exp(s))) ** 2)  # noqa: E731
    dsig_ds = math.sqrt(float(q @ ef.field_metric(card, q) @ q))
    lam_num = -(lnU(h) - lnU(-h)) / (2 * h) / dsig_ds
    assert abs(lam_num - um.slope_from_card(card)) < 1e-8
    assert um.slope_from_card(card) < 4 / math.sqrt(6)


def test_slope_xi_map_and_alpha_to_zero_limit() -> None:
    for xi in (1e-4, 1e-2, 0.5, 7.0):
        assert abs(um.xi_from_slope(um.slope_from_xi(xi)) - xi) < 1e-12 * max(1, xi)
        errs = []
        for a in (1e-2 * xi, 1e-3 * xi, 1e-4 * xi):   # asymptotic once xi_chi X0 << xi_phi phi0^2
            card = v2.CardV2(xi_phi=xi, xi_chi=0.3, lam_chi=1.0, alpha=a, beta=0.0)
            errs.append(abs(um.slope_from_card(card) - um.slope_from_xi(xi)))
        assert errs[2] < errs[1] < errs[0] and errs[0] / errs[1] > 5     # error ~ alpha / lambda_chi
    with pytest.raises(ValueError):
        um.xi_from_slope(1.7)


def test_today_is_normalised() -> None:
    lam = 0.8
    A = um.solve_amplitude(lam, steps=STEPS)
    a, H2, w = um.integrate(lam, A, steps=STEPS)
    assert abs(a[-1] - 1) < 1e-12 and abs(H2[-1] - 1) < 1e-9


def test_shift_symmetry_initial_value_only_rescales_amplitude() -> None:
    lam, s0 = 1.1, 0.7
    A = um.solve_amplitude(lam, steps=STEPS)
    _, H2a, wa_ = um.integrate(lam, A, steps=STEPS)
    _, H2b, wb_ = um.integrate(lam, A * math.exp(lam * s0), steps=STEPS, sig0=s0)
    assert np.max(np.abs(wa_ - wb_)) < 1e-12 and np.max(np.abs(H2a - H2b)) < 1e-12 * np.max(H2a)


def test_lcdm_limit_through_general_path() -> None:
    a, w, _ = um.w_of_a(1e-3, steps=STEPS)
    assert np.max(np.abs(1 + w[a > 0.1])) < 1e-6


@pytest.mark.parametrize("lam", [0.15, 0.3])
def test_scherrer_sen_thawing_limit(lam: float) -> None:
    """Small slope: today's 1 + w agrees with the Scherrer & Sen (2008) closed form; the gap is O(lam^2)."""
    a, w, _ = um.w_of_a(lam, steps=STEPS)
    ss = um.scherrer_sen(um.omega_de_today(), lam)
    assert abs((1 + w[-1]) / ss - 1) < 0.01
    i = int(np.argmin(np.abs(a - 0.7)))
    # along the history: Omega_DE(a) from H2 and Omega_m
    om_a = 1 - (3 * um.OMEGA_M0 * a[i] ** -3 + 3 * um.OMEGA_R0 * a[i] ** -4) / (3 * _[i])
    assert abs((1 + w[i]) / um.scherrer_sen(om_a, lam) - 1) < 0.02


def test_scherrer_sen_gap_shrinks_with_slope() -> None:
    gaps = []
    for lam in (0.8, 0.4, 0.2):
        a, w, _ = um.w_of_a(lam, steps=STEPS)
        gaps.append(abs((1 + w[-1]) / um.scherrer_sen(um.omega_de_today(), lam) - 1))
    assert gaps[0] > gaps[1] > gaps[2]
    assert 2.5 < gaps[0] / gaps[1] < 6 and 2.5 < gaps[1] / gaps[2] < 6     # ~ lam^2


def test_rk4_convergence_order() -> None:
    lam = 1.2
    A = um.solve_amplitude(lam, steps=4000)
    vals = [um.integrate(lam, A, steps=n)[2][-1] for n in (100, 200, 400)]
    ref = um.integrate(lam, A, steps=6400)[2][-1]
    e = [abs(v - ref) for v in vals]
    order = math.log2(e[0] / e[1]), math.log2(e[1] / e[2])
    assert all(3.5 < o < 4.5 for o in order), order


def test_cpl_direction_is_locked() -> None:
    """One parameter: wa / (1 + w0) stays between -1.55 and -1.25 for every xi_phi (result 3)."""
    for xi in (1e-3, 0.03, 0.3, 10.0):
        a, w, _ = um.w_of_a(um.slope_from_xi(xi), steps=STEPS)
        w0, wa = um.cpl_fit(a, w)
        assert -1.55 < wa / (1 + w0) < -1.25
