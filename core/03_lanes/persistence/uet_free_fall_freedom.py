"""Layer 2 -> 3, wave D16: how free is a freely falling frame in the real universe?

Question (author, 2026-11-24): "in the cosmological view, can the free-falling frame really be free, free of
the other bodies in this universe? If not, a one-body universe cannot be simulated correctly."

GR (equivalence principle) removes, in a falling frame, every gravitational pull that is the same across the
frame. What it cannot remove is the tidal part, the change of the pull across the frame,
    T_ij = -d^2 Phi / dx_i dx_j      (units 1/s^2),
which for a point mass M at distance d has eigenvalues (2, -1, -1) G M / d^3, and for the cosmological
constant is isotropic, +H_L^2 delta_ij with H_L^2 = Lambda c^2 / 3. The background expansion of matter acts
the same way (+H^2 (Omega_L - Omega_m/2) delta_ij today).

[AI derivation] A bound system of mass m and size r holds itself together at the rate G m / r^3 (its own
"binding tide"). The others leave a fraction
    epsilon_source = |largest tidal eigenvalue of the source| / (G m / r^3)
of that in its free fall. epsilon << 1: the system may be treated as alone (the one-body picture is a good
approximation); epsilon ~ 1: it is not separable from that source (Hill / tidal radius; for Lambda, the
zero-gravity radius r_ZG = (G m / H_L^2)^(1/3)).

Inputs are measured values from the literature, chosen by the AI as illustrations (masses and sizes of
bound systems are round values; see SYSTEMS). They are not fitted and test nothing.

Consequence [AI interpretation]: freedom is local and graded. No falling frame is free of the others in
the tidal sense; the size of the leftover sets whether the one-body universe is a fair model of a piece of
ours. Nearest known theory: Hill sphere, tidal radius, Lambda zero-gravity radius (Chernin). Not UET-distinct.
"""

from __future__ import annotations

import importlib

import numpy as np

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")

G, M_SUN, MPC = cd.G_NEWTON, cd.M_SUN, cd.MPC
H0, H_L, OM, OL = cd.H0, cd.H_L, cd.OMEGA_M, cd.OMEGA_L
AU = 1.495978707e11
PC = MPC / 1e6
KPC = MPC / 1e3

# Galactic tide in the solar neighbourhood: vertical part 4 pi G rho_0 dominates (rho_0 ~ 0.1 M_sun/pc^3,
# mid-plane density, e.g. McKee et al. 2015 give 0.084 to 0.1); radial part of a flat rotation curve V^2/R^2.
RHO0_DISK = 0.1 * M_SUN / PC ** 3
V0, R0 = 230e3, 8.2 * KPC


def acceleration_point(x, M: float, X=(0.0, 0.0, 0.0)):
    """Newtonian acceleration of a point mass M at X; works with complex x (complex-step)."""

    d = np.asarray(x) - np.asarray(X, float)
    r = np.sqrt(np.sum(d * d))
    return -G * M * d / r ** 3


def acceleration_lambda(x):
    return H_L ** 2 * np.asarray(x)


def tidal_tensor_complex_step(acc, x, h: float = 1e-30):
    """T_ij = d a_i / d x_j by complex-step differentiation (no subtraction error)."""

    x = np.asarray(x, float)
    T = np.zeros((3, 3))
    for j in range(3):
        xc = x.astype(complex)
        xc[j] += 1j * h * max(1.0, np.linalg.norm(x))
        T[:, j] = np.imag(acc(xc)) / (h * max(1.0, np.linalg.norm(x)))
    return T


def point_tide(M: float, d: float) -> float:
    return 2.0 * G * M / d ** 3


def lambda_tide() -> float:
    return H_L ** 2


def background_tide_today() -> float:
    """Isotropic relative acceleration of comoving neighbours per unit separation: a''/a today."""

    return H0 ** 2 * (OL - OM / 2.0)


def galactic_tide_local() -> float:
    return max(4.0 * np.pi * G * RHO0_DISK, V0 ** 2 / R0 ** 2)


def binding_tide(m: float, r: float) -> float:
    return G * m / r ** 3


def tidal_radius(m: float, M: float, d: float) -> float:
    """Size at which the point tide of M equals the system's own binding tide: d (m / 2M)^(1/3)."""

    return d * (m / (2.0 * M)) ** (1.0 / 3.0)


def zero_gravity_radius(m: float) -> float:
    return (G * m / H_L ** 2) ** (1.0 / 3.0)


def l1_distance(m: float, M: float, d: float) -> float:
    """Distance from m to the inner Lagrange point of the circular two-body orbit (rotating frame)."""

    from scipy.optimize import brentq

    mu = m / (m + M)
    # positions on the x axis: M at -mu d, m at (1 - mu) d; L1 between them, measured from m
    def f(s):
        x = (1 - mu) * d - s
        w2 = G * (m + M) / d ** 3
        return -G * M / (x + mu * d) ** 2 + G * m / s ** 2 + w2 * x
    return brentq(f, 1e-12 * d, (1 - 1e-9) * d, xtol=1e-15 * d, rtol=1e-15)


# Bound systems (AI-chosen round values) and the outside sources acting on them.
SYSTEMS = {
    "Earth": {"m": 5.9722e24, "r": 6.371e6, "sources": {
        "Moon": point_tide(7.342e22, 3.844e8),
        "Sun": point_tide(M_SUN, AU),
        "Jupiter_closest": point_tide(1.898e27, 4.2 * AU),
        "Milky_Way_local": galactic_tide_local(),
        "Lambda": lambda_tide()}},
    "Solar_system_to_Neptune": {"m": M_SUN, "r": 30.0 * AU, "sources": {
        "Alpha_Centauri_AB": point_tide(2.0 * M_SUN, 1.34 * PC),
        "Milky_Way_local": galactic_tide_local(),
        "Lambda": lambda_tide()}},
    "Milky_Way_halo": {"m": 1.0e12 * M_SUN, "r": 250.0 * KPC, "sources": {
        "Andromeda": point_tide(1.5e12 * M_SUN, 0.765 * MPC),
        "Virgo_cluster": point_tide(1.2e15 * M_SUN, 16.5 * MPC),
        "Lambda": lambda_tide()}},
    "Local_Group": {"m": 3.0e12 * M_SUN, "r": 1.0 * MPC, "sources": {
        "Virgo_cluster": point_tide(1.2e15 * M_SUN, 16.5 * MPC),
        "Lambda": lambda_tide()}},
    "Virgo_cluster": {"m": 1.2e15 * M_SUN, "r": 2.2 * MPC, "sources": {
        "Lambda": lambda_tide()}},
}


def freedom_table() -> dict:
    out = {}
    for name, s in SYSTEMS.items():
        own = binding_tide(s["m"], s["r"])
        eps = {k: v / own for k, v in s["sources"].items()}
        top = max(eps, key=eps.get)
        out[name] = {"epsilon": eps, "largest": top, "epsilon_largest": eps[top],
                     "epsilon_lambda": eps["Lambda"],
                     "zero_gravity_radius_over_size": zero_gravity_radius(s["m"]) / s["r"]}
    return out


if __name__ == "__main__":
    for name, row in freedom_table().items():
        print(name, row["largest"], f"{row['epsilon_largest']:.2e}", "Lambda", f"{row['epsilon_lambda']:.2e}",
              "r_ZG/r", f"{row['zero_gravity_radius_over_size']:.2f}")
