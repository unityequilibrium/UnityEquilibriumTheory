"""
UET Visualization: Galaxy Rotation Curve (Topic 0.1)
====================================================
Generates the Parity Plot (Observed vs Predicted) for SPARC galaxies.
Extracted from legacy Research_Galaxy_Rotation.py.
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import importlib
from pathlib import Path



# --- ROBUST PATH FINDER ---


# Setup local imports
topic_path = root_path / "docs" / "topics" / "0.1_Galaxy_Rotation_Problem"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    Engine_Galaxy_V3 = importlib.import_module("Engine_Galaxy_V3")
    UETGalaxyEngine = Engine_Galaxy_V3.UETGalaxyEngine
    GalaxyParams = Engine_Galaxy_V3.GalaxyParams
except ImportError as e:
    print(f"ENGINE IMPORT ERROR: {e}")
    sys.exit(1)

# Output Directory
OUTPUT_DIR = topic_path / "Result" / "01_Showcase"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def load_data():
    """Load SPARC data from JSON."""
    data_path = topic_path / "Data" / "03_Research" / "sparc_data.json"
    if not data_path.exists():
        data_path = root_path / "Data" / "03_Research" / "sparc_data.json"

    if not data_path.exists():
        print(f"Data not found at {data_path}")
        return []

    with open(data_path, "r") as f:
        return json.load(f)


def generate_parity_plot():
    print("Generating Galaxy Rotation Parity Plot...")

    galaxies = load_data()
    if not galaxies:
        print("No data found.")
        return

    results = []

    # Fast re-calculation for visualization
    for g in galaxies:
        params = GalaxyParams(
            mass_disk=g["M_disk_Msun"],
            radius_disk=g["R_disk_kpc"],
            mass_bulge=g.get("M_bulge_Msun", 0.0),
            galaxy_type=g["type"],
        )
        engine = UETGalaxyEngine(params)
        v_uet = engine.compute_velocity_at_radius(g["R_kpc"])

        results.append({"type": g["type"], "v_obs": g["v_obs"], "v_uet": v_uet})

    # Plotting Logic
    v_obs = [r["v_obs"] for r in results]
    v_uet = [r["v_uet"] for r in results]
    types = [r["type"] for r in results]

    plt.figure(figsize=(10, 6))
    plt.style.use("dark_background")

    colors = {
        "spiral": "#00aaff",
        "dwarf": "#00ff00",
        "lsb": "#00ffff",
        "compact": "#ff0055",
        "ultrafaint": "#aa00ff",
    }

    for t in set(types):
        x = [r["v_obs"] for r in results if r["type"] == t]
        y = [r["v_uet"] for r in results if r["type"] == t]
        plt.scatter(
            x, y, label=t.upper(), color=colors.get(t, "gray"), alpha=0.8, edgecolors="none"
        )

    max_v = max(max(v_obs), max(v_uet))
    plt.plot([0, max_v], [0, max_v], "w--", alpha=0.5, label="Ideal 1:1")

    plt.xlabel("Observed Velocity (km/s)")
    plt.ylabel("UET Predicted Velocity (km/s)")
    plt.title("UET Galaxy Rotation: Zero Curve Fitting", fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.2)

    out_path = OUTPUT_DIR / "Galaxy_Rotation_Parity_Refactored.png"
    plt.savefig(out_path, dpi=150)
    print(f"[SUCCESS] Saved to {out_path}")
    plt.close()


if __name__ == "__main__":
    generate_parity_plot()
