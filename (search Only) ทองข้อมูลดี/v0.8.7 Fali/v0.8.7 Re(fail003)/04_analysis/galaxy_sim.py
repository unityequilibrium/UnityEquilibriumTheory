import numpy as np
import matplotlib.pyplot as plt
import os

"""
UET COSMOLOGICAL APPLICATION: GALAXY ROTATION CURVES
----------------------------------------------------
Goal: Test if UET's "Information Closure" (I) can explain the "Dark Matter" effect.

Galaxy: NGC 6503 (Standard Spiral)
Data Source: SPARC Database (Lelli et al. 2016)
File: research_v3/01_data/NGC6503_rotmod.dat

Physics:
1. V_obs: Observed velocity (Flat at large r).
2. V_newton: Predicted velocity from visible matter (Drops at large r).
3. V_uet: V_newton + UET Correction.
"""


def get_ngc6503_data():
    """
    Load data from local SPARC file.
    """
    file_path = os.path.join("research_v3", "01_data", "NGC6503_rotmod.dat")
    print(f"Loading real data from: {file_path}")

    # Load data, skipping header comments
    try:
        data = np.loadtxt(file_path, comments="#")
    except OSError:
        print(f"Error: File not found at {file_path}")
        return None, None, None, None

    # Columns: R (0), V_obs (1), V_err (2), V_gas (3), V_disk (4), V_bulge (5)
    r = data[:, 0]
    v_obs = data[:, 1]
    v_gas = data[:, 3]
    v_disk = data[:, 4]

    return r, v_obs, v_gas, v_disk


def uet_closure_field(r, r0=5.0, alpha=0.5):
    """
    Metric for 'Information Closure' (I) of space at distance r.
    Hypothesis: Space 'closes' or 'thickens' as information density drops.
    """
    return (r / r0) ** alpha


def run_simulation():
    print("Running Galaxy Simulation: NGC 6503 (Real SPARC Data)...")

    # 1. Load Data
    r, v_obs, v_gas, v_disk = get_ngc6503_data()
    if r is None:
        return

    # 2. Physics: Calculate Total Newtonian Velocity (Baryonic)
    # V_baryon^2 = V_gas^2 + V_disk^2
    v_newton = np.sqrt(v_gas**2 + v_disk**2)

    # 3. UET: Calculate the "Dark Force" from Closure (I)
    # Tuning the UET Model
    V_terminal = 100.0  # Interaction strength
    r_scale = 3.5  # Characteristic length

    # UET prediction for the "Missing Component"
    v_uet_component = V_terminal * np.sqrt(1 - np.exp(-r / r_scale))

    # Total UET Prediction
    v_total_uet = np.sqrt(v_newton**2 + v_uet_component**2)

    # 4. Analysis
    residual = np.mean(np.abs(v_total_uet - v_obs))
    print(f"UET Fit Residual: {residual:.4f} km/s")

    return r, v_obs, v_newton, v_total_uet, v_uet_component


def plot_results(r, v_obs, v_newton, v_total_uet, v_uet_component):
    output_dir = "research_v3/04_analysis/results"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 6))

    # Plot Data
    plt.errorbar(r, v_obs, yerr=5.0, fmt="ko", label="Observed (SPARC Data)", alpha=0.7)

    # Plot Newton
    plt.plot(r, v_newton, "b--", linewidth=2, label="Newton (Visible Matter)")

    # Plot UET
    plt.plot(r, v_total_uet, "r-", linewidth=3, label="UET Prediction (Gravity + Closure)")

    # Plot the "Invisible" Component
    plt.plot(r, v_uet_component, "g:", linewidth=1.5, label="UET Closure Field (I)")

    plt.title("Galaxy NGC 6503: Newton vs UET (Real Data Validation)")
    plt.xlabel("Radius (kpc)")
    plt.ylabel("Rotation Velocity (km/s)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    output_path = f"{output_dir}/galaxy_rotation_curve_sparc.png"
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")


if __name__ == "__main__":
    results = run_simulation()
    if results:
        plot_results(*results)
