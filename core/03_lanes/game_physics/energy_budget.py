"""Game-physics lane: energy budgeting for sleeping, from the layer-2 burn law. [AI proposal and derivation]

Scene: an explosion throws N disks (radius RAD) across a floor; they slide with Coulomb friction (MU, G) and
collide with restitution E_REST. This is the debris a game keeps simulating for seconds after an explosion.

Rule. A body with kinetic energy E burns it at P = MU m G |v|, so (work-energy theorem / burn law tau = int dE / P)
it can still travel at most  d = E / (MU m G) = v^2 / (2 MU G)  and it stops after  t = v / (MU G).
If its reach disk (radius RAD + d) overlaps no other body's reach disk (sleeping bodies: RAD), no future contact
is possible, so the body is moved straight to its stopping point and put to sleep. This is exact for this
friction law, not a threshold heuristic. Bodies with RAD + d > RHO_CAP are not tested (conservative).
Baseline: the usual engine rule (PhysX / Box2D style): sleep after speed < V_SLEEP for T_SLEEP; wake on contact.
Both modes share one uniform-grid broadphase (cell 2 RAD); cost = body updates + pair tests.
Nearest known methods: energy-threshold sleeping (PhysX sleepThreshold), conservative advancement, event-driven
simulation. Results: core/03_lanes/game_physics/README.md.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict

import numpy as np

MU, G, E_REST, RAD = 0.4, 9.8, 0.3, 0.1
V_SLEEP, T_SLEEP = 0.05, 0.5
H = 2 * RAD
RHO_CAP = 0.6


def scene(N: int, seed: int):
    rng = np.random.default_rng(seed)
    ang = rng.uniform(0, 2 * math.pi, N)
    r0 = np.sqrt(rng.uniform(0, 1, N)) * 1.5
    x = np.c_[r0 * np.cos(ang), r0 * np.sin(ang)]
    sp = rng.uniform(0.5, 6.0, N)
    v = np.c_[np.cos(ang), np.sin(ang)] * sp[:, None] + rng.normal(0, 0.3, (N, 2))
    return x, v


def stop_distance(speed):
    return np.asarray(speed) ** 2 / (2 * MU * G)


def friction_step(v, awake, dt):
    sp = np.sqrt((v[awake] ** 2).sum(1))
    dec = MU * G * dt
    v[awake] *= np.where(sp > dec, (sp - dec) / np.maximum(sp, 1e-12), 0.0)[:, None]


def cells_of(p, r):
    i0, i1 = int(math.floor((p[0] - r) / H)), int(math.floor((p[0] + r) / H))
    j0, j1 = int(math.floor((p[1] - r) / H)), int(math.floor((p[1] + r) / H))
    return [(i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)]


def collide(x, v, awake) -> int:
    """Grid broadphase + impulse resolution for pairs with at least one awake body. Returns pair tests."""
    grid = defaultdict(list)
    keys = np.floor(x / H).astype(int)
    for k, (a, b) in enumerate(keys):
        grid[(a, b)].append(k)
    tests, seen, R2 = 0, set(), 2 * RAD
    for i in np.where(awake)[0]:
        a, b = keys[i]
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                for j in grid.get((a + da, b + db), ()):
                    if j == i:
                        continue
                    key = (min(i, j), max(i, j))
                    if key in seen:
                        continue
                    seen.add(key)
                    tests += 1
                    dv = x[i] - x[j]
                    dn = math.sqrt(dv @ dv) + 1e-12
                    if dn >= R2:
                        continue
                    n = dv / dn
                    rel = (v[i] - v[j]) @ n
                    push = 0.5 * (R2 - dn) * n
                    x[i] += push
                    x[j] -= push
                    if rel < 0:
                        J = -(1 + E_REST) * rel / 2
                        v[i] += J * n
                        v[j] -= J * n
                        awake[i] = awake[j] = True
    return tests


def reach_free(x, v, awake):
    """Awake bodies whose reach disk overlaps no other reach disk. Returns (indices, speeds, pair tests)."""
    spd = np.sqrt((v ** 2).sum(1))
    rho = np.where(awake, stop_distance(spd), 0.0) + RAD
    grid = defaultdict(list)
    for i in range(len(x)):
        for c in cells_of(x[i], min(rho[i], RHO_CAP)):
            grid[c].append(i)
    fast = [i for i in np.where(awake)[0] if rho[i] > RHO_CAP]
    tests, free = 0, []
    for i in [i for i in np.where(awake)[0] if rho[i] <= RHO_CAP]:
        near = set()
        for c in cells_of(x[i], rho[i]):              # overlapping disks share a cell of their reach boxes
            near.update(grid.get(c, ()))
        ok = True
        for j in list(near) + fast:
            if j == i:
                continue
            tests += 1
            if math.hypot(*(x[i] - x[j])) < rho[i] + rho[j]:
                ok = False
                break
        if ok:
            free.append(i)
    return free, spd, tests


def run(N, seed, dt, mode, t_end=6.0, every=4):
    """mode: 'baseline' (threshold sleeping), 'budget' (threshold + energy budget), 'reference' (no sleeping)."""
    x, v = scene(N, seed)
    awake = np.ones(N, bool)
    slow_t = np.zeros(N)
    updates = tests = 0
    t0 = time.perf_counter()
    s = 0
    for s in range(int(round(t_end / dt))):
        if mode == "budget" and s % every == 0:
            free, spd, t_r = reach_free(x, v, awake)
            tests += t_r
            if free:
                f = np.array(free)
                vh = v[f] / np.maximum(spd[f], 1e-12)[:, None]
                x[f] += vh * stop_distance(spd[f])[:, None]
                v[f] = 0.0
                awake[f] = False
        updates += int(awake.sum())
        friction_step(v, awake, dt)
        x[awake] += v[awake] * dt
        tests += collide(x, v, awake)
        if mode != "reference":
            slow = awake & (np.sqrt((v ** 2).sum(1)) < V_SLEEP)
            slow_t = np.where(slow, slow_t + dt, 0.0)
            go = awake & (slow_t >= T_SLEEP)
            v[go] = 0.0
            awake[go] = False
        if not awake.any():
            break
    return {"x": x, "updates": updates, "tests": tests, "wall": time.perf_counter() - t0, "t_settled": (s + 1) * dt}
