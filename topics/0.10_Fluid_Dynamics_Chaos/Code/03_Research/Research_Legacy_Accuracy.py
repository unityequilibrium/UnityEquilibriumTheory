"""
Accuracy Validation: Poiseuille Flow
=====================================
Compare NS and UET against analytical solution for Poiseuille flow.

Poiseuille Flow Analytical Solution:
    u(y) = (ΔP / 2μL) * y * (H - y)

    Where:
    - ΔP = pressure drop
    - μ = dynamic viscosity
    - L = pipe length
    - H = pipe height
    - y = position from bottom wall

This provides GROUND TRUTH for accuracy comparison.
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


import numpy as np
import sys
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager

import json
import importlib


# Setup local imports for Topic 0.10
topic_path = root_path / "docs" / "topics" / "0.10_Fluid_Dynamics_Chaos"
engine_path = topic_path / "Code" / "01_Engine"
competitor_path = topic_path / "Code" / "04_Competitor"

if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))
if str(competitor_path) not in sys.path:
    sys.path.insert(0, str(competitor_path))

try:
    from Competitor_NS_2D import NavierStokesSolver, FluidProperties
    from Engine_UET_2D import UETFluidSolver, UETParameters
except ImportError as e:
    print(f"CRITICAL: Engine/Competitor import failed: {e}")
    sys.exit(1)


def analytical_poiseuille(y: np.ndarray, H: float, dP_dx: float, mu: float) -> np.ndarray:
    """
    Analytical solution for Poiseuille flow.

    u(y) = (dP/dx) / (2μ) * y * (H - y)
    """
    return (dP_dx / (2 * mu)) * y * (H - y)


def test_ns_accuracy():
    """Test NS solver accuracy against analytical Poiseuille."""
    print("=" * 60)
    print("ACCURACY TEST: NS vs Analytical Poiseuille")
    print("=" * 60)

    # Parameters
    nx, ny = 64, 32
    H = 1.0  # Channel height
    L = 2.0  # Channel length

    # Fluid properties (water)
    data_dir = Path(__file__).resolve().parents[2] / "Data" / "03_Research"
    try:
        fluid = FluidProperties.load(data_dir / "water_properties_20C.json")
    except:
        fluid = FluidProperties(density=998.2, viscosity=1.002e-3)

    mu = fluid.viscosity
    rho = fluid.density

    # Pressure gradient (moderate to keep Re low for validation)
    dP_dx = 0.1  # Pa/m

    # Expected max velocity (at center)
    u_max_analytical = (dP_dx / (2 * mu)) * (H / 2) * (H - H / 2)
    print(f"Analytical u_max: {u_max_analytical:.4e} m/s")

    # Run NS solver
    solver = NavierStokesSolver(nx=nx, ny=ny, lx=L, ly=H, dt=0.0001, fluid=fluid)
    solver.set_boundary_conditions("poiseuille")

    # Apply body force equivalent to pressure gradient
    # F = -dP/dx / rho
    body_force = dP_dx / rho

    # Run with body force
    steps = 500
    for i in range(steps):
        solver.step()
        # Add body force to u velocity
        solver.u[:, 1:-1] += body_force * solver.dt
        solver.apply_boundary_conditions()

    # Extract centerline velocity profile
    y = np.linspace(0, H, ny)
    u_numerical = solver.u[:, nx // 2]  # Velocity at mid-length

    # Analytical solution
    u_analytical = analytical_poiseuille(y[1:-1], H, dP_dx, mu)

    # Calculate error
    error = np.mean(np.abs(u_numerical[1:-1] - u_analytical)) / np.max(np.abs(u_analytical)) * 100

    print(f"NS Average Error: {error:.2f}%")

    return {
        "solver": "NS",
        "error_percent": error,
        "u_analytical_max": u_max_analytical,
        "u_numerical_max": np.max(u_numerical),
    }


def test_uet_accuracy():
    """Test UET solver accuracy against analytical Poiseuille."""
    print("\n" + "=" * 60)
    print("ACCURACY TEST: UET vs Analytical Poiseuille")
    print("=" * 60)

    # Parameters
    nx, ny = 64, 32
    H = 1.0
    L = 2.0

    # UET parameters tuned for Poiseuille-like flow
    params = UETParameters(kappa=0.001, beta=0.01, alpha=1.0, C0=1.0)
    solver = UETFluidSolver(nx=nx, ny=ny, lx=L, ly=H, dt=0.0001, params=params)

    # Set up pressure-driven flow via density gradient
    solver.set_boundary_conditions("poiseuille")

    # Run
    steps = 500
    solver.run(steps=steps, verbose=False)

    # Extract velocity profile (derived from density gradient)
    y = np.linspace(0, H, ny)

    # UET velocity is derived from -∇C
    # For comparison, we look at the y-profile of u at mid-x
    u_uet = solver.u[:, nx // 2]

    # Normalize to match Poiseuille profile shape
    if np.max(np.abs(u_uet)) > 0:
        u_uet_normalized = u_uet / np.max(np.abs(u_uet))
    else:
        u_uet_normalized = u_uet

    # Analytical profile (normalized)
    u_analytical = analytical_poiseuille(y[1:-1], H, 1.0, 1.0)
    u_analytical_normalized = u_analytical / np.max(np.abs(u_analytical))

    # Calculate shape error (correlation)
    if len(u_uet_normalized[1:-1]) == len(u_analytical_normalized):
        correlation = np.corrcoef(u_uet_normalized[1:-1], u_analytical_normalized)[0, 1]
    else:
        correlation = 0.0

    print(f"UET Profile Correlation: {correlation:.4f}")
    print(f"(1.0 = perfect parabolic profile)")

    return {
        "solver": "UET",
        "profile_correlation": correlation,
        "note": "UET uses density field, velocity is derived",
    }


def run_accuracy_validation():
    """Run all accuracy tests."""
    print("\n" + "=" * 70)
    print("ACCURACY VALIDATION: NS and UET vs Analytical Solutions")
    print("=" * 70)

    results = {
        "test_type": "accuracy_validation",
        "benchmark": "Poiseuille Flow (Analytical)",
        "results": [],
    }

    # Run tests
    ns_result = test_ns_accuracy()
    results["results"].append(ns_result)

    uet_result = test_uet_accuracy()
    results["results"].append(uet_result)

    # Summary
    print("\n" + "=" * 60)
    print("ACCURACY SUMMARY")
    print("=" * 60)
    print(f"NS Error: {ns_result['error_percent']:.2f}%")
    print(f"UET Correlation: {uet_result['profile_correlation']:.4f}")

    # Save
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.10_Fluid_Dynamics_Chaos",
        experiment_name="Research_Legacy_Accuracy",
        pillar="03_Research",
        category="log",
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    with open(result_dir / "accuracy_validation.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📊 Results saved to: {result_dir / 'accuracy_validation.json'}")

    return results


if __name__ == "__main__":
    run_accuracy_validation()
