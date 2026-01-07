"""
Physical Mappings for UET Fields

Maps abstract C, I fields to physical quantities for visualization and analysis.
This module bridges the mathematical UET framework with real-world physics.

Usage:
    from uet_core.mappings import map_to_temperature, map_to_density
    
    T = map_to_temperature(C, I, T_min=0, T_max=100)
    rho = map_to_density(C, I)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np


# =============================================================================
# Temperature Mappings (Thermodynamics)
# =============================================================================

def map_to_temperature(
    C: np.ndarray, 
    I: np.ndarray, 
    T_min: float = 0.0, 
    T_max: float = 100.0
) -> np.ndarray:
    """
    Map C, I fields to temperature.
    
    The average (C + I)/2 represents the local temperature state.
    Normalized from [-1, 1] range to [T_min, T_max].
    
    Args:
        C: Consensus field
        I: Inertia field
        T_min: Minimum temperature (default: 0°C)
        T_max: Maximum temperature (default: 100°C)
        
    Returns:
        Temperature field in specified units
        
    Example:
        >>> T = map_to_temperature(C, I, T_min=20, T_max=80)
        >>> print(f"Temperature range: {T.min():.1f} - {T.max():.1f}°C")
    """
    # Average of C and I, typically in [-1, 1]
    field_avg = (C + I) / 2
    
    # Normalize to [0, 1] then scale to temperature range
    field_normalized = (field_avg + 1) / 2  # [-1, 1] -> [0, 1]
    field_normalized = np.clip(field_normalized, 0, 1)
    
    return T_min + field_normalized * (T_max - T_min)


def map_to_heat_flux(
    C: np.ndarray, 
    I: np.ndarray, 
    dx: float = 1.0,
    k: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Map C, I fields to heat flux vector (Fourier's law).
    
    q = -k ∇T
    
    Args:
        C, I: UET fields
        dx: Grid spacing
        k: Thermal conductivity
        
    Returns:
        (qx, qy): Heat flux components
    """
    T = map_to_temperature(C, I)
    
    # Gradient using central differences
    dT_dx = (np.roll(T, -1, axis=1) - np.roll(T, 1, axis=1)) / (2 * dx)
    dT_dy = (np.roll(T, -1, axis=0) - np.roll(T, 1, axis=0)) / (2 * dx)
    
    return -k * dT_dx, -k * dT_dy


# =============================================================================
# Density Mappings (Fluid Dynamics / Materials)
# =============================================================================

def map_to_density(
    C: np.ndarray, 
    I: np.ndarray, 
    rho_min: float = 0.0, 
    rho_max: float = 1.0
) -> np.ndarray:
    """
    Map C, I fields to mass/energy density.
    
    Uses the magnitude |(C, I)|² as a measure of local energy density.
    
    Args:
        C: Consensus field
        I: Inertia field
        rho_min: Minimum density
        rho_max: Maximum density
        
    Returns:
        Density field
    """
    # Energy density from field magnitudes
    energy_density = C**2 + I**2
    
    # Normalize
    rho_normalized = energy_density / (2.0 + 1e-10)  # Max when C=I=±1
    rho_normalized = np.clip(rho_normalized, 0, 1)
    
    return rho_min + rho_normalized * (rho_max - rho_min)


def map_to_concentration(
    C: np.ndarray, 
    I: np.ndarray,
    c_min: float = 0.0,
    c_max: float = 1.0
) -> np.ndarray:
    """
    Map C field to chemical concentration (phase field interpretation).
    
    C ≈ +1: Phase A (e.g., solid, species A)
    C ≈ -1: Phase B (e.g., liquid, species B)
    C ≈ 0: Interface
    
    Args:
        C: Consensus (order parameter) field
        I: Inertia field (unused for concentration, kept for API consistency)
        c_min: Concentration for C = -1
        c_max: Concentration for C = +1
        
    Returns:
        Concentration field [c_min, c_max]
    """
    c_normalized = (C + 1) / 2  # [-1, 1] -> [0, 1]
    c_normalized = np.clip(c_normalized, 0, 1)
    return c_min + c_normalized * (c_max - c_min)


# =============================================================================
# Velocity Mappings (Fluid Dynamics)
# =============================================================================

def map_to_velocity(
    C: np.ndarray, 
    I: np.ndarray, 
    dx: float = 1.0,
    scale: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Map C, I gradients to velocity field.
    
    Interprets gradients of C, I as flow direction:
    - vx ~ -∂C/∂x (flow from high C to low C)
    - vy ~ -∂I/∂y (flow from high I to low I)
    
    Args:
        C, I: UET fields
        dx: Grid spacing
        scale: Velocity scaling factor
        
    Returns:
        (vx, vy): Velocity components
    """
    # C gradient -> x velocity
    dC_dx = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2 * dx)
    
    # I gradient -> y velocity  
    dI_dy = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2 * dx)
    
    return -scale * dC_dx, -scale * dI_dy


def map_to_vorticity(
    C: np.ndarray, 
    I: np.ndarray, 
    dx: float = 1.0
) -> np.ndarray:
    """
    Map fields to vorticity (curl of velocity).
    
    ω = ∂vy/∂x - ∂vx/∂y
    
    Args:
        C, I: UET fields
        dx: Grid spacing
        
    Returns:
        Vorticity field (scalar in 2D)
    """
    vx, vy = map_to_velocity(C, I, dx)
    
    dvy_dx = (np.roll(vy, -1, axis=1) - np.roll(vy, 1, axis=1)) / (2 * dx)
    dvx_dy = (np.roll(vx, -1, axis=0) - np.roll(vx, 1, axis=0)) / (2 * dx)
    
    return dvy_dx - dvx_dy


# =============================================================================
# Gravity / Cosmology Mappings
# =============================================================================

def map_to_gravitational_potential(
    C: np.ndarray, 
    I: np.ndarray,
    G: float = 1.0
) -> np.ndarray:
    """
    Map density to gravitational potential.
    
    Solves Poisson equation: ∇²Φ = 4πGρ
    using spectral methods (periodic boundary).
    
    Args:
        C, I: UET fields
        G: Gravitational constant (scaled)
        
    Returns:
        Gravitational potential field
    """
    rho = map_to_density(C, I)
    
    N = C.shape[0]
    
    # FFT-based Poisson solver
    rho_hat = np.fft.fft2(rho)
    
    # Wave numbers
    kx = np.fft.fftfreq(N) * 2 * np.pi
    ky = np.fft.fftfreq(N) * 2 * np.pi
    KX, KY = np.meshgrid(kx, ky)
    K2 = KX**2 + KY**2
    K2[0, 0] = 1  # Avoid division by zero
    
    # Solve ∇²Φ = 4πGρ -> Φ_hat = -4πGρ_hat / k²
    Phi_hat = -4 * np.pi * G * rho_hat / K2
    Phi_hat[0, 0] = 0  # Remove mean (gauge)
    
    return np.real(np.fft.ifft2(Phi_hat))


def map_to_gravity_field(
    C: np.ndarray, 
    I: np.ndarray,
    dx: float = 1.0,
    G: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Map to gravitational acceleration field.
    
    g = -∇Φ
    
    Args:
        C, I: UET fields
        dx: Grid spacing
        G: Gravitational constant
        
    Returns:
        (gx, gy): Gravity components
    """
    Phi = map_to_gravitational_potential(C, I, G)
    
    gx = -(np.roll(Phi, -1, axis=1) - np.roll(Phi, 1, axis=1)) / (2 * dx)
    gy = -(np.roll(Phi, -1, axis=0) - np.roll(Phi, 1, axis=0)) / (2 * dx)
    
    return gx, gy


# =============================================================================
# Equilibrium / Order Parameter Mappings
# =============================================================================

def map_to_order_parameter(C: np.ndarray, I: np.ndarray) -> np.ndarray:
    """
    Map to local order parameter (phase field).
    
    φ = (C - I) / 2
    
    φ > 0: C-dominated (consensus)
    φ < 0: I-dominated (inertia)
    φ ≈ 0: Balanced state
    
    Returns:
        Order parameter field [-1, 1]
    """
    return (C - I) / 2


def map_to_equilibrium_bias(C: np.ndarray, I: np.ndarray) -> np.ndarray:
    """
    Map to equilibrium bias indicator.
    
    bias = |C| - |I|
    
    bias > 0: System favors C equilibrium
    bias < 0: System favors I equilibrium
    
    Returns:
        Bias field
    """
    return np.abs(C) - np.abs(I)


def map_to_stability(
    C: np.ndarray, 
    I: np.ndarray,
    threshold: float = 0.1
) -> np.ndarray:
    """
    Map to local stability indicator.
    
    Uses |∇C|² + |∇I|² as instability measure.
    Low gradient = stable, high gradient = unstable.
    
    Args:
        C, I: UET fields
        threshold: Stability threshold
        
    Returns:
        Stability field: 1 = stable, 0 = unstable
    """
    dx = 1.0 / C.shape[0]
    
    # Gradient magnitudes
    dC_dx = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2 * dx)
    dC_dy = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2 * dx)
    dI_dx = (np.roll(I, -1, axis=1) - np.roll(I, 1, axis=1)) / (2 * dx)
    dI_dy = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2 * dx)
    
    grad_mag_sq = dC_dx**2 + dC_dy**2 + dI_dx**2 + dI_dy**2
    
    # Stability: low gradient = stable (1), high gradient = unstable (0)
    stability = np.exp(-grad_mag_sq / threshold**2)
    
    return stability


# =============================================================================
# Multi-scale / Coarse-graining
# =============================================================================

def coarse_grain(field: np.ndarray, factor: int = 2) -> np.ndarray:
    """
    Coarse-grain a field by averaging blocks.
    
    Args:
        field: Input field
        factor: Reduction factor (must divide field size)
        
    Returns:
        Coarse-grained field
    """
    N = field.shape[0]
    if N % factor != 0:
        raise ValueError(f"Factor {factor} must divide field size {N}")
    
    N_new = N // factor
    result = np.zeros((N_new, N_new))
    
    for i in range(N_new):
        for j in range(N_new):
            block = field[i*factor:(i+1)*factor, j*factor:(j+1)*factor]
            result[i, j] = np.mean(block)
    
    return result


# =============================================================================
# Convenience: All-in-one Mapping
# =============================================================================

@dataclass
class PhysicalFields:
    """Container for all physical field mappings."""
    temperature: np.ndarray
    density: np.ndarray
    velocity_x: np.ndarray
    velocity_y: np.ndarray
    order_parameter: np.ndarray
    stability: np.ndarray


def map_all(
    C: np.ndarray, 
    I: np.ndarray,
    dx: float = 1.0,
    T_range: Tuple[float, float] = (0, 100),
    rho_range: Tuple[float, float] = (0, 1)
) -> PhysicalFields:
    """
    Compute all physical mappings at once.
    
    Args:
        C, I: UET fields
        dx: Grid spacing
        T_range: Temperature range (min, max)
        rho_range: Density range (min, max)
        
    Returns:
        PhysicalFields dataclass with all mappings
    """
    T = map_to_temperature(C, I, T_range[0], T_range[1])
    rho = map_to_density(C, I, rho_range[0], rho_range[1])
    vx, vy = map_to_velocity(C, I, dx)
    phi = map_to_order_parameter(C, I)
    stab = map_to_stability(C, I)
    
    return PhysicalFields(
        temperature=T,
        density=rho,
        velocity_x=vx,
        velocity_y=vy,
        order_parameter=phi,
        stability=stab
    )


# =============================================================================
# 3D Extensions
# =============================================================================

def map_to_temperature_3d(
    C: np.ndarray, 
    I: np.ndarray, 
    T_min: float = 0.0, 
    T_max: float = 100.0
) -> np.ndarray:
    """3D version of temperature mapping."""
    field_avg = (C + I) / 2
    field_normalized = (field_avg + 1) / 2
    field_normalized = np.clip(field_normalized, 0, 1)
    return T_min + field_normalized * (T_max - T_min)


def map_to_density_3d(
    C: np.ndarray, 
    I: np.ndarray, 
    rho_min: float = 0.0, 
    rho_max: float = 1.0
) -> np.ndarray:
    """3D version of density mapping."""
    energy_density = C**2 + I**2
    rho_normalized = energy_density / (2.0 + 1e-10)
    rho_normalized = np.clip(rho_normalized, 0, 1)
    return rho_min + rho_normalized * (rho_max - rho_min)


def map_to_velocity_3d(
    C: np.ndarray, 
    I: np.ndarray, 
    dx: float = 1.0,
    scale: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    3D velocity field from gradients.
    
    Returns:
        (vx, vy, vz): Velocity components
    """
    dC_dx = (np.roll(C, -1, axis=2) - np.roll(C, 1, axis=2)) / (2 * dx)
    dC_dy = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2 * dx)
    dI_dz = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2 * dx)
    
    return -scale * dC_dx, -scale * dC_dy, -scale * dI_dz
