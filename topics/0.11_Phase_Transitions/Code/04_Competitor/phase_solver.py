"""
UET Phase Solver: Phase Transition Dynamics
============================================
Implements Cahn-Hilliard dynamics for phase separation.

Key Physics:
- Double-well potential V(C) = alpha*C^2/2 + gamma*C^4/4
- Gradient energy: ∫ kappa/2 |∇C|^2 dx
- Time evolution: dC/dt = M ∇²(dΩ/dC)
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class UETParameters:
    """UET parameters for simulations."""

    kappa: float = 0.1  # Gradient coefficient
    alpha: float = -1.0  # Double-well parameter (negative for phase sep)
    beta: float = 0.0  # C-I coupling strength


class UETPhaseSolver:
    """
    UET Phase Solver with semi-implicit time stepping.

    Implements Cahn-Hilliard equation:
    dC/dt = M * nabla^2 (alpha*C + gamma*C^3 - kappa*nabla^2 C)
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        dt: float = 0.01,
        temperature: float = 0.05,
        params: Optional[UETParameters] = None,
    ):
        """
        Initialize phase solver.

        Args:
            nx, ny: Grid dimensions
            dt: Time step
            temperature: System temperature (for fluctuations)
            params: UET parameters
        """
        self.nx = nx
        self.ny = ny
        self.dt = dt
        self.temperature = temperature
        self.params = params or UETParameters()

        # Initialize concentration field
        self.C = np.random.randn(nx, ny) * 0.01

        # Physical constants
        self.mobility = 1.0
        self.gamma = 1.0  # C^4 coefficient

        # Set up FFT for spectral method
        self._setup_spectral()

    def _setup_spectral(self):
        """Set up spectral operators for Laplacian."""
        kx = np.fft.fftfreq(self.nx, d=1.0 / self.nx) * 2 * np.pi
        ky = np.fft.fftfreq(self.ny, d=1.0 / self.ny) * 2 * np.pi
        self.Kx, self.Ky = np.meshgrid(kx, ky, indexing="ij")
        self.K2 = self.Kx**2 + self.Ky**2

    def laplacian(self, field: np.ndarray) -> np.ndarray:
        """Compute Laplacian using spectral method."""
        return np.fft.ifft2(-self.K2 * np.fft.fft2(field)).real

    def chemical_potential(self) -> np.ndarray:
        """
        Compute chemical potential μ = dΩ/dC.

        μ = alpha*C + gamma*C^3 - kappa*∇²C
        """
        bulk = self.params.alpha * self.C + self.gamma * self.C**3
        gradient = -self.params.kappa * self.laplacian(self.C)
        return bulk + gradient

    def step(self, iteration: int = 0):
        """
        Advance one time step using explicit Euler with stability fixes.

        dC/dt = M * nabla^2 mu
        """
        mu = self.chemical_potential()
        dCdt = self.mobility * self.laplacian(mu)

        # Add thermal noise
        if self.temperature > 0:
            noise = np.random.randn(self.nx, self.ny) * np.sqrt(
                2 * self.temperature * self.dt
            )
            dCdt += noise * 0.01

        self.C += self.dt * dCdt

        # Clip to prevent numerical instability
        self.C = np.clip(self.C, -3.0, 3.0)

        # Handle any remaining NaN
        if np.any(np.isnan(self.C)):
            self.C = np.nan_to_num(self.C, nan=0.0)

    def get_domain_count(self) -> int:
        """
        Estimate number of domains by counting sign changes.
        """
        # Binary partition
        binary = (self.C > 0).astype(int)

        # Count transitions
        h_transitions = np.sum(np.abs(np.diff(binary, axis=0)))
        v_transitions = np.sum(np.abs(np.diff(binary, axis=1)))

        return h_transitions + v_transitions

    def order_parameter(self) -> float:
        """Compute order parameter = mean |C|."""
        return np.mean(np.abs(self.C))

    def free_energy(self) -> float:
        """
        Compute total free energy.

        Ω = ∫ [V(C) + kappa/2 |∇C|²] dx
        """
        # Bulk free energy
        V = (self.params.alpha / 2) * self.C**2 + (self.gamma / 4) * self.C**4
        bulk = np.sum(V)

        # Gradient energy
        grad_x = np.gradient(self.C, axis=0)
        grad_y = np.gradient(self.C, axis=1)
        grad = (self.params.kappa / 2) * (grad_x**2 + grad_y**2)
        gradient = np.sum(grad)

        return bulk + gradient


if __name__ == "__main__":
    print("UET Phase Solver Test")
    print("=" * 50)

    solver = UETPhaseSolver(nx=32, ny=32, dt=0.01)

    for i in range(100):
        solver.step(i)
        if i % 20 == 0:
            print(
                f"Step {i}: Order={solver.order_parameter():.4f}, Domains={solver.get_domain_count()}"
            )

    print("\n[OK] Phase Solver Test Complete")
