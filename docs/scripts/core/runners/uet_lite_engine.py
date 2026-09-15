"""
UET Core-4 Engine (Lite)
========================
A simplified, optimized implementation of the UET Master Equation using only the 4 Fundamental Forces.
This engine is designed to be mathematically equivalent to the full 7-term equation in standard regimes,
but significantly faster and easier to calibrate.

The 4 Fundamental Forces:
1. Potentials (Energy): V(C)
   - Unified potential landscape.
2. Geometry (Space): (κ/2)|∇C|²
   - Space-memory gradient and diffusion.
3. Information (Entropy): β C·I
   - Information-energy coupling (Landauer).
4. Interface (Exchange): γ_J (J_in - J_out)
   - Semi-open system boundary conditions.

Simplifications from v2 (Master Equation):
- 'Natural Will' (W_N) is normalized into the gradient term.
- 'Dynamic Game' (β_U) is modulated dynamically within α and γ parameters.
- 'Layer Coherence' (λ) is treated as a Z-axis spatial gradient.

Usage:
    engine = UETLiteEngine(params)
    C_new = engine.step(C, dt, I, J_in, J_out)
"""

import numpy as np
from typing import Optional, Dict, Any


class UETLiteEngine:
    def __init__(self, params: Any = None):
        self.params = params

    def step(
        self,
        C: np.ndarray,
        dt: float,
        dx: float = 0.1,
        I: Optional[np.ndarray] = None,
        J_in: Optional[np.ndarray] = None,
        J_out: Optional[np.ndarray] = None,
        constraints: Optional[Dict] = None,
    ) -> np.ndarray:
        """
        Execute one dynamics step using the Core-4 forces.

        dC/dt = -δΩ/δC = Reaction + Diffusion + Information + Exchange
        """
        # 1. Potentials (Reaction): -dV/dC
        # V(C) = (α/2)(C-C0)² + (γ/4)(C-C0)⁴
        # Force = - (α(C-C0) + γ(C-C0)³)
        diff = C - self.params.C0
        reaction = -(self.params.alpha * diff + self.params.gamma * diff**3)

        # 2. Geometry (Diffusion): κ∇²C
        # Represents the spatial memory/gradient penalty.
        if C.ndim == 1:
            laplacian = np.zeros_like(C)
            laplacian[1:-1] = (C[2:] - 2 * C[1:-1] + C[:-2]) / dx**2
            # Neumann BCs (zero gradient at ends for self-contained space)
            laplacian[0] = laplacian[1]
            laplacian[-1] = laplacian[-2]
            diffusion = self.params.kappa * laplacian
        elif C.ndim == 2:
            # 5-point stencil for 2D Laplacian
            laplacian = np.zeros_like(C)
            laplacian[1:-1, 1:-1] = (
                C[2:, 1:-1] - 2 * C[1:-1, 1:-1] + C[:-2, 1:-1]
            ) / dx**2 + (C[1:-1, 2:] - 2 * C[1:-1, 1:-1] + C[1:-1, :-2]) / dx**2
            diffusion = self.params.kappa * laplacian
        else:
            # For 0D/Scalar cases (Cosmology), diffusion is zero
            diffusion = 0.0

        # 3. Information (Entropy Source): -βI
        # The cost of information: dE = T dS → Energy required to write info.
        if I is not None:
            # Note: The term in Ω is +β C·I, so the force (-δΩ/δC) is -β I
            info_force = -self.params.beta * I
        else:
            info_force = 0.0

        # 4. Interface (Exchange): γ_J(J_in - J_out)
        # Represents the semi-open nature of the system.
        if J_in is not None and J_out is not None:
            exchange_force = self.params.gamma_J * (J_in - J_out)
        else:
            exchange_force = 0.0

        # Total Derivative
        dC_dt = reaction + diffusion + info_force + exchange_force

        # Update State
        C_new = C + dt * dC_dt

        # Optional: Apply Constraints (NEA - Necessary Energy Adjustment)
        if constraints:
            C_min = constraints.get("C_min", -np.inf)
            C_max = constraints.get("C_max", np.inf)
            C_new = np.clip(C_new, C_min, C_max)

        return C_new

    def compute_omega(
        self,
        C: np.ndarray,
        dx: float = 0.1,
        I: Optional[np.ndarray] = None,
        J_in: Optional[np.ndarray] = None,
        J_out: Optional[np.ndarray] = None,
    ) -> float:
        """
        Compute the Omega functional (Core-4 Version).
        Ω = ∫ [ V(C) + (κ/2)|∇C|² + β C·I + γ_J(J_in-J_out)·C ] dx
        """
        # Volume element
        if C.ndim == 1:
            dV = dx
        elif C.ndim == 2:
            dV = dx**2
        else:
            dV = 1.0  # Scalar case

        # 1. Potential Energy
        diff = C - self.params.C0
        V_term = (self.params.alpha / 2) * diff**2 + (self.params.gamma / 4) * diff**4
        omega_V = np.sum(V_term) * dV

        # 2. Gradient Energy (Geometry)
        if C.ndim == 1:
            grad = np.gradient(C, dx)
            grad_sq = grad**2
        elif C.ndim == 2:
            my, mx = np.gradient(C, dx)
            grad_sq = mx**2 + my**2
        else:
            grad_sq = 0.0
        omega_G = (self.params.kappa / 2) * np.sum(grad_sq) * dV

        # 3. Information Energy
        if I is not None:
            omega_I = self.params.beta * np.sum(C * I) * dV
        else:
            omega_I = 0.0

        # 4. Exchange Energy
        if J_in is not None and J_out is not None:
            omega_E = self.params.gamma_J * np.sum((J_in - J_out) * C) * dV
        else:
            omega_E = 0.0

        return omega_V + omega_G + omega_I + omega_E
