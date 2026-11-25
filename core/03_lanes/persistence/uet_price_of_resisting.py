"""Layer 2 -> 3, wave D19: what does it cost to resist the motion the universe gives you?

Question (author, 2026-11-24): resisting is trying to stand still in a universe that is always moving;
a rocket fighting the atmosphere, is that trying to be still? AI reading (AUTHOR_PROPOSITION 4): in GR there
is no absolute rest, but there is an absolute difference between free fall (proper acceleration 0) and being
pushed off it (proper acceleration a != 0). Resisting = a != 0. What is its price?

[AI derivation]
D19a Speed spent on resisting gravity. A rocket that climbs vertically in a uniform field g with exhaust
     speed v_e, mass ratio Rm = m0/mf and lift-off thrust-to-weight lam0 burns for t_b = v_e (1 - 1/Rm)/(lam0 g)
     and loses exactly g t_b of its ideal speed v_e ln Rm:
         gravity loss = v_e (1 - 1/Rm)/lam0,   fraction = (1 - 1/Rm)/(lam0 ln Rm).
     Hovering (holding still above the ground) buys nothing and costs g per second of speed; the jet power to
     hover a mass m is m g v_e / 2. Standing on the ground resists with zero power: the floor pushes, it does
     no work (a solid structure resists for free).
D19b Time spent on resisting. Between the same two events, the clock that falls freely ages most (GR:
     geodesics maximise proper time). A clock thrown straight up and caught after a ground-clock time T gains
         delta tau = g^2 T^3 / (24 c^2)
     over the clock held still on the ground (weak field, from tau = int (1 + Phi/c^2 - v^2/2c^2) dt along
     the parabola). The exact Schwarzschild radial geodesic tends to this with relative correction of order
     (g T / c)^2 and h/R.

Consequence [AI interpretation]: resisting has a measurable price in energy (only when something is consumed
to push, as in a rocket) and always in proper time (the pushed clock ages less). The universe's free motion
is the free one; staying still against it is paid for. Nearest known theory: rocket gravity losses
(Tsiolkovsky), maximal aging of geodesics, gravitational time dilation (Pound-Rebka, optical clocks).
Not UET-distinct. Illustrative rocket numbers are AI choices, not a real vehicle; a strictly vertical climb
loses far more than a real launch, which tilts over early so that less of the burn is spent holding up.
"""

from __future__ import annotations

from math import log, sqrt

import numpy as np
from scipy.integrate import solve_ivp

C = 299792458.0
G_EARTH = 9.80665  # standard gravity, m/s^2


def gravity_loss_closed(v_e: float, Rm: float, lam0: float) -> float:
    return v_e * (1.0 - 1.0 / Rm) / lam0


def gravity_loss_fraction(Rm: float, lam0: float) -> float:
    return (1.0 - 1.0 / Rm) / (lam0 * log(Rm))


def vertical_ascent(v_e: float, Rm: float, lam0: float, g: float = G_EARTH):
    """Integrate m dv/dt = T - m g with constant mass flow; returns (burnout speed, gravity loss)."""

    m0 = 1.0
    thrust = lam0 * m0 * g
    mdot = thrust / v_e
    t_b = (m0 - m0 / Rm) / mdot
    sol = solve_ivp(lambda t, y: [thrust / (m0 - mdot * t) - g], (0.0, t_b), [0.0], method="DOP853",
                    rtol=1e-13, atol=1e-12)
    v = float(sol.y[0, -1])
    return v, v_e * log(Rm) - v


def hover_speed_cost(t: float, g: float = G_EARTH) -> float:
    return g * t


def hover_jet_power(m: float, v_e: float, g: float = G_EARTH) -> float:
    return 0.5 * m * g * v_e


def thrown_clock_gain_closed(T: float, g: float = G_EARTH, c: float = C) -> float:
    return g * g * T ** 3 / (24.0 * c * c)


def thrown_clock_gain_weak_numeric(T: float, g: float = G_EARTH, c: float = C, N: int = 4001) -> float:
    """int (g z/c^2 - v^2/(2c^2)) dt along the free-fall path z(0) = z(T) = 0 (Simpson rule)."""

    from scipy.integrate import simpson

    t = np.linspace(0.0, T, N)
    v0 = g * T / 2.0
    z = v0 * t - 0.5 * g * t * t
    v = v0 - g * t
    return float(simpson(g * z / c ** 2 - v * v / (2.0 * c * c), x=t))


def perturbed_path_gain(T: float, eps: float, k: int, g: float = G_EARTH, c: float = C, N: int = 4001) -> float:
    """Same functional for z + eps sin(k pi t/T): a path that is pushed off free fall."""

    from scipy.integrate import simpson

    t = np.linspace(0.0, T, N)
    v0 = g * T / 2.0
    z = v0 * t - 0.5 * g * t * t + eps * np.sin(k * np.pi * t / T)
    v = v0 - g * t + eps * k * np.pi / T * np.cos(k * np.pi * t / T)
    return float(simpson(g * z / c ** 2 - v * v / (2.0 * c * c), x=t))


def thrown_clock_gain_schwarzschild(M: float, R: float, u: float):
    """Geometric units (G = c = 1). Clock thrown radially up from r = R with proper speed u and caught there.

    Returns (proper time gained over the static clock at R, static clock's proper time T, its proper
    acceleration g = M / (R^2 sqrt(1 - 2M/R))).
    """

    f0 = 1.0 - 2.0 * M / R
    E = sqrt(f0 + u * u)

    def rhs(tau, y):
        r, rd, t = y
        return [rd, -M / r ** 2, E / (1.0 - 2.0 * M / r)]

    def back(tau, y):
        return y[0] - R
    back.terminal, back.direction = True, -1
    sol = solve_ivp(rhs, (0.0, 1e9), [R, u, 0.0], events=back, method="DOP853", rtol=1e-13, atol=1e-16)
    tau = float(sol.t_events[0][0])
    t = float(sol.y_events[0][0][2])
    T = sqrt(f0) * t
    return tau - T, T, M / (R * R * sqrt(f0))


def illustration() -> dict:
    """AI-chosen illustrative numbers (not a real vehicle): v_e = 3000 m/s, Rm = 8, lam0 = 1.3."""

    return {"gravity_loss_m_s": gravity_loss_closed(3000.0, 8.0, 1.3),
            "gravity_loss_fraction": gravity_loss_fraction(8.0, 1.3),
            "hover_one_minute_m_s": hover_speed_cost(60.0),
            "hover_power_one_tonne_MW": hover_jet_power(1000.0, 3000.0) / 1e6,
            "thrown_clock_gain_2s_s": thrown_clock_gain_closed(2.0)}


if __name__ == "__main__":
    print(illustration())
