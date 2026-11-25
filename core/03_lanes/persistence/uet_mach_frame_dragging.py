"""Layer 2 -> 3, wave D17: does the matter around a frame decide what "not rotating" means? (Mach)

Question (author, 2026-11-24, after D16): a freely falling frame is never free of the tides of other bodies.
Is it free of them in its rotation, i.e. does "not rotating" (the inertial compass a gyroscope keeps) belong
to the frame alone, or is it set by the matter around it?

GR model: a thin spherical shell of mass M and Schwarzschild radius R rotating slowly at Omega (as seen from
far away), in equilibrium with tangential stress only (p_r = 0, p_t = rho m / (2 (r - 2m)) from the
anisotropic TOV equation). To first order in Omega the metric gains g_t phi = -omega r^2 sin^2 theta, and
omega_bar = Omega - omega obeys (Hartle 1967, with the tangential stress in the source)

    (r^4 j omega_bar')' = 16 pi r^4 e^lambda (rho + p_t) j omega_bar,     j = e^(-(nu + lambda)/2),   G = c = 1.

Inside the shell space is flat and omega is a constant: local inertial frames there rotate at omega relative
to the distant stars. Outside, omega = 2 J / r^3.

[AI derivation, general code path] dragging_numeric() integrates the equation through a shell of finite
thickness w and reads omega_in / Omega; as w -> 0 it tends to the closed form of Brill and Cohen (1966),
    omega_in / Omega = 4 alpha (2 - alpha) / ((1 + alpha)(3 - alpha)),   M/R = 2 alpha / (1 + alpha)^2,
with the weak-field limit (4/3) G M / (R c^2) (Lense-Thirring 1918) and omega_in -> Omega as the shell
approaches its own horizon (R -> 2 G M / c^2): then the inside frames turn fully with the shell.

Illustration [AI interpretation, not a cosmological model]: treating the matter inside the Hubble radius
c/H0 as such a shell gives G M / (R c^2) = Omega_m / 2 = 0.16 (matter) and 1/2 (all of the critical
density, the horizon value). The well-known coincidence that G M / (R c^2) is of order one for the
observable universe is what makes full dragging, a Machian "not rotating relative to the matter", possible;
a flat-space shell does not prove it. Whether GR is Machian in cosmology is a research question (it is not
in general: Minkowski space has inertia without matter).

Consequence [AI interpretation]: the "freedom" of a falling frame stops at its rotation too. Nearby matter
drags it by (4/3) G M/(R c^2) (Earth on a satellite gyroscope: tens of milliarcseconds per year, measured
by Gravity Probe B); enough matter, closed enough, drags it fully. Nearest known theory: Lense-Thirring,
Brill-Cohen, Hartle slow rotation. Not UET-distinct.
"""

from __future__ import annotations

from math import log, pi, sqrt

import numpy as np
from scipy.integrate import solve_ivp

OMEGA_M = 0.315  # Planck 2018, as in uet_cosmic_divider


def alpha_from_compactness(x: float) -> float:
    """Isotropic shell parameter alpha for x = G M/(R c^2) < 1/2 (Schwarzschild radius R)."""

    if not 0.0 < x < 0.5:
        raise ValueError("need 0 < G M/(R c^2) < 1/2")
    return ((1.0 - x) - sqrt(1.0 - 2.0 * x)) / x


def dragging_closed_form(x: float) -> float:
    a = alpha_from_compactness(x)
    return 4.0 * a * (2.0 - a) / ((1.0 + a) * (3.0 - a))


def dragging_weak_field(x: float) -> float:
    return 4.0 * x / 3.0


def _rho(r: float, M: float, R: float, w: float) -> float:
    if abs(r - R) >= w:
        return 0.0
    norm = 4.0 * pi * w * (R * R * 16.0 / 15.0 + w * w * 16.0 / 105.0)  # integral of 4 pi r^2 (1-x^2)^2 dr
    return M * (1.0 - ((r - R) / w) ** 2) ** 2 / norm


def dragging_numeric(x: float, w_rel: float) -> float:
    """omega_in / Omega for a shell of thickness 2 w = 2 w_rel R, by integrating the slow-rotation equation."""

    M = 1.0
    R = M / x
    w = w_rel * R

    def rhs(r, y):
        m, lnj, wb, u = y
        rho = _rho(r, M, R, w)
        e_lam = 1.0 / (1.0 - 2.0 * m / r)
        p_t = rho * m / (2.0 * (r - 2.0 * m))
        nu_p = 2.0 * m / (r * (r - 2.0 * m))
        lam_p = (8.0 * pi * r * rho - 2.0 * m / r ** 2) * e_lam
        j = np.exp(lnj)
        return [4.0 * pi * r * r * rho, -(nu_p + lam_p) / 2.0, u / (r ** 4 * j),
                16.0 * pi * r ** 4 * e_lam * (rho + p_t) * j * wb]

    sol = solve_ivp(rhs, (R - w, R + w), [0.0, 0.0, 1.0, 0.0], method="DOP853", rtol=1e-13, atol=1e-20)
    if not sol.success:
        raise RuntimeError(sol.message)
    m, lnj, wb, u = sol.y[:, -1]
    r = R + w
    dwb = u / (r ** 4 * np.exp(lnj))
    B = dwb * r ** 4 / 3.0          # outside: omega_bar = A - B / r^3, A = Omega (omega -> 0 far away)
    A = wb + B / r ** 3
    return 1.0 - 1.0 / A            # inside omega_bar = 1 = Omega - omega_in


def dragging_thin_limit(x: float, w_rels=(0.004, 0.002, 0.001)) -> float:
    """Richardson extrapolation to zero thickness (first-order error in w, checked in the tests)."""

    v = [dragging_numeric(x, w) for w in w_rels]
    r1 = 2.0 * v[1] - v[0]
    r2 = 2.0 * v[2] - v[1]
    return (4.0 * r2 - r1) / 3.0


def hubble_sphere_compactness(omega: float = 1.0) -> float:
    """G M/(R c^2) for density omega * rho_crit inside R = c/H: (4 pi/3) G rho R^2/c^2 = omega/2."""

    return omega / 2.0


def illustration() -> dict:
    x_m = hubble_sphere_compactness(OMEGA_M)
    return {"compactness_hubble_matter": x_m, "drag_hubble_matter_shell": dragging_closed_form(x_m),
            "compactness_hubble_critical": hubble_sphere_compactness(1.0),
            "drag_shell_x_0_45": dragging_closed_form(0.45)}


if __name__ == "__main__":
    print(illustration())
