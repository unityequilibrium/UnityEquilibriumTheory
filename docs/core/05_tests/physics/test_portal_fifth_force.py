"""Wave B1b: the portal fifth force when chi is ordinary matter (author decision 2026-11-10).

(a) Non-relativistic matter: a rotating O(2) mode that solves the implemented matter
    equation carries rho = m_chi^2 X up to O(lambda X / m_chi^2) (known limit, order 2 in A).
(b) The static psi equation sourced by a uniform sphere, solved by finite differences,
    converges to the analytic exterior field used for the Yukawa strength.
(c) The ratio of the portal potential to Newtonian gravity at m_psi r -> 0 equals
    alpha = g_c^2 / (2 kappa m_chi^4).
"""

from __future__ import annotations

import importlib
import math

import numpy as np
import pytest
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from docs.core.uet_covariant_matter import CovariantMatterConfig, coupled_matter_stress_tensor, matter_eom_residual
from docs.core.uet_covariant_response import CovariantResponseConfig

pytestmark = pytest.mark.physics

ff = importlib.import_module("docs.core.03_lanes.scalar_tensor.uet_portal_fifth_force")
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def _rotating_mode_ratio(amplitude: float, m2: float = 0.8, lam: float = 0.5) -> float:
    response = CovariantResponseConfig(epsilon_nc=0.5, einstein_coupling=1.0, cosmological_constant=0.0,
                                       phi_equilibrium=0.0, response_kinetic=1.0, response_mass_sq=1.0,
                                       response_quartic=1.0, curvature_coupling=0.0, equilibrium_density=0.0)
    matter = CovariantMatterConfig(matter_kinetic=1.0, matter_mass_sq=m2, matter_quartic=lam, response_coupling=0.0)
    omega = math.sqrt(m2 + lam * amplitude**2)  # frequency that solves the matter equation
    t = 0.37
    chi = amplitude * np.array([math.cos(omega * t), math.sin(omega * t)])
    dchi_dt = amplitude * omega * np.array([-math.sin(omega * t), math.cos(omega * t)])
    box = omega**2 * chi  # box = -d_t^2 in (-,+,+,+)
    assert np.max(np.abs(matter_eom_residual(box, chi, 0.0, response, matter))) < 1e-12
    grads = np.array([[dchi_dt[0], 0, 0, 0], [dchi_dt[1], 0, 0, 0]])
    rho = coupled_matter_stress_tensor(ETA, None, chi, grads, 0.0, response, matter)[0, 0]
    X = float(chi @ chi)
    return ff.nonrelativistic_x(rho, m2) / X


def test_nonrelativistic_matter_carries_x_equal_rho_over_m2() -> None:
    errors = [abs(_rotating_mode_ratio(a) - 1.0) for a in (0.1, 0.05, 0.025)]
    orders = [math.log2(errors[i] / errors[i + 1]) for i in range(2)]
    assert errors[-1] < 1e-3
    assert all(1.9 < o < 2.1 for o in orders), (errors, orders)


def _solve_sphere(n: int, m_psi: float, radius: float, source: float, r_max: float) -> tuple[np.ndarray, np.ndarray]:
    """Solve u'' - m^2 u = -source * r * rho(r), u = r psi, u(0) = 0, u(r_max) = 0; grid node at r = radius."""
    r = np.linspace(0.0, r_max, n + 1)
    h = r[1] - r[0]
    rho = np.where(r <= radius + 1e-12, 1.0, 0.0)
    rho[np.isclose(r, radius)] = 0.5  # cell-average at the surface keeps second order
    inner = r[1:-1]
    a = diags([np.ones(n - 2), -(2.0 + (m_psi * h) ** 2) * np.ones(n - 1), np.ones(n - 2)], [-1, 0, 1], format="csc")
    u = spsolve(a, -source * inner * rho[1:-1] * h * h)
    return inner, u / inner


@pytest.mark.parametrize("m_psi", [0.3, 1.5])
def test_static_sphere_field_converges_to_analytic_exterior(m_psi: float) -> None:
    radius, g_c, m_chi2, r_max = 1.0, 0.7, 0.9, 30.0
    source = g_c / (2.0 * m_chi2)
    mass = 4.0 / 3.0 * math.pi * radius**3  # rho = 1 inside
    r_probe = 2.0
    exact = ff.exterior_psi_uniform_sphere(r_probe, mass, radius, m_psi, g_c, m_chi2)
    errs = []
    for n in (3000, 6000, 12000):
        r, psi = _solve_sphere(n, m_psi, radius, source, r_max)
        errs.append(abs(np.interp(r_probe, r, psi) / exact - 1.0))
    orders = [math.log2(errs[i] / errs[i + 1]) for i in range(2)]
    assert errs[-1] < 1e-5, errs
    assert all(o > 1.7 for o in orders), (errs, orders)


def test_portal_to_gravity_ratio_is_alpha() -> None:
    g_c, m_chi2, kappa, m_psi = 0.4, 0.9, 1.3, 1e-6
    M, m2, r = 2.0, 0.5, 3.0
    psi = ff.exterior_psi_uniform_sphere(r, M, 1e-3, m_psi, g_c, m_chi2)
    portal = -0.5 * (g_c / m_chi2) * m2 * psi
    newton = -(kappa / (8.0 * math.pi)) * M * m2 / r
    assert abs(portal / newton / ff.yukawa_alpha(g_c, m_chi2, kappa) - 1.0) < 1e-5


def test_gravitational_strength_portal_is_tiny_in_ev() -> None:
    """Scale anchor: alpha = 1 for nucleon matter needs only g_c ~ 5e-10 eV."""
    kappa = 1.0 / ff.REDUCED_PLANCK_MASS_EV**2
    g1 = ff.g_c_for_alpha(1.0, ff.NUCLEON_MASS_EV, kappa)
    assert 4e-10 < g1 < 6e-10
    assert abs(ff.yukawa_alpha(g1, ff.NUCLEON_MASS_EV**2, kappa) - 1.0) < 1e-12
