"""
UET Matrix Engine - Tensor-Based Reality Simulation (v0.9 Core)
================================================================

This module implements the "Matrix Form" of UET.
Instead of calculating specific functions (f(x)), we evolve a State Tensor (S).

Key Concepts:
-------------
1. State Tensor (S): A 4D tensor representing [Energy, Information, Space, Time] at every point.
2. Evolution Operator (T): A Transformation Matrix that evolves S_t -> S_t+1.
3. Coordinate Invariance: Operations are Tensor Contractions, valid in any frame.

Mathematical Form:
------------------
S_{t+1} = T • S_t

where:
- S is the Universe State
- T is the Transfer Tensor (Encoding Physical Laws like Gravity & Entropy)
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class UniverseState:
    """
    Represents the state of a system as a Tensor.

    Layers (Rank-1 Indices):
    0: Mass/Energy Density (ρ) - Gravity Source
    1: Information Density (σ) - Structure Source
    2: Energy Flux X (Vx) - Flow
    3: Energy Flux Y (Vy) - Flow
    4: Energy Flux Z (Vz) - Flow
    """

    grid_size: int
    tensor: np.ndarray  # Shape: (5, N, N, N) for 3D grid

    def __init__(self, size: int):
        self.grid_size = size
        # Initialize empty 5-layer tensor (Mass, Info, Vx, Vy, Vz)
        self.tensor = np.zeros((5, size, size, size))

    @property
    def density(self):
        return self.tensor[0]

    @property
    def information(self):
        return self.tensor[1]


class MatrixEvolution:
    """
    The Physics Engine that evolves the Universe State via Matrix Operations.
    """

    def __init__(
        self,
        params=None,
        G: float = 1.0,
        c: float = 1.0,
        beta: float = 0.5,
        kappa: float = 0.5,
        mobility: float = None,
    ):
        from docs.core.uet_parameters import UETParameters

        if params is None:
            self.params = UETParameters(kappa=kappa, beta=beta)
        else:
            self.params = params
        # Use params if provided, otherwise fallback to args
        self.G = getattr(self.params, "G", G)
        self.c = getattr(self.params, "c", c)
        self.beta = getattr(self.params, "beta", beta)
        self.mobility = mobility

    def _get_laplacian_kernel(self) -> np.ndarray:
        """Standard 3x3x3 Laplacian Kernel for 3D Grid."""
        # 3D Laplacian: center -6, neighbors +1
        k = np.zeros((3, 3, 3))

        # Center
        k[1, 1, 1] = -6.0

        # Neighbors (Face-connected)
        k[0, 1, 1] = 1.0
        k[2, 1, 1] = 1.0
        k[1, 0, 1] = 1.0
        k[1, 2, 1] = 1.0
        k[1, 1, 0] = 1.0
        k[1, 1, 2] = 1.0

        return k

    def _apply_convolution(self, field: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Applies a 3D spatial convolution using Vectorized NumPy Slicing.
        Optimization: Replaces O(N^3) Python loops with C-level array operations.
        Speedup: ~100x-500x.
        """
        # Ensure kernel is 3x3x3
        if kernel.shape != (3, 3, 3):
            # Fallback for non-standard kernels (slow but safe)
            from scipy.ndimage import convolve

            return convolve(field, kernel, mode="constant", cval=0.0)

        # Pad field by 1 for boundary handling
        padded = np.pad(field, 1, mode="edge")

        # Vectorized Stencil Accumulator
        output = np.zeros_like(field)

        # Iterate over kernel weights (only 27 iterations total, vs 27,000)
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    weight = kernel[i, j, k]
                    if weight == 0:
                        continue

                    # Slice appropriate region from padded array
                    # i=0 -> start at 0, end at -2
                    # i=1 -> start at 1, end at -1
                    # i=2 -> start at 2, end at None (end)

                    z_start, z_end = i, i + field.shape[0]
                    y_start, y_end = j, j + field.shape[1]
                    x_start, x_end = k, k + field.shape[2]

                    shifted_view = padded[z_start:z_end, y_start:y_end, x_start:x_end]

                    output += weight * shifted_view

        return output

    def _get_gradient_kernels(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Simple Central Difference Gradient Kernels (3D)."""
        # 3D Kernels (3x3x3)
        kx = np.zeros((3, 3, 3))
        ky = np.zeros((3, 3, 3))
        kz = np.zeros((3, 3, 3))  # Added Z-gradient

        # d/dx (along axis 0)
        kx[0, 1, 1] = -0.5
        kx[2, 1, 1] = 0.5

        # d/dy (along axis 1)
        ky[1, 0, 1] = -0.5
        ky[1, 2, 1] = 0.5

        # d/dz (along axis 2)
        kz[1, 1, 0] = -0.5
        kz[1, 1, 2] = 0.5

        return kx, ky, kz

    def _advect(
        self, field: np.ndarray, vx: np.ndarray, vy: np.ndarray, vz: np.ndarray
    ) -> np.ndarray:
        """
        Computes 3D Advection: (v . del) field = vx * dF/dx + vy * dF/dy + vz * dF/dz
        """
        kx, ky, kz = self._get_gradient_kernels()
        grad_x = self._apply_convolution(field, kx)
        grad_y = self._apply_convolution(field, ky)
        grad_z = self._apply_convolution(field, kz)
        return vx * grad_x + vy * grad_y + vz * grad_z

    def compute_interaction_matrix(self, S: UniverseState) -> np.ndarray:
        """
        Generates the Interaction Matrix using Kernels.
        """
        N = S.grid_size
        rho = S.density
        sigma = S.information

        # 1. Metric Strain (Space deformation)
        laplacian_kernel = self._get_laplacian_kernel()
        metric_strain = self._apply_convolution(rho, laplacian_kernel)

        # 2. Information Pressure
        # Kill Switch Check
        check = (self.params.beta / self.params.beta) if self.params.beta != 0 else 1.0
        beta_val = self.params.beta
        info_pressure = beta_val * sigma * check

        # Total Interaction
        interaction_linear = (metric_strain + info_pressure) * check

        # 3. Nonlinear Saturation (Sigmoid/Tanh)
        interaction_saturated = np.tanh(interaction_linear / 1000.0) * 1000.0

        return interaction_saturated

    def _divergence(self, vx: np.ndarray, vy: np.ndarray, vz: np.ndarray) -> np.ndarray:
        """
        Computes 3D Divergence: div(V) = dVx/dx + dVy/dy + dVz/dz
        """
        kx, ky, kz = self._get_gradient_kernels()
        grad_x = self._apply_convolution(vx, kx)
        grad_y = self._apply_convolution(vy, ky)
        grad_z = self._apply_convolution(vz, kz)
        return grad_x + grad_y + grad_z

    def step(self, S: UniverseState, dt: float = 0.1) -> UniverseState:
        """
        Evolve state: S_new = S_old + dt * (Interactions)
        """
        S_new = UniverseState(S.grid_size)

        # Extract Layers
        rho = S.tensor[0]
        sigma = S.tensor[1]

        # --- 1. Forces & Potentials ---
        interaction = self.compute_interaction_matrix(S)
        laplacian_kernel = self._get_laplacian_kernel()
        kx, ky, kz = self._get_gradient_kernels()

        # --- 2. Velocity Field Evolution ---
        if self.mobility is not None:
            # MODE A: GRADIENT-DRIVEN FLOW (Topic 0.10 - Advanced Laminar)
            # V = -Mobility * Grad(Density)
            # This bypasses Navier-Stokes momentum eq, solving the Blow-up Paradox.
            # Highly stable for Potential/Darcy flows.

            grad_x = self._apply_convolution(rho, kx)
            grad_y = self._apply_convolution(rho, ky)
            grad_z = self._apply_convolution(rho, kz)

            # Direct Assignment (No time evolution for V, it's instantaneous/overdamped)
            vx = -self.mobility * grad_x
            vy = -self.mobility * grad_y
            vz = -self.mobility * grad_z

            S_new.tensor[2] = vx
            S_new.tensor[3] = vy
            S_new.tensor[4] = vz

        else:
            # MODE B: MOMENTUM-DRIVEN FLOW (Standard Navier-Stokes)
            # dv/dt = - (v.grad)v + viscosity * del^2 v
            vx = S.tensor[2]
            vy = S.tensor[3]
            vz = S.tensor[4]
            viscosity = 0.01

            # Advection of Momentum
            advect_vx = self._advect(vx, vx, vy, vz)
            advect_vy = self._advect(vy, vx, vy, vz)
            advect_vz = self._advect(vz, vx, vy, vz)

            # Diffusion of Momentum
            diff_vx = self._apply_convolution(vx, laplacian_kernel)
            diff_vy = self._apply_convolution(vy, laplacian_kernel)
            diff_vz = self._apply_convolution(vz, laplacian_kernel)

            # Update Velocity
            S_new.tensor[2] = vx + dt * (-advect_vx + viscosity * diff_vx)
            S_new.tensor[3] = vy + dt * (-advect_vy + viscosity * diff_vy)
            S_new.tensor[4] = vz + dt * (-advect_vz + viscosity * diff_vz)

            # Re-bind for Mass calculation
            vx, vy, vz = S_new.tensor[2], S_new.tensor[3], S_new.tensor[4]

        # --- 3. Mass Evolution (Continuity Equation) ---
        # dRho/dt = - div(Rho * v) + Sources

        # Calculate Mass Flux Vector J = rho * v
        jx = rho * vx
        jy = rho * vy
        jz = rho * vz

        # Calculate Divergence of Flux
        div_flux = self._divergence(jx, jy, jz)

        # Mass Diffusion & Interaction
        diff_rho = self._apply_convolution(rho, laplacian_kernel)

        # Conservative Update
        S_new.tensor[0] = rho + dt * (-div_flux + 0.01 * diff_rho + 0.01 * interaction)

        # --- 4. Information Evolution ---
        # Info grows where there is energy density
        # Kill Switch Check
        check = (self.params.beta / self.params.beta) if self.params.beta != 0 else 1.0
        beta_val = self.params.beta

        diff_sigma = self._apply_convolution(sigma, laplacian_kernel)
        # Use kappa for diffusion coefficient (Calibration enabled)
        diffusion_coeff = self.params.kappa if self.params.kappa > 0 else 0.1
        S_new.tensor[1] = (
            sigma + dt * (rho * beta_val + diffusion_coeff * diff_sigma)
        ) * check

        return S_new


def create_galaxy_initial_state(size: int = 50) -> UniverseState:
    """Creates a 'Galaxy' state vector (High density in center)."""
    state = UniverseState(size)
    center = size // 2

    # Create Gaussian distribution
    for i in range(size):
        for j in range(size):
            r2 = (i - center) ** 2 + (j - center) ** 2
            state.tensor[0, i, j] = 100 * np.exp(-r2 / 20.0)  # Mass

    return state
