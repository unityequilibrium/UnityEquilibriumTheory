"""Jordan-to-Einstein-frame map of the UET parent action onto DEF parameters.

Theory Card UET_PARENT v1, section 6 (W5 of docs/STANDARD.md). The parent
action in canonical variables is

    L_J = F(psi)(R - 2 Lambda)/(2 kappa) - K(psi)(grad psi)^2/2 - V_J(psi) + L_m[g],
    F = 1 + kappa xi_c psi^2,  K = 1.

With g* = F g and the Damour-Esposito-Farese (DEF) normalization
S* = (1/2kappa) int sqrt(-g*)[R* - 2 (grad* phi)^2] + S_m[A^2(phi) g*]:

    (d phi/d psi)^2 = kappa K/(2F) + (3/4)(F'/F)^2,   A = F^(-1/2),
    alpha = d ln A/d phi = -(F'/F) / (2 s),  beta = d alpha/d phi,
    s = d phi/d psi.

ASSUMPTION (declared, not derived): ordinary matter (neutron-star fluid,
white dwarfs, the solar system) couples minimally to the Jordan metric g,
exactly as the O(2) sector does. Without this the DEF mapping does not apply.

Natural units, kappa = 8 pi G. No dissipative sector, no trace feedback.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Callable

MAPPING_STATUS = "CANDIDATE_JORDAN_TO_DEF_MAP"
MATTER_COUPLING_ASSUMPTION = "ordinary matter couples minimally to the Jordan metric g"


@dataclass(frozen=True)
class JordanCouplings:
    """Jordan-frame coupling functions and their first two derivatives at one psi."""

    F: float
    dF: float
    d2F: float
    K: float = 1.0
    dK: float = 0.0

    def __post_init__(self) -> None:
        values = (self.F, self.dF, self.d2F, self.K, self.dK)
        if not all(isfinite(v) for v in values):
            raise ValueError("coupling values must be finite")
        if self.F <= 0.0:
            raise ValueError("F must be positive (attractive gravity, no ghost)")


def dphi_dpsi(c: JordanCouplings, kappa: float) -> float:
    """Return s = d phi/d psi for DEF normalization; requires s^2 > 0."""

    u = c.dF / c.F
    s2 = kappa * c.K / (2.0 * c.F) + 0.75 * u * u
    if s2 <= 0.0:
        raise ValueError("Einstein-frame scalar kinetic term is not positive (ghost)")
    return sqrt(s2)


def def_alpha_beta(c: JordanCouplings, kappa: float) -> tuple[float, float]:
    """Return (alpha, beta) of DEF at the point described by ``c``."""

    if kappa <= 0.0:
        raise ValueError("kappa must be positive")
    u = c.dF / c.F
    du = c.d2F / c.F - u * u
    s = dphi_dpsi(c, kappa)
    ds2 = kappa * c.dK / (2.0 * c.F) - kappa * c.K * c.dF / (2.0 * c.F**2) + 1.5 * u * du
    ds = ds2 / (2.0 * s)
    alpha = -u / (2.0 * s)
    dalpha = -(du * s - u * ds) / (2.0 * s * s)
    return alpha, dalpha / s


def ppn_from_def(alpha0: float, beta0: float) -> tuple[float, float]:
    """Return (gamma_PPN - 1, beta_PPN - 1) for a massless scalar (DEF 1992)."""

    a2 = alpha0 * alpha0
    return -2.0 * a2 / (1.0 + a2), 0.5 * beta0 * a2 / (1.0 + a2) ** 2


def uet_couplings(psi: float, xi_c: float, kappa: float) -> JordanCouplings:
    """UET parent: F = 1 + kappa xi_c psi^2, K = 1 (canonical psi)."""

    return JordanCouplings(
        F=1.0 + kappa * xi_c * psi * psi,
        dF=2.0 * kappa * xi_c * psi,
        d2F=2.0 * kappa * xi_c,
    )


def uet_def_parameters(xi_c: float, kappa: float, psi0: float = 0.0) -> dict[str, float]:
    """DEF and PPN parameters of the UET parent around asymptotic value psi0.

    At psi0 = 0: alpha0 = 0 and beta0 = -2 xi_c exactly.
    """

    alpha0, beta0 = def_alpha_beta(uet_couplings(psi0, xi_c, kappa), kappa)
    gamma_m1, beta_ppn_m1 = ppn_from_def(alpha0, beta0)
    return {
        "alpha0": alpha0,
        "beta0": beta0,
        "gamma_ppn_minus_1": gamma_m1,
        "beta_ppn_minus_1": beta_ppn_m1,
    }


def uet_einstein_frame_mass_sq_at_origin(
    m_psi2: float, xi_c: float, kappa: float, Lambda: float = 0.0, vacuum_density: float = 0.0
) -> float:
    """Einstein-frame scalar mass squared at psi = 0.

    Jordan potential V_J = m_psi2 psi^2/2 + lambda psi^4/4 + F Lambda/kappa + vacuum_density,
    Einstein potential V* = V_J / F^2 and canonical field psi near 0, giving
    m*^2 = m_psi2 - 2 xi_c Lambda - 4 kappa xi_c vacuum_density.
    (vacuum_density = epsilon rho_star in Theory Card variables.)
    """

    return m_psi2 - 2.0 * xi_c * Lambda - 4.0 * kappa * xi_c * vacuum_density


def general_def_alpha_beta(
    F: Callable[[float], float],
    dF: Callable[[float], float],
    d2F: Callable[[float], float],
    K: Callable[[float], float],
    dK: Callable[[float], float],
    psi: float,
    kappa: float,
) -> tuple[float, float]:
    """Convenience wrapper for any Jordan-frame F(psi), K(psi)."""

    return def_alpha_beta(JordanCouplings(F(psi), dF(psi), d2F(psi), K(psi), dK(psi)), kappa)
