"""
Variational derivatives (chemical potentials) for canonical Ω.
Used for sanity checks: FD directional derivative vs inner product <δΩ/δu, η>.
"""
from __future__ import annotations
import numpy as np
from .operators import spectral_laplacian
from .potentials import from_dict

def mu_C(C: np.ndarray, pot, kappa: float, L: float) -> np.ndarray:
    pot_obj = from_dict(pot) if isinstance(pot, dict) else pot
    return pot_obj.dV(C) - kappa * spectral_laplacian(C, L)

def mu_CI(C: np.ndarray, I: np.ndarray, potC, potI, beta: float, kC: float, kI: float, L: float) -> tuple[np.ndarray, np.ndarray]:
    potC_obj = from_dict(potC) if isinstance(potC, dict) else potC
    potI_obj = from_dict(potI) if isinstance(potI, dict) else potI
    muC = potC_obj.dV(C) - beta*I - kC * spectral_laplacian(C, L)
    muI = potI_obj.dV(I) - beta*C - kI * spectral_laplacian(I, L)
    return muC, muI

def inner_dx2(a: np.ndarray, b: np.ndarray, L: float) -> float:
    if a.shape != b.shape:
        raise ValueError("inner_dx2 shape mismatch")
    N = a.shape[0]
    dx = L/N
    return float(np.sum(a*b) * dx*dx)
