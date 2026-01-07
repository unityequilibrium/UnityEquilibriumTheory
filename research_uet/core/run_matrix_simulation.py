"""
Matrix UET Runner (CLI)
=======================
The main entry point for running v0.9 Tensor Simulations.

Usage:
  python run_matrix_simulation.py --config my_config.json

Process:
1. Load Config (JSON).
2. Initialize Matrix Engine & State.
3. Run Evolution Loop.
4. Generate Heatmap Outputs (PNG).
"""

import argparse
import sys
import os
import numpy as np

# Add path
sys.path.append(os.path.dirname(__file__))

from research_uet.core.uet_matrix_engine import MatrixEvolution, UniverseState
from research_uet.core.uet_matrix_toolkit import MatrixConfig, MatrixVisualizer


def run_simulation(config_path):
    print("=" * 60)
    print("🌌 MATRIX UET STUDIO (CLI)")
    print("=" * 60)

    # 1. Load Config
    print(f"Loading config: {config_path}")
    cfg = MatrixConfig.from_json(config_path)
    print(f"Grid: {cfg.grid_size}x{cfg.grid_size} | Steps: {cfg.steps} | Beta: {cfg.beta}")

    # 2. Init State (Center Mass for Demo)
    state = UniverseState(cfg.grid_size)
    center = cfg.grid_size // 2
    # Create valid indices for a small center mass
    state.tensor[0, center - 2 : center + 3, center - 2 : center + 3] = 10.0  # Mass Block

    # 3. Init Engine
    engine = MatrixEvolution(beta=cfg.beta)

    # 4. Evolution Loop
    print("\nRunning Evolution...")
    for t in range(cfg.steps):
        state = engine.step(state, dt=cfg.dt)
        if t % 50 == 0:
            print(f"Step {t}/{cfg.steps} complete...")

    # 5. Output
    print(f"\nSimulation Complete. Generating Heatmaps in: {cfg.output_dir}")
    vis = MatrixVisualizer()
    vis.plot_state_layers(state, os.path.join(cfg.output_dir, "final_state"))

    print("✅ DONE.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UET Matrix Simulation")
    parser.add_argument("--config", type=str, required=True, help="Path to JSON config file")

    args = parser.parse_args()

    try:
        run_simulation(args.config)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
