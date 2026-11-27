"""Can selection by persistence fix the parent action's parameters inside one universe? (wave C1, STRESS_12 option C)

Question: the author's layer 3 says that what persists is what managed its resources well, with the abundance law
N = b tau (core/03_lanes/persistence). Cosmological natural selection (Smolin; review arXiv:hep-th/0612185) uses
the same idea across universes. Inside one universe, what could such a selection fix?

Results [AI derivation; checked in core/05_tests/physics/test_selection_of_scale.py].
1. Selection acts on solutions, not on constants. Couplings of the action (xi_c, lambda, g_c, ...) have no field
   equation, so no dynamics inside one universe, persistence included, can change them. Selection can only pick
   among states: vacua, phases, field values. For phases that are born at rate b_i and last tau_i, the steady
   state fractions are N_i / N = b_i tau_i / sum_j b_j tau_j (Little's law, the layer-3 law); checked here with a
   stochastic birth-death simulation.
2. In the scale-invariant restriction (wave S1) the only scale, <psi> (which sets M_Pl^2 = xi_c <psi>^2), is a
   state and could in principle be selected. But it is a flat direction: every psi0 is a static de Sitter
   solution with the same lifetime (infinite), so selection by persistence is neutral and fixes nothing.
3. If the flat direction is broken by the card's mass term (the cosmon of wave D1), nothing is static: on the
   attractor the Jordan-frame Planck mass drifts with d ln F / dN = 4 xi / (1 + 4 xi), i.e.
   dG/dt / G = -4 xi H / (1 + 4 xi) (derived from the Einstein-frame attractor and the frame change; checked by
   integrating the Jordan-frame equations). Under Cassini (xi <= 5.75e-6) this is at most 2.3e-5 H, 96 times
   below the lunar-laser-ranging bound 2.2e-3 H0 that C1 uses.
So inside one universe persistence selection cannot fix the couplings of the card; it could fix them only if they
were promoted to fields (moduli), which changes the action (author decision), or across universes, as in
cosmological natural selection, which the author's layer 3 does not claim. Nearest known theory: Little's law,
cosmological natural selection, the cosmon. Not UET-distinct.
"""

from __future__ import annotations

import importlib
import math
import random

s1 = importlib.import_module("core.03_lanes.scalar_tensor.uet_scale_symmetry")

LLR_GDOT_H0 = 2.2e-3


def steady_state_fractions(b, tau):
    w = [bi * ti for bi, ti in zip(b, tau)]
    tot = sum(w)
    return [x / tot for x in w]


def simulate_phases(b, tau, t_end: float, seed: int = 1) -> list[float]:
    """Gillespie simulation: phase i is born at rate b_i (Poisson) and each copy dies at rate 1/tau_i.
    Returns time-averaged fractions over the second half of the run."""
    rng = random.Random(seed)
    k = len(b)
    n = [0] * k
    t, acc, t_acc = 0.0, [0.0] * k, 0.0
    while t < t_end:
        rates = list(b) + [n[i] / tau[i] for i in range(k)]
        R = sum(rates)
        dt = rng.expovariate(R)
        if t > t_end / 2:
            tot = sum(n)
            if tot:
                for i in range(k):
                    acc[i] += dt * n[i] / tot
                t_acc += dt
        t += dt
        u, j = rng.random() * R, 0
        while u > rates[j]:
            u -= rates[j]
            j += 1
        if j < k:
            n[j] += 1
        else:
            n[j - k] -= 1
    return [a / t_acc for a in acc]


def drift_rate(xi: float) -> float:
    """d ln F / dN on the cosmon attractor (Jordan frame)."""
    return 4.0 * xi / (1.0 + 4.0 * xi)


def jordan_drift_numeric(xi: float, m2: float = 1.0, psi0: float = 3.0, N: float = 300.0, h: float = 0.002) -> float:
    """Integrate the Jordan-frame FRW equations of S1 + mass (no matter) and return d ln F / dN at the end."""
    md = s1.SIModel(xi, 0.0, m2=m2)
    psi, pi = psi0, 0.0

    def rhs(p, q):
        H = s1.hubble(md, p, q)
        _, acc = s1.accelerations(md, p, q, H)
        return q / H, acc / H

    for _ in range(int(N / h)):
        a1, b1 = rhs(psi, pi)
        a2, b2 = rhs(psi + h / 2 * a1, pi + h / 2 * b1)
        a3, b3 = rhs(psi + h / 2 * a2, pi + h / 2 * b2)
        a4, b4 = rhs(psi + h * a3, pi + h * b3)
        psi += h / 6 * (a1 + 2 * a2 + 2 * a3 + a4)
        pi += h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
    return 2.0 * rhs(psi, pi)[0] / psi


def report() -> dict:
    xi = s1.cassini_xi_max()
    d = drift_rate(xi)
    return {"gdot_over_G_H_max_at_cassini": d, "llr_over_drift": LLR_GDOT_H0 / d}


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
