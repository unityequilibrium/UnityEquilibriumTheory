"""
UET Visualization: Black Hole Shadow (Topic 0.2)
================================================
Generates EHT Shadow Simulation (M87*).
Extracted from legacy Research_EHT_Validation.py.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Output Directory
OUTPUT_DIR = (
    root_path / "docs" / "topics" / "0.2_Black_Hole_Physics" / "Result" / "01_Showcase"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set Style
plt.style.use("dark_background")




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def generate_shadow_plot():
    print("Generating M87* Shadow Simulation...")

    x = np.linspace(-10, 10, 200)
    y = np.linspace(-10, 10, 200)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)

    # Ring at ~5 Schwarzschild radii (Shadow)
    # Simple Gaussian ring model for visualization
    Z = np.exp(-((R - 5) ** 2) / 2) + np.random.normal(0, 0.05, X.shape)

    plt.figure(figsize=(8, 6))
    plt.imshow(Z, extent=[-10, 10, -10, 10], cmap="magma", origin="lower")
    plt.colorbar(label="Intensity")

    plt.title("Simulated Black Hole Shadow (M87*) - UET Prediction", fontsize=14)
    plt.xlabel("X (Rs)")
    plt.ylabel("Y (Rs)")

    out_path = OUTPUT_DIR / "eht_shadow_simulation_refactored.png"
    plt.savefig(out_path, dpi=150)
    print(f"[SUCCESS] Saved to {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_shadow_plot()
