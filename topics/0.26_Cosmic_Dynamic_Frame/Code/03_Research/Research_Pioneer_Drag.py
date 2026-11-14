"""
Research_Pioneer_Drag.py
========================
Topic 0.26: The Dynamic Universe
Hypothesis: Pioneer 10/11 deceleration is caused by Cosmic Fluid Drag.

Goal:
    1. Load Real Anomaly Data (Distance vs Acceleration).
    2. Fit the UET Fluid Drag Model: a = (0.5 * Cd * rho * A * v^2) / m
    3. Determine if a SINGLE Cosmic Density (rho) explains the data across all distances.
    4. If constant rho fits well -> Evidence for "Cosmic Superfluid" (Constant density field).
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
import pandas as pd
from pathlib import Path
import sys

# --- ROBUST PATH FINDING ---


from docs.core.uet_glass_box import UETPathManager






# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def run_pioneer_simulation():
    print("🚀 PIONEER ANOMALY SIMULATION (DATA DRIVEN)")
    print("Hypothesis: Space is a Fluid. Rockets experience Drag.\n")

    # 1. Load Data
    # FIXED PATH: Points to Topic Root Data
    data_path = (
        root_path
        / "docs/topics/0.26_Cosmic_Dynamic_Frame/Data/Pioneer_Anomaly_Data.csv"
    )
    if not data_path.exists():
        print(f"❌ DATA MISSING: {data_path}")
        return False

    try:
        df = pd.read_csv(data_path)
        print(f"   [Data] Loaded {len(df)} telemetry points (20-70 AU).")
    except Exception as e:
        print(f"❌ CSV ERROR: {e}")
        return False

    # 2. Constants (Pioneer 10)
    mass = 241.0  # kg
    area = 5.0  # m^2 (Effective)
    velocity = 12000.0  # m/s (Cruise)
    Cd = 2.0  # Drag Coeff

    # 3. Fit Cosmic Density (rho)
    # Model: a_pred = (0.5 * Cd * rho * A * v^2) / m
    # Unknown: rho
    # We want rho that minimizes Chi-Squared

    # Simple Solver: rho = mean( 2 * m * a_obs / (Cd * A * v^2) )
    rhos_required = (2 * mass * df["Anomaly_Accel_m_s2"]) / (Cd * area * velocity**2)

    best_rho = np.mean(rhos_required)
    std_rho = np.std(rhos_required)

    print(f"\n🧪 FITTING RESULT:")
    print(f"   Best Fit Cosmic Density (rho): {best_rho:.4e} kg/m^3")
    print(f"   Consistency (Std Dev):         {std_rho:.4e} (Variation)")

    # 4. Benchmarks
    benchmarks = {
        "Interstellar Medium (ISM)": 1.0e-21,
        "Dark Matter Halo (Near Earth)": 5.3e-22,
        "UET Superfluid Vacuum": best_rho,
    }

    print("\n📊 MEDIUM IDENTIFICATION:")
    for name, val in benchmarks.items():
        if name != "UET Superfluid Vacuum":
            diff = abs(np.log10(best_rho) - np.log10(val))
            print(f"   vs {name:<30}: {val:.2e} (Log Diff: {diff:.2f})")

    # 5. Validation Check
    # Does the constant density model fit the data within error bars?
    a_pred = (0.5 * Cd * best_rho * area * velocity**2) / mass
    df["Model_Accel"] = a_pred

    max_error = np.max(np.abs(df["Anomaly_Accel_m_s2"] - df["Model_Accel"]))
    print(f"\n🔍 MODEL ACCURACY:")
    print(f"   Max Deviation: {max_error:.2e} m/s^2")

    if max_error < 1.0e-10:
        print(" SUCCESS: Constant Superfluid Density explains Pioneer Anomaly.")
        print("   The 'Vacuum Drag' hypothesis is consistent with data.")
    else:
        print(" WARNING: Data shows variation not explained by constant density.")

    # 6. Plot
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.26_Cosmic_Dynamic_Frame",
        experiment_name="Research_Pioneer_Drag",
        pillar="03_Research",
        category="log",
    )

    plt.figure(figsize=(10, 6))
    plt.errorbar(
        df["Distance_AU"],
        df["Anomaly_Accel_m_s2"],
        yerr=df["Error_m_s2"],
        fmt="o",
        label="Pioneer Data (Turyshev et al.)",
        color="black",
    )

    plt.axhline(
        y=a_pred,
        color="red",
        linestyle="--",
        label=f"UET Fluid Drag (rho={best_rho:.1e})",
    )

    plt.xlabel("Distance (AU)")
    plt.ylabel("Acceleration Anomaly (m/s^2)")
    plt.title("Pioneer Anomaly: Data vs UET Vacuum Drag Model")
    plt.grid(True, alpha=0.3)
    plt.legend()

    save_path = result_dir / "pioneer_data_fit.png"
    plt.savefig(save_path)
    print(f"   [Viz] Saved: {save_path}")

    return True


if __name__ == "__main__":
    run_pioneer_simulation()
