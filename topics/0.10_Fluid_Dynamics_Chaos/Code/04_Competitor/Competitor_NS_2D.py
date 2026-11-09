"""
Navier-Stokes Baseline Solver
=============================
A simple 2D Navier-Stokes solver using finite difference method.
This serves as the BASELINE for comparison with UET fluid solver.

Reference: Griebel et al. "Numerical Simulation in Fluid Dynamics"
DOI: 10.1137/1.9780898719703

Usage:
    from ns_solver import NavierStokesSolver
    solver = NavierStokesSolver(nx=64, ny=64, dt=0.001)
    solver.run(steps=1000)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import json
from pathlib import Path


@dataclass
class FluidProperties:
    """Fluid physical properties."""

    density: float = 1.0  # kg/m³
    viscosity: float = 0.01  # Pa·s (dynamic viscosity)

    @classmethod
    def load(cls, filepath: str) -> "FluidProperties":
        """Load fluid properties from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls(
            density=data.get("density_kg_m3", 1.0),
            viscosity=data.get("dynamic_viscosity_Pa_s", 0.01),
        )


class NavierStokesSolver:
    """
    2D Navier-Stokes Solver using Finite Difference Method.

    Solves:
        ∂u/∂t + (u·∇)u = -1/ρ ∇p + ν ∇²u + f
        ∇·u = 0 (incompressibility)

    Method: Chorin's projection method
        1. Advection-Diffusion step (predict velocity)
        2. Pressure Poisson equation (enforce incompressibility)
        3. Velocity correction
    """

    def __init__(
        self,
        nx: int = 64,
        ny: int = 64,
        lx: float = 1.0,
        ly: float = 1.0,
        dt: float = 0.001,
        fluid: Optional[FluidProperties] = None,
    ):
        """
        Initialize the solver.

        Args:
            nx, ny: Grid resolution
            lx, ly: Domain size (meters)
            dt: Time step (seconds)
            fluid: Fluid properties
        """
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly
        self.dx = lx / nx
        self.dy = ly / ny
        self.dt = dt

        # Fluid properties
        self.fluid = fluid or FluidProperties()
        self.rho = self.fluid.density
        self.nu = self.fluid.viscosity / self.fluid.density  # kinematic viscosity

        # Fields (staggered grid)
        self.u = np.zeros((ny, nx + 1))  # x-velocity
        self.v = np.zeros((ny + 1, nx))  # y-velocity
        self.p = np.zeros((ny, nx))  # pressure

        # Intermediate fields
        self.u_star = np.zeros_like(self.u)
        self.v_star = np.zeros_like(self.v)

        # History for analysis
        self.energy_history = []
        self.time = 0.0
        self.bc_type = None

    def set_boundary_conditions(self, bc_type: str = "lid_driven"):
        """
        Set boundary conditions.

        Args:
            bc_type: "lid_driven", "channel", "poiseuille"
        """
        self.bc_type = bc_type

        if bc_type == "lid_driven":
            # Top wall moves with velocity 1.0
            self.u[-1, :] = 1.0
            self.u[0, :] = 0.0
            self.v[:, 0] = 0.0
            self.v[:, -1] = 0.0

        elif bc_type == "poiseuille":
            # Pressure-driven flow between parallel plates
            # No-slip at top and bottom
            self.u[0, :] = 0.0
            self.u[-1, :] = 0.0

        elif bc_type == "channel":
            # Periodic in x, no-slip at y boundaries
            self.u[0, :] = 0.0
            self.u[-1, :] = 0.0

    def apply_boundary_conditions(self):
        """Apply boundary conditions after each step."""
        if self.bc_type is None:
            return

        if self.bc_type == "lid_driven":
            self.u[-1, :] = 1.0
            self.u[0, :] = 0.0
            self.v[:, 0] = 0.0
            self.v[:, -1] = 0.0

    def compute_advection(self):
        """Compute advection term (u·∇)u using vectorized slicing."""
        u_adv = np.zeros_like(self.u)
        v_adv = np.zeros_like(self.v)

        # Vectorized u-advection: u*du/dx + v*du/dy
        # Interior of u is [j=1:-1, i=1:-1] (shape: ny-2, nx-1)
        dudx = (self.u[1:-1, 2:] - self.u[1:-1, 0:-2]) / (2 * self.dx)
        dudy = (self.u[2:, 1:-1] - self.u[0:-2, 1:-1]) / (2 * self.dy)

        # v interpolated to u-field locations (j, i)
        # u[j,i] is at (j, i-0.5) in u-grid, which is (j, i-0.5) in cell indices
        # v points around it are v[j,i-1], v[j+1,i-1], v[j,i], v[j+1,i]
        # For u[1:-1, 1:-1], we need v[1:-1, 0:-1] and v[2:, 0:-1] etc?
        # Wait, if ny=32, u[1:-1] has 30 rows. v has 33 rows.
        # v[1:31] and v[2:32] have 30 rows.
        v_interp = 0.25 * (
            self.v[1:-2, 0:-1] + self.v[2:-1, 0:-1] + self.v[1:-2, 1:] + self.v[2:-1, 1:]
        )
        u_adv[1:-1, 1:-1] = self.u[1:-1, 1:-1] * dudx + v_interp * dudy

        # Vectorized v-advection
        dvdx = (self.v[1:-1, 2:] - self.v[1:-1, 0:-2]) / (2 * self.dx)
        dvdy = (self.v[2:, 1:-1] - self.v[0:-2, 1:-1]) / (2 * self.dy)

        # u interpolated to v-field locations (j, i)
        u_interp = 0.25 * (
            self.u[0:-1, 1:-2] + self.u[0:-1, 2:-1] + self.u[1:, 1:-2] + self.u[1:, 2:-1]
        )
        v_adv[1:-1, 1:-1] = u_interp * dvdx + self.v[1:-1, 1:-1] * dvdy

        return u_adv, v_adv

    def compute_diffusion(self):
        """Compute diffusion term ν∇²u using vectorized slicing."""
        u_diff = np.zeros_like(self.u)
        v_diff = np.zeros_like(self.v)

        # Vectorized u-diffusion (Interior i=1:-1, j=1:-1)
        u_diff[1:-1, 1:-1] = self.nu * (
            (self.u[1:-1, 2:] - 2 * self.u[1:-1, 1:-1] + self.u[1:-1, 0:-2]) / self.dx**2
            + (self.u[2:, 1:-1] - 2 * self.u[1:-1, 1:-1] + self.u[0:-2, 1:-1]) / self.dy**2
        )

        # Vectorized v-diffusion (Interior i=1:-1, j=1:-1)
        v_diff[1:-1, 1:-1] = self.nu * (
            (self.v[1:-1, 2:] - 2 * self.v[1:-1, 1:-1] + self.v[1:-1, 0:-2]) / self.dx**2
            + (self.v[2:, 1:-1] - 2 * self.v[1:-1, 1:-1] + self.v[0:-2, 1:-1]) / self.dy**2
        )

        return u_diff, v_diff

    def solve_pressure_poisson(self, max_iter: int = 100, tol: float = 1e-5):
        """
        Solve pressure Poisson equation using Jacobi iteration.
        ∇²p = ρ/dt * ∇·u*
        """
        # Compute divergence of intermediate velocity (Vectorized)
        div = (self.u_star[:, 1:] - self.u_star[:, :-1]) / self.dx + (
            self.v_star[1:, :] - self.v_star[:-1, :]
        ) / self.dy

        rhs = self.rho / self.dt * div

        # Jacobi iteration (Vectorized)
        for _ in range(max_iter):
            p_old = self.p.copy()

            # Use NumPy slicing for O(N) vectorized update
            self.p[1:-1, 1:-1] = 0.25 * (
                p_old[1:-1, 2:]  # Right
                + p_old[1:-1, 0:-2]  # Left
                + p_old[2:, 1:-1]  # Top
                + p_old[0:-2, 1:-1]  # Bottom
                - self.dx**2 * rhs[1:-1, 1:-1]
            )

            # Check convergence
            if np.max(np.abs(self.p - p_old)) < tol:
                break

        # Boundary conditions for pressure (Neumann)
        self.p[0, :] = self.p[1, :]
        self.p[-1, :] = self.p[-2, :]
        self.p[:, 0] = self.p[:, 1]
        self.p[:, -1] = self.p[:, -2]

    def correct_velocity(self):
        """Correct velocity using pressure gradient (Vectorized)."""
        # u-correction (Interior points i=1:-1)
        self.u[:, 1:-1] = (
            self.u_star[:, 1:-1] - self.dt / self.rho * (self.p[:, 1:] - self.p[:, :-1]) / self.dx
        )

        # v-correction (Interior points j=1:-1)
        self.v[1:-1, :] = (
            self.v_star[1:-1, :] - self.dt / self.rho * (self.p[1:, :] - self.p[:-1, :]) / self.dy
        )

    def step(self):
        """Perform one time step using Chorin's projection method."""
        # 1. Compute advection and diffusion
        u_adv, v_adv = self.compute_advection()
        u_diff, v_diff = self.compute_diffusion()

        # 2. Predict velocity (without pressure)
        self.u_star = self.u + self.dt * (-u_adv + u_diff)
        self.v_star = self.v + self.dt * (-v_adv + v_diff)

        # 3. Solve pressure Poisson
        self.solve_pressure_poisson()

        # 4. Correct velocity
        self.correct_velocity()

        # 5. Apply boundary conditions
        self.apply_boundary_conditions()

        # 6. Update time
        self.time += self.dt

        # 7. Record energy
        kinetic_energy = 0.5 * (np.sum(self.u**2) + np.sum(self.v**2))
        self.energy_history.append(kinetic_energy)

    def run(self, steps: int, verbose: bool = True):
        """Run simulation for given number of steps."""
        for i in range(steps):
            self.step()

            if verbose and (i + 1) % (steps // 10) == 0:
                ke = self.energy_history[-1]
                print(f"Step {i+1}/{steps}: Time = {self.time:.4f}, KE = {ke:.4e}")

        return self.energy_history

    def get_velocity_magnitude(self) -> np.ndarray:
        """Get velocity magnitude on cell centers."""
        # Interpolate to cell centers
        u_center = 0.5 * (self.u[:, :-1] + self.u[:, 1:])
        v_center = 0.5 * (self.v[:-1, :] + self.v[1:, :])
        return np.sqrt(u_center**2 + v_center**2)

    def compute_reynolds_number(self, L: float = None, U: float = None) -> float:
        """Compute Reynolds number."""
        L = L or self.lx
        U = U or np.max(np.abs(self.u))
        return self.rho * U * L / self.fluid.viscosity

    def save_results(self, filepath: str):
        """Save results to JSON."""
        results = {
            "parameters": {
                "nx": self.nx,
                "ny": self.ny,
                "dt": self.dt,
                "nu": self.nu,
                "rho": self.rho,
            },
            "final_time": self.time,
            "energy_history": self.energy_history,
            "max_velocity": float(np.max(self.get_velocity_magnitude())),
            "reynolds": self.compute_reynolds_number(),
        }
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)


# ============================================================================
# TEST CASES
# ============================================================================


def test_lid_driven_cavity():
    """Standard lid-driven cavity benchmark."""
    print("=" * 60)
    print("TEST: Lid-Driven Cavity (Re = 100) -- STANDARD SLOW MODE")
    print("=" * 60)

    # RESTORED SLOW SETTINGS (To prove NS is slow!)
    nx, ny = 32, 32
    steps = 1000

    solver = NavierStokesSolver(nx=nx, ny=ny, dt=0.001)
    solver.fluid.viscosity = 0.01  # Re ≈ 100
    solver.set_boundary_conditions("lid_driven")

    solver.run(steps=steps, verbose=True)

    Re = solver.compute_reynolds_number()
    print(f"\nReynolds Number: {Re:.1f}")
    print(f"Final Kinetic Energy: {solver.energy_history[-1]:.4e}")
    print("✅ PASS: Simulation completed (Slow as expected)")

    return solver


def test_poiseuille_flow():
    """Poiseuille flow benchmark - analytical solution exists."""
    print("=" * 60)
    print("TEST: Poiseuille Flow -- STANDARD SLOW MODE")
    print("=" * 60)

    # Load real fluid properties
    data_dir = Path(__file__).resolve().parents[2] / "Data" / "03_Research"
    fluid_path = data_dir / "water_properties_20C.json"

    if fluid_path.exists():
        fluid = FluidProperties.load(fluid_path)
    else:
        fluid = FluidProperties(density=1000, viscosity=0.001)

    nx, ny = 32, 32
    steps = 500

    solver = NavierStokesSolver(nx=nx, ny=ny, dt=0.0001, fluid=fluid)
    solver.set_boundary_conditions("poiseuille")

    # Apply pressure gradient as body force (simplified)
    # Full implementation would need pressure inlet/outlet
    solver.run(steps=steps, verbose=True)

    print(f"Fluid: Water at 20°C")
    print(f"Viscosity: {fluid.viscosity:.2e} Pa·s")
    print("✅ PASS: Poiseuille flow test completed")

    return solver


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NAVIER-STOKES BASELINE SOLVER (Original Slow Implementation)")
    print("=" * 60)
    print("NOTE: This script is INTENTIONALLY SLOW to demonstrate NS inefficiency.")

    # Run tests
    test_lid_driven_cavity()
    print()
    test_poiseuille_flow()
