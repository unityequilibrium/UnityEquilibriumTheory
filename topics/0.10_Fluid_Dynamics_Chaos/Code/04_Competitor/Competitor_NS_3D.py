"""
3D Navier-Stokes Solver (Competitor)
=====================================
Isolating the 3D NS baseline for comparison with UET.
"""

import numpy as np


class NavierStokes3D:
    """Simplified 3D Navier-Stokes solver."""

    def __init__(
        self,
        nx: int = 16,
        ny: int = 16,
        nz: int = 16,
        dt: float = 0.001,
        nu: float = 0.01,
    ):
        self.nx, self.ny, self.nz = nx, ny, nz
        self.dx = self.dy = self.dz = 1.0 / nx
        self.dt = dt
        self.nu = nu

        # Velocity fields
        self.u = np.zeros((nz, ny, nx))
        self.v = np.zeros((nz, ny, nx))
        self.w = np.zeros((nz, ny, nx))
        self.p = np.zeros((nz, ny, nx))

        self.time = 0.0

    def set_lid_driven_bc(self, U_lid: float = 1.0):
        """Set 3D lid-driven cavity BC."""
        self.U_lid = U_lid
        self.u[-1, :, :] = U_lid

    def compute_laplacian_3d(self, f: np.ndarray) -> np.ndarray:
        """Compute 3D Laplacian."""
        lap = np.zeros_like(f)
        dx2 = self.dx**2

        # Interior points only
        lap[1:-1, 1:-1, 1:-1] = (
            (f[1:-1, 1:-1, 2:] - 2 * f[1:-1, 1:-1, 1:-1] + f[1:-1, 1:-1, :-2]) / dx2
            + (f[1:-1, 2:, 1:-1] - 2 * f[1:-1, 1:-1, 1:-1] + f[1:-1, :-2, 1:-1]) / dx2
            + (f[2:, 1:-1, 1:-1] - 2 * f[1:-1, 1:-1, 1:-1] + f[:-2, 1:-1, 1:-1]) / dx2
        )
        return lap

    def step(self):
        """Simplified Euler step with diffusion only for stability."""
        # Diffusion only (skip advection for stability)
        lap_u = self.compute_laplacian_3d(self.u)
        lap_v = self.compute_laplacian_3d(self.v)
        lap_w = self.compute_laplacian_3d(self.w)

        self.u += self.dt * self.nu * lap_u
        self.v += self.dt * self.nu * lap_v
        self.w += self.dt * self.nu * lap_w

        # Reapply BC
        self.u[-1, :, :] = self.U_lid
        self.u[0, :, :] = 0
        self.u[:, 0, :] = 0
        self.u[:, -1, :] = 0
        self.u[:, :, 0] = 0
        self.u[:, :, -1] = 0

        self.time += self.dt

    def get_max_gradient(self) -> float:
        """Get maximum gradient magnitude."""
        dudx = np.gradient(self.u, self.dx, axis=2)
        dudy = np.gradient(self.u, self.dx, axis=1)
        dudz = np.gradient(self.u, self.dx, axis=0)
        return float(np.max(np.sqrt(dudx**2 + dudy**2 + dudz**2)))

    def get_max_laplacian(self) -> float:
        """Get maximum Laplacian."""
        return float(np.max(np.abs(self.compute_laplacian_3d(self.u))))

    def is_smooth(self) -> bool:
        """Check if solution remains smooth."""
        return (
            np.isfinite(self.u).all()
            and np.isfinite(self.v).all()
            and np.isfinite(self.w).all()
            and np.max(np.abs(self.u)) < 1e10
        )
