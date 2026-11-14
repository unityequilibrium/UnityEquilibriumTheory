"""
UET Fluid Dynamics Test - Brownian Motion
==========================================
Tests UET prediction for Brownian motion (Einstein relation).
Data: Perrin 1908 Nobel Prize work.
"""

import sys
from pathlib import Path
import math
import json

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
# The script is at: .../docs/topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/Research_Brownian.py
# docs is 4 levels up from this file.
# The repo root is the parent folder of docs.
try:
    # Attempt to go up to find the parent of docs
    repo_root = current_path
    for _ in range(10):
        if (
            repo_root / "docs"
        ).exists() and not repo_root.name == "docs":
            break
        repo_root = repo_root.parent
except Exception:
    # Fallback to fixed depth if search fails
    repo_root = current_path.parents[5]

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Engine Import via Importlib to bypass folder naming issues (0.10)
try:
    import importlib.util

    # Corrected path construction to avoid duplication
    engine_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.10_Fluid_Dynamics_Chaos"
        / "Code"
        / "01_Engine"
        / "Engine_UET_2D.py"
    )

    if not engine_file.exists():
        raise FileNotFoundError(f"Engine file not found at: {engine_file}")

    spec = importlib.util.spec_from_file_location("Engine_UET_2D", str(engine_file))
    engine_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_mod)
    UETFluidSolver = engine_mod.UETFluidSolver
    PhysicalProperties = engine_mod.PhysicalProperties
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)

# Initialize Engine with water context to get viscosity
engine = UETFluidSolver(physical=PhysicalProperties(viscosity=1.002e-3))


def perrin_1908_data():
    """Load Perrin's experimental data from standardized Data pillar."""
    # Data is relative to docs
    data_file = (
        repo_root
        / "docs"
        / "topics"
        / "0.10_Fluid_Dynamics_Chaos"
        / "Data"
        / "03_Research"
        / "perrin_1908_data.json"
    )
    if data_file.exists():
        with open(data_file, "r") as f:
            return json.load(f)
    # Nobel fallback
    return {
        "temperature_K": 293.15,
        "particle_radius_m": 2.1e-07,
        "viscosity_Pa_s": 1.002e-03,
        "diffusion_coefficient_measured_m2_s": 8.7e-13,
        "avogadro_measured": 6.4e23,
    }


def uet_diffusion_coefficient(T, eta, r):
    """Delegated to Engine."""
    return engine.compute_brownian_diffusion(T, r)


def uet_mean_squared_displacement(D, t):
    """MSD calculation (pure geometric)."""
    return 6 * D * t


def run_test():
    """Run Brownian motion test."""
    print("=" * 70)
    print("UET BROWNIAN MOTION TEST")
    print("Data: Perrin 1908 (Nobel Prize 1926)")
    print("=" * 70)

    data = perrin_1908_data()
    T = data["temperature_K"]
    eta = data["viscosity_Pa_s"]
    r = data["particle_radius_m"]
    D_exp = data["diffusion_coefficient_measured_m2_s"]

    D_uet = uet_diffusion_coefficient(T, eta, r)

    print("\n[1] DIFFUSION COEFFICIENT")
    print("-" * 50)
    print(f"  Temperature:     {T} K")
    print(f"  Viscosity:       {eta:.3e} Pa*s")
    print(f"  Particle radius: {r*1e6:.1f} microns")
    print(f"")
    print(f"  Perrin measured: D = {D_exp:.2e} m^2/s")
    print(f"  UET predicted:   D = {D_uet:.2e} m^2/s")

    error = abs(D_uet - D_exp) / D_exp * 100
    print(f"\n  Error: {error:.1f}%")

    passed = error < 20
    print(f"  {'PASS' if passed else 'FAIL'}")

    print("\n[2] MEAN SQUARED DISPLACEMENT")
    print("-" * 50)

    times = [1, 10, 60, 600]  # seconds
    print("| Time (s) | MSD (micron^2) |")
    print("|:---------|:---------------|")

    for t in times:
        msd = uet_mean_squared_displacement(D_uet, t)
        msd_um2 = msd * 1e12
        print(f"| {t:8} | {msd_um2:14.2f} |")

    print("\n[3] UET INTERPRETATION")
    print("-" * 50)
    print(
        """
    Brownian motion in UET:
    1. Particles (C field) are in thermal equilibrium with info field (I)
    2. Fluctuations scale with k_B*T (Axiomatic Link)
    3. Einstein relation D = k_B*T/6pi*eta*r is a natural UET symmetry.
    """
    )

    print("=" * 70)
    print(f"RESULT: {'PASS' if passed else 'NEEDS CALIBRATION'}")
    print("=" * 70)

    return passed


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
