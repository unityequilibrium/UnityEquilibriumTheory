"""Game-physics lane: replace many light debris particles by friction + noise (layer-2 coarse graining). [AI derivation]

Question (author, 2026-11-28): can UET-derived physics make game physics cheaper while staying correct?

Model. A heavy disk (mass M, radius R) moves through N light point debris (mass m, density n, temperature T) in a
periodic 2D box, elastic specular collisions, no debris-debris collisions (full model, cost ~ N per step).
Reduced model (cost ~ 1 per step) built from three UET bookkeeping rules:
  1. layer-2 friction and noise from a closed system (C_LAYER2_OPEN_FROM_CLOSED), with the velocity-dependent
     kinetic-theory drag of a hard disk in a 2D ideal gas, heavy-disk limit:
         F(V) = -2 m n R s0^2 int_0^{2 pi} cos(th) G(V cos(th) / s0) dth,  s0^2 = T / m,
         G(c) = (1 + c^2) Phi(c) + c phi(c);
     slow limit F = -gamma0 V, gamma0 = 2 sqrt(2 pi) m n R s0; fast limit F -> -(8/3) m n R V^2;
     noise from fluctuation-dissipation, sqrt(2 gamma0 T dt) / M;
  2. energy bookkeeping (burn law): what the body loses heats the debris, N T + M V^2/2 + N m U^2/2 = const;
  3. momentum bookkeeping (Noether): the debris drifts with the momentum it received, U = (P0 - M V)/(N m),
     and the drag acts on the relative velocity V - U.
Nothing is calibrated: every coefficient follows from m, n, R, T.
Nearest known methods: Langevin / Brownian coarse graining (Mori-Zwanzig), Epstein drag. Not UET-distinct; what
UET supplies is the list of balances the reduced model must keep. Results: core/03_lanes/game_physics/README.md.
"""

from __future__ import annotations

import math

import numpy as np

_TH = np.linspace(0, 2 * math.pi, 721)[:-1]


def G(c):
    c = np.asarray(c, dtype=float)
    Phi = 0.5 * (1 + np.vectorize(math.erf)(c / math.sqrt(2)))
    phi = np.exp(-0.5 * c * c) / math.sqrt(2 * math.pi)
    return (1 + c * c) * Phi + c * phi


def drag(V: float, m: float, n: float, R: float, T: float) -> float:
    """Signed drag force (along V) on the disk moving at speed V >= 0."""
    s0 = math.sqrt(T / m)
    c = V * np.cos(_TH) / s0
    return float(-2 * m * n * R * s0 * s0 * np.mean(np.cos(_TH) * G(c)) * 2 * math.pi)


def gamma0(m: float, n: float, R: float, T: float) -> float:
    return 2 * math.sqrt(2 * math.pi) * m * n * R * math.sqrt(T / m)


class Scene:
    def __init__(self, M=200.0, R=1.0, m=1.0, T=1.0, L=20.0, N=2000):
        self.M, self.R, self.m, self.T, self.L, self.N = M, R, m, T, L, N
        self.n = N / L ** 2
        c = np.linspace(0, 12, 1201)
        self._c = c
        self._K = np.array([-drag(ci, 1.0, 1.0, 1.0, 1.0) / 2.0 for ci in c])   # shape with m = n = R = s0 = 1

    def drag_fast(self, V: float, T: float) -> float:
        s0 = math.sqrt(T / self.m)
        return 2 * self.m * self.n * self.R * s0 * s0 * float(np.interp(V / s0, self._c, self._K))

    # full model ------------------------------------------------------------------------------------------
    def full_run(self, V0, steps, dt, seed, fixed_velocity=False):
        """Returns V(t) (steps x 2); with fixed_velocity the disk is infinitely heavy and the mean force is returned."""
        M, R, m, L, N = self.M, self.R, self.m, self.L, self.N
        rng = np.random.default_rng(seed)
        x = rng.uniform(0, L, (N, 2))
        X = np.array([L / 2, L / 2])
        d = x - X
        x[(d ** 2).sum(1) < R * R] += 2 * R
        v = rng.normal(0, math.sqrt(self.T / m), (N, 2))
        V = np.array([V0, 0.0])
        out = np.empty((steps, 2))
        impulse = np.zeros(2)
        t0 = int(0.5 / dt)
        for s in range(steps):
            x += v * dt
            x %= L
            X = (X + V * dt) % L
            d = x - X
            d -= L * np.round(d / L)
            r2 = (d ** 2).sum(1)
            hit = r2 < R * R
            if hit.any():
                nn = d[hit] / np.sqrt(r2[hit])[:, None]
                rel = ((v[hit] - V) * nn).sum(1)
                go = rel < 0
                if go.any():
                    nn, rel = nn[go], rel[go]
                    mu = m if fixed_velocity else m * M / (m + M)
                    J = 2 * mu * rel
                    idx = np.where(hit)[0][go]
                    v[idx] -= (J / m)[:, None] * nn
                    if fixed_velocity:
                        if s >= t0:
                            impulse += (J[:, None] * nn).sum(0)
                    else:
                        V = V + (J[:, None] * nn).sum(0) / M
            out[s] = V
        if fixed_velocity:
            return float(impulse[0] / ((steps - t0) * dt))
        return out

    # reduced models --------------------------------------------------------------------------------------
    def reduced_run(self, V0, steps, dt, seed):
        M, m, N = self.M, self.m, self.N
        rng = np.random.default_rng(seed)
        V = np.array([V0, 0.0])
        E0 = N * self.T + 0.5 * M * V0 * V0
        P0 = np.array([M * V0, 0.0])
        out = np.empty((steps, 2))
        for s in range(steps):
            U = (P0 - M * V) / (N * m)
            Tg = (E0 - 0.5 * M * (V @ V) - 0.5 * N * m * (U @ U)) / N
            W = V - U
            sp = math.sqrt(W @ W)
            f = -self.drag_fast(sp, Tg) * (W / sp) if sp > 0 else np.zeros(2)
            g0 = gamma0(m, self.n, self.R, Tg)
            V = V + f / M * dt + math.sqrt(2 * g0 * Tg * dt) / M * rng.normal(size=2)
            out[s] = V
        return out

    def linear_langevin_run(self, V0, steps, dt, seed):
        """Plain linear friction (no drag law, no bookkeeping), exact Ornstein-Uhlenbeck update; the comparison case."""
        rng = np.random.default_rng(seed)
        g = gamma0(self.m, self.n, self.R, self.T)
        a = math.exp(-g / self.M * dt)
        sd = math.sqrt(self.T / self.M * (1 - a * a))
        V = np.array([V0, 0.0])
        out = np.empty((steps, 2))
        for s in range(steps):
            V = a * V + sd * rng.normal(size=2)
            out[s] = V
        return out

    def equilibrium_V2(self, V0) -> float:
        """<|V|^2> at full equilibrium of the closed box: centre-of-mass drift plus equipartition of what is left."""
        M, m, N = self.M, self.m, self.N
        vcm = M * V0 / (M + N * m)
        E0 = N * self.T + 0.5 * M * V0 * V0
        T_eq = (E0 - 0.5 * (M + N * m) * vcm * vcm) / (N + 1)
        return vcm * vcm + 2 * T_eq / M
