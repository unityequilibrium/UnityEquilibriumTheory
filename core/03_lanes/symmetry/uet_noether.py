"""Noether coverage of the parent action: which quantities the action conserves, and why (wave N1).

Question: the parent action has spacetime translations, Lorentz rotations and boosts, diffeomorphisms (with
gravity) and an internal O(2) rotation of the matter doublet. Do the conserved quantities that Noether's theorems
attach to these symmetries hold for the implemented equations, including the portal exchange?

Results [AI derivation; checked in core/05_tests/physics/test_noether.py]:
1. Internal O(2) (first theorem). N^mu = Z (chi_1 d^mu chi_2 - chi_2 d^mu chi_1) obeys the off-shell identity
       d_mu N^mu = chi_1 E_2 - chi_2 E_1          (E_A: matter Euler-Lagrange residuals)
   with the portal on. The portal couples phi to |chi|^2, which is O(2) invariant, so matter can trade energy
   with space (C_EXCHANGE_DERIVED) but cannot create or destroy chi charge: chi number is a conserved resource.
2. Diffeomorphisms (second theorem), with gravity, in a Bianchi I universe with lapse N:
       N d/dt (dL/dN) = sum_q E_q dq/dt       (q = a, b, c, phi, chi_1, chi_2)
   so the Hamiltonian constraint (total energy of matter + phi + geometry = 0) is preserved once the other
   equations hold. Total energy is conserved; matter energy alone is not.
   On an inhomogeneous, non-diagonal metric (functions of t and x, and separately of all of t, x, y, z; g_tx != 0)
   the full generalized Bianchi
   identity holds for the implemented residuals:
       nabla^mu E_mu_nu = -kappa (E_phi d_nu phi + sum_A E_A d_nu chi_A)
   (E_mu_nu: metric residual, E_phi: response residual, E_A: matter residuals), so every component of the total
   stress is conserved on shell, not only the energy.
3. Translations and boosts (first theorem, flat space, no gravity), on a 1+1 lattice of phi, chi_1, chi_2 with the
   action's potentials and portal: energy E, momentum P, charge Q and the boost charge
       K = int x H dx - t P
   are conserved, the lattice-broken ones (P, K) with second-order convergence in dx. K is conserved only if
   every field has the same light cone (energy flux = momentum density, a symmetric stress tensor).
4. Rotations (first theorem, 2+1 lattice): angular momentum L = int (x P_y - y P_x) is conserved with
   second-order convergence in dx, together with E, P_x, P_y and the O(2) charge.

Nearest known theory: Noether (1918) first and second theorems; ADM Hamiltonian constraint; Poincare charges of
scalar field theory. Not UET-distinct. Natural units, signature (-,+,+,+).
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass

import numpy as np

cov = importlib.import_module("core.02_equations.covariant.uet_covariant_matter")
resp = importlib.import_module("core.02_equations.covariant.uet_covariant_response")


@dataclass(frozen=True)
class FlatParams:
    """Flat-space parameters of the parent action (gravity decoupled)."""
    epsilon: float
    k: float
    mu2: float
    lambda_phi: float
    phi_star: float
    Z: float
    m2: float
    lambda_chi: float
    h: float
    phi_speed_sq: float = 1.0  # 1 for the action; other values only for the negative control

    @classmethod
    def from_configs(cls, rc, mc) -> "FlatParams":
        return cls(rc.epsilon_nc, rc.response_kinetic, rc.response_mass_sq, rc.response_quartic,
                   rc.phi_equilibrium, mc.matter_kinetic, mc.matter_mass_sq, mc.matter_quartic,
                   mc.response_coupling)


def potential_density(p: FlatParams, phi, chi1, chi2):
    """eps U(phi) + W(|chi|^2) + V_int, without the constant eps rho_star (it does not affect the dynamics)."""
    d = phi - p.phi_star
    c2 = chi1 * chi1 + chi2 * chi2
    return (p.epsilon * (0.5 * p.mu2 * d * d + 0.25 * p.lambda_phi * d**4)
            + 0.5 * p.m2 * c2 + 0.25 * p.lambda_chi * c2 * c2 - 0.5 * p.epsilon * p.h * d * c2)


def _forces(p: FlatParams, phi, chi1, chi2):
    d = phi - p.phi_star
    c2 = chi1 * chi1 + chi2 * chi2
    f_phi = -(p.epsilon * (p.mu2 * d + p.lambda_phi * d**3) - 0.5 * p.epsilon * p.h * c2)
    common = p.m2 + p.lambda_chi * c2 - p.epsilon * p.h * d
    return f_phi, -common * chi1, -common * chi2


@dataclass
class Lattice:
    """phi, chi_1, chi_2 and their canonical momenta on a periodic 1+1 grid."""
    x: np.ndarray
    phi: np.ndarray
    chi1: np.ndarray
    chi2: np.ndarray
    pphi: np.ndarray
    p1: np.ndarray
    p2: np.ndarray
    t: float = 0.0

    @property
    def dx(self) -> float:
        return float(self.x[1] - self.x[0])


def _lap(f, dx):
    return (np.roll(f, -1) - 2.0 * f + np.roll(f, 1)) / (dx * dx)


def _grad(f, dx):
    return (np.roll(f, -1) - np.roll(f, 1)) / (2.0 * dx)


def step(p: FlatParams, s: Lattice, dt: float) -> None:
    """One kick-drift-kick (Stormer-Verlet) step of Hamilton's equations."""
    mphi, mchi = p.epsilon * p.k, p.Z
    for _ in (0, 1):
        f_phi, f1, f2 = _forces(p, s.phi, s.chi1, s.chi2)
        s.pphi += 0.5 * dt * (mphi * p.phi_speed_sq * _lap(s.phi, s.dx) + f_phi)
        s.p1 += 0.5 * dt * (mchi * _lap(s.chi1, s.dx) + f1)
        s.p2 += 0.5 * dt * (mchi * _lap(s.chi2, s.dx) + f2)
        if _ == 0:
            s.phi += dt * s.pphi / mphi
            s.chi1 += dt * s.p1 / mchi
            s.chi2 += dt * s.p2 / mchi
    s.t += dt


def _densities(p: FlatParams, s: Lattice):
    mphi, mchi, dx = p.epsilon * p.k, p.Z, s.dx
    # gradient energy centred on the site: mean of the forward and backward squared differences
    g2 = lambda f: 0.5 * (((np.roll(f, -1) - f) / dx) ** 2 + ((f - np.roll(f, 1)) / dx) ** 2)  # noqa: E731
    H = (s.pphi**2 / (2 * mphi) + s.p1**2 / (2 * mchi) + s.p2**2 / (2 * mchi)
         + 0.5 * mphi * p.phi_speed_sq * g2(s.phi) + 0.5 * mchi * (g2(s.chi1) + g2(s.chi2))
         + potential_density(p, s.phi, s.chi1, s.chi2))
    Pd = -(s.pphi * _grad(s.phi, dx) + s.p1 * _grad(s.chi1, dx) + s.p2 * _grad(s.chi2, dx))
    return H, Pd


def charges(p: FlatParams, s: Lattice) -> dict[str, float]:
    """Energy, momentum, O(2) charge (N^0 of uet_covariant_matter) and boost charge K = int x H - t P."""
    H, Pd = _densities(p, s)
    dx = s.dx
    E, P = float(H.sum() * dx), float(Pd.sum() * dx)
    Q = float(-(s.chi1 * s.p2 - s.chi2 * s.p1).sum() * dx)  # N^0 = -Z (chi1 dt chi2 - chi2 dt chi1)
    K = float((s.x * H).sum() * dx - s.t * P)
    return {"E": E, "P": P, "Q": Q, "K": K}


def wave_packets(p: FlatParams, n: int, half_width: float = 40.0) -> Lattice:
    """Localized moving packets: a charged chi packet and a phi packet travelling the other way."""
    x = np.linspace(-half_width, half_width, n, endpoint=False)
    g1 = np.exp(-((x + 6.0) / 2.5) ** 2)
    g2 = np.exp(-((x - 5.0) / 3.0) ** 2)
    kc, kp, wc = 1.3, -0.9, 1.6
    chi1, chi2 = 0.6 * g1 * np.cos(kc * x), 0.6 * g1 * np.sin(kc * x)
    phi = p.phi_star + 0.5 * g2 * np.cos(kp * x)
    p1, p2 = p.Z * wc * 0.6 * g1 * np.sin(kc * x), -p.Z * wc * 0.6 * g1 * np.cos(kc * x)
    pphi = p.epsilon * p.k * 0.8 * 0.5 * g2 * np.sin(kp * x)
    return Lattice(x, phi, chi1, chi2, pphi, p1, p2)


def metric_residual_symbolic(g, ginv, einstein, gamma, phi, chi, p: dict, coords):
    """Theory Card metric equation E_mu_nu as a sympy matrix (the form the code implements numerically):
    E = F (G + Lambda g) + eps (g box f - nabla nabla f) - kappa (T_m + eps T_phi), f = xi (phi - phi_*)^2."""
    import sympy as sp
    n = len(coords)
    d = phi - p["phi_star"]
    f = p["xi"] * d**2
    F = 1 + p["epsilon"] * f
    hess = sp.Matrix(n, n, lambda a, b: sp.diff(f, coords[a], coords[b])
                     - sum(gamma[c][a][b] * sp.diff(f, coords[c]) for c in range(n)))
    box_f = sum(ginv[i, j] * hess[i, j] for i in range(n) for j in range(n))
    grad = lambda u: [sp.diff(u, v) for v in coords]  # noqa: E731
    kin = lambda du: sum(ginv[i, j] * du[i] * du[j] for i in range(n) for j in range(n))  # noqa: E731
    dphi, dch = grad(phi), [grad(u) for u in chi]
    c2 = chi[0] ** 2 + chi[1] ** 2
    V = p["m2"] * c2 / 2 + p["lambda_chi"] * c2**2 / 4 - p["epsilon"] * p["h"] * d * c2 / 2
    U = p["rho_star"] + p["mu2"] * d**2 / 2 + p["lambda_phi"] * d**4 / 4
    Tm = sp.Matrix(n, n, lambda i, j: p["Z"] * (dch[0][i] * dch[0][j] + dch[1][i] * dch[1][j])
                   - g[i, j] * (p["Z"] * (kin(dch[0]) + kin(dch[1])) / 2 + V))
    Tp = sp.Matrix(n, n, lambda i, j: p["k"] * dphi[i] * dphi[j] - g[i, j] * (p["k"] * kin(dphi) / 2 + U))
    E = sp.Matrix(n, n, lambda i, j: F * (einstein[i, j] + p["Lambda"] * g[i, j]) + p["epsilon"] * (g[i, j] * box_f - hess[i, j])
                  - p["kappa"] * (Tm[i, j] + p["epsilon"] * Tp[i, j]))
    return E, hess


def divergence_evaluator(E, ginv, gamma, coords, active):
    """Compile E, g^-1 and Gamma once; return a function point -> nabla^mu E_mu_nu (mpmath derivatives along
    the coordinates in `active`; the others must not appear in the fields or the metric)."""
    import mpmath
    import sympy as sp
    n = len(coords)
    args = [coords[a] for a in active]
    comp = lambda e: sp.lambdify(args, e, "mpmath")  # noqa: E731
    fE = [[comp(E[i, j]) for j in range(n)] for i in range(n)]
    fgi = [[comp(ginv[i, j]) for j in range(n)] for i in range(n)]
    fgm = [[[comp(gamma[l][a][m]) for m in range(n)] for a in range(n)] for l in range(n)]

    def at(point: list[float], dps: int = 40) -> list[float]:
        mpmath.mp.dps = dps
        x = [mpmath.mpf(v) for v in point]
        Ev = [[fE[i][j](*x) for j in range(n)] for i in range(n)]
        dE = [[[mpmath.mpf(0)] * n for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                for k, a in enumerate(active):
                    order = [1 if q == k else 0 for q in range(len(args))]
                    dE[i][j][a] = dE[j][i][a] = mpmath.diff(fE[i][j], x, order)
        gi = [[fgi[i][j](*x) for j in range(n)] for i in range(n)]
        gm = [[[fgm[l][a][m](*x) for m in range(n)] for a in range(n)] for l in range(n)]
        return [float(sum(gi[m][a] * (dE[m][nu][a] - sum(gm[l][a][m] * Ev[l][nu] + gm[l][a][nu] * Ev[m][l]
                                                           for l in range(n)))
                          for m in range(n) for a in range(n))) for nu in range(n)]
    return at


def _lap2(f, dx):
    return (np.roll(f, -1, 0) + np.roll(f, 1, 0) + np.roll(f, -1, 1) + np.roll(f, 1, 1) - 4.0 * f) / (dx * dx)


def run_2d(p: FlatParams, n: int, t_end: float, half_width: float = 16.0, courant: float = 0.2) -> tuple[dict, dict]:
    """2+1 lattice: energy, both momenta, O(2) charge and angular momentum L = int (x P_y - y P_x) at 0 and t_end."""
    xs = np.linspace(-half_width, half_width, n, endpoint=False)
    dx = float(xs[1] - xs[0])
    x, y = np.meshgrid(xs, xs, indexing="ij")
    g1 = np.exp(-(((x + 3.0) / 2.0) ** 2 + ((y - 1.0) / 2.0) ** 2))
    g2 = np.exp(-(((x - 2.0) / 2.2) ** 2 + ((y + 2.5) / 2.2) ** 2))
    kc, wc = 1.1, 1.5
    f = {"phi": p.phi_star + 0.5 * g2 * np.cos(0.8 * x),
         "chi1": 0.6 * g1 * np.cos(kc * y), "chi2": 0.6 * g1 * np.sin(kc * y)}
    mphi, mchi = p.epsilon * p.k, p.Z
    pi = {"phi": mphi * 0.4 * g2 * np.sin(0.8 * x),
          "chi1": mchi * wc * 0.6 * g1 * np.sin(kc * y), "chi2": -mchi * wc * 0.6 * g1 * np.cos(kc * y)}
    mass = {"phi": mphi, "chi1": mchi, "chi2": mchi}
    stiff = {"phi": mphi * p.phi_speed_sq, "chi1": mchi, "chi2": mchi}

    def kick(h):
        fp, f1, f2 = _forces(p, f["phi"], f["chi1"], f["chi2"])
        for key, force in (("phi", fp), ("chi1", f1), ("chi2", f2)):
            pi[key] += h * (stiff[key] * _lap2(f[key], dx) + force)

    def measure(t):
        H = potential_density(p, f["phi"], f["chi1"], f["chi2"]).copy()
        Px, Py = np.zeros_like(x), np.zeros_like(x)
        for key in f:
            fwd_x, bwd_x = (np.roll(f[key], -1, 0) - f[key]) / dx, (f[key] - np.roll(f[key], 1, 0)) / dx
            fwd_y, bwd_y = (np.roll(f[key], -1, 1) - f[key]) / dx, (f[key] - np.roll(f[key], 1, 1)) / dx
            H += pi[key] ** 2 / (2 * mass[key]) + 0.25 * stiff[key] * (fwd_x**2 + bwd_x**2 + fwd_y**2 + bwd_y**2)
            Px -= pi[key] * 0.5 * (fwd_x + bwd_x)
            Py -= pi[key] * 0.5 * (fwd_y + bwd_y)
        a = dx * dx
        Q = float(-(f["chi1"] * pi["chi2"] - f["chi2"] * pi["chi1"]).sum() * a)
        return {"E": float(H.sum() * a), "Px": float(Px.sum() * a), "Py": float(Py.sum() * a), "Q": Q,
                "L": float((x * Py - y * Px).sum() * a)}

    steps = int(round(t_end / (courant * dx)))
    dt = t_end / steps
    start = measure(0.0)
    for _ in range(steps):
        kick(0.5 * dt)
        for key in f:
            f[key] += dt * pi[key] / mass[key]
        kick(0.5 * dt)
    return start, measure(t_end)


def run(p: FlatParams, n: int, t_end: float, courant: float = 0.2) -> tuple[dict, dict]:
    """Evolve the packets to t_end; return the charges at t = 0 and at t_end."""
    s = wave_packets(p, n)
    steps = int(round(t_end / (courant * s.dx)))
    dt = t_end / steps
    start = charges(p, s)
    for _ in range(steps):
        step(p, s, dt)
    return start, charges(p, s)
