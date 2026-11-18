"""Wave SI-1: parent-action matter sector in SI units (module uet_si_bose_fluid.py).

1. Known limit through the general code path: the relativistic O(2) sound speed tends to the
   Bogoliubov speed sqrt(g n / m) with g = lam / (2 m^2), with an error proportional to g n / m.
2. Unit identity: the Bogoliubov speed computed in natural units (eV) and converted with hbar, c
   equals the speed computed directly in SI.
3. Identity: the contact strength of the portal Yukawa potential, by quadrature, equals
   -4 pi alpha G m^2 / m_psi^2, and delta_a = M int V / (4 pi) for an atom of mass M = A m_N.
"""

from __future__ import annotations

import importlib.util
import sys
from math import pi
from pathlib import Path

import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "open_system" / "uet_si_bose_fluid.py"
_SPEC = importlib.util.spec_from_file_location("uet_si_bose_fluid", _PATH)
sb = sys.modules.setdefault("uet_si_bose_fluid", importlib.util.module_from_spec(_SPEC))
_SPEC.loader.exec_module(sb)

C_SI = 299792458.0


def test_relativistic_sound_speed_tends_to_bogoliubov():
    m, lam = 1.0, 0.5
    errs, small = [], []
    for eps in (1e-2, 1e-3, 1e-4):
        n, c_rel = sb.relativistic_state(m * (1.0 + eps), m, lam)
        c_bog = sb.bogoliubov_speed_natural(n, m, lam)
        errs.append(abs(c_rel / c_bog - 1.0))
        small.append(sb.gp_coupling(lam, m) * n / m)
    assert errs[0] > errs[1] > errs[2]
    assert errs[2] < 1e-3
    assert errs[1] / errs[2] == pytest.approx(10.0, rel=0.05)  # first order in g n / m
    assert errs[2] / small[2] == pytest.approx(errs[1] / small[1], rel=0.05)


def test_natural_and_si_routes_agree():
    a, n = 100.4 * sb.BOHR_M, 1e20
    mass_ev = sb.MASS_EV["Rb87"]
    lam = sb.lam_from_scattering_length(a, mass_ev)
    n_ev3 = n * sb.HBAR_C_EV_M**3
    c_nat = sb.bogoliubov_speed_natural(n_ev3, mass_ev, lam) * C_SI
    c_si = sb.bogoliubov_speed_si(n, a, mass_ev * sb.EV_J / C_SI**2)
    assert c_nat == pytest.approx(c_si, rel=1e-9)
    assert 1e-3 < c_si < 1e-2  # mm/s scale, as for dilute alkali condensates


def test_yukawa_contact_strength_and_scattering_length_shift():
    alpha, m_psi = 0.7, 2.0
    m_n = 1.3
    num = sb.yukawa_contact_strength(alpha, m_n, m_psi)
    assert num == pytest.approx(-4.0 * pi * alpha * sb.G_NAT_EV2 * m_n**2 / m_psi**2, rel=1e-10)
    big_a = 4
    atom = big_a * m_n
    g_atom = big_a**2 * num  # each nucleon pair contributes
    da_from_g = atom * g_atom / (4.0 * pi) * sb.HBAR_C_EV_M
    assert sb.scattering_length_shift_m(alpha, atom, m_psi) == pytest.approx(da_from_g, rel=1e-10)
