"""Wave B8: layers 2-3 for psi with ordinary matter as the bath (module uet_psi_matter_burn.py).

1. Known limit: the exact classical momentum-transfer cross section tends to its first-order (Born)
   form, with an error proportional to the coupling.
2. Identity through two code paths: the kinetic drag with the first-order cross section equals the
   B6 linear-response drag (Fourier route).
3. Closed dynamics: the kinetic drag built from exact orbits (no expansion in the coupling) agrees
   with B6 linear response, and the gap shrinks as the coupling shrinks.
4. Free psi waves: the Landau absorption factor for omega/k >= 1 and non-relativistic matter is
   astronomically small, and it vanishes for a static field.
5. Layer 3: tau = int M dv / F(v) equals (M/k) ln(v0/v_min) for a linear drag F = k v.
"""

from __future__ import annotations

import importlib.util
import sys
from math import log
from pathlib import Path

import pytest

pytestmark = pytest.mark.physics

_PATH = Path(__file__).resolve().parents[2] / "03_lanes" / "open_system" / "uet_psi_matter_burn.py"
_SPEC = importlib.util.spec_from_file_location("uet_psi_matter_burn", _PATH)
pm = sys.modules.setdefault("uet_psi_matter_burn", importlib.util.module_from_spec(_SPEC))
_SPEC.loader.exec_module(pm)

A, V = 1.0, 0.7


@pytest.mark.filterwarnings("ignore")
def test_exact_cross_section_tends_to_born():
    errs = [abs(pm.momentum_transfer_cross_section(0.5, u0, A) / pm.momentum_transfer_cross_section_born(0.5, u0, A) - 1)
            for u0 in (1e-1, 1e-2, 1e-3)]
    assert errs[0] > errs[1] > errs[2]
    assert errs[2] < 2e-3
    assert errs[1] / errs[2] == pytest.approx(10.0, rel=0.2)  # first order in the coupling


def test_kinetic_born_equals_b6_linear_response():
    u0 = 0.1
    lr = pm.b6.linear_response_drag(pm.gaussian_potential_k2(u0, A), V, 1.0, 1.0, 1.0, 1e-4, 40.0)
    kb = pm.kinetic_drag(lambda u: pm.momentum_transfer_cross_section_born(u, u0, A), V, 1.0, 1.0, 1.0)
    assert kb == pytest.approx(lr, rel=1e-9)


@pytest.mark.filterwarnings("ignore")
def test_exact_orbits_reproduce_linear_response():
    gaps = []
    for u0 in (1e-1, 3e-2):
        lr = pm.b6.linear_response_drag(pm.gaussian_potential_k2(u0, A), V, 1.0, 1.0, 1.0, 1e-4, 40.0)
        ke = pm.kinetic_drag(pm.tabulated_cross_section(u0, A, 1e-2, V + 9.0, 40), V, 1.0, 1.0, 1.0)
        gaps.append(abs(ke / lr - 1))
    assert gaps[0] < 2e-2
    assert gaps[1] < 3e-3
    assert gaps[1] < gaps[0]


def test_free_waves_are_not_absorbed():
    assert pm.free_wave_absorption_log(1.0, 5e-5) < -1e8
    t = 1.0
    assert pm.b6.im_density_response(0.0, 1.0, 1.0, t, 1.0) == 0.0


def test_lifetime_linear_drag():
    k, mass = 0.3, 2.0
    tau = pm.lifetime_by_integration(lambda v: k * v, mass, 5.0, 0.05)
    assert tau == pytest.approx(mass / k * log(100.0), rel=1e-10)
