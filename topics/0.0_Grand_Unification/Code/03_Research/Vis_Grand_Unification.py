"""
Vis_Grand_Unification.py
========================
Visualizing the "Sand Dune" Effect:
Transforming Quantum Noise (Micro) into Gravity (Macro).

This script generates a plot showing how chaotic quantum fluctuations
integrate into smooth geometric curvature when viewed at larger scales.
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
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Path Setup
current_path = Path(__file__).resolve()
# Go up to 'docs' parent (assuming deep structure)
root_path = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        root_path = parent
        break

if root_path and str(root_path) not in sys.path:
    sys.path.append(str(root_path))

try:
    from docs.core.uet_glass_box import UETPathManager
except ImportError as e:
    print(f"Setup Error: {e}")
    # Fallback for manual run
    pass


def generate_unification_plot():
    print("Generating Grand Unification Visualization...")

    # 1. Define Scale (Zoom Level)
    # Scale from 1 (Micro/Quantum) to 100 (Macro/Gravity)
    scales = np.linspace(1, 100, 1000)

    # 2. Simulate Quantum Noise (Micro)
    # High frequency, high amplitude at small scales
    np.random.seed(42)
    noise = np.random.normal(0, 1, len(scales)) * np.exp(-scales / 20.0)

    # 3. Simulate Gravity Curvature (Macro)
    # Smooth curve emerging at large scales
    gravity = 1.0 - np.exp(-scales / 30.0)

    # 4. Unified Field (The Sum)
    unified_field = gravity + 0.2 * noise

    # 5. Plotting
    plt.figure(figsize=(12, 6))

    # Plot 1: The Unified View
    plt.plot(scales, unified_field, color="#d4af37", lw=2, label="Unified Field (UET)")
    plt.plot(
        scales,
        gravity,
        color="black",
        linestyle="--",
        alpha=0.5,
        label="General Relativity (Smooth)",
    )

    plt.fill_between(
        scales,
        unified_field - 0.2 * np.exp(-scales / 20.0),
        unified_field + 0.2 * np.exp(-scales / 20.0),
        color="#d4af37",
        alpha=0.2,
        label="Quantum Uncertainty",
    )

    plt.xlabel("Scale (Micro $\\to$ Macro)", fontsize=12)
    plt.ylabel("Field Amplitude", fontsize=12)
    plt.title("Grand Unification: From Quantum Noise to Gravity", fontsize=14, fontweight="bold")

    # Annotations
    plt.text(5, 0.1, "Quantum Realm\n(High Entropy)", ha="center", color="red")
    plt.text(80, 0.9, "Gravity Realm\n(Smooth Geometry)", ha="center", color="black")

    plt.legend()
    plt.grid(True, alpha=0.3)

    # Save
    try:
        # Saving directly to Result/01_Showcase for immediate visibility
        result_dir = UETPathManager.get_result_dir(
            topic_id="0.0_Grand_Unification",
            experiment_name="Research_Sand_Dune_Duality",
            pillar="01_Showcase",
            category="showcase",
        )
        # Use showcase category to be safe, or just force the path

        output_path = result_dir / "Research_Sand_Dune_Duality_Plot.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✅ Generated: {output_path}")
    except Exception as e:
        print(f"Save Error: {e}")
        plt.show()


if __name__ == "__main__":
    generate_unification_plot()
