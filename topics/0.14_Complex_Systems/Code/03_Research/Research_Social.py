"""
UET Test: Social Network Equilibrium
=====================================

Tests: UET equilibrium dynamics in social network data
- Facebook/Twitter ego networks
- Social polarization dynamics

Uses real data from SNAP (Stanford Network Analysis Project).

Updated for UET V3.0
"""

import numpy as np
import os
import sys
from pathlib import Path


# --- ROBUST PATH FINDER (5x4 Grid Standard) ---
_root = Path(__file__).resolve().parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
if _root.name == "docs":
    sys.path.insert(0, str(_root.parent))
    from docs import ROOT_PATH

    root_path = ROOT_PATH
else:
    print("CRITICAL: Root path not found.")
    sys.exit(1)

TOPIC_DIR = root_path / "docs" / "topics" / "0.14_Complex_Systems"
DATA_PATH = TOPIC_DIR / "Data" / "03_Research" / "social"

# --- DYNAMIC ENGINE IMPORT ---
try:
    import importlib.util

    engine_path = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Complexity.py"
    spec = importlib.util.spec_from_file_location("Engine_Complexity", str(engine_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    UETComplexityEngine = mod.UETComplexityEngine
except Exception as e:
    print(f"CRITICAL: Engine not found: {e}")
    UETComplexityEngine = None


def load_ego_network(filename):
    """Load ego network edges from text file."""
    edges = []
    filepath = DATA_PATH / filename

    if filepath.exists():
        with open(filepath, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        edges.append((int(parts[0]), int(parts[1])))
                    except ValueError:
                        continue
    return edges


def analyze_network_equilibrium(edges, name):
    """
    Analyze network for UET equilibrium properties.

    UET Interpretation:
    - Balanced degree distribution = stable equilibrium
    - Power-law degree = self-organized criticality
    - High clustering = local equilibrium regions
    """
    if not edges:
        return None

    # Build adjacency from edges
    nodes = set()
    degree = {}

    for u, v in edges:
        nodes.add(u)
        nodes.add(v)
        degree[u] = degree.get(u, 0) + 1
        degree[v] = degree.get(v, 0) + 1

    n_nodes = len(nodes)
    n_edges = len(edges)

    if n_nodes == 0:
        return None

    engine = UETComplexityEngine(name="Social_Stability_Analyzer")

    # Degree statistics
    degrees = np.array(list(degree.values()))

    # Delegate to Engine
    metrics = engine.calculate_stability_metrics(degrees)

    # Degree distribution entropy (delegated to Engine)
    # We use some distribution metrics here
    entropy_result = engine.compute_complexity_metrics(degrees, fs=1.0)

    return {
        "name": name,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "avg_degree": metrics["mean"],
        "max_degree": int(np.max(degrees)),
        "std_degree": metrics["std"],
        "density": 2 * n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0,
        "entropy": entropy_result["entropy"],
        "equilibrium_score": metrics["equilibrium_score"],
    }


def load_polarization_data():
    """Load social polarization time series."""
    filepath = DATA_PATH / "social_polarization.csv"

    if filepath.exists():
        try:
            import pandas as pd

            df = pd.read_csv(filepath)
            return df
        except Exception:
            return None
    return None


def run_test():
    """Run social network equilibrium test."""
    print("\n" + "=" * 60)
    print("[SOCIAL] UET TEST: Social Network Equilibrium")
    print("=" * 60)
    print("\nEquation: Omega = V(C) + kappa|grad(C)|^2 + beta*C*I")
    print("UET Prediction: Networks evolve toward balanced equilibrium")

    results = []

    # Analyze ego networks
    networks = [
        ("facebook_ego_edges.txt", "Facebook Ego Network"),
        ("twitter_ego_edges.txt", "Twitter Ego Network"),
    ]

    print("\n[1] EGO NETWORK ANALYSIS")
    print("-" * 40)

    for filename, display_name in networks:
        edges = load_ego_network(filename)
        if edges:
            metrics = analyze_network_equilibrium(edges, display_name)
            if metrics:
                results.append(metrics)
                print(f"\n   {display_name}:")
                print(f"      Nodes: {metrics['n_nodes']:,}")
                print(f"      Edges: {metrics['n_edges']:,}")
                print(f"      Avg Degree: {metrics['avg_degree']:.1f}")
                print(f"      Density: {metrics['density']:.4f}")
                print(f"      Entropy: {metrics['entropy']:.2f}")
                print(f"      Equilibrium Score: {metrics['equilibrium_score']:.3f}")
        else:
            print(f"   [WARN] Could not load {filename}")

    # Analyze polarization
    print("\n[2] POLARIZATION DYNAMICS")
    print("-" * 40)

    polar_df = load_polarization_data()
    if polar_df is not None and len(polar_df) > 0:
        print(f"   Data points: {len(polar_df)}")
        if "polarization" in polar_df.columns:
            avg_polar = polar_df["polarization"].mean()
            std_polar = polar_df["polarization"].std()
            print(f"   Average Polarization: {avg_polar:.3f}")
            print(f"   Std Polarization: {std_polar:.3f}")
        else:
            print(f"   Columns: {list(polar_df.columns)}")
    else:
        print("   [WARN] No polarization data available")

    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)

    if results:
        avg_eq = np.mean([r["equilibrium_score"] for r in results])
        avg_entropy = np.mean([r["entropy"] for r in results])
        total_nodes = sum(r["n_nodes"] for r in results)
        total_edges = sum(r["n_edges"] for r in results)

        print(f"   Networks analyzed: {len(results)}")
        print(f"   Total nodes: {total_nodes:,}")
        print(f"   Total edges: {total_edges:,}")
        print(f"   Average Equilibrium Score: {avg_eq:.3f}")
        print(f"   Average Entropy: {avg_entropy:.2f}")

        # Grade
        if avg_eq > 0.3:
            grade = "***** STABLE EQUILIBRIUM"
            status = "PASS"
        elif avg_eq > 0.2:
            grade = "**** MODERATE BALANCE"
            status = "PASS"
        else:
            grade = "*** LOW BALANCE"
            status = "WARN"

        print(f"\n   Grade: {grade}")
        print(f"   Status: {status}")

        return {
            "status": status,
            "networks": len(results),
            "avg_equilibrium": avg_eq,
            "results": results,
        }
    else:
        print("   [FAIL] No networks analyzed")
        return {"status": "FAIL", "error": "No data"}


if __name__ == "__main__":
    result = run_test()
    print(f"\n[OK] Test complete: {result['status']}")
