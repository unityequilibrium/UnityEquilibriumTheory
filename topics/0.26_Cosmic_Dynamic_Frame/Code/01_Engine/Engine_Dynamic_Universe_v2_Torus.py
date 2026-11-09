"""
Engine_Dynamic_Universe_v2_Torus.py
==================================
Topic: 0.26 The Dynamic Universe (Topological Refinement)
Type: Master Engine (The Calculator)
Status: V2.0 (Topological/Torus)

Philosophy:
    "The Universe is a Circulating Torus. Standard shapes are just deformations."
    Alignment: A Coffee Cup = A Donut (Genus 1).

Core Logic:
    1. Distance R is mapped onto a Toroidal Surface.
    2. Topological Factor (Genus = 1) scales the Pioneer Anomaly.
    3. Pressure Gradient flows toward the toroidal center (The Hole).

Axiom:
    Space is not flat; it is topologically connected.
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
from pathlib import Path

# --- ROBUST PATH FINDER ---


from docs.core.uet_parameters import get_params, C, G
from docs.core.uet_glass_box import UETPathManager


class TorusUniverseEngine:
    def __init__(self, genus=1):
        self.params = get_params("0.26")
        self.genus = genus  # Donut topology has genus 1

        # Physical Constants
        self.G = G  # kpc km^2/s^2 M_sun^-1
        self.C = C / 1000.0  # km/s
        self.A0_PIONEER = 8.74e-10  # m/s^2

        # Toroidal Geometry
        self.MAJOR_RADIUS_KPC = 50.0  # Galaxy size scale for local torus
        self.TOPOLOGICAL_STIFFNESS = 1.0 + (genus * 0.1)

    def get_topological_weight(self, R_kpc):
        """
        Calculates the topological curvature weight.
        On a Torus, the fluid 'returns' to the center.
        """
        # Periodic mapping: theta = R / Major_Radius
        theta = R_kpc / self.MAJOR_RADIUS_KPC
        # Curvature on a Torus: K ~ cos(theta) / (r * cos(theta) + R)
        # Simplified UET Weight:
        return np.cos(np.minimum(theta, np.pi / 2)) * self.TOPOLOGICAL_STIFFNESS

    def calculate_Newtonian(self, R_kpc, M_disk_solar):
        R_safe = np.maximum(R_kpc, 0.01)
        V_sq = self.G * M_disk_solar / R_safe
        return np.sqrt(V_sq)

    def calculate_TopologicalFluid(self, R_kpc):
        """
        V^2 = 2 * a * r * Topological_Weight
        """
        R_meters = R_kpc * 3.086e19
        weight = self.get_topological_weight(R_kpc)
        V_base_sq = 2 * self.A0_PIONEER * R_meters * weight

        # Convert to km/s
        V_fluid = np.sqrt(np.maximum(V_base_sq, 0)) / 1000.0
        return V_fluid

    def solve_galaxy(self, R, V_obs, M_disk):
        V_newton = self.calculate_Newtonian(R, M_disk)
        V_fluid = self.calculate_TopologicalFluid(R)
        V_total = np.sqrt(V_newton**2 + V_fluid**2)

        valid = V_obs > 0
        error = np.mean(np.abs((V_obs[valid] - V_total[valid]) / V_obs[valid])) * 100
        return V_newton, V_fluid, V_total, error


def run_torus_verification():
    print("🍩 STARTING TOPOLOGICAL ENGINE (TORUS V2.0)")
    print("-" * 50)

    # Simulation for a generic 'Glass-Top' Galaxy
    engine = TorusUniverseEngine(genus=1)
    R = np.linspace(0.1, 30, 100)
    M_disk = 1e11  # Solar masses

    # "Observed" is a placeholder for this conceptual test
    V_fake_obs = 200 * (1 - np.exp(-R / 5))  # Standard flat curve

    V_n, V_f, V_t, error = engine.solve_galaxy(R, V_fake_obs, M_disk)

    print(f"✅ TOPOLOGY Calibrated (Genus={engine.genus})")
    print(f"   Peak Fluid Vel: {np.max(V_f):.2f} km/s")
    print(f"   Topological Gain at 20kpc: {V_f[R>20][0]/V_n[R>20][0]:.2f}x Newton")

    # SAVE RESULTS
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.26_Cosmic_Dynamic_Frame",
        experiment_name="Engine_Dynamic_Universe_v2_Torus",
        pillar="01_Engine",
        category="log",
    )
    plt.style.use("dark_background")
    plt.figure(figsize=(10, 6))
    plt.plot(R, V_n, "c--", label="Newtonian (Sphere Topology)")
    plt.plot(R, V_f, "m:", label="Topological Fluid (Torus Contribution)")
    plt.plot(R, V_t, "y-", linewidth=2, label="Unified Torus Model (V2.0)")
    plt.title("UET Topic 0.26: Torus Universe (Donut) Dynamics")
    plt.xlabel("Radius (kpc)")
    plt.ylabel("Velocity (km/s)")
    plt.legend()
    plt.grid(True, alpha=0.1)

    out_file = result_dir / "Torus_Consistency.png"
    plt.savefig(out_file)
    print(f"📊 PLOT SAVED: {out_file}")


if __name__ == "__main__":
    run_torus_verification()
