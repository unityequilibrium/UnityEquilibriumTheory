"""Wave D17: frame dragging inside a slowly rotating shell (Mach's question).

(a) Derivation check: integrating the slow-rotation equation through a shell of finite thickness and
    extrapolating to zero thickness gives the Brill-Cohen closed form at 10 random compactnesses, rel < 1e-7.
(b) Convergence test: the finite-thickness error falls with order 1 in the thickness.
(c) Known limits with convergence order: weak field omega_in/Omega -> (4/3) G M/(R c^2) with relative
    deviation of order 1 in G M/(R c^2) (numeric and closed form); towards the shell's horizon
    1 - omega_in/Omega -> 0 with order 1 in (1 - 2 G M/(R c^2)) (d f/d alpha = 0 at alpha = 1).
(d) Identity: the Hubble sphere of density omega rho_crit has G M/(R c^2) = omega / 2 (Planck 2018 H0).
"""

from __future__ import annotations

import importlib
from math import log, pi

import numpy as np
import pytest

pytestmark = pytest.mark.physics

m = importlib.import_module("docs.core.03_lanes.persistence.uet_mach_frame_dragging")
cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")


@pytest.mark.parametrize("seed", range(10))
def test_numeric_shell_matches_brill_cohen(seed: int) -> None:
    x = np.random.default_rng(27000 + seed).uniform(0.005, 0.42)
    assert abs(m.dragging_thin_limit(x) / m.dragging_closed_form(x) - 1.0) < 1e-7


def test_thickness_convergence_order_one() -> None:
    x = 0.2
    exact = m.dragging_closed_form(x)
    ws = [0.02, 0.01, 0.005]
    errs = [abs(m.dragging_numeric(x, w) - exact) for w in ws]
    orders = [log(errs[i] / errs[i + 1]) / log(ws[i] / ws[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.05


def test_weak_field_limit_order_one() -> None:
    xs = [1e-2, 1e-3, 1e-4]
    devs = [abs(m.dragging_closed_form(x) / m.dragging_weak_field(x) - 1.0) for x in xs]
    orders = [log(devs[i] / devs[i + 1]) / log(xs[i] / xs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01
    # the general code path agrees in the weak field
    assert abs(m.dragging_thin_limit(1e-3) / m.dragging_weak_field(1e-3) - 1.0) < 2e-3


def test_full_dragging_at_the_horizon_order_one() -> None:
    gs = [1e-4, 1e-6, 1e-8]  # g = 1 - 2 G M/(R c^2)
    devs = [1.0 - m.dragging_closed_form((1.0 - g) / 2.0) for g in gs]
    orders = [log(devs[i] / devs[i + 1]) / log(gs[i] / gs[i + 1]) for i in range(2)]
    for o in orders:
        assert abs(o - 1.0) < 0.01
    xs = np.linspace(0.01, 0.49, 25)
    d = [m.dragging_closed_form(x) for x in xs]
    assert np.all(np.diff(d) > 0) and d[-1] < 1.0


def test_hubble_sphere_compactness_identity() -> None:
    R = cd.C_LIGHT / cd.H0
    rho_c = 3.0 * cd.H0 ** 2 / (8.0 * pi * cd.G_NEWTON)
    for omega in (cd.OMEGA_M, 1.0):
        M = omega * rho_c * 4.0 * pi / 3.0 * R ** 3
        assert abs(cd.G_NEWTON * M / (R * cd.C_LIGHT ** 2) / m.hubble_sphere_compactness(omega) - 1.0) < 1e-12


def test_illustration_numbers() -> None:
    out = m.illustration()
    assert abs(out["compactness_hubble_matter"] - 0.1575) < 1e-12
    assert 0.22 < out["drag_hubble_matter_shell"] < 0.23
