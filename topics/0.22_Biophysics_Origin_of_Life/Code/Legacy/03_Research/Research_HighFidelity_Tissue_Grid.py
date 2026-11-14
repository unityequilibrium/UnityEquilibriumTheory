"""
UET High-Fidelity Cancer Analysis: Multi-Cell Tissue Network
===========================================================
Topic: 0.22 Biophysics & Origin of Life
Goal: Model spatial tumor growth, heterogeneity, and T-cell infiltration.
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

# --- ENVIRONMENT SETUP ---
script_path = Path(__file__).resolve()
project_root = script_path.parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from docs.core.uet_glass_box import UETPathManager


def run_high_fidelity_simulation():
    print("🔬 UET HIGH-FIDELITY: MULTI-CELL TISSUE SIMULATION")
    print("=" * 60)

    # 1. Spatial Environment Setup
    grid_size = 20
    tissue = np.ones((grid_size, grid_size))

    # 2. Introduce Heterogeneity
    center = grid_size // 2
    tissue[center - 2 : center + 2, center - 2 : center + 2] = np.random.uniform(0.1, 0.3, (4, 4))
    tissue[2:4, grid_size - 4 : grid_size - 2] = np.random.uniform(0.3, 0.45, (2, 2))

    print(f"Tissue Grid: {grid_size}x{grid_size} ({grid_size**2} units)")

    # 3. Time Evolution
    iterations = 5
    for gen in range(iterations):
        new_tissue = tissue.copy()
        for x in range(1, grid_size - 1):
            for y in range(1, grid_size - 1):
                if tissue[x, y] < 0.5:
                    neighbor_noise = np.random.uniform(0.01, 0.05)
                    new_tissue[x - 1 : x + 2, y - 1 : y + 2] -= neighbor_noise
        tissue = np.clip(new_tissue, 0.0, 1.0)

    print(f"Final Global Coherence: {np.mean(tissue):.4f}")

    # 4. T-Cell Response
    print("\n[Immune Response: T-Cell Infiltration]")
    t_cells = 20
    for _ in range(t_cells):
        tx, ty = np.random.randint(0, grid_size, 2)
        if tissue[tx, ty] < 0.5:
            if np.random.rand() < 0.7:
                tissue[tx, ty] = 1.0

    # --- VISUALIZATION ---
    result_dir = UETPathManager.get_result_dir(
        topic_id="0.22_Biophysics_Origin_of_Life",
        experiment_name="Research_HighFidelity_Tissue_Grid",
        pillar="03_Research",
        category="log",
    )

    plt.figure(figsize=(8, 6))
    plt.imshow(tissue, cmap="RdYlGn", origin="lower", vmin=0, vmax=1)
    plt.colorbar(label="UET Coherence (C)")
    plt.title(f"Tissue State Post-Infiltration (Gen {iterations})")
    plt.xlabel("X (Cell Map)")
    plt.ylabel("Y (Cell Map)")

    save_path = result_dir / "Fig_Tissue_Coherence_Map.png"
    plt.savefig(save_path)
    plt.close()
    print(f"\n  > Visualization Saved: {save_path}")

    return True


if __name__ == "__main__":
    run_high_fidelity_simulation()
