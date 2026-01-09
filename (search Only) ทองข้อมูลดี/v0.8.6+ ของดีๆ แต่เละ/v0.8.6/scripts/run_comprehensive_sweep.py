#!/usr/bin/env python
"""
Comprehensive UET Parameter Sweep - 500K Total Runs

Sweeps over:
- Grid sizes: 16, 32, 64
- Time durations: 1, 2, 5, 10
- Parameter combinations: kappa x beta x s
- Simulation types: stability, seizure, traffic, galaxy

Usage:
    python scripts/run_comprehensive_sweep.py --total 500000
"""
import numpy as np
from pathlib import Path
from joblib import Parallel, delayed
import json
import time
import argparse
from itertools import product


def run_uet_single(params):
    """Run single UET simulation with full parameter set."""
    seed = params['seed']
    N = params['N']
    T = params['T']
    dt = params['dt']
    kappa = params['kappa']
    beta = params['beta']
    s = params['s']
    sim_type = params['type']
    
    np.random.seed(seed)
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    # Type-specific initial conditions
    if sim_type == "galaxy":
        x = np.linspace(-1, 1, N)
        X, Y = np.meshgrid(x, x)
        R = np.sqrt(X**2 + Y**2) + 0.01
        C = 0.5 * np.exp(-R**2 / (2 * 0.3**2))
        I = 0.3 * np.exp(-R / 0.5)
    elif sim_type == "seizure":
        C = np.random.randn(N, N) * 0.2
        I = np.random.randn(N, N) * 0.1
    elif sim_type == "traffic":
        C = np.random.rand(N, N) * 0.5
        I = np.ones((N, N)) * 0.3
    else:  # stability
        C = np.random.randn(N, N) * 0.1
        I = np.random.randn(N, N) * 0.1
    
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
        I = np.clip(I, -5, 5)
        
        # Compute Omega periodically
        if step % max(1, n_steps // 10) == 0:
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
    
    return {
        "seed": seed,
        "N": N,
        "T": T,
        "kappa": kappa,
        "beta": beta,
        "s": s,
        "type": sim_type,
        "omega_final": omega_final,
        "omega_var": omega_var,
        "stable": omega_var < 1e6 and not np.isnan(omega_final),
    }


def generate_parameter_grid(total_runs):
    """Generate parameter combinations to reach target runs."""
    
    # Parameter options
    grid_sizes = [16, 32, 64, 128]              # 4 sizes
    time_durations = [1.0, 2.0, 5.0, 10.0]      # 4 durations
    kappas = [0.1, 0.3, 0.5, 1.0]               # 4 kappa
    betas = [0.1, 0.5, 1.0, 1.5]                # 4 beta
    s_values = [-0.5, 0.0, 0.5]                 # 3 bias
    types = ["stability", "seizure", "traffic", "galaxy"]  # 4 types
    
    # Calculate per-combo
    n_combos = len(grid_sizes) * len(time_durations) * len(kappas) * len(betas) * len(s_values) * len(types)
    seeds_per_combo = max(1, total_runs // n_combos)
    
    print(f"  Grid sizes: {grid_sizes}")
    print(f"  Time durations: {time_durations}")
    print(f"  Combinations: {n_combos}")
    print(f"  Seeds per combo: {seeds_per_combo}")
    print(f"  Total runs: {n_combos * seeds_per_combo:,}")
    
    params_list = []
    for N, T, kappa, beta, s, sim_type in product(grid_sizes, time_durations, kappas, betas, s_values, types):
        for seed in range(seeds_per_combo):
            params_list.append({
                "seed": seed,
                "N": N,
                "T": T,
                "dt": 0.02,
                "kappa": kappa,
                "beta": beta,
                "s": s,
                "type": sim_type,
            })
    
    return params_list


def main():
    parser = argparse.ArgumentParser(description="Comprehensive UET Sweep")
    parser.add_argument("--total", type=int, default=10000, help="Target total runs")
    parser.add_argument("--n_jobs", type=int, default=-1, help="Parallel jobs")
    parser.add_argument("--out", default="sweep_results", help="Output directory")
    
    args = parser.parse_args()
    
    print("="*70)
    print("🌐 COMPREHENSIVE UET PARAMETER SWEEP")
    print("="*70)
    print(f"  Target runs: {args.total:,}")
    
    # Generate parameter grid
    params_list = generate_parameter_grid(args.total)
    actual_runs = len(params_list)
    
    print(f"  Actual runs: {actual_runs:,}")
    print("="*70)
    
    start_time = time.time()
    
    # Run in parallel
    results = Parallel(n_jobs=args.n_jobs, verbose=10)(
        delayed(run_uet_single)(p) for p in params_list
    )
    
    elapsed = time.time() - start_time
    
    # Analyze by type
    print("\n" + "="*70)
    print("📊 RESULTS BY SIMULATION TYPE")
    print("="*70)
    
    summary_by_type = {}
    for sim_type in ["stability", "seizure", "traffic", "galaxy"]:
        type_results = [r for r in results if r["type"] == sim_type]
        omegas = [r["omega_final"] for r in type_results if r["stable"]]
        stable_count = sum(1 for r in type_results if r["stable"])
        
        if omegas:
            summary_by_type[sim_type] = {
                "count": len(type_results),
                "stable": stable_count,
                "stability_rate": stable_count / len(type_results),
                "omega_mean": float(np.mean(omegas)),
                "omega_std": float(np.std(omegas)),
                "omega_ci_95": [float(np.percentile(omegas, 2.5)), float(np.percentile(omegas, 97.5))],
            }
            print(f"\n  {sim_type.upper()}")
            print(f"    Runs: {len(type_results):,}")
            print(f"    Stable: {stable_count:,} ({stable_count/len(type_results)*100:.1f}%)")
            print(f"    Ω mean: {np.mean(omegas):.2f} ± {np.std(omegas):.2f}")
    
    # Analyze by grid size
    print("\n" + "="*70)
    print("📊 RESULTS BY GRID SIZE")
    print("="*70)
    
    summary_by_N = {}
    for N in [16, 32, 64]:
        n_results = [r for r in results if r["N"] == N]
        stable_count = sum(1 for r in n_results if r["stable"])
        summary_by_N[N] = {
            "count": len(n_results),
            "stable": stable_count,
            "stability_rate": stable_count / len(n_results) if n_results else 0,
        }
        print(f"  N={N}: {stable_count:,}/{len(n_results):,} stable ({stable_count/len(n_results)*100:.1f}%)")
    
    print("\n" + "="*70)
    print("⏱️ PERFORMANCE")
    print("="*70)
    print(f"  Total time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Speed: {actual_runs/elapsed:.1f} runs/sec")
    print(f"  Time for 500K: {500000/actual_runs*elapsed/60:.1f} min")
    print("="*70)
    
    # Save results
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    
    full_summary = {
        "total_runs": actual_runs,
        "elapsed_seconds": elapsed,
        "runs_per_second": actual_runs / elapsed,
        "by_type": summary_by_type,
        "by_grid_size": summary_by_N,
    }
    
    with open(out_dir / "comprehensive_summary.json", "w") as f:
        json.dump(full_summary, f, indent=2)
    
    # Save all results for later analysis
    with open(out_dir / "all_results.json", "w") as f:
        json.dump(results, f)
    
    print(f"\n💾 Saved to: {out_dir}/")


if __name__ == "__main__":
    main()
