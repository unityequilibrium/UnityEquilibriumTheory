#!/usr/bin/env python
"""
Batch UET Simulation Runner for Large-Scale Studies

Runs thousands of simulations in parallel for uncertainty quantification.

Usage:
    python scripts/run_batch_simulation.py --n_runs 100 --n_jobs 8
    python scripts/run_batch_simulation.py --n_runs 10000 --n_jobs -1
"""
import numpy as np
from pathlib import Path
from joblib import Parallel, delayed
import json
import time
import argparse


def run_uet_single(seed, N=32, T=2.0, dt=0.02, kappa=0.3, beta=0.5, s=0.0):
    """Run single UET simulation with given seed."""
    np.random.seed(seed)
    
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    # Random initial conditions
    C = np.random.randn(N, N) * 0.1
    I = np.random.randn(N, N) * 0.1
    
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
    
    # Compute final Omega
    gx = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
    gy = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
    kinetic = 0.5 * kappa * (gx**2 + gy**2)
    potential = (C**2 - 1)**2 / 4
    coupling = 0.5 * beta * (C - I)**2
    omega = np.sum(kinetic + potential + coupling) * dx**2
    
    return {
        "seed": seed,
        "omega": float(omega),
        "C_mean": float(np.mean(C)),
        "I_mean": float(np.mean(I)),
    }


def main():
    parser = argparse.ArgumentParser(description="Batch UET Simulation")
    parser.add_argument("--n_runs", type=int, default=100, help="Number of runs")
    parser.add_argument("--n_jobs", type=int, default=-1, help="Number of parallel jobs (-1 = all cores)")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    parser.add_argument("--out", default="batch_results", help="Output directory")
    
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 BATCH UET SIMULATION")
    print("="*60)
    print(f"  Runs: {args.n_runs:,}")
    print(f"  Jobs: {args.n_jobs}")
    print(f"  Grid: {args.N}x{args.N}")
    print("="*60)
    
    start_time = time.time()
    
    # Run in parallel
    results = Parallel(n_jobs=args.n_jobs, verbose=10)(
        delayed(run_uet_single)(seed, N=args.N) for seed in range(args.n_runs)
    )
    
    elapsed = time.time() - start_time
    
    # Analyze results
    omegas = [r["omega"] for r in results]
    omega_mean = np.mean(omegas)
    omega_std = np.std(omegas)
    omega_ci_low = np.percentile(omegas, 2.5)
    omega_ci_high = np.percentile(omegas, 97.5)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  Ω mean:  {omega_mean:.4f}")
    print(f"  Ω std:   {omega_std:.4f}")
    print(f"  95% CI:  [{omega_ci_low:.4f}, {omega_ci_high:.4f}]")
    print(f"  Time:    {elapsed:.2f}s")
    print(f"  Speed:   {args.n_runs/elapsed:.1f} runs/sec")
    print("="*60)
    
    # Estimate time for 500,000
    time_500k = (500_000 / args.n_runs) * elapsed
    print(f"\n⏱️ Estimated time for 500,000 runs: {time_500k/3600:.1f} hours")
    
    # Save results
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    
    summary = {
        "n_runs": args.n_runs,
        "omega_mean": omega_mean,
        "omega_std": omega_std,
        "omega_ci_95": [omega_ci_low, omega_ci_high],
        "elapsed_seconds": elapsed,
        "runs_per_second": args.n_runs / elapsed,
    }
    
    with open(out_dir / "batch_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Saved to: {out_dir}/batch_summary.json")


if __name__ == "__main__":
    main()
