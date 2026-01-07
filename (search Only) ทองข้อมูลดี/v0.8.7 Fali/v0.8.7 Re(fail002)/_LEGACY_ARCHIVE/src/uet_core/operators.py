"""
Spectral operators for periodic domains.
"""
from __future__ import annotations
import numpy as np

def _kgrid_1d(N: int, L: float) -> np.ndarray:
    # numpy.fft.fftfreq gives cycles/unit; multiply by 2π to get radians/unit
    return 2*np.pi*np.fft.fftfreq(N, d=L/N)

def spectral_laplacian(u: np.ndarray, L: float) -> np.ndarray:
    """
    Compute Δu using FFT on a 2D periodic grid.
    Convention: Δ̂u(k) = -|k|^2 û(k)
    """
    if u.ndim != 2:
        raise ValueError("spectral_laplacian currently supports 2D arrays only.")
    N0, N1 = u.shape
    if N0 != N1:
        raise ValueError("spectral_laplacian expects square grid for v0.1.")
    N = N0
    k = _kgrid_1d(N, L)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    k2 = kx*kx + ky*ky
    uhat = np.fft.fftn(u)
    lap_hat = -k2 * uhat
    return np.fft.ifftn(lap_hat).real

def spectral_grad_energy(u: np.ndarray, L: float) -> float:
    """
    Return ∫ |∇u|^2 dx using Parseval in k-space:
    ∫ |∇u|^2 dx = Σ |k|^2 |û(k)|^2 * (dx^2) / (N^2) * ??? 
    We'll compute directly in physical space via spectral derivatives for clarity.
    """
    if u.ndim != 2:
        raise ValueError("spectral_grad_energy currently supports 2D arrays only.")
    N0, N1 = u.shape
    if N0 != N1:
        raise ValueError("spectral_grad_energy expects square grid for v0.1.")
    N = N0
    k = _kgrid_1d(N, L)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    uhat = np.fft.fftn(u)
    ux = np.fft.ifftn(1j*kx*uhat).real
    uy = np.fft.ifftn(1j*ky*uhat).real
    dx = L/N
    return float(np.sum(ux*ux + uy*uy) * dx*dx)
