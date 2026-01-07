#!/usr/bin/env python3
"""
🧬 BIOPHYSICS: F = -∇C Chemotaxis Analysis
===========================================

Tests the gradient flow hypothesis on chemotaxis:
- Cell movement toward chemical attractant
- Fish's law: J = -D∇C

Hypothesis: v_cell ∝ -∇C (cells move down concentration gradient)

Note: This analysis uses SIMULATED cell trajectories.
For real data, we need published cell tracking datasets.

TODO: Download real data from:
- Cell Tracking Challenge (celltrackingchallenge.net)
- Published E. coli chemotaxis experiments

Author: GDS Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from dataclasses import dataclass
from typing import List, Tuple
import json

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent
RESULTS_DIR = DATA_DIR.parent / "results"
FIGURES_DIR = DATA_DIR.parent / "figures"


@dataclass
class ChemotaxisResult:
    """Result from chemotaxis analysis."""

    experiment_name: str
    n_cells: int
    n_steps: int
    correlation: float
    p_value: float
    slope: float
    direction_accuracy: float  # % moving toward higher concentration
    consistent: bool

    def to_dict(self):
        return {
            "experiment_name": self.experiment_name,
            "n_cells": int(self.n_cells),
            "n_steps": int(self.n_steps),
            "correlation": float(self.correlation),
            "p_value": float(self.p_value),
            "slope": float(self.slope),
            "direction_accuracy": float(self.direction_accuracy),
            "consistent": bool(self.consistent),
        }


def create_concentration_field(grid_size: int, field_type: str = "linear"):
    """
    Create chemical concentration field.

    Types:
    - linear: C = C0 * (1 - x/L) - Linear gradient
    - gaussian: C = C0 * exp(-r²/σ²) - Point source
    - cosine: C = C0 * cos(πx/L) - Sinusoidal
    """
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)

    if field_type == "linear":
        # Gradient from left (high) to right (low)
        C = 1.0 - X
    elif field_type == "gaussian":
        # Point source at center
        r2 = (X - 0.5) ** 2 + (Y - 0.5) ** 2
        C = np.exp(-r2 / 0.1)
    elif field_type == "cosine":
        C = 0.5 * (1 + np.cos(np.pi * X))
    else:
        C = 1.0 - X

    return C, X, Y


def compute_gradient_at_position(C, x, y, grid_size, dx=0.01):
    """Compute concentration gradient at position (x, y)."""
    # Convert to grid indices
    ix = int(x * (grid_size - 1))
    iy = int(y * (grid_size - 1))

    # Clamp to valid range
    ix = np.clip(ix, 1, grid_size - 2)
    iy = np.clip(iy, 1, grid_size - 2)

    # Central difference
    grad_x = (C[iy, ix + 1] - C[iy, ix - 1]) / (2 * dx)
    grad_y = (C[iy + 1, ix] - C[iy - 1, ix]) / (2 * dx)

    return grad_x, grad_y


def simulate_chemotaxis(
    n_cells: int = 100,
    n_steps: int = 500,
    grid_size: int = 100,
    field_type: str = "linear",
    mobility: float = 0.5,
    noise: float = 0.1,
    dt: float = 0.001,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate bacterial chemotaxis.

    Model: v = -D∇C + noise

    This is a SIMULATION, not real data.
    """
    np.random.seed(42)

    C, X, Y = create_concentration_field(grid_size, field_type)

    # Initialize random cell positions
    positions = np.random.rand(n_cells, 2)

    all_gradients = []
    all_velocities = []

    for step in range(n_steps):
        for i in range(n_cells):
            x, y = positions[i]

            # Skip if out of bounds
            if x < 0.05 or x > 0.95 or y < 0.05 or y > 0.95:
                continue

            # Compute local gradient
            grad_x, grad_y = compute_gradient_at_position(C, x, y, grid_size)

            # Velocity = -mobility * gradient + noise
            vx = -mobility * grad_x + noise * np.random.randn()
            vy = -mobility * grad_y + noise * np.random.randn()

            # Record
            all_gradients.append([grad_x, grad_y])
            all_velocities.append([vx, vy])

            # Update position
            positions[i, 0] = np.clip(x + vx * dt, 0, 1)
            positions[i, 1] = np.clip(y + vy * dt, 0, 1)

    return np.array(all_gradients), np.array(all_velocities), C


def analyze_chemotaxis(
    experiment_name: str,
    n_cells: int = 100,
    n_steps: int = 500,
    field_type: str = "linear",
    noise: float = 0.1,
) -> ChemotaxisResult:
    """Run chemotaxis analysis."""

    print(f"\n🧬 Analyzing {experiment_name}...")
    print(f"   Field type: {field_type}, Cells: {n_cells}, Noise: {noise}")

    gradients, velocities, C = simulate_chemotaxis(
        n_cells=n_cells, n_steps=n_steps, field_type=field_type, noise=noise
    )

    # Analyze x-component (main gradient direction for linear)
    grad_x = gradients[:, 0]
    vel_x = velocities[:, 0]

    # Remove near-zero entries
    mask = np.abs(grad_x) > 0.01
    grad_x = grad_x[mask]
    vel_x = vel_x[mask]

    if len(grad_x) < 100:
        print("   ⚠️ Not enough data points")
        return None

    # Correlation
    corr, p_value = stats.pearsonr(grad_x, vel_x)
    slope, _, _, _, _ = stats.linregress(grad_x, vel_x)

    # Direction accuracy: how often does velocity oppose gradient?
    direction_correct = np.sum((grad_x * vel_x) < 0) / len(grad_x)

    # For constant gradient fields, correlation can be low even with correct direction
    # Use direction accuracy > 80% as alternative criterion
    consistent = ((corr < -0.5) and (p_value < 0.05)) or (direction_correct > 0.8)

    print(f"   Samples: {len(grad_x)}")
    print(f"   Correlation (v vs ∇C): {corr:.4f}")
    print(f"   p-value: {p_value:.2e}")
    print(f"   Direction accuracy: {direction_correct:.1%}")
    print(f"   Consistent with v = -D∇C: {'✅ YES' if consistent else '❌ NO'}")

    return ChemotaxisResult(
        experiment_name=experiment_name,
        n_cells=n_cells,
        n_steps=n_steps,
        correlation=corr,
        p_value=p_value,
        slope=slope,
        direction_accuracy=direction_correct,
        consistent=consistent,
    )


def run_full_analysis():
    """Run all chemotaxis experiments."""

    print("\n" + "🧬" * 30)
    print("   BIOPHYSICS: CHEMOTAXIS ANALYSIS")
    print("🧬" * 30)

    print("\n⚠️  NOTE: This uses SIMULATED data.")
    print("   For real validation, need published cell tracking data.")

    results = []

    # Experiment 1: Linear gradient, low noise
    result = analyze_chemotaxis(
        "Linear-LowNoise", n_cells=100, n_steps=500, field_type="linear", noise=0.05
    )
    if result:
        results.append(result)

    # Experiment 2: Linear gradient, high noise
    result = analyze_chemotaxis(
        "Linear-HighNoise", n_cells=100, n_steps=500, field_type="linear", noise=0.5
    )
    if result:
        results.append(result)

    # Experiment 3: Gaussian source
    result = analyze_chemotaxis(
        "Gaussian-Source", n_cells=100, n_steps=500, field_type="gaussian", noise=0.1
    )
    if result:
        results.append(result)

    # Experiment 4: Many cells
    result = analyze_chemotaxis(
        "Linear-ManyCells", n_cells=500, n_steps=200, field_type="linear", noise=0.1
    )
    if result:
        results.append(result)

    if not results:
        print("\n❌ No valid results")
        return

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY: v = -D∇C Test (SIMULATED)")
    print("=" * 70)

    print(f"\n{'Experiment':<20} {'Cells':<8} {'Corr':<10} {'Dir Acc':<10} {'v=-D∇C?':<10}")
    print("-" * 60)

    n_consistent = 0
    for r in results:
        status = "✅ YES" if r.consistent else "❌ NO"
        if r.consistent:
            n_consistent += 1
        print(
            f"{r.experiment_name:<20} {r.n_cells:<8} {r.correlation:>+.4f}   {r.direction_accuracy:>6.1%}   {status}"
        )

    print("-" * 60)
    print(f"\n✅ {n_consistent}/{len(results)} experiments CONSISTENT with v = -D∇C")

    print("\n⚠️  CAVEAT: This is simulated data, not real cell tracking!")
    print("   Simulation ASSUMES v = -D∇C + noise, so correlation is expected.")
    print("   Real validation requires published experimental data.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results_dict = {
        "experiments": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "consistent": n_consistent,
            "caveat": "Simulated data - need real cell tracking for validation",
        },
    }

    output_json = RESULTS_DIR / "chemotaxis_analysis.json"
    with open(output_json, "w") as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n📄 Results saved: {output_json}")

    # Create figure
    create_summary_figure(results)

    return results


def create_summary_figure(results: List[ChemotaxisResult]):
    """Create summary visualization."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Correlation by experiment
    ax = axes[0]
    names = [r.experiment_name for r in results]
    corrs = [r.correlation for r in results]
    colors = ["green" if r.consistent else "red" for r in results]

    ax.barh(range(len(results)), corrs, color=colors, alpha=0.7)
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels(names)
    ax.axvline(0, color="black", linestyle="--")
    ax.set_xlabel("Correlation (v vs ∇C)")
    ax.set_title("Chemotaxis: v = -D∇C Test")
    ax.set_xlim(-1.1, 0.2)

    # Plot 2: Direction accuracy
    ax = axes[1]
    acc = [r.direction_accuracy * 100 for r in results]
    ax.bar(range(len(results)), acc, color="steelblue", alpha=0.7)
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("Direction Accuracy (%)")
    ax.set_title("Cells Moving Toward Attractant")
    ax.axhline(50, color="red", linestyle="--", label="Random = 50%")
    ax.legend()

    plt.suptitle("Biophysics: Chemotaxis Analysis (SIMULATED)", fontsize=14, fontweight="bold")
    plt.tight_layout()

    output = FIGURES_DIR / "chemotaxis_analysis.png"
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"📊 Figure saved: {output}")
    plt.close()


if __name__ == "__main__":
    run_full_analysis()
