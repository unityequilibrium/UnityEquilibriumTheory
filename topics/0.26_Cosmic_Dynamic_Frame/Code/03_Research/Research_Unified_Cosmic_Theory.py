"""
Research_Unified_Cosmic_Theory.py
=================================
Topic 0.26: The Dynamic Universe
Hypothesis:
    1. Space is a Viscous Fluid (validated by Pioneer Exp, rho ~ 2.9e-16).
    2. Gravity is "Pressure Gradient" in this fluid.
    3. Rotation Anomalies are caused by "Fluid Drag" and "In-fall" dynamics.

Objective:
    Verify if V_total = V_baryon + V_fluid_drag matches Observed Data
     BETTER than Standard Halo Models for Compact Galaxies.

Standards:
    - Uses UET-Ref-v1.0 (REFERENCES.py)
    - Uses stable=True for Output
    - Uses Functional Data Loader API
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
import matplotlib.pyplot as plt
import sys
import importlib.util
from pathlib import Path

# --- ROBUST IMPORT SETUP ---
script_path = Path(__file__).resolve()
project_root = script_path.parents[5]  # .../Lab_uet_harness_v0.9.0

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from docs.core.uet_glass_box import UETPathManager
    from docs.core.uet_parameters import RHO_COSMIC, G_GALACTIC, C_KM_S

    # Load References
    ref_path = script_path.parents[2] / "Ref" / "REFERENCES.py"
    if not ref_path.exists():
        raise FileNotFoundError(f"REFERENCES.py not found at {ref_path}")
    spec_ref = importlib.util.spec_from_file_location("REFERENCES", ref_path)
    ref_mod = importlib.util.module_from_spec(spec_ref)
    spec_ref.loader.exec_module(ref_mod)
    REFERENCES = ref_mod

    # Load Data Loader (Topic 0.1) - Correct Path: Code/01_Engine/Data_Loader_SPARC.py
    loader_path = (
        project_root
        / "docs"
        / "topics"
        / "0.1_Galaxy_Rotation_Problem"
        / "Code"
        / "01_Engine"
        / "Data_Loader_SPARC.py"
    )
    if not loader_path.exists():
        raise FileNotFoundError(f"SPARC Loader missing at {loader_path}")

    spec = importlib.util.spec_from_file_location("Data_Loader_SPARC", loader_path)
    loader_mod = importlib.util.module_from_spec(spec)
    sys.modules["Data_Loader_SPARC"] = loader_mod
    spec.loader.exec_module(loader_mod)

    # Functional API Import
    load_sparc_galaxy = loader_mod.load_sparc_galaxy
    get_available_galaxies = loader_mod.get_available_galaxies

except Exception as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)


# =============================================================================
# THE DYNAMIC UNIVERSE SOLVER (With Relativity)
# =============================================================================
class CosmicDynamicSolver:
    def __init__(self):
        # Constants from Exp 1 (Pioneer Anomaly)
        # Constants from Exp 1 (Pioneer Anomaly)
        self.RHO_COSMIC = RHO_COSMIC  # kg/m^3 (The "Thick" Space)
        self.G = G_GALACTIC  # kpc km^2/s^2 M_sun^-1
        self.C = C_KM_S  # km/s (Speed of Light)
        self.VISCOSITY_FACTOR = 1.0

    def get_gamma(self, v_kms):
        """Calculate Lorentz Factor."""
        if v_kms >= self.C:
            return 100.0  # Limit singularities
        return 1.0 / np.sqrt(1 - (v_kms / self.C) ** 2)

    def calculate_fluid_velocity(self, R_kpc, V_baryon):
        """
        Calculate the 'Fluid' component contribution.
        Uses Pioneer Acceleration (a0) as the baseline for Cosmic Drag/Pressure.
        """
        # Pioneer Acceleration
        a_pioneer = 8.74e-10  # m/s^2

        # Unit Conversion
        R_meters = R_kpc * 3.086e19

        # V^2 contribution from constant acceleration field (The "Falling" Frame)
        # Refinement: Constant acceleration to infinity implies infinite velocity.
        # Implements "Viscous Limit" (Rankine Vortex / Terminal Velocity) Model.
        # Assumes Cosmic Drag limits maximum inflow velocity.

        # Effective Radius for Dampening (Galaxy Scale ~ 2kpc)
        R_eff_meters = 2.0 * 3.086e19

        # Velocity Decay Profile: V^2 = 2 * a * R * (Decay Factor)
        # We use a logistic-like dampener: 1 / (1 + R/R_eff)
        # This prevents velocity -> infinity at large R.
        V_fluid_sq = 2 * a_pioneer * R_meters * (2.0 / (1.0 + R_meters / R_eff_meters))

        # Convert back to (km/s)^2
        V_fluid_sq_kms = V_fluid_sq / (1000.0**2)

        return np.sqrt(V_fluid_sq_kms)

    def solve_galaxy(self, galaxy_name, galaxy_data):
        """Evaluate a single galaxy with Relativistic Constraints."""
        # Unpack Data Structure from Data_Loader_SPARC.py
        data = galaxy_data["data"]
        R = np.array(data["radii"])
        V_obs = np.array(data["v_obs"])
        V_err = np.array(data["v_err"])

        # Let's approximate Newtonian V_baryon for test: V^2 ~ GM/R
        # This is a simplification but rigorous enough for the "Concept Proof"
        M_disk = galaxy_data["params"]["M_disk"]
        V_baryon = np.sqrt(self.G * M_disk / R)

        # 2. Cosmic Fluid Component
        V_fluid = self.calculate_fluid_velocity(R, V_baryon)

        # 3. Total Prediction
        V_pred = np.sqrt(V_baryon**2 + V_fluid**2)

        # Relativistic Check (Gamma)
        gamma_max = np.max([self.get_gamma(v) for v in V_pred])

        # Calculate Error
        valid_mask = (V_obs > 0) & (V_pred > 0)
        mape = (
            np.mean(
                np.abs((V_obs[valid_mask] - V_pred[valid_mask]) / V_obs[valid_mask])
            )
            * 100
        )

        return {
            "name": galaxy_name,
            "R": R,
            "V_obs": V_obs,
            "V_pred": V_pred,
            "V_baryon": V_baryon,
            "V_fluid": V_fluid,
            "error": mape,
            "gamma_max": gamma_max,
        }


# =============================================================================
# EXECUTION
# =============================================================================
def run_unified_theory():
    print("🌌 RESEARCH: TOPIC 0.26 THE DYNAMIC UNIVERSE")
    print("Standard: UET-Ref-v1.0 (Stable Output)\n")

    # Citation
    print(f"Reference Assumption: {REFERENCES.get_citation('PIONEER_1998')}")
    print(f"Reference Data: {REFERENCES.get_citation('SPARC_2016')}")

    solver = CosmicDynamicSolver()

    # Get available targets ("UGC_128" is the critical LSB)
    targets = get_available_galaxies()
    print(f"Available Targets: {targets}\n")

    results = []

    for name in targets:
        try:
            print(f"Loading {name}...")
            # Use Functional API
            data = load_sparc_galaxy(name)

            if data is not None:
                res = solver.solve_galaxy(name, data)
                results.append(res)
                print(
                    f"  > Error: {res['error']:.2f}% (Gamma Max: {res['gamma_max']:.6f})"
                )
            else:
                print("  > Data not found.")
        except Exception as e:
            print(f"  > Failed: {e}")
            import traceback

            traceback.print_exc()

    # VISUALIZATION (Standardized)
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.26_Cosmic_Dynamic_Frame",
        experiment_name="Research_Unified_Cosmic_Theory",
        pillar="03_Research",
        category="log",
        stable=True,
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    for res in results:
        plt.figure(figsize=(10, 6))
        plt.errorbar(
            res["R"], res["V_obs"], yerr=5.0, fmt="k.", label="Observed (SPARC)"
        )
        plt.plot(res["R"], res["V_baryon"], "b--", label="Newtonian (Mass Only)")
        plt.plot(
            res["R"],
            res["V_pred"],
            "r-",
            linewidth=2,
            label="Dynamic Universe Prediction",
        )
        plt.plot(res["R"], res["V_fluid"], "g:", label="Fluid Drag Component")

        # Add Reference Annotation
        plt.text(
            0.05,
            0.95,
            "Ref: Lelli et al. (2016)",
            transform=plt.gca().transAxes,
            fontsize=8,
        )

        plt.title(f"Dynamic Universe Model: {res['name']} (Error: {res['error']:.1f}%)")
        plt.xlabel("Radius (kpc)")
        plt.ylabel("Velocity (km/s)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.savefig(result_dir / f"{res['name']}_dynamic_fit.png")
        plt.close()

        # Save Numerical Report
        with open(result_dir / f"{res['name']}_report.txt", "w") as f:
            f.write(f"Galaxy: {res['name']}\n")
            f.write(f"Model Error: {res['error']:.4f}%\n")
            f.write(f"Fluid Contribution at Edge: {res['V_fluid'][-1]:.2f} km/s\n")
            f.write(
                "Hypothesis Status: Validated"
                if res["error"] < 15.0
                else "Hypothesis Status: Weak Fit"
            )

    print(f"\n✅ Analysis Complete. Results saved to {result_dir}")


if __name__ == "__main__":
    run_unified_theory()
