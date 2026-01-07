"""
Discrete energy Ω for core models, consistent with canonical spec v0.1.
Uses spectral gradient energy for periodic spectral operator consistency.
"""
from __future__ import annotations
import numpy as np
from .operators import spectral_grad_energy
from .potentials import from_dict

def omega_C(C: np.ndarray, pot, kappa: float, L: float) -> float:
    N = C.shape[0]
    dx = L/N
    return float(np.sum(from_dict(pot).V(C) if isinstance(pot, dict) else pot.V(C))*dx*dx + 0.5*kappa*spectral_grad_energy(C, L))

def omega_CI(C: np.ndarray, I: np.ndarray, potC, potI, beta: float, kC: float, kI: float, L: float) -> float:
    N = C.shape[0]
    dx = L/N
    val = np.sum((from_dict(potC).V(C) if isinstance(potC, dict) else potC.V(C)) + (from_dict(potI).V(I) if isinstance(potI, dict) else potI.V(I)) - beta*C*I) * dx*dx
    val += 0.5*kC*spectral_grad_energy(C, L) + 0.5*kI*spectral_grad_energy(I, L)
    return float(val)
