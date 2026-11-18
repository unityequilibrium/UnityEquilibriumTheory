"""Layer 3 mapped term by term onto the Lotka-Volterra competition model of Saavedra et al. (2025).

Saavedra, Arroyo, Deng, Marquet and Kempes, "Integrating metabolic scaling and coexistence theories",
Ecology (2025), doi 10.1002/ecy.70173, Eqs. (4)-(6), (11)-(14):

    dN_i/dt / N_i = (r_i / K_i) (K_i - sum_j a_ij N_j),   a_ii = 1,   K_i = r_i / a_hat_ii,
    a_ij = a0' C_j / C_i                     (C_i: consumption per unit biomass),
    with metabolic scaling  C_i ~ M_i^(-1/4)  =>  a_ij ~ (M_j / M_i)^(-1/4).

UET layer 3 (uet_persistence_selection.py), number density n_i, one shared free-energy pool R:

    dn_i/dt = (a_i R - 1/tau_i) n_i,        dR/dt = S - delta R - R sum_i a_i F_i n_i,
    tau_i = F_i / P_i (burn law).

Reduction (derived here, checked numerically in core/05_tests/physics/test_layer3_lv_map.py):
the pool relaxes on the time scale 1/delta. If it is fast compared with the populations and the
draw sum_j a_j F_j n_j is small against delta, the quasi-steady pool is

    R = S / (delta + sum_j a_j F_j n_j)  ~  (S/delta) (1 - sum_j a_j F_j n_j / delta),

and layer 3 becomes Lotka-Volterra in number density with

    r_i      = a_i S / delta - 1/tau_i
    a_hat_ij = a_i a_j F_j S / delta^2
    a_ij     = a_hat_ij / a_hat_ii = (a_j F_j) / (a_i F_i)
    K_i      = r_i / a_hat_ii.

So the per-capita draw a_i F_i plays the role of Saavedra's consumption C_i, with a0' = 1.
Converting to biomass density (N_i = M_i n_i) multiplies a_ij by M_i / M_j.

Metabolic scaling inside layer 3 [AI interpretation]: a store proportional to mass (F ~ M), burn power
P ~ M^(3/4) and capture a ~ M^(-1/4) give tau ~ M^(1/4) and a_i F_i ~ M^(3/4); in biomass density
a_ij = (M_j/M_i)^(3/4) (M_i/M_j) = (M_j/M_i)^(-1/4), which is Saavedra's Eq. (14).

What differs (stated, not hidden):
- With one pool the interaction matrix a_ij = C_j / C_i has rank 1 (a0' = 1 off the diagonal too), so
  only the lowest-R* type persists. Saavedra et al. take off-diagonal a0 = S^(-1/2) < 1, an effective
  niche difference; in UET that has to come from more than one resource (A4: two resources).
- Saavedra et al. take the mortality d_i from metabolic scaling; UET derives it as 1/tau_i = P_i/F_i
  from the free-energy store, the same law used for stars and isotopes (T008, T009).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np


def lv_parameters(capture: Sequence[float], stores: Sequence[float], powers: Sequence[float],
                  supply: float, decay: float) -> dict[str, np.ndarray]:
    """Lotka-Volterra parameters (number density) of layer 3 in the fast, weak-draw pool limit."""
    a = np.asarray(capture, float)
    F = np.asarray(stores, float)
    P = np.asarray(powers, float)
    tau = F / P
    draw = a * F
    r = a * supply / decay - 1.0 / tau
    a_hat = np.outer(a, draw) * supply / decay**2
    A = a_hat / np.diag(a_hat)[:, None]
    K = r / np.diag(a_hat)
    return {"r": r, "a_hat": a_hat, "A": A, "K": K, "tau": tau, "draw": draw}


def lv_rhs(n: np.ndarray, r: np.ndarray, K: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Saavedra et al. Eq. (4): dn_i/dt = (r_i / K_i) n_i (K_i - sum_j A_ij n_j)."""
    return r / K * n * (K - A @ n)


def layer3_rhs(n: np.ndarray, R: float, capture: np.ndarray, stores: np.ndarray, powers: np.ndarray,
               supply: float, decay: float) -> tuple[np.ndarray, float]:
    """Full layer-3 consumer-resource model (same equations as uet_persistence_selection.competition_rhs)."""
    tau = stores / powers
    dn = (capture * R - 1.0 / tau) * n
    dR = supply - decay * R - R * float(np.sum(capture * stores * n))
    return dn, dR


def integrate(rhs, y0: np.ndarray, horizon: float, dt: float) -> np.ndarray:
    """Classical RK4 for y' = rhs(y)."""
    y = np.array(y0, float)
    for _ in range(int(round(horizon / dt))):
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return y


def to_biomass_interaction(A_number: np.ndarray, masses: Sequence[float]) -> np.ndarray:
    """Interaction matrix for biomass density N_i = M_i n_i: A_bio_ij = A_ij M_i / M_j."""
    M = np.asarray(masses, float)
    return A_number * np.outer(M, 1.0 / M)


def metabolic_types(masses: Sequence[float], a0: float = 1.0, f0: float = 1.0, p0: float = 1.0):
    """Capture, store and burn power under metabolic scaling: a ~ M^-1/4, F ~ M, P ~ M^3/4."""
    M = np.asarray(masses, float)
    return a0 * M**-0.25, f0 * M, p0 * M**0.75
