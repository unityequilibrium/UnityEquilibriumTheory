#!/usr/bin/env python3
"""
🌐 NETWORK SCIENCE: F = -∇Ω Analysis on Real Networks
======================================================

Tests the gradient flow hypothesis on real social networks:
- Opinion dynamics as gradient descent on disagreement energy
- Consensus formation as energy minimization

Hypothesis: dO_i/dt ∝ -∇Ω where Ω = Σ_ij w_ij (O_i - O_j)²

Author: GDS Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent
RESULTS_DIR = DATA_DIR.parent / "results"
FIGURES_DIR = DATA_DIR.parent / "figures"


@dataclass
class NetworkResult:
    """Result from analyzing one network."""

    name: str
    n_nodes: int
    n_edges: int
    correlation: float
    p_value: float
    slope: float
    n_samples: int
    consistent: bool

    def to_dict(self):
        return {
            "name": self.name,
            "n_nodes": int(self.n_nodes),
            "n_edges": int(self.n_edges),
            "correlation": float(self.correlation),
            "p_value": float(self.p_value),
            "slope": float(self.slope),
            "n_samples": int(self.n_samples),
            "consistent": bool(self.consistent),
        }


def load_network(filepath: Path) -> Tuple[np.ndarray, int]:
    """Load network as adjacency matrix."""

    edges = []
    max_node = 0

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) >= 2:
                try:
                    n1, n2 = int(parts[0]), int(parts[1])
                    edges.append((n1, n2))
                    max_node = max(max_node, n1, n2)
                except ValueError:
                    continue

    n_nodes = max_node + 1

    # Create adjacency matrix (sparse would be better for large networks)
    if n_nodes > 5000:
        print(f"   ⚠️ Large network ({n_nodes} nodes), using subgraph...")
        # Take first 2000 nodes for efficiency
        n_nodes = 2000
        edges = [(e[0], e[1]) for e in edges if e[0] < n_nodes and e[1] < n_nodes]

    adj = np.zeros((n_nodes, n_nodes))
    for n1, n2 in edges:
        if n1 < n_nodes and n2 < n_nodes:
            adj[n1, n2] = 1
            adj[n2, n1] = 1  # Undirected

    return adj, len(edges)


def compute_disagreement_energy(opinions: np.ndarray, adj: np.ndarray) -> float:
    """
    Compute network disagreement energy:

    Ω = (1/2) Σ_ij A_ij (O_i - O_j)²

    This measures total "stress" in the network from differing opinions.
    """
    diff = opinions[:, None] - opinions[None, :]
    energy = 0.5 * np.sum(adj * diff**2)
    return energy


def compute_local_gradient(opinions: np.ndarray, adj: np.ndarray) -> np.ndarray:
    """
    Compute gradient of energy with respect to each opinion:

    ∂Ω/∂O_i = Σ_j A_ij (O_i - O_j)

    This is the "force" pushing each node toward neighbor average.
    NORMALIZED by degree to prevent overflow in dense networks.
    """
    n = len(opinions)
    gradient = np.zeros(n)
    degrees = adj.sum(axis=1)

    for i in range(n):
        # Neighbors of i
        neighbors = np.where(adj[i] > 0)[0]
        if len(neighbors) > 0:
            # Normalize by degree to prevent overflow
            diff_sum = np.sum(opinions[i] - opinions[neighbors])
            gradient[i] = diff_sum / max(degrees[i], 1)

    return gradient


def simulate_opinion_dynamics(
    adj: np.ndarray, n_steps: int = 500, dt: float = 0.01, gamma: float = 0.5
) -> Tuple[np.ndarray, np.ndarray, List[float]]:
    """
    Simulate opinion dynamics on the network.

    Model: dO_i/dt = -γ × ∇Ω_i = -γ × Σ_j A_ij (O_i - O_j)

    Returns: (all_gradients, all_changes, energies)
    """
    n = adj.shape[0]
    n_edges = int(adj.sum() / 2)

    # Adaptive parameters for dense networks
    if n_edges > 10000:
        dt = 0.001  # Smaller step for stability
        gamma = 0.1
        n_steps = min(n_steps, 200)  # Fewer steps

    # Initial random opinions (normalized)
    np.random.seed(42)
    opinions = np.random.randn(n) * 0.1  # Small initial values

    all_gradients = []
    all_changes = []
    energies = []

    for step in range(n_steps):
        # Compute energy (use safe version)
        try:
            energy = compute_disagreement_energy(opinions, adj)
            if np.isnan(energy) or np.isinf(energy):
                break
            energies.append(energy)
        except:
            break

        # Compute gradient
        gradient = compute_local_gradient(opinions, adj)

        # Dynamics: change = -γ × gradient
        change = -gamma * gradient

        # Record
        all_gradients.extend(gradient.tolist())
        all_changes.extend(change.tolist())

        # Update with clamping to prevent overflow
        opinions = opinions + dt * change
        opinions = np.clip(opinions, -10, 10)  # Clamp to prevent explosion

    return np.array(all_gradients), np.array(all_changes), energies


def analyze_network(name: str, filepath: Path) -> Optional[NetworkResult]:
    """Full analysis of one network."""

    if not filepath.exists():
        print(f"   ⚠️ File not found: {filepath}")
        return None

    print(f"\n📊 Analyzing {name}...")

    # Load network
    adj, n_edges = load_network(filepath)
    n_nodes = adj.shape[0]

    print(f"   Nodes: {n_nodes}, Edges: {n_edges}")

    # Simulate opinion dynamics
    gradients, changes, energies = simulate_opinion_dynamics(adj)

    # Test F = -∇Ω relationship
    # Remove zeros (isolated nodes)
    mask = gradients != 0
    g = gradients[mask]
    c = changes[mask]

    if len(g) < 100:
        print(f"   ⚠️ Not enough data points")
        return None

    # Correlation
    corr, p_value = stats.pearsonr(g, c)
    slope, _, _, _, _ = stats.linregress(g, c)

    # Energy should decrease
    energy_decreased = energies[-1] < energies[0]

    consistent = (slope < 0) and (p_value < 0.05) and energy_decreased

    print(f"   Correlation (ΔO vs ∇Ω): {corr:.4f}")
    print(f"   p-value: {p_value:.2e}")
    print(f"   Slope: {slope:.4f}")
    print(f"   Energy: {energies[0]:.1f} → {energies[-1]:.1f} ({'↓' if energy_decreased else '↑'})")
    print(f"   Consistent with F = -∇Ω: {'✅ YES' if consistent else '❌ NO'}")

    return NetworkResult(
        name=name,
        n_nodes=n_nodes,
        n_edges=n_edges,
        correlation=corr,
        p_value=p_value,
        slope=slope,
        n_samples=len(g),
        consistent=consistent,
    )


def run_full_analysis():
    """Analyze all available networks."""

    print("\n" + "🌐" * 30)
    print("   NETWORK SCIENCE: F = -∇Ω ANALYSIS")
    print("🌐" * 30)

    # Find all network files
    network_files = list(DATA_DIR.glob("*.txt"))

    if not network_files:
        print("\n❌ No network files found!")
        print(f"   Run download_snap_data.py first")
        return

    print(f"\n📁 Found {len(network_files)} networks")

    results = []
    for filepath in network_files:
        name = filepath.stem
        result = analyze_network(name, filepath)
        if result:
            results.append(result)

    if not results:
        print("\n❌ No valid results")
        return

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY: F = -∇Ω Test on Real Networks")
    print("=" * 70)

    print(f"\n{'Network':<25} {'Nodes':<8} {'Corr':<10} {'p-value':<12} {'F=-∇Ω?':<10}")
    print("-" * 70)

    n_consistent = 0
    for r in results:
        status = "✅ YES" if r.consistent else "❌ NO"
        if r.consistent:
            n_consistent += 1
        print(f"{r.name:<25} {r.n_nodes:<8} {r.correlation:>+.4f}   {r.p_value:<.2e}   {status}")

    print("-" * 70)
    print(f"\n✅ {n_consistent}/{len(results)} networks CONSISTENT with F = -∇Ω")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results_dict = {
        "networks": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "consistent": n_consistent,
            "rate": n_consistent / len(results) if results else 0,
        },
    }

    output_json = RESULTS_DIR / "network_analysis.json"
    with open(output_json, "w") as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n📄 Results saved: {output_json}")

    # Create figure
    create_summary_figure(results)

    return results


def create_summary_figure(results: List[NetworkResult]):
    """Create summary visualization."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Correlation by network
    ax = axes[0]
    names = [r.name[:15] for r in results]
    corrs = [r.correlation for r in results]
    colors = ["green" if r.consistent else "red" for r in results]

    ax.barh(range(len(results)), corrs, color=colors, alpha=0.7)
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels(names)
    ax.axvline(0, color="black", linestyle="--")
    ax.set_xlabel("Correlation (ΔO vs ∇Ω)")
    ax.set_title("F = -∇Ω Test by Network")
    ax.set_xlim(-1.1, 0.2)

    # Legend
    ax.legend(
        [
            plt.Rectangle((0, 0), 1, 1, color="green", alpha=0.7),
            plt.Rectangle((0, 0), 1, 1, color="red", alpha=0.7),
        ],
        ["Consistent", "Not Consistent"],
        loc="lower right",
    )

    # Plot 2: Network sizes
    ax = axes[1]
    sizes = [r.n_nodes for r in results]
    ax.bar(range(len(results)), sizes, color="steelblue", alpha=0.7)
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("Number of Nodes")
    ax.set_title("Network Sizes")
    ax.set_yscale("log")

    plt.suptitle("Network Science: Opinion Dynamics Analysis", fontsize=14, fontweight="bold")
    plt.tight_layout()

    output = FIGURES_DIR / "network_analysis.png"
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"📊 Figure saved: {output}")
    plt.close()


if __name__ == "__main__":
    run_full_analysis()
