"""Wave B6: the psi friction derived from the parent action (module uet_portal_drag_derived.py).

1. Known limit through the general code path: the linear-response drag with the gravitational
   potential equals Chandrasekhar's dynamical friction at every speed (slow, comparable, fast).
2. Physical identity: Im chi_nn vanishes at omega = 0 and is odd in omega (no friction on a static or
   uniform field; dissipation, not gain).
3. Derived relation: the low-frequency limit of alpha_c^2 Im chi / omega equals friction_coefficient,
   which falls as 1/k (Gamma is not a constant).
4. Identity: with m_psi -> 0 the portal drag is alpha^2 times the gravitational drag; a finite range
   only lowers it.
5. Units: portal_alpha reproduces the T005 statement that g_c = 5.12e-10 eV is alpha = 1 for nucleons.
"""

from __future__ import annotations

import importlib.util
from math import log
from pathlib import Path

import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "open_system" / "uet_portal_drag_derived.py"
_SPEC = importlib.util.spec_from_file_location("uet_portal_drag_derived", _PATH)
dd = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(dd)

M_BODY = 1.8982e27
N_GAS = 2.6e5
MP = dd.PROTON_MASS_KG
SIGMA = 2.0e4
K_MIN, K_MAX = 1.0 / 7.8e11, 1.0 / 7.1492e7


@pytest.mark.parametrize("v", [2.0e3, 3.0e4, 4.0e5])
def test_linear_response_reproduces_chandrasekhar(v):
    f_lr = dd.linear_response_drag(dd.gravity_potential_k2(M_BODY, MP), v, N_GAS, MP, SIGMA, K_MIN, K_MAX)
    f_ch = dd.chandrasekhar_drag(M_BODY, N_GAS * MP, v, SIGMA, log(K_MAX / K_MIN))
    assert f_lr == pytest.approx(f_ch, rel=1e-6)


def test_density_response_is_dissipative_and_vanishes_static():
    t = MP * SIGMA**2
    assert dd.im_density_response(0.0, 1e-6, N_GAS, t, SIGMA) == 0.0
    a = dd.im_density_response(1e-3, 1e-6, N_GAS, t, SIGMA)
    assert a > 0.0
    assert dd.im_density_response(-1e-3, 1e-6, N_GAS, t, SIGMA) == pytest.approx(-a)


@pytest.mark.parametrize("k", [1e-9, 1e-7])
def test_friction_is_low_frequency_limit_and_scales_as_inverse_k(k):
    t, alpha_c = MP * SIGMA**2, 3.0
    omega = 1e-6 * k * SIGMA
    limit = alpha_c**2 * dd.im_density_response(omega, k, N_GAS, t, SIGMA) / omega
    gamma_k = dd.friction_coefficient(k, alpha_c, N_GAS, t, SIGMA)
    assert limit == pytest.approx(gamma_k, rel=1e-9)
    assert dd.friction_coefficient(10 * k, alpha_c, N_GAS, t, SIGMA) == pytest.approx(gamma_k / 10, rel=1e-12)


def test_portal_drag_is_alpha_squared_gravity():
    v, alpha = 4.0e5, 6e-11
    grav = dd.linear_response_drag(dd.gravity_potential_k2(M_BODY, MP), v, N_GAS, MP, SIGMA, K_MIN, K_MAX)
    massless = dd.linear_response_drag(dd.portal_potential_k2(M_BODY, MP, alpha, 0.0), v, N_GAS, MP, SIGMA, K_MIN, K_MAX)
    ranged = dd.linear_response_drag(dd.portal_potential_k2(M_BODY, MP, alpha, 1.0 / 1e9), v, N_GAS, MP, SIGMA, K_MIN, K_MAX)
    assert massless == pytest.approx(alpha**2 * grav, rel=1e-6)
    assert ranged < massless


def test_alpha_unit_matches_t005():
    assert dd.portal_alpha(5.12e-10) == pytest.approx(1.0, rel=0.02)
