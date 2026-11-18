"""Layer 2 second law and burn chain from the parent action (stage 3, wave L2-2).

Question: with the spectral function rho(w, q) of phi derived from the action (uet_layer2_from_action.py), do the
author's layer 2 statements follow without being added?

    d_iS >= 0                      (second law for the open system)
    P = T dS_prod/dt               (power burned = heat into the bath)
    bits written = P / (T ln 2)    (reversed Landauer, AUTHOR_PROPOSITION point 8)

Derivation [AI derivation, standard linear-response thermodynamics]:
1. Positivity: rho(w, q) >= 0 for w > 0 because Pi> - Pi< is a sum of phase-space integrals of
   (1+n1)(1+n2) - n1 n2 = 1 + n1 + n2 > 0 (decay) and n2 - n1 >= 0 for E2 < E1 (scattering). Checked numerically.
2. Heat current between a phi mode held at temperature T_phi and the chi bath at T (golden rule, one mode, w > 0):
       J = w rho(w) [n(w, T_phi) - n(w, T)]
   has the sign of T_phi - T, so heat flows from hot to cold.
3. Entropy production rate  sigma = J (1/T - 1/T_phi) >= 0, with equality only when T_phi = T.
4. A coherent oscillation of phi (energy E, all of it free energy, zero entropy) decays at the rate
   Gamma = rho/(2w) of uet_layer2_from_action; the power burned is P = Gamma E, the entropy it writes into the
   bath is P/T and the bits written are P/(T ln 2). Everything on the right is fixed by the action's portal.

Nearest known theory: Kubo linear response and the detailed-balance proof of the second law; Landauer (1961).
Not UET-distinct. Natural units, k_B = 1.
"""

from __future__ import annotations

import importlib
from math import log

l2 = importlib.import_module("core.03_lanes.open_system.uet_layer2_from_action")


def heat_current(w: float, q: float, T_phi: float, T: float, M: float, sigma: float) -> float:
    """Net energy per unit time from a phi mode at T_phi into the chi bath at T (w > 0)."""
    if w <= 0.0:
        raise ValueError("use w > 0")
    rho = l2.rho_q0(w, T, M, sigma) if q == 0.0 else l2.spectral(w, q, T, M, sigma)
    return w * rho * (l2.bose(w, T_phi) - l2.bose(w, T))


def entropy_production(w: float, q: float, T_phi: float, T: float, M: float, sigma: float) -> float:
    """sigma = J (1/T - 1/T_phi): entropy created per unit time by the exchange."""
    return heat_current(w, q, T_phi, T, M, sigma) * (1.0 / T - 1.0 / T_phi)


def coherent_burn(energy: float, w: float, q: float, T: float, M: float, sigma: float) -> dict[str, float]:
    """A coherent phi oscillation of energy E burns free energy into the bath at P = Gamma E."""
    gamma = l2.damping_rate(w, q, T, M, sigma)
    P = gamma * energy
    return {"damping_rate": gamma, "power": P, "entropy_rate": P / T, "bits_rate": P / (T * log(2.0))}
