"""UET engine (core/engine): its entry points reproduce the derived modules and known physics.

1. Identity through two code paths: the engine's portal alpha (fifth-force module) equals
   g_c^2 / (16 pi G m^4) computed in the SI-1 module.
2. Known limits of the two-body potential: Newtonian for r >> lambda, (1 + alpha) Newtonian for r << lambda.
3. Known limit: DEF beta0 = -2 xi_c and PPN gamma = 1 at psi0 = 0 through the general Jordan-frame map.
4. Layer 2 -> 3: closed-form lifetime equals direct integration of dF/dt = -P(F) for n = 0, 1, 7/2.
5. Layer 3 against an independent dynamical solution: a two-member decay chain integrated as ODEs
   reaches N_d/N_p = lambda_p/(lambda_d - lambda_p), which the abundance law N = b tau gives as
   tau_d/tau_p when lambda_p << lambda_d.
6. Identity: bits written per second agrees with the B8 module.
"""

from __future__ import annotations

import sys
from math import log
from pathlib import Path

import pytest
from scipy.integrate import solve_ivp

pytestmark = pytest.mark.physics

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from core.engine import layer1, layer23  # noqa: E402
from core.engine._load import load  # noqa: E402


def test_portal_alpha_two_paths():
    si = load("03_lanes/open_system/uet_si_bose_fluid.py")
    for g_c in (1e-12, 5.1e-10, 3e-8):
        p = layer1.CanonicalParameters(m_psi_ev=1e-3, g_c_ev=g_c, xi_c=0.0)
        assert layer1.portal_alpha(p) == pytest.approx(si.portal_alpha(g_c), rel=1e-3)


def test_two_body_potential_limits():
    p = layer1.CanonicalParameters(m_psi_ev=5.1e-3, g_c_ev=5.1e-10, xi_c=0.0)
    lam, alpha = layer1.yukawa_range_m(p), layer1.portal_alpha(p)
    newton = lambda r: -6.67430e-11 * 2.0 * 3.0 / r  # noqa: E731
    assert layer1.two_body_potential_si(1e3 * lam, 2.0, 3.0, p) / newton(1e3 * lam) == pytest.approx(1.0, abs=1e-12)
    assert layer1.two_body_potential_si(1e-4 * lam, 2.0, 3.0, p) / newton(1e-4 * lam) == pytest.approx(1.0 + alpha, rel=1e-4)


def test_def_limit():
    for xi_c in (0.5, 2.0, 3.7):
        d = layer1.def_parameters(layer1.CanonicalParameters(m_psi_ev=1e-20, g_c_ev=0.0, xi_c=xi_c))
        assert d["beta0"] == pytest.approx(-2.0 * xi_c, rel=1e-12)
        assert d["alpha0"] == 0.0
        assert d["gamma_ppn_minus_1"] == 0.0


@pytest.mark.parametrize("n", [0.0, 1.0, 3.5])
def test_lifetime_closed_form_matches_integration(n):
    f0, p0, f_min = 10.0, 2.0, 5.0
    closed = layer23.lifetime(f0, p0, n, f_min)
    numeric = layer23.lifetime_numerical(lambda f: layer23.burn_power(f, f0, p0, n), f0, f_min, 1e-3)
    assert numeric == pytest.approx(closed, rel=1e-6)


def test_abundance_law_matches_decay_chain_dynamics():
    lam_p, lam_d = 1e-4, 1.0
    sol = solve_ivp(lambda t, y: [-lam_p * y[0], lam_p * y[0] - lam_d * y[1]], (0.0, 40.0), [1.0, 0.0],
                    rtol=1e-11, atol=1e-14)
    ratio_dynamics = sol.y[1, -1] / sol.y[0, -1]
    assert ratio_dynamics == pytest.approx(lam_p / (lam_d - lam_p), rel=1e-6)
    ratio_engine = layer23.abundance_ratio(1.0 / lam_d, 1.0 / lam_p)
    assert ratio_engine == pytest.approx(ratio_dynamics, rel=2e-4)


@pytest.mark.parametrize("n", [2.0, 3.5, 5.0])
def test_cooling_luminosity_function_from_engine_lifetimes(n):
    """Known limit: the faint-end slope from engine lifetimes tends to 0.4 (n - 1)/n (Mestel-type cooling)."""
    pilot = load("03_lanes/persistence/engine_pilot_stars.py")
    closed = layer23.luminosity_function_slope_per_mag(n)
    errs = [abs(pilot.wd_slope_numerical(n, l_ratio) / closed - 1.0) for l_ratio in (1e-2, 1e-4, 1e-8)]
    assert errs[0] > errs[1] > errs[2]
    assert errs[2] < 1e-4


def test_bit_rate_two_paths():
    b8 = load("03_lanes/open_system/uet_psi_matter_burn.py")
    assert layer23.bit_rate(9.3e-12, 1.2e5) == pytest.approx(b8.bits_per_second(9.3e-12, 1.2e5), rel=1e-6)
    assert layer23.bits_written(1.0, 300.0) == pytest.approx(1.0 / (1.380649e-23 * 300.0 * log(2.0)), rel=1e-12)
