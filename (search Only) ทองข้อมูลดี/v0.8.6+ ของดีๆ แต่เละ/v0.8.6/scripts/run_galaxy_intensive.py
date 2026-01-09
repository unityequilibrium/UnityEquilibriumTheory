#!/usr/bin/env python
"""
Galaxy-Only Intensive Sweep

Focus on galaxy simulations with optimized parameters for stability.
Uses optimal params from auto-tuning: kappa=0.01, beta=1.82, s=-0.22

Usage:
    python scripts/run_galaxy_intensive.py --n_runs 100000 --n_jobs -1
"""
import numpy as np
from pathlib import Path
from joblib import Parallel, delayed
import json
import time
import argparse


def run_galaxy_single(params):
    """Run single galaxy simulation."""
    seed = params['seed']
    N = params['N']
    T = params['T']
    dt = params['dt']
    kappa = params['kappa']
    beta = params['beta']
    s = params['s']
    
    np.random.seed(seed)
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    # Galaxy initial conditions
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2) + 0.01
    
    # Visible matter (exponential disk + bulge)
    C = 0.5 * np.exp(-R**2 / (2 * 0.3**2)) + 0.3 * np.exp(-R / 0.4)
    # Dark matter (NFW-like halo)
    I = 0.4 * np.exp(-R / 0.5)
    
    omega_history = []
    
    for step in range(n_steps):
        # Laplacian
        lap_C = (np.roll(C, 1, 0) + np.roll(C, -1, 0) + 
                 np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C) / dx**2
        lap_I = (np.roll(I, 1, 0) + np.roll(I, -1, 0) + 
                 np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4*I) / dx**2
        
        # Potential
        dV_C = C * (C**2 - 1)
        dV_I = I * (I**2 - 1)
        
        # Update
        C = C + dt * (kappa * lap_C - dV_C - beta * (C - I) + s)
        I = I + dt * (kappa * lap_I - dV_I - beta * (I - C))
        
        # Clip
        C = np.clip(C, -5, 5)
        I = I + np.clip(I, -5, 5)
        
        # Compute Omega periodically
        if step % max(1, n_steps // 20) == 0:
            gx = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
            gy = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
            kinetic = 0.5 * kappa * (gx**2 + gy**2)
            potential = (C**2 - 1)**2 / 4
            coupling = 0.5 * beta * (C - I)**2
            omega = float(np.sum(kinetic + potential + coupling) * dx**2)
            omega_history.append(omega)
    
    # Final stats
    omega_final = omega_history[-1] if omega_history else 0
    omega_var = float(np.var(omega_history)) if len(omega_history) > 1 else 0
    omega_mean = float(np.mean(omega_history)) if omega_history else 0
    
    # Check stability
    stable = (omega_var < 1e6 and 
              not np.isnan(omega_final) and 
              not np.isinf(omega_final) and
              omega_final > 0)
    
    return {
        "seed": seed,
        "N": N,
        "T": T,
        "kappa": kappa,
        "beta": beta,
        "s": s,
        "omega_final": omega_final,
        "omega_mean": omega_mean,
        "omega_var": omega_var,
        "stable": stable,
    }


def main():
    parser = argparse.ArgumentParser(description="Galaxy Intensive Sweep")
    parser.add_argument("--n_runs", type=int, default=10000, help="Number of runs")
    parser.add_argument("--n_jobs", type=int, default=-1, help="Parallel jobs")
    parser.add_argument("--out", default="galaxy_intensive_results", help="Output directory")
    
    args = parser.parse_args()
    
    print("="*70)
    print("🌌 GALAXY INTENSIVE SWEEP")
    print("="*70)
    print(f"  Target runs: {args.n_runs:,}")
    
    # Optimal parameters from auto-tuning
    optimal_kappa = 0.01
    optimal_beta = 1.82
    optimal_s = -0.22
    
    # Parameter variations around optimal
    kappa_range = [0.005, 0.01, 0.02, 0.05]
    beta_range = [1.5, 1.82, 2.0, 2.5]
    s_range = [-0.3, -0.22, -0.1, 0.0]
    
    grid_sizes = [32, 64, 128]
    time_durations = [2.0, 5.0, 10.0]
    
    # Generate parameter combinations
    from itertools import product
    
    n_combos = len(kappa_range) * len(beta_range) * len(s_range) * len(grid_sizes) * len(time_durations)
    seeds_per_combo = max(1, args.n_runs // n_combos)
    
    print(f"  Kappa range: {kappa_range}")
    print(f"  Beta range: {beta_range}")
    print(f"  S range: {s_range}")
    print(f"  Grid sizes: {grid_sizes}")
    print(f"  Time durations: {time_durations}")
    print(f"  Combinations: {n_combos}")
    print(f"  Seeds per combo: {seeds_per_combo}")
    print(f"  Total runs: {n_combos * seeds_per_combo:,}")
    print("="*70)
    
    params_list = []
    for kappa, beta, s, N, T in product(kappa_range, beta_range, s_range, grid_sizes, time_durations):
        for seed in range(seeds_per_combo):
            params_list.append({
                "seed": seed,
                "N": N,
                "T": T,
                "dt": 0.01,  # Smaller dt for stability
                "kappa": kappa,
                "beta": beta,
                "s": s,
            })
    
    start_time = time.time()
    
    # Run in parallel
    results = Parallel(n_jobs=args.n_jobs, verbose=10)(
        delayed(run_galaxy_single)(p) for p in params_list
    )
    
    elapsed = time.time() - start_time
    
    # Analyze results
    stable_results = [r for r in results if r["stable"]]
    unstable_results = [r for r in results if not r["stable"]]
    
    print("\n" + "="*70)
    print("📊 GALAXY RESULTS")
    print("="*70)
    print(f"  Total runs: {len(results):,}")
    print(f"  Stable: {len(stable_results):,} ({len(stable_results)/len(results)*100:.1f}%)")
    print(f"  Unstable: {len(unstable_results):,} ({len(unstable_results)/len(results)*100:.1f}%)")
    
    if stable_results:
        omegas = [r["omega_final"] for r in stable_results]
        print(f"\n  Ω mean: {np.mean(omegas):.2f}")
        print(f"  Ω std: {np.std(omegas):.2f}")
        print(f"  Ω 95% CI: [{np.percentile(omegas, 2.5):.2f}, {np.percentile(omegas, 97.5):.2f}]")
    
    # Analyze by grid size
    print("\n" + "="*70)
    print("📊 STABILITY BY GRID SIZE")
    print("="*70)
    
    for N in grid_sizes:
        n_results = [r for r in results if r["N"] == N]
        n_stable = sum(1 for r in n_results if r["stable"])
        print(f"  N={N}: {n_stable:,}/{len(n_results):,} stable ({n_stable/len(n_results)*100:.1f}%)")
    
    # Find best parameters
    print("\n" + "="*70)
    print("🎯 BEST PARAMETERS (highest stability)")
    print("="*70)
    
    # Group by parameter combo
    from collections import defaultdict
    combo_stats = defaultdict(lambda: {"stable": 0, "total": 0})
    
    for r in results:
        key = (r["kappa"], r["beta"], r["s"])
        combo_stats[key]["total"] += 1
        if r["stable"]:
            combo_stats[key]["stable"] += 1
    
    # Sort by stability rate
    sorted_combos = sorted(combo_stats.items(), 
                           key=lambda x: x[1]["stable"]/x[1]["total"], 
                           reverse=True)
    
    for i, (combo, stats) in enumerate(sorted_combos[:5]):
        rate = stats["stable"] / stats["total"] * 100
        print(f"  {i+1}. κ={combo[0]:.3f}, β={combo[1]:.2f}, s={combo[2]:.2f} → {rate:.1f}% stable")
    
    print("\n" + "="*70)
    print("⏱️ PERFORMANCE")
    print("="*70)
    print(f"  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Speed: {len(results)/elapsed:.1f} runs/sec")
    print("="*70)
    
    # Save results
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    
    summary = {
        "total_runs": len(results),
        "stable_runs": len(stable_results),
        "stability_rate": len(stable_results) / len(results),
        "elapsed_seconds": elapsed,
        "runs_per_second": len(results) / elapsed,
        "best_params": {
            "kappa": sorted_combos[0][0][0],
            "beta": sorted_combos[0][0][1],
            "s": sorted_combos[0][0][2],
            "stability_rate": sorted_combos[0][1]["stable"] / sorted_combos[0][1]["total"],
        } if sorted_combos else None,
    }
    
    with open(out_dir / "galaxy_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    with open(out_dir / "galaxy_all_results.json", "w") as f:
        json.dump(results, f)
    
    print(f"\n💾 Saved to: {out_dir}/")


if __name__ == "__main__":
    main()
