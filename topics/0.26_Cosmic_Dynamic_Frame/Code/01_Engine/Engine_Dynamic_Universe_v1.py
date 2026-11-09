"""
Engine_Dynamic_Universe_v1.py
=============================
Topic: 0.26 The Dynamic Universe
Type: Master Engine (The Calculator)
Status: V1.3 (Tuned)

Philosophy:
    "The Universe is a Falling Fluid. Gravity is Pressure. Inertia is Drag."

Core Logic:
    Acceleration_Total = Acc_Newtonian + Acc_Fluid_Dynamic

    1. Acc_Newtonian: Standard GM/r^2 (Baryonic Mass)
    2. Acc_Fluid_Dynamic:
       - Base Magnitude: Derived from Pioneer Anomaly (a0 ~ 8.7e-10 m/s^2)
       - Scale Decay: A logistic function that dampens the viscosity at large scales (Interstellar vs Intergalactic density).

Usage:
    python Engine_Dynamic_Universe_v1.py
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

# =============================================================================
# 1. ROBUST ENVIRONMENT SETUP
# =============================================================================
script_path = Path(__file__).resolve()
project_root = script_path.parents[5]  # .../Lab_uet_harness_v0.9.0

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from docs.core.uet_glass_box import UETPathManager

    # Load References (Topic 0.26)
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
    print(f"CRITICAL ENGINE FAILURE (Import): {e}")
    sys.exit(1)


# =============================================================================
# 2. THE UNIFIED PHYSICS ENGINE
# =============================================================================
class DynamicUniverseEngine:
    def __init__(self):
        # Universal Constants
        self.G = 4.301e-6  # kpc km^2/s^2 M_sun^-1
        self.C = 299792.458  # km/s

        # Cosmic Parameters (The "Fine Tuning" of the Universe)
        self.A0_PIONEER = 8.74e-10  # m/s^2 (Measured by Anderson et al.)

        # Scale Decay Parameters (The "Fix" for the Paradox)
        # V1.3 Hypothesis: Tighter "Core" confinement?
        # Try R_SCALE = 1.0 kpc, Power = 2.0 (Inverse Square)
        self.R_SCALE_KPC = 1.0  # Tighter screening
        self.DECAY_POWER = 2.0  # Standard Inverse Square Field

    def get_decay_factor(self, R_kpc):
        """
        Calculates how much the Cosmic Viscosity 'thins out' at distance R.
        Model: Logistic-like or Power-law decay.
        """
        # Using a "Core Halo" style screening:
        # factor = 1 / (1 + (R / R_scale)^power )
        return 1.0 / (1.0 + (R_kpc / self.R_SCALE_KPC) ** self.DECAY_POWER)

    def calculate_Newtonian(self, R_kpc, M_disk_solar):
        """Standard Gravity."""
        # V^2 = GM/r
        # Avoid division by zero
        R_safe = np.maximum(R_kpc, 0.01)
        V_sq = self.G * M_disk_solar / R_safe
        return np.sqrt(V_sq)

    def calculate_CosmicFluid(self, R_kpc):
        """
        The 'Falling Universe' Component.
        V_fluid determined by Integrated Acceleration Field * Decay Factor.
        """
        # 1. Base Potential Energy from Constant Acceleration (Pioneer)
        # V^2 = 2 * a * d
        R_meters = R_kpc * 3.086e19
        V_base_sq_ms = 2 * self.A0_PIONEER * R_meters

        # 2. Apply Scale Decay (The Medium gets thinner)
        decay = self.get_decay_factor(R_kpc)
        V_effective_sq_ms = V_base_sq_ms * decay

        # 3. Convert to km/s
        V_fluid = np.sqrt(V_effective_sq_ms) / 1000.0
        return V_fluid

    def solve_system(self, name, data):
        """Solves the dynamics for a given system (Galaxy/Star)."""
        # Unpack
        raw_data = data["data"]
        R = np.array(raw_data["radii"])
        V_obs = np.array(raw_data["v_obs"])
        M_disk = data["params"]["M_disk"]

        # 1. Newtonian Term
        V_newton = self.calculate_Newtonian(R, M_disk)

        # 2. Fluid Term
        V_fluid = self.calculate_CosmicFluid(R)

        # 3. Unified Result (Vector Sum / Energy Sum)
        # Hypothesis: V_total^2 = V_newton^2 + V_fluid^2
        V_total = np.sqrt(V_newton**2 + V_fluid**2)

        # Validation
        valid = V_obs > 0
        error = np.mean(np.abs((V_obs[valid] - V_total[valid]) / V_obs[valid])) * 100

        return {
            "name": name,
            "R": R,
            "V_obs": V_obs,
            "V_newton": V_newton,
            "V_fluid": V_fluid,
            "V_total": V_total,
            "error": error,
        }


# =============================================================================
# 3. REPORTING & VISUALIZATION
# =============================================================================
def generate_report(results, output_dir):
    print("\n📊 ENGINE REPORT (V1.3 Tuned):")
    print(f"{'Target':<10} | {'Error':<8} | {'Status'}")
    print("-" * 30)

    for res in results:
        print(
            f"{res['name']:<10} | {res['error']:6.2f}% | {'✅' if res['error'] < 20 else '⚠️'}"
        )

        # Plot
        plt.figure(figsize=(10, 6))
        plt.style.use("dark_background")

        plt.errorbar(res["R"], res["V_obs"], yerr=5, fmt="wo", label="Observed (Real)")
        plt.plot(res["R"], res["V_newton"], "c--", label="Newtonian (Static)")
        plt.plot(res["R"], res["V_fluid"], "m:", label="Cosmic Fluid (Dynamic)")
        plt.plot(
            res["R"], res["V_total"], "y-", linewidth=2, label="Unified Engine v1.3"
        )

        plt.title(f"Dynamic Universe V1.3: {res['name']} (Inv.Sq Decay, R_s=1kpc)")
        plt.xlabel("Radius (kpc)")
        plt.ylabel("Velocity (km/s)")
        plt.legend()
        plt.grid(True, alpha=0.2)

        save_path = output_dir / f"{res['name']}_engine_v1_3.png"
        plt.savefig(save_path)
        plt.close()
        # print(f"    > Plot saved: {save_path.name}")


def run_engine():
    print("⚙️  STARTING ENGINE: DYNAMIC UNIVERSE V1.3")
    print("---------------------------------------")

    output_dir = UETPathManager.get_result_dir(
        topic_id="0.26_Cosmic_Dynamic_Frame",
        experiment_name="Engine_Dynamic_Universe_v1",
        pillar="01_Engine",
        category="log",
        stable=True,
    )

    engine = DynamicUniverseEngine()
    targets = get_available_galaxies()

    results = []
    for target in targets:
        data = load_sparc_galaxy(target)
        res = engine.solve_system(target, data)
        results.append(res)

    generate_report(results, output_dir)
    print("\n✅ V1.3 Verification Complete.")


if __name__ == "__main__":
    run_engine()
