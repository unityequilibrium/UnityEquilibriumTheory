#!/usr/bin/env python
"""
UET GPU-Accelerated Simulation using JAX

100-1000x faster than NumPy on GPU!

Requirements:
    pip install jax jaxlib  # CPU
    pip install jax[cuda12]  # NVIDIA GPU
    pip install jax[metal]   # Apple M1/M2/M3

Usage:
    python scripts/run_uet_jax.py --n_runs 10000 --N 64
    python scripts/run_uet_jax.py --n_runs 100000 --device gpu
    
New modular usage:
    from uet_core.solvers import UETSolver
    solver = UETSolver(N=64, kappa=0.3, beta=0.5)
    results = solver.run_batch(10000)
"""
import sys
import json
import argparse
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from uet_core.solvers import UETSolver, UETParams, check_jax_devices, JAX_AVAILABLE

# Legacy imports for backwards compatibility
try:
    import jax
except ImportError:
    jax = None


def main():
    parser = argparse.ArgumentParser(description="UET JAX GPU Simulation")
    parser.add_argument("--n_runs", type=int, default=1000)
    parser.add_argument("--N", type=int, default=32)
    parser.add_argument("--T", type=float, default=2.0)
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument("--kappa", type=float, default=0.3)
    parser.add_argument("--beta", type=float, default=0.5)
    parser.add_argument("--s", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "gpu"])
    parser.add_argument("--out", default="jax_results")
    
    args = parser.parse_args()
    
    # Force CPU if requested
    if args.device == "cpu" and jax is not None:
        jax.config.update('jax_platform_name', 'cpu')
    
    print("="*70)
    print("🚀 UET JAX GPU-ACCELERATED SIMULATION")
    print("="*70)
    print(f"  Runs: {args.n_runs:,}")
    print(f"  Grid: {args.N}x{args.N}")
    print(f"  T={args.T}, dt={args.dt}")
    print(f"  κ={args.kappa}, β={args.beta}, s={args.s}")
    
    # Check device
    device_type, devices = check_jax_devices()
    print(f"  JAX devices: {devices}")
    print(f"  Platform: {device_type}")
    
    if JAX_AVAILABLE:
        print("  Using JAX acceleration! 🚀")
    else:
        print("  Using NumPy fallback (slower)")
    
    # Create solver with parameters
    params = UETParams(
        N=args.N,
        T=args.T,
        dt=args.dt,
        kappa=args.kappa,
        beta=args.beta,
        s=args.s,
        seed=args.seed,
    )
    
    solver = UETSolver(params=params)
    results = solver.run_batch(args.n_runs, verbose=True)
    
    # Print results
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"  Ω mean: {results['omega_mean']:.4f}")
    print(f"  Ω std:  {results['omega_std']:.4f}")
    print(f"  95% CI: [{results['omega_ci_95'][0]:.4f}, {results['omega_ci_95'][1]:.4f}]")
    print(f"\n  Time:   {results['elapsed_seconds']:.2f}s")
    print(f"  Speed:  {results['runs_per_second']:.1f} runs/sec")
    print("="*70)
    
    # Comparison
    numpy_speed = 87  # From earlier benchmark
    speedup = results['runs_per_second'] / numpy_speed
    print(f"\n  Speedup vs NumPy parallel: {speedup:.1f}x")
    
    # Save results
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    
    summary = {
        "n_runs": args.n_runs,
        "grid_size": args.N,
        "omega_mean": results['omega_mean'],
        "omega_std": results['omega_std'],
        "omega_ci_95": results['omega_ci_95'],
        "elapsed_seconds": results['elapsed_seconds'],
        "runs_per_second": results['runs_per_second'],
        "device": results['device'],
        "backend": results['backend'],
        "jax_available": JAX_AVAILABLE,
        "params": results['params'],
    }
    
    with open(out_dir / "jax_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Saved to: {out_dir}/jax_summary.json")


if __name__ == "__main__":
    main()
