"""
Research: Dynamic Alpha Learning
================================
Theoretical study: Does the Efficiency Constant (Gamma/Alpha) vary with Density?

Hypothesis:
Zero Curve Fitting assumes Gamma=0.48 (Universal).
This script tests if letting Gamma vary improves fit, implying "Environmental Adaptation".
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


import sys
from pathlib import Path

# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


from docs.core.uet_glass_box import UETPathManager

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
import importlib



code_dir = str(Path(__file__).resolve().parent.parent)
if code_dir not in sys.path:
    sys.path.append(code_dir)

# Import Engine logic components (We need internal logic, so we might duplicate parts or import)
# For research speed, we mock the engine internals to allow parameter sweeping
# since Engine_Galaxy_V3 is hardcoded for Zero Curve Fitting.




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def uet_velocity_variable_gamma(gamma, r_kpc, M_disk, R_disk):
    G = 4.302e-6
    RHO_0 = 5e7
    RATIO_0 = 8.5

    vol = (4 / 3) * np.pi * R_disk**3
    rho = M_disk / (vol + 1e-10)

    # Variable Gamma
    ratio = RATIO_0 * (rho / RHO_0) ** (-gamma)

    # Saturation (Standard V3.1)
    rho_crit = 1.5e9
    screening = 1.0 / (1.0 + (rho / rho_crit) ** 2.0)

    M_I = ratio * M_disk * screening

    # NFW Profile
    c = np.clip(10.0 * (M_I / 1e12) ** (-0.1), 5, 20)
    R_I = 10 * R_disk
    x_h = r_kpc / (R_I / c)
    f_x = np.log(1 + x_h) - x_h / (1 + x_h)
    f_c = np.log(1 + c) - c / (1 + c)

    M_I_enc = M_I * (f_x / f_c)

    x = r_kpc / R_disk
    M_disk_enc = M_disk * (1 - (1 + x) * np.exp(-x))

    M_total = M_disk_enc + M_I_enc  # Ignore bulge for simple sweep
    return np.sqrt(G * M_total / r_kpc)


def load_data():
    """Load SPARC data from JSON."""
    data_path = (
        root_path
        / "docs"
        / "topics"
        / "0.1_Galaxy_Rotation_Problem"
        / "Data"
        / "03_Research"
        / "sparc_data.json"
    )
    if not data_path.exists():
        data_path = root_path / "Data" / "03_Research" / "sparc_data.json"

    if not data_path.exists():
        raise FileNotFoundError(f"Data not found at {data_path}")

    with open(data_path, "r") as f:
        return json.load(f)


def run_learning():
    print("=" * 60)
    print("[BRAIN] UET ALPHA LEARNING EXPERIMENT")
    print("=" * 60)

    galaxies = load_data()
    results = []

    for g in galaxies:

        def loss(gamma):
            v = uet_velocity_variable_gamma(
                gamma, g["R_kpc"], g["M_disk_Msun"], g["R_disk_kpc"]
            )
            return abs(v - g["v_obs"])

        res = minimize_scalar(loss, bounds=(0.0, 1.0), method="bounded")
        best_gamma = res.x

        # Calculate density for plotting
        vol = (4 / 3) * np.pi * g["R_disk_kpc"] ** 3
        rho = g["M_disk_Msun"] / vol

        results.append({"rho": rho, "gamma": best_gamma, "type": g["type"]})

    print(f"Optimized Gamma for {len(results)} galaxies.")

    # Plot
    rhos = [r["rho"] for r in results]
    gammas = [r["gamma"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.semilogx(rhos, gammas, "o", alpha=0.6)
    plt.xlabel("Baryon Density (Msun/kpc^3)")
    plt.ylabel("Optimal Gamma")
    plt.title("Environmental Adaptation: Optimal Gamma vs Density")
    plt.grid(True)

    # --- ADDED ANALYSIS ---
    # Linear Regression: Gamma = m * log10(rho) + c
    log_rhos = np.log10(rhos)
    m, c = np.polyfit(log_rhos, gammas, 1)
    print("\n[ANALYSIS] Derived Relationship:")
    print(f"Gamma = {m:.4f} * Log10(Rho) + {c:.4f}")

    # Check R-squared
    correlation_matrix = np.corrcoef(log_rhos, gammas)
    correlation_xy = correlation_matrix[0, 1]
    r_squared = correlation_xy**2
    print(f"R-squared: {r_squared:.4f}")

    if r_squared > 0.5:
        print(">> STRONG EVIDENCE for Density-Dependent Gamma.")
    else:
        print(">> WEAK EVIDENCE. Tuning might be individual.")
    # ----------------------

    result_dir = UETPathManager.get_result_dir(
        topic_id="0.1_Galaxy_Rotation_Problem",
        experiment_name="Research_Alpha_Learning",
        pillar="03_Research",
        category="log",
    )
    out_dir = result_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_dir / "alpha_learning.png")
    print(f"Plot saved to {out_dir / 'alpha_learning.png'}")


if __name__ == "__main__":
    run_learning()
