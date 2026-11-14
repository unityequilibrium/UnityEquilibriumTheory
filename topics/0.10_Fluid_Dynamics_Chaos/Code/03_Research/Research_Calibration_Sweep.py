"""
UET Natural Parameter Verification (Topic 0.10)
==============================================
Verify that UET parameters derived from NIST physical constants (Zero Curve Fitting)
yield accurate physical velocity profiles.

This script replaces the legacy "Parameter Sweep" with a direct physical mapping.
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
import json
from pathlib import Path
import sys
import importlib

# Robust Root Finding
from docs import ROOT_PATH

root_path = ROOT_PATH

# Add Topic Directory to sys.path to allow sibling imports (01_Engine)
topic_dir = root_path / "docs" / "topics" / "0.10_Fluid_Dynamics_Chaos" / "Code"
if str(topic_dir) not in sys.path:
    sys.path.append(str(topic_dir))

from docs.core.uet_glass_box import UETPathManager

UETFluidSolver = importlib.import_module("01_Engine.Engine_UET_2D").UETFluidSolver
PhysicalProperties = importlib.import_module("01_Engine.Engine_UET_2D").PhysicalProperties


def analytical_poiseuille(y, H, dP_dx, mu):
    """Analytical Poiseuille velocity profile."""
    return (dP_dx / (2 * mu)) * y * (H - y)


def verify_physical_fluid(name: str, physical: PhysicalProperties, steps: int = 5000):
    """Verify UET against a specific physical fluid."""
    print(f"\n🧪 VERIFYING FLUID: {name}")
    print("-" * 40)
    print(f"Density (rho): {physical.density} kg/m^3")
    print(f"Viscosity (mu): {physical.viscosity} Pa*s")

    # Target Analytical Solution
    H = 1.0
    dP_dx = 0.1
    y = np.linspace(0, H, 32)
    u_anal = analytical_poiseuille(y, H, dP_dx, physical.viscosity)
    target_u_max = np.max(u_anal)

    # Initialize UET Solver (Derives Kappa/Beta naturally)
    # Use lx=1.0 (L=H) for faster convergence across the domain
    solver = UETFluidSolver(nx=64, ny=32, lx=1.0, ly=H, dt=0.001, physical=physical)

    print(f"Derived kappa (Kappa): {solver.params.kappa:.6f}")
    print(f"Derived beta (Beta):  {solver.params.beta:.6f}")

    # Run to steady state
    solver.set_boundary_conditions("poiseuille")
    solver.run(steps=steps, verbose=False)

    # Extract UET results
    u_uet = solver.u[:, solver.nx // 2]
    u_uet_mag = np.max(np.abs(u_uet))

    # Check for NaNs or stagnation
    if np.isnan(u_uet).any() or u_uet_mag == 0:
        print("⚠️ Warning: Simulation failed to develop flux.")
        return None

    # Calculate Accuracy Metrics
    u_anal_norm = u_anal / target_u_max
    u_uet_norm = np.abs(u_uet) / u_uet_mag

    # Trim edges to avoid BC numerical noise
    correlation = np.corrcoef(u_anal_norm[2:-2], u_uet_norm[2:-2])[0, 1]
    magnitude_ratio = u_uet_mag / target_u_max

    print(f"Shape Correlation: {correlation:.4f}")
    print(f"Magnitude Ratio:   {magnitude_ratio:.6f}")

    return {
        "fluid": name,
        "correlation": correlation,
        "magnitude_ratio": magnitude_ratio,
        "kappa": solver.params.kappa,
        "beta": solver.params.beta,
        "u_max_uet": u_uet_mag,
        "u_max_target": target_u_max,
    }


def run_verification_suite():
    """Run verification for different fluid types."""
    print("=" * 60)
    print("UET NATURAL PARAMETER VERIFICATION (ZERO CURVE FITTING)")
    print("=" * 60)

    # 1. Baseline Run (M=1.0)
    water_low = PhysicalProperties(density=998.2, viscosity=1.002e-3, mobility=1.0)
    res_low = verify_physical_fluid("NIST Water (M=1.0)", water_low)

    # 2. Derived Mobility Run (Zero Curve Fitting)
    # The 'Informational-Physical Bridge' is now centrally managed in uet_parameters.py
    # and applied by the UETFluidSolver automatically.

    water_physical = PhysicalProperties(density=998.2, viscosity=1.002e-3)
    res_water = verify_physical_fluid("Water (Zero Curve Fitting)", water_physical)

    # 3. Glycerin Comparison (High Viscosity)
    glycerin_physical = PhysicalProperties(density=1260.0, viscosity=1.49)
    res_glycerin = verify_physical_fluid(
        "Glycerin (Zero Curve Fitting)", glycerin_physical, steps=3000
    )

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    if res_water:
        print(f"Water Accuracy (Shape): {res_water['correlation']:.4f}")
        print(f"Water Accuracy (Mag):   {res_water['magnitude_ratio']:.4f}")
    if res_glycerin:
        print(f"Glycerin Accuracy:      {res_glycerin['correlation']:.4f}")

    # Save results
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.10_Fluid_Dynamics_Chaos",
        experiment_name="Research_Calibration_Sweep",
        pillar="03_Research",
        category="log",
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    from docs.core.uet_parameters import FLUID_MOBILITY_BRIDGE

    with open(result_dir / "physical_verification_results.json", "w") as f:
        json.dump(
            {
                "water": res_water,
                "glycerin": res_glycerin,
                "bridge_constant": FLUID_MOBILITY_BRIDGE,
            },
            f,
            indent=2,
            default=str,
        )

    print(f"\n📊 Results saved to: {result_dir / 'physical_verification_results.json'}")


if __name__ == "__main__":
    run_verification_suite()
